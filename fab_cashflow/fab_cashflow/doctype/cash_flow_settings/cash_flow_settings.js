frappe.ui.form.on("Cash Flow Settings", {
	rebuild(frm) {
		frappe.call({
			method: "fab_cashflow.forecast.rebuild_forecast",
			freeze: true,
			freeze_message: __("Rebuilding cash flow forecast..."),
			callback: (r) => {
				const m = r.message || {};
				frappe.msgprint({
					title: __("Forecast rebuilt"),
					message: __("{0} events from {1} to {2}", [m.events, m.from, m.to]),
					indicator: "green",
				});
			},
		});
	},
});
