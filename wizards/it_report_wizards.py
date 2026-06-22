# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItReportInventoryWizard(models.TransientModel):
    _name = 'it.report.inventory'
    _description = 'Wizard rapport inventaire filtré'

    department_id = fields.Many2one('hr.department', 'Département')
    category_id = fields.Many2one('it.equipment.category', 'Catégorie')

    def action_print_report(self):
        """Générer le rapport PDF d'inventaire filtré."""
        self.ensure_one()
        domain = [('state', '!=', 'retired')]
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        if self.category_id:
            domain.append(('category_id', '=', self.category_id.id))

        equipments = self.env['it.equipment'].search(domain)
        if not equipments:
            raise ValidationError(_('Aucun équipement ne correspond aux filtres sélectionnés.'))

        return self.env.ref('it_parc.report_it_inventory').report_action(
            equipments,
            data={
                'department_name': self.department_id.name or _('Tous'),
                'category_name': self.category_id.name or _('Toutes'),
            },
        )


class ItReportMaintenanceWizard(models.TransientModel):
    _name = 'it.report.maintenance'
    _description = 'Wizard rapport maintenance par période'

    date_from = fields.Date('Date début', required=True,
                            default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date('Date fin', required=True, default=fields.Date.today)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_to < wizard.date_from:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))

    def action_print_report(self):
        """Générer le rapport PDF des maintenances sur la période."""
        self.ensure_one()
        interventions = self.env['it.intervention'].search([
            ('state', '=', 'done'),
            ('date_start', '>=', self.date_from),
            ('date_start', '<=', self.date_to),
        ])
        if not interventions:
            raise ValidationError(_('Aucune intervention terminée sur cette période.'))

        return self.env.ref('it_parc.report_it_maintenance').report_action(
            interventions,
            data={
                'date_from': str(self.date_from),
                'date_to': str(self.date_to),
            },
        )
