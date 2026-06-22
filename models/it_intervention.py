# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id'

    name = fields.Char('Référence', required=True, copy=False, readonly=True, 
                       default=lambda self: _('Nouveau'))
    equipment_id = fields.Many2one('it.equipment', 'Équipement', required=True, tracking=True)
    technician_id = fields.Many2one('hr.employee', 'Technicien', required=True, tracking=True)
    type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
    ], 'Type', required=True, default='corrective', tracking=True)
    date_start = fields.Datetime('Date de début', required=True, default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime('Date de fin', tracking=True)
    duration = fields.Float('Durée (heures)', compute='_compute_duration', store=True)
    cost = fields.Float('Coût', digits='Product Price', tracking=True)
    description = fields.Text('Description', required=True)
    report = fields.Text('Rapport d\'intervention')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], 'État', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('it.intervention') or _('Nouveau')
                )
        return super().create(vals_list)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for intervention in self:
            if intervention.date_start and intervention.date_end:
                delta = intervention.date_end - intervention.date_start
                intervention.duration = delta.total_seconds() / 3600.0
            else:
                intervention.duration = 0.0

    def action_start(self):
        """Démarrer l'intervention"""
        self.ensure_one()
        self.state = 'in_progress'
        if self.equipment_id:
            self.equipment_id.state = 'maintenance'

    def action_done(self):
        """Terminer l'intervention"""
        self.ensure_one()
        if not self.date_end:
            self.date_end = fields.Datetime.now()
        self.state = 'done'
        if self.equipment_id and self.equipment_id.state == 'maintenance':
            prior = self.equipment_id.assignment_ids.filtered(lambda a: a.state == 'active')
            self.equipment_id.state = 'assigned' if prior else 'draft'

    def action_cancel(self):
        """Annuler l'intervention"""
        self.ensure_one()
        self.state = 'cancelled'
        if self.equipment_id and self.equipment_id.state == 'maintenance':
            prior = self.equipment_id.assignment_ids.filtered(lambda a: a.state == 'active')
            self.equipment_id.state = 'assigned' if prior else 'draft'

    def action_print_maintenance_report(self):
        """Ouvrir le wizard de rapport maintenance par période"""
        return {
            'name': _('Historique des maintenances'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.report.maintenance',
            'view_mode': 'form',
            'target': 'new',
        }
