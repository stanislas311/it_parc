# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, severity desc, id'

    name = fields.Char('Message', required=True, tracking=True)
    type = fields.Selection([
        ('warranty', 'Garantie'),
        ('contract', 'Contrat'),
        ('maintenance', 'Maintenance'),
    ], 'Type', required=True, tracking=True)
    severity = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
    ], 'Sévérité', required=True, default='medium', tracking=True)
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now, tracking=True)
    state = fields.Selection([
        ('new', 'Nouvelle'),
        ('acknowledged', 'Reconnue'),
        ('resolved', 'Résolue'),
    ], 'État', default='new', tracking=True)
    
    equipment_id = fields.Many2one('it.equipment', 'Équipement')
    contract_id = fields.Many2one('it.contract', 'Contrat')
    notes = fields.Text('Notes')
    
    def action_acknowledge(self):
        """Reconnaître l'alerte"""
        self.ensure_one()
        self.state = 'acknowledged'

    def action_resolve(self):
        """Résoudre l'alerte"""
        self.ensure_one()
        self.state = 'resolved'

    @api.model
    def cron_check_warranty_expiration(self):
        """Tâche planifiée pour vérifier les garanties expirantes"""
        alert_threshold = self.env['ir.config_parameter'].sudo().get_param(
            'it_parc.warranty_alert_threshold', default=30)
        threshold_days = int(alert_threshold)
        
        today = fields.Date.today()
        alert_date = today + timedelta(days=threshold_days)
        
        expiring_equipments = self.env['it.equipment'].search([
            ('warranty_end_date', '<=', alert_date),
            ('warranty_end_date', '>=', today),
            ('state', '!=', 'retired'),
        ])
        
        for equipment in expiring_equipments:
            days_remaining = (equipment.warranty_end_date - today).days
            existing_alert = self.search([
                ('equipment_id', '=', equipment.id),
                ('type', '=', 'warranty'),
                ('state', '!=', 'resolved'),
            ], limit=1)
            
            if not existing_alert:
                self.create({
                    'name': f'Garantie {equipment.name} expire dans {days_remaining} jours',
                    'type': 'warranty',
                    'equipment_id': equipment.id,
                    'severity': 'high' if days_remaining <= 7 else 'medium',
                })
