# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItContractRenewal(models.TransientModel):
    _name = 'it.contract.renewal'
    _description = 'Renouvellement de contrat'

    contract_id = fields.Many2one('it.contract', 'Contrat', required=True, ondelete='cascade')
    new_end_date = fields.Date('Nouvelle date de fin', required=True)
    new_amount = fields.Float('Nouveau montant', digits='Product Price')
    notes = fields.Text('Notes')
    
    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            # Par défaut, prolonger d'un an
            if self.contract_id.end_date:
                self.new_end_date = self.contract_id.end_date + timedelta(days=365)
            self.new_amount = self.contract_id.amount
    
    def action_renew(self):
        """Renouveler le contrat"""
        self.ensure_one()
        
        # Créer un nouveau contrat
        new_contract = self.contract_id.copy({
            'start_date': self.contract_id.end_date,
            'end_date': self.new_end_date,
            'amount': self.new_amount,
            'is_renewed': False,
        })
        
        # Marquer l'ancien contrat comme renouvelé
        self.contract_id.write({'is_renewed': True})
        self.contract_id.message_post(
            body=_('Contrat renouvelé. Nouveau contrat: %s') % new_contract.name
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.contract',
            'res_id': new_contract.id,
            'view_mode': 'form',
            'target': 'current',
        }
