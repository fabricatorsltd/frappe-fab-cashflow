frappe.views.calendar["Cash Flow Event"] = {
	field_map: {
		start: "event_date",
		end: "event_date",
		id: "name",
		title: "description",
		allDay: 1,
	},
	get_events_method: "frappe.desk.calendar.get_events",
	style_map: {
		Inflow: "success",
		Outflow: "danger",
	},
	options: {
		header: {
			left: "prev,next today",
			center: "title",
			right: "month,agendaWeek",
		},
	},
};
