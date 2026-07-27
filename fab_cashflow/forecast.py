from __future__ import annotations

import frappe
from frappe.utils import add_days, add_months, flt, formatdate, get_first_day, get_last_day, getdate, today


def _settings():
    return frappe.get_single("Cash Flow Settings")


@frappe.whitelist()
def rebuild_forecast() -> dict:
    """Regenerate materialized Cash Flow Events from every source within the
    horizon. Manual events (generated = 0) are preserved."""
    s = _settings()
    company = s.company
    start = getdate(today())
    end = add_days(start, int(s.horizon_days or 120))
    grace = int(s.overdue_grace_days or 0)
    cutoff = add_days(start, -grace) if grace else None

    frappe.db.delete("Cash Flow Event", {"generated": 1})

    events = []
    events += _customer_inflows(company, start, end, cutoff)
    events += _supplier_outflows(company, start, end, cutoff)
    events += _recurring_outflows(start, end)
    events += _amex_settlements(s, start, end)
    events += _tax_deadlines(company, start, end)
    events += _payroll_outflows(company, start, end, s)

    for e in events:
        doc = frappe.get_doc({"doctype": "Cash Flow Event", "generated": 1, **e})
        doc.flags.ignore_permissions = True
        doc.insert()
    frappe.db.commit()
    return {"events": len(events), "from": str(start), "to": str(end)}


def _monthly_average_credit(account, months, company) -> float:
    """Average monthly credit posted on an account over the last N whole months.

    Used to project payroll from history while there is no HR master data yet;
    once JetHR posts real Salary Slips the same accounts carry the real figures,
    so the projection tracks reality without a code change.
    """
    if not account or months <= 0:
        return 0.0
    period_end = get_first_day(today())
    period_start = add_months(period_end, -months)
    total = frappe.db.sql(
        """select sum(credit) from `tabGL Entry`
           where account=%s and company=%s and is_cancelled=0
           and posting_date>=%s and posting_date<%s""",
        (account, company, period_start, period_end),
    )[0][0]
    return round(flt(total) / months, 2)


def _on_day(month_start, day) -> "date":
    last = getdate(get_last_day(month_start)).day
    return getdate(month_start).replace(day=min(int(day or 1), last))


def _f24_due_date(month_start, base_day):
    """National F24 rule: the 16th, moved to the 20th in August (Ferragosto), and
    pushed to the next Monday when it lands on a weekend."""
    day = 20 if getdate(month_start).month == 8 else int(base_day or 16)
    due = _on_day(month_start, day)
    while getdate(due).weekday() >= 5:
        due = add_days(due, 1)
    return due


def _payroll_outflows(company, start, end, settings):
    """Project monthly net salary and payroll F24 from the recent GL average."""
    months = int(settings.payroll_lookback_months or 0)
    if months <= 0:
        return []
    net = _monthly_average_credit(settings.payroll_net_account, months, company)
    f24 = _monthly_average_credit(settings.payroll_f24_account, months, company)
    if not net and not f24:
        return []

    out = []
    cursor = get_first_day(start)
    while cursor <= end:
        if net > 0:
            day = _on_day(cursor, settings.payroll_pay_day or 10)
            if start <= day <= end:
                out.append(_event(day, "Outflow", net, "Payroll", "payroll-net", "Stipendi netti"))
        if f24 > 0:
            day = _f24_due_date(cursor, settings.payroll_f24_day)
            if start <= day <= end:
                out.append(_event(day, "Outflow", f24, "Payroll", "payroll-f24", "F24 personale (INPS/IRPEF)"))
        cursor = add_months(cursor, 1)
    return out


def opening_balance(settings=None) -> float:
    """Cash on the tracked account as of today, the forecast's starting point.

    Balance is taken at today's date on purpose: entries already posted with a
    future date (e.g. scheduled F24 payments) must not lower the starting point.
    Those future movements still reach the forecast as projected outflows through
    their own sources, so counting them in the opening too would be double.
    """
    settings = settings or _settings()
    if not settings.cash_account:
        return 0.0
    from erpnext.accounts.utils import get_balance_on

    return flt(get_balance_on(settings.cash_account, date=today()))


def _event(date, direction, amount, source_type, ref, description):
    return {
        "event_date": getdate(date),
        "direction": direction,
        "amount": flt(amount, 2),
        "source_type": source_type,
        "source_ref": ref,
        "description": description,
    }


def _due(date, start):
    d = getdate(date or start)
    return start if d < start else d  # overdue items land on the first forecast day


def _stale(due_raw, cutoff):
    """Overdue beyond the grace window: backlog to reconcile, not future cash."""
    return cutoff is not None and due_raw < cutoff


def _overdue_label(party, due_raw, start):
    """Flag items pulled onto the first forecast day with their real due date."""
    if due_raw < start:
        return f"{party} (scaduta {formatdate(due_raw, 'dd/MM/yyyy')})"
    return party


def _customer_inflows(company, start, end, cutoff=None):
    out = []
    for r in frappe.get_all(
        "Sales Invoice",
        filters={"company": company, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "customer", "due_date", "outstanding_amount"],
    ):
        due_raw = getdate(r.due_date or start)
        if _stale(due_raw, cutoff):
            continue
        due = _due(r.due_date, start)
        if due <= end:
            label = _overdue_label(r.customer, due_raw, start)
            out.append(_event(due, "Inflow", r.outstanding_amount, "Sales Invoice", r.name, label))
    return out


def _supplier_outflows(company, start, end, cutoff=None):
    out = []
    for r in frappe.get_all(
        "Purchase Invoice",
        filters={"company": company, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "supplier", "due_date", "outstanding_amount"],
    ):
        due_raw = getdate(r.due_date or start)
        if _stale(due_raw, cutoff):
            continue
        due = _due(r.due_date, start)
        if due <= end:
            label = _overdue_label(r.supplier, due_raw, start)
            out.append(_event(due, "Outflow", r.outstanding_amount, "Purchase Invoice", r.name, label))
    return out


def _invoice_covers_period(supplier, d, frequency, amount, tolerance_pct):
    """A real Purchase Invoice for this recurring charge already exists in d's period.

    The recurring payment only fills periods with no actual invoice yet: once the
    real invoice lands it is either projected by _supplier_outflows (still open)
    or already out of the bank balance (paid), so projecting it again would double
    count. Matching is by supplier + period + amount within tolerance, not supplier
    alone: a supplier can bill several streams in one month (e.g. Google licenses
    vs GCP usage), and a differently-sized invoice must not suppress this charge.
    Period is the calendar month for Monthly, the calendar year for Annual; credit
    notes never count as coverage.
    """
    from frappe.utils import get_first_day, get_last_day, get_year_ending, get_year_start

    period_start, period_end = (
        (get_first_day(d), get_last_day(d)) if frequency == "Monthly"
        else (get_year_start(d), get_year_ending(d))
    )
    band = abs(flt(amount)) * flt(tolerance_pct) / 100.0
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={
            "supplier": supplier,
            "docstatus": 1,
            "is_return": 0,
            "posting_date": ["between", [period_start, period_end]],
        },
        pluck="grand_total",
    )
    return any(abs(flt(total) - flt(amount)) <= band for total in invoices)


def _recurring_outflows(start, end):
    out = []
    for r in frappe.get_all(
        "Recurring Payment",
        filters={"active": 1},
        fields=["name", "supplier", "amount", "frequency", "next_due_date", "description", "match_tolerance"],
    ):
        step = 1 if r.frequency == "Monthly" else 12
        tolerance = flt(r.match_tolerance) if r.match_tolerance is not None else 20.0
        d = getdate(r.next_due_date)
        while d <= end:
            if d >= start and not _invoice_covers_period(r.supplier, d, r.frequency, r.amount, tolerance):
                out.append(
                    _event(d, "Outflow", r.amount, "Recurring Payment", r.name, r.description or r.supplier)
                )
            d = add_months(d, step)
    return out


def _amex_settlements(s, start, end):
    """One settlement per cycle, on the charge day. A settlement on the charge day
    of month M covers the cycle from cycle_day of month M-2 to the day before
    cycle_day of month M-1 (e.g. charge 3 Mar covers 16 Jan to 15 Feb). Amount is
    the net charges booked on the Amex account in that cycle."""
    out = []
    if not s.amex_account:
        return out
    cycle_day = int(s.amex_cycle_day or 16)
    charge_day = min(int(s.amex_charge_day or 3), 28)

    month = add_months(start, -1)
    for _ in range(14):  # cover the window plus margins
        settle = getdate(f"{month.year}-{month.month:02d}-{charge_day:02d}")
        if start <= settle <= end:
            cycle_start = getdate(f"{add_months(month, -2).year}-{add_months(month, -2).month:02d}-{cycle_day:02d}")
            cycle_end = add_days(getdate(f"{add_months(month, -1).year}-{add_months(month, -1).month:02d}-{cycle_day:02d}"), -1)
            amount = _amex_cycle_amount(s.amex_account, cycle_start, cycle_end)
            if amount > 0:
                out.append(
                    _event(settle, "Outflow", amount, "Amex Settlement", None, f"Amex {cycle_start} to {cycle_end}")
                )
        month = add_months(month, 1)
    return out


def _amex_cycle_amount(account, cycle_start, cycle_end) -> float:
    rows = frappe.get_all(
        "GL Entry",
        filters={"account": account, "posting_date": ["between", [cycle_start, cycle_end]], "is_cancelled": 0},
        fields=["debit", "credit"],
    )
    # a purchase paid via Amex credits the Amex account; the net credit is the spend
    net = sum(flt(r.credit) - flt(r.debit) for r in rows)
    return net if net > 0 else 0.0


def _tax_deadlines(company, start, end):
    out = []
    if not frappe.db.exists("DocType", "Tax Calendar Event"):
        return out
    for r in frappe.get_all(
        "Tax Calendar Event",
        filters={"company": company, "event_date": ["between", [start, end]], "amount": [">", 0]},
        fields=["name", "event_date", "amount", "direction", "event_type"],
    ):
        direction = "Inflow" if (r.direction or "").lower().startswith("in") else "Outflow"
        out.append(_event(r.event_date, direction, r.amount, "Tax Deadline", r.name, r.event_type or "Tax"))
    return out
