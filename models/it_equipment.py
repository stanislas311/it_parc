# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id'

    name = fields.Char('Nom/Numéro de série', required=True, tracking=True)
    category_id = fields.Many2one('it.equipment.category', 'Catégorie', required=True, tracking=True)
    brand = fields.Char('Marque', tracking=True)
    model = fields.Char('Modèle', tracking=True)
    purchase_date = fields.Date('Date d\'achat', tracking=True)
    warranty_end_date = fields.Date('Fin de garantie', tracking=True)
    purchase_price = fields.Float('Prix d\'achat', digits='Product Price')
    location = fields.Char('Localisation', tracking=True)
    department_id = fields.Many2one('hr.department', 'Département', tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré'),
    ], 'État', default='draft', tracking=True)
    notes = fields.Text('Notes')
    assignment_ids = fields.One2many('it.assignment', 'equipment_id', 'Affectations')
    current_assignment_id = fields.Many2one('it.assignment', 'Affectation actuelle',
                                            compute='_compute_current_assignment', store=False)
    intervention_ids = fields.One2many('it.intervention', 'equipment_id', 'Interventions')
    contract_ids = fields.Many2many('it.contract', 'it_contract_equipment_rel', 
                                     'equipment_id', 'contract_id', 'Contrats')
    image = fields.Binary('Image')
    
    @api.depends('assignment_ids')
    def _compute_current_assignment(self):
        for equipment in self:
            current = equipment.assignment_ids.filtered(lambda a: a.state == 'active')
            equipment.current_assignment_id = current[0] if current else False

    @api.constrains('warranty_end_date', 'purchase_date')
    def _check_dates(self):
        for equipment in self:
            if equipment.purchase_date and equipment.warranty_end_date:
                if equipment.warranty_end_date < equipment.purchase_date:
                    raise ValidationError(_('La fin de garantie doit être après la date d\'achat.'))

    def action_assign(self):
        """Action pour affecter l'équipement"""
        self.ensure_one()
        return {
            'name': _('Affecter l\'équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.assignment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_id': self.id},
        }

    def action_reassign(self):
        """Wizard de réaffectation vers un autre employé/département"""
        self.ensure_one()
        if not self.current_assignment_id:
            raise ValidationError(_('Aucune affectation active pour cet équipement.'))
        return {
            'name': _('Réaffecter l\'équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.assignment.reassign',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_assignment_id': self.current_assignment_id.id},
        }

    def action_return(self):
        """Action pour retourner l'équipement"""
        self.ensure_one()
        if self.current_assignment_id:
            self.current_assignment_id.action_return()
        else:
            self.state = 'draft'

    def action_retire(self):
        """Mettre l'équipement au rebut"""
        self.ensure_one()
        if self.current_assignment_id:
            self.current_assignment_id.action_return()
        self.state = 'retired'

    def action_set_maintenance(self):
        """Passer l'équipement en maintenance"""
        self.ensure_one()
        self.state = 'maintenance'

    def action_print_equipment_card(self):
        """Imprimer la fiche équipement PDF"""
        return self.env.ref('it_parc.report_it_equipment_card').report_action(self)

    def name_get(self):
        result = []
        for equipment in self:
            name = f"[{equipment.category_id.name}] {equipment.name}"
            if equipment.brand:
                name += f" - {equipment.brand}"
            result.append((equipment.id, name))
        return result


class ItEquipmentCategory(models.Model):
    _name = 'it.equipment.category'
    _description = 'Catégorie d\'équipement'
    _order = 'name'

    name = fields.Char('Nom', required=True)
    description = fields.Text('Description')
    equipment_ids = fields.One2many('it.equipment', 'category_id', 'Équipements')
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Le nom de la catégorie doit être unique.')
    ]
