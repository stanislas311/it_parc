# -*- coding: utf-8 -*-

from odoo import models, api


class ItDashboard(models.AbstractModel):
    _name = 'it.dashboard'
    _description = 'Tableau de bord IT Parc'

    @api.model
    def get_dashboard_data(self):
        """Retourne les KPIs et données graphiques pour le dashboard OWL."""
        Equipment = self.env['it.equipment']
        Contract = self.env['it.contract']
        Intervention = self.env['it.intervention']
        Alerte = self.env['it.alerte']
        Category = self.env['it.equipment.category']

        total_equipment = Equipment.search_count([])
        assigned_count = Equipment.search_count([('state', '=', 'assigned')])
        maintenance_count = Equipment.search_count([('state', '=', 'maintenance')])
        active_contracts = Contract.search_count([('state', '=', 'active')])
        pending_interventions = Intervention.search_count([
            ('state', 'in', ['draft', 'in_progress']),
        ])
        active_alerts = Alerte.search_count([('state', '=', 'new')])
        high_alerts = Alerte.search_count([
            ('state', '=', 'new'),
            ('severity', '=', 'high'),
        ])

        categories = Category.search([])
        chart_data = []
        max_value = 0
        for category in categories:
            count = Equipment.search_count([('category_id', '=', category.id)])
            if count:
                chart_data.append({'label': category.name, 'value': count})
                max_value = max(max_value, count)

        state_data = []
        state_labels = dict(Equipment._fields['state'].selection)
        for state_key, state_label in state_labels.items():
            count = Equipment.search_count([('state', '=', state_key)])
            if count:
                state_data.append({
                    'label': state_label,
                    'value': count,
                    'state': state_key,
                })

        for item in chart_data:
            item['percent'] = round((item['value'] / max_value) * 100) if max_value else 0

        recent_interventions_recs = Intervention.search_read(
            [], ['name', 'equipment_id', 'type', 'state', 'date_start'], limit=5, order='date_start desc'
        )
        recent_interventions = []
        for rec in recent_interventions_recs:
            recent_interventions.append({
                'id': rec['id'],
                'name': rec['name'],
                'equipment_name': rec['equipment_id'][1] if rec.get('equipment_id') else '',
                'type': rec['type'],
                'state': rec['state'],
                'date_start': str(rec['date_start']) if rec.get('date_start') else '',
            })

        return {
            'company': 'TECHPARK CI',
            'subtitle': 'Gestion du parc informatique — Abidjan',
            'kpis': {
                'totalEquipment': total_equipment,
                'assignedEquipment': assigned_count,
                'activeContracts': active_contracts,
                'pendingInterventions': pending_interventions,
                'activeAlerts': active_alerts,
                'maintenanceEquipment': maintenance_count,
                'highAlerts': high_alerts,
            },
            'chartData': chart_data,
            'stateData': state_data,
            'recentInterventions': recent_interventions,
        }
