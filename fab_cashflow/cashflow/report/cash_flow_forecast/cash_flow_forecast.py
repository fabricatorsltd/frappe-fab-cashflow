import frappe
from frappe.utils import flt

from fab_cashflow.forecast import opening_balance


def execute(filters=None):
    columns = [
        {"label": "Date", "fieldname": "event_date", "fieldtype": "Date", "width": 100},
        {"label": "Description", "fieldname": "description", "fieldtype": "Data", "width": 240},
        {"label": "Source", "fieldname": "source_type", "fieldtype": "Data", "width": 140},
        {"label": "Inflow", "fieldname": "inflow", "fieldtype": "Currency", "width": 110},
        {"label": "Outflow", "fieldname": "outflow", "fieldtype": "Currency", "width": 110},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": 130},
    ]

    balance = opening_balance()
    data = [{"description": "Opening balance", "balance": balance}]

    events = frappe.get_all(
        "Cash Flow Event",
        fields=["event_date", "description", "source_type", "direction", "amount"],
        order_by="event_date asc, direction desc",
    )
    for e in events:
        inflow = flt(e.amount) if e.direction == "Inflow" else 0
        outflow = flt(e.amount) if e.direction == "Outflow" else 0
        balance += inflow - outflow
        data.append(
            {
                "event_date": e.event_date,
                "description": e.description,
                "source_type": e.source_type,
                "inflow": inflow,
                "outflow": outflow,
                "balance": balance,
            }
        )
    return columns, data
