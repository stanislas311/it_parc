# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItAlertScan(models.TransientModel):
    _name = 'it.alert.scan'
    _description = 'Scan manuel des alertes'

    warranty_threshold = fields.Integer('Seuil garantie (jours)', default=30, required=True)
    contract_threshold = fields.Integer('Seuil contrat (jours)', default=30, required=True)
    scan_result = fields.Text('Résultat du scan', readonly=True)
    
    def action_scan(self):
        """Scanner les garanties et contrats expirants"""
        self.ensure_one()
        
        warranty_alerts = 0
        contract_alerts = 0
        total_alerts = 0
        
        today = fields.Date.today()
        warranty_alert_date = today + timedelta(days=self.warranty_threshold)
        contract_alert_date = today + timedelta(days=self.contract_threshold)
        
        # Scanner les garanties
        expiring_equipments = self.env['it.equipment'].search([
            ('warranty_end_date', '<=', warranty_alert_date),
            ('warranty_end_date', '>=', today),
            ('state', '!=', 'retired'),
        ])
        
        for equipment in expiring_equipments:
            days_remaining = (equipment.warranty_end_date - today).days
            existing_alert = self.env['it.alerte'].search([
                ('equipment_id', '=', equipment.id),
                ('type', '=', 'warranty'),
                ('state', '!=', 'resolved'),
            ], limit=1)
            
            if not existing_alert:
                self.env['it.alerte'].create({
                    'name': f'Garantie {equipment.name} expire dans {days_remaining} jours',
                    'type': 'warranty',
                    'equipment_id': equipment.id,
                    'severity': 'high' if days_remaining <= 7 else 'medium',
                })
                warranty_alerts += 1
        
        # Scanner les contrats
        expiring_contracts = self.env['it.contract'].search([
            ('end_date', '<=', contract_alert_date),
            ('end_date', '>=', today),
            ('state', '=', 'active'),
        ])
        
        for contract in expiring_contracts:
            existing_alert = self.env['it.alerte'].search([
                ('contract_id', '=', contract.id),
                ('type', '=', 'contract'),
                ('state', '!=', 'resolved'),
            ], limit=1)
            
            if not existing_alert:
                self.env['it.alerte'].create({
                    'name': f'Contrat {contract.name} expire dans {contract.days_remaining} jours',
                    'type': 'contract',
                    'contract_id': contract.id,
                    'severity': 'high' if contract.days_remaining <= 7 else 'medium',
                })
                contract_alerts += 1
        
        total_alerts = warranty_alerts + contract_alerts
        
        result = f"""Résultat du scan manuel
======================
Alertes de garantie créées: {warranty_alerts}
Alertes de contrat créées: {contract_alerts}
Total des nouvelles alertes: {total_alerts}
"""
        
        self.scan_result = result
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.alert.scan',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
