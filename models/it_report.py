# -*- coding: utf-8 -*-

from odoo import models, api


class ReportItEquipmentCard(models.AbstractModel):
    _name = 'report.it_parc.report_it_equipment_card_template'
    _description = 'Rapport fiche équipement'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['it.equipment'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'it.equipment',
            'docs': docs,
            'company_name': 'TECHPARK CI',
            'company_address': 'Abidjan-Cocody, Côte d\'Ivoire',
        }


class ReportItInventory(models.AbstractModel):
    _name = 'report.it_parc.report_it_inventory_template'
    _description = 'Rapport inventaire IT'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['it.equipment'].browse(docids)
        data = data or {}
        return {
            'doc_ids': docids,
            'doc_model': 'it.equipment',
            'docs': docs,
            'department_name': data.get('department_name', 'Tous'),
            'category_name': data.get('category_name', 'Toutes'),
            'company_name': 'TECHPARK CI',
            'company_address': 'Abidjan-Cocody, Côte d\'Ivoire',
        }


class ReportItMaintenance(models.AbstractModel):
    _name = 'report.it_parc.report_it_maintenance_template'
    _description = 'Rapport historique maintenance'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['it.intervention'].browse(docids)
        data = data or {}
        total_cost = sum(docs.mapped('cost'))
        return {
            'doc_ids': docids,
            'doc_model': 'it.intervention',
            'docs': docs,
            'date_from': data.get('date_from', ''),
            'date_to': data.get('date_to', ''),
            'total_cost': total_cost,
            'company_name': 'TECHPARK CI',
            'company_address': 'Abidjan-Cocody, Côte d\'Ivoire',
        }
