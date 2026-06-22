# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItAssignment(models.Model):
    _name = 'it.assignment'
    _description = 'Affectation d\'équipement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id'

    equipment_id = fields.Many2one('it.equipment', 'Équipement', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Employé', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', 'Département', tracking=True)
    date_start = fields.Datetime('Date de début', required=True, default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime('Date de fin', tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('returned', 'Retournée'),
    ], 'État', default='active', tracking=True)
    notes = fields.Text('Notes')
    transfer_history_ids = fields.One2many('it.assignment.transfer', 'assignment_id', 'Historique des transferts')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.department_id:
            self.department_id = self.employee_id.department_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('state', 'active') == 'active' and vals.get('equipment_id'):
                existing = self.search([
                    ('equipment_id', '=', vals['equipment_id']),
                    ('state', '=', 'active'),
                ], limit=1)
                if existing:
                    equipment = self.env['it.equipment'].browse(vals['equipment_id'])
                    raise ValidationError(_(
                        'L\'équipement %(eq)s possède déjà une affectation active.',
                        eq=equipment.name,
                    ))
        records = super().create(vals_list)
        for record in records:
            if record.equipment_id and record.state == 'active':
                record.equipment_id.write({
                    'state': 'assigned',
                    'department_id': record.department_id.id,
                })
        return records

    def action_return(self):
        """Retourner l'équipement"""
        self.ensure_one()
        self.state = 'returned'
        self.date_end = fields.Datetime.now()
        if self.equipment_id:
            self.equipment_id.state = 'draft'
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_reassign(self):
        """Ouvrir le wizard de réaffectation"""
        self.ensure_one()
        return {
            'name': _('Réaffecter l\'équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.assignment.reassign',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_assignment_id': self.id},
        }


class ItAssignmentTransfer(models.Model):
    _name = 'it.assignment.transfer'
    _description = 'Transfert d\'affectation'
    _order = 'date desc'

    assignment_id = fields.Many2one('it.assignment', 'Affectation', required=True, ondelete='cascade')
    from_employee_id = fields.Many2one('hr.employee', 'De l\'employé')
    to_employee_id = fields.Many2one('hr.employee', 'Vers employé')
    from_department_id = fields.Many2one('hr.department', 'Du département', required=True)
    to_department_id = fields.Many2one('hr.department', 'Vers département', required=True)
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now)
    reason = fields.Text('Motif')
