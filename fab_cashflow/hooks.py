app_name = "fab_cashflow"
app_title = "Fab Cashflow"
app_publisher = "fabricators"
app_description = "Cash flow forecast: recurring payments, Amex settlement cycle, tax deadlines"
app_email = "support@fabricators.ltd"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "fab_cashflow",
# 		"logo": "/assets/fab_cashflow/logo.png",
# 		"title": "Fab Cashflow",
# 		"route": "/fab_cashflow",
# 		"has_permission": "fab_cashflow.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/fab_cashflow/css/fab_cashflow.css"
# app_include_js = "/assets/fab_cashflow/js/fab_cashflow.js"

# include js, css files in header of web template
# web_include_css = "/assets/fab_cashflow/css/fab_cashflow.css"
# web_include_js = "/assets/fab_cashflow/js/fab_cashflow.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "fab_cashflow/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "fab_cashflow/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "fab_cashflow.utils.jinja_methods",
# 	"filters": "fab_cashflow.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "fab_cashflow.install.before_install"
# after_install = "fab_cashflow.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "fab_cashflow.uninstall.before_uninstall"
# after_uninstall = "fab_cashflow.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "fab_cashflow.utils.before_app_install"
# after_app_install = "fab_cashflow.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "fab_cashflow.utils.before_app_uninstall"
# after_app_uninstall = "fab_cashflow.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "fab_cashflow.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "fab_cashflow.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"fab_cashflow.tasks.all"
# 	],
# 	"daily": [
# 		"fab_cashflow.tasks.daily"
# 	],
# 	"hourly": [
# 		"fab_cashflow.tasks.hourly"
# 	],
# 	"weekly": [
# 		"fab_cashflow.tasks.weekly"
# 	],
# 	"monthly": [
# 		"fab_cashflow.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "fab_cashflow.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "fab_cashflow.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "fab_cashflow.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "fab_cashflow.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["fab_cashflow.utils.before_request"]
# after_request = ["fab_cashflow.utils.after_request"]

# Job Events
# ----------
# before_job = ["fab_cashflow.utils.before_job"]
# after_job = ["fab_cashflow.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"fab_cashflow.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

