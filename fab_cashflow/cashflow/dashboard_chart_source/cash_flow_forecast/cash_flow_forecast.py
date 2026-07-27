# Copyright (c) 2026, Fabricators and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	"""Projected end-of-day bank balance across the forecast horizon.

	Reads the generated Cash Flow Event rows, nets them per day and walks the
	running balance forward from the current bank balance, so the chart shows one
	clean point per day instead of one per event.
	"""
	from fab_cashflow.forecast import opening_balance

	events = frappe.get_all(
		"Cash Flow Event",
		fields=["event_date", "direction", "amount"],
		order_by="event_date asc",
	)

	daily: dict[str, float] = {}
	for event in events:
		delta = flt(event.amount) if event.direction == "Inflow" else -flt(event.amount)
		day = str(event.event_date)
		daily[day] = daily.get(day, 0.0) + delta

	balance = opening_balance()
	labels: list[str] = []
	values: list[float] = []
	for day in sorted(daily):
		balance += daily[day]
		labels.append(day)
		values.append(round(balance, 2))

	return {
		"labels": labels,
		"datasets": [{"name": _("Projected Balance"), "values": values, "chartType": "line"}],
		"type": "Line",
	}
