# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItAssignmentReassign(models.TransientModel):
    _name = 'it.assignment.reassign'
    _description = 'Wizard de réaffectation'

    assignment_id = fields.Many2one('it.assignment', 'Affectation actuelle', required=True)
    equipment_id = fields.Many2one(
        'it.equipment', related='assignment_id.equipment_id', readonly=True,
    )
    current_employee_id = fields.Many2one(
        'hr.employee', related='assignment_id.employee_id', readonly=True,
    )
    current_department_id = fields.Many2one(
        'hr.department', related='assignment_id.department_id', readonly=True,
    )
    new_employee_id = fields.Many2one('hr.employee', 'Nouvel employé', required=True)
    new_department_id = fields.Many2one('hr.department', 'Nouveau département', required=True)
    reason = fields.Text('Motif de réaffectation', required=True)

    @api.onchange('new_employee_id')
    def _onchange_new_employee_id(self):
        if self.new_employee_id and self.new_employee_id.department_id:
            self.new_department_id = self.new_employee_id.department_id

    def action_reassign(self):
        """Réaffecter l'équipement à un nouvel employé et département."""
        self.ensure_one()
        if self.assignment_id.state != 'active':
            raise ValidationError(_('Seule une affectation active peut être réaffectée.'))

        old_employee = self.current_employee_id.name or _('Non défini')
        old_department = self.current_department_id.name or _('Non défini')

        self.env['it.assignment.transfer'].create({
            'assignment_id': self.assignment_id.id,
            'from_employee_id': self.assignment_id.employee_id.id,
            'to_employee_id': self.new_employee_id.id,
            'from_department_id': self.assignment_id.department_id.id,
            'to_department_id': self.new_department_id.id,
            'date': fields.Datetime.now(),
            'reason': self.reason,
        })

        self.assignment_id.write({
            'employee_id': self.new_employee_id.id,
            'department_id': self.new_department_id.id,
        })

        if self.equipment_id:
            self.equipment_id.write({
                'department_id': self.new_department_id.id,
            })
            self.equipment_id.message_post(body=_(
                'Réaffectation : %(old_emp)s (%(old_dept)s) → %(new_emp)s (%(new_dept)s). Motif : %(reason)s',
                old_emp=old_employee,
                old_dept=old_department,
                new_emp=self.new_employee_id.name,
                new_dept=self.new_department_id.name,
                reason=self.reason,
            ))

        return {'type': 'ir.actions.act_window_close'}
