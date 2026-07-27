from __future__ import annotations

import frappe
from frappe.utils import add_days, add_months, flt, getdate, today


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

    frappe.db.delete("Cash Flow Event", {"generated": 1})

    events = []
    events += _customer_inflows(company, start, end)
    events += _supplier_outflows(company, start, end)
    events += _recurring_outflows(start, end)
    events += _amex_settlements(s, start, end)
    events += _tax_deadlines(company, start, end)

    for e in events:
        doc = frappe.get_doc({"doctype": "Cash Flow Event", "generated": 1, **e})
        doc.flags.ignore_permissions = True
        doc.insert()
    frappe.db.commit()
    return {"events": len(events), "from": str(start), "to": str(end)}


def opening_balance(settings=None) -> float:
    """Current balance of the tracked cash account, the forecast's starting point."""
    settings = settings or _settings()
    if not settings.cash_account:
        return 0.0
    from erpnext.accounts.utils import get_balance_on

    return flt(get_balance_on(settings.cash_account))


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


def _customer_inflows(company, start, end):
    out = []
    for r in frappe.get_all(
        "Sales Invoice",
        filters={"company": company, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "customer", "due_date", "outstanding_amount"],
    ):
        due = _due(r.due_date, start)
        if due <= end:
            out.append(_event(due, "Inflow", r.outstanding_amount, "Sales Invoice", r.name, r.customer))
    return out


def _supplier_outflows(company, start, end):
    out = []
    for r in frappe.get_all(
        "Purchase Invoice",
        filters={"company": company, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "supplier", "due_date", "outstanding_amount"],
    ):
        due = _due(r.due_date, start)
        if due <= end:
            out.append(_event(due, "Outflow", r.outstanding_amount, "Purchase Invoice", r.name, r.supplier))
    return out


def _recurring_outflows(start, end):
    out = []
    for r in frappe.get_all(
        "Recurring Payment",
        filters={"active": 1},
        fields=["name", "supplier", "amount", "frequency", "next_due_date", "description"],
    ):
        step = 1 if r.frequency == "Monthly" else 12
        d = getdate(r.next_due_date)
        while d <= end:
            if d >= start:
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
