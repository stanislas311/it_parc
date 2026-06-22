# -*- coding: utf-8 -*-
{
    'name': 'IT Parc - Gestion du Parc Informatique',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Gestion complète du parc informatique TECHPARK CI',
    'description': """
Module de gestion du parc informatique pour Odoo 18 — TECHPARK CI
===================================================================

Fonctionnalités principales :
- Gestion de l'inventaire des équipements (workflow Brouillon → Affecté → Maintenance → Retiré)
- Suivi des affectations aux employés et départements avec historique
- Enregistrement des interventions de maintenance (corrective/préventive)
- Gestion des contrats fournisseurs (maintenance, licences)
- Alertes automatiques pour les garanties et contrats expirants
- Import en masse via CSV
- Rapports PDF (fiche équipement, inventaire, historique)
- Exports Excel (inventaire, coûts, contrats)
- Dashboard OWL personnalisé avec KPIs et graphiques
    """,
    'author': 'TECHPARK CI — DSI',
    'website': 'https://www.techpark.ci',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
        'hr',
        'stock',
        'purchase',
        'account',
        'maintenance',
        'contacts',
    ],
    'data': [
        'security/it_parc_security.xml',
        'security/ir.model.access.csv',
        'data/it_parc_data.xml',
        'data/it_parc_demo.xml',
        'views/it_equipment_views.xml',
        'views/it_assignment_views.xml',
        'views/it_intervention_views.xml',
        'views/it_contract_views.xml',
        'views/it_alerte_views.xml',
        'views/it_dashboard_views.xml',
        'wizards/it_import_csv_views.xml',
        'wizards/it_contract_renewal_views.xml',
        'wizards/it_alert_scan_views.xml',
        'wizards/it_assignment_reassign_views.xml',
        'wizards/it_report_wizards_views.xml',
        'report/it_equipment_report.xml',
        'report/it_inventory_report.xml',
        'report/it_maintenance_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'it_parc/static/src/js/dashboard.js',
            'it_parc/static/src/xml/dashboard.xml',
            'it_parc/static/src/scss/dashboard.scss',
        ],
    },
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
