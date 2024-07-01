from flask import url_for

PAGES = {
    'dashboard': {
        'url': url_for('user.dashboard'),
        'title': 'Dashboard',
    },
    'hosts': {
        'url': url_for('user.hosts'),
        'title': 'Hosts',
    },
    'smartlead': {
        'url': url_for('user.smartlead', page=1),
        'title': 'Smartlead',
    },
    'seeds': {
        'url': url_for('user.seeds'),
        'title': 'Seeds',
    },
    'emails': {
        'url': url_for('user.emails'),
        'title': 'Emails',
    },
    'csv_uploads': {
        'url': url_for('user.csv_uploads'),
        'title': 'Attribute Uploads',
    },
    'vps': {
        'url': url_for('user.vps'),
        'title': 'VPS',
    },
    'email_groups': {
        'url': url_for('user.email_groups'),
        'title': 'Email groups',
    },
}

PAGES_FOR_VIEW = {
    'admin': [
        'dashboard',
        'hosts',
        'smartlead',
        'seeds',
        'emails',
        'csv_uploads',
        'email_groups',
        'vps',
    ],
    'selfService': ['dashboard', 'hosts', 'csv_uploads'],
    'inboxPlacementOnly': ['dashboard', 'hosts', 'seeds'],
    'inboxPlacementAudit': ['dashboard', 'hosts', 'seeds'],
}
