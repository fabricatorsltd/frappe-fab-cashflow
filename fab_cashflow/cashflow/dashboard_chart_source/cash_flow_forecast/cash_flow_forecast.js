frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Cash Flow Forecast"] = {
	method: "fab_cashflow.cashflow.dashboard_chart_source.cash_flow_forecast.cash_flow_forecast.get",
	filters: [],
};
