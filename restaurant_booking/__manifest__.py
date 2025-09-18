{
    "name": "Restaurant Booking",
    "version": "18.0.0.0.1",
    "author": "github.com/hungdannt",
    "category": "Website",
    "depends": ["base", "website", "pos_restaurant"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/restaurant_booking_views.xml",
        "views/portal_templates.xml",
        "views/restaurant_table_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "restaurant_booking/static/src/scss/booking.scss",
            "restaurant_booking/static/src/js/booking.js",
            "restaurant_booking/static/src/table_booking_template.xml",
        ],
    },
    "installable": True,
    "application": True,
}
