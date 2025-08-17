{
    "name": "Snooker Club Management",
    'description': """
        An Application for managing Real Estate Property!
        Manage your buildings, floors, properties and contract
    """,
    'version': '17.0.1.0',
    'summary': 'System with in-depth management of Projects, Buildings, Floors, Properties, Real Estate PMS - Odoo App',
    'sequence': -100,
    'license': 'AGPL-3',

    "depends": ["base", "sale", "account"],
    "author": "Eagle ICT Solutions",
    "category": "Snooker Management",
    "summary": "Manages snooker table reservations, billing, and expenses",

    "data": [
        "security/ir.model.access.csv",
        "security/snooker_security.xml",
        "views/snooker_menu.xml",

        "data/scheduled_jobs.xml",
        "views/snooker_reservation_views.xml",
        "views/snooker_payment_wizard_view.xml",
        "views/snooker_expense_payment_wizard_view.xml",
        "views/snooker_expense_views.xml",
        "views/snooker_financial_report_views.xml",
        "views/snooker_table_view.xml",

    ],
    'installable': True,
    'application': True,
    'auto-install': False,
}
