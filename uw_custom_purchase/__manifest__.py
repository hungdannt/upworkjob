{
    'name': 'Custom Purchase Order Report',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Custom Purchase Order Report with Indian GST Format',
    'description': 'Custom Purchase Order PDF Report with company details, GST, and signature fields',
    'author': 'Your Company',
    'depends': ['purchase', 'base', 'account'],
    'data': [
        'views/purchase_order_views.xml',
        'report/purchase_order_report.xml',
        'views/res_partner_views.xml',
    ],
    'external_dependencies': {
        'python': ['num2words'],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
