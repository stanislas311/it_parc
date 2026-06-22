# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class ItContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc, id'

    name = fields.Char('Référence', required=True, tracking=True)
    supplier_id = fields.Many2one('res.partner', 'Fournisseur', required=True, 
                                  domain=[('supplier_rank', '>', 0)], tracking=True)
    type = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('license', 'Licence'),
    ], 'Type', required=True, tracking=True)
    start_date = fields.Date('Date de début', required=True, tracking=True)
    end_date = fields.Date('Date de fin', required=True, tracking=True)
    amount = fields.Float('Montant', digits='Product Price', tracking=True)
    equipment_ids = fields.Many2many('it.equipment', 'it_contract_equipment_rel',
                                     'contract_id', 'equipment_id', 'Équipements couverts')
    notes = fields.Text('Notes')
    days_remaining = fields.Integer('Jours restants', compute='_compute_days_remaining', store=True)
    is_renewed = fields.Boolean('Renouvelé', default=False, tracking=True)
    state = fields.Selection([
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('renewed', 'Renouvelé'),
    ], 'État', compute='_compute_state', store=True, tracking=True)

    @api.depends('end_date')
    def _compute_days_remaining(self):
        today = fields.Date.today()
        for contract in self:
            if contract.end_date:
                delta = contract.end_date - today
                contract.days_remaining = delta.days
            else:
                contract.days_remaining = 0

    @api.depends('end_date', 'is_renewed')
    def _compute_state(self):
        today = fields.Date.today()
        for contract in self:
            if contract.is_renewed:
                contract.state = 'renewed'
            elif contract.end_date and contract.end_date < today:
                contract.state = 'expired'
            else:
                contract.state = 'active'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for contract in self:
            if contract.start_date and contract.end_date:
                if contract.end_date < contract.start_date:
                    raise ValidationError(_('La date de fin doit être après la date de début.'))

    def action_renew(self):
        """Wizard de renouvellement"""
        self.ensure_one()
        return {
            'name': _('Renouveler le contrat'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.contract.renewal',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def cron_check_expiring_contracts(self):
        """Tâche planifiée pour vérifier les contrats expirants"""
        alert_threshold = self.env['ir.config_parameter'].sudo().get_param(
            'it_parc.contract_alert_threshold', default=30)
        threshold_days = int(alert_threshold)
        
        today = fields.Date.today()
        alert_date = today + timedelta(days=threshold_days)
        
        expiring_contracts = self.search([
            ('end_date', '<=', alert_date),
            ('end_date', '>=', today),
            ('state', '=', 'active'),
        ])
        
        for contract in expiring_contracts:
            self.env['it.alerte'].create({
                'name': f'Contrat {contract.name} expire dans {contract.days_remaining} jours',
                'type': 'contract',
                'contract_id': contract.id,
                'severity': 'high' if contract.days_remaining <= 7 else 'medium',
            })
