# -*- coding: utf-8 -*-

import io
import base64
from collections import defaultdict
from datetime import timedelta
import xlsxwriter
from odoo import models, fields, api, _


class ItEquipment(models.Model):
    _inherit = 'it.equipment'

    def action_export_inventory_excel(self):
        """Exporter l'inventaire complet en Excel."""
        equipments = self.search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Inventaire')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1B4F72',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
        })
        cell_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})

        headers = [
            'Nom/Série', 'Catégorie', 'Marque', 'Modèle', 'Date achat',
            'Fin garantie', 'Prix (FCFA)', 'Localisation', 'Département', 'État',
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 16)

        state_labels = dict(self._fields['state'].selection)
        for row, equipment in enumerate(equipments, start=1):
            worksheet.write(row, 0, equipment.name or '', cell_format)
            worksheet.write(row, 1, equipment.category_id.name or '', cell_format)
            worksheet.write(row, 2, equipment.brand or '', cell_format)
            worksheet.write(row, 3, equipment.model or '', cell_format)
            worksheet.write(row, 4, str(equipment.purchase_date or ''), cell_format)
            worksheet.write(row, 5, str(equipment.warranty_end_date or ''), cell_format)
            worksheet.write(row, 6, equipment.purchase_price or 0, money_format)
            worksheet.write(row, 7, equipment.location or '', cell_format)
            worksheet.write(row, 8, equipment.department_id.name or '', cell_format)
            worksheet.write(row, 9, state_labels.get(equipment.state, ''), cell_format)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'inventaire_techpark_it_parc.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def action_print_inventory_report(self):
        """Ouvrir le wizard de rapport inventaire filtré."""
        return {
            'name': _('Rapport d\'inventaire'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.report.inventory',
            'view_mode': 'form',
            'target': 'new',
        }


class ItIntervention(models.Model):
    _inherit = 'it.intervention'

    def action_export_costs_excel(self):
        """Exporter la synthèse des coûts par équipement et par mois."""
        interventions = self.search([('state', '=', 'done')])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Coûts Maintenance')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1B4F72',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
        })
        cell_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        total_format = workbook.add_format({
            'bold': True, 'bg_color': '#D5E8F0', 'border': 1, 'num_format': '#,##0.00',
        })

        headers = ['Équipement', 'Catégorie', 'Mois', 'Nb interventions', 'Durée (h)', 'Coût total (FCFA)']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 18)

        # Agrégation par équipement et mois
        aggregation = defaultdict(lambda: {'count': 0, 'duration': 0.0, 'cost': 0.0, 'category': ''})
        for intervention in interventions:
            if not intervention.equipment_id or not intervention.date_start:
                continue
            month_key = intervention.date_start.strftime('%Y-%m')
            key = (intervention.equipment_id.id, month_key)
            aggregation[key]['count'] += 1
            aggregation[key]['duration'] += intervention.duration or 0
            aggregation[key]['cost'] += intervention.cost or 0
            aggregation[key]['category'] = intervention.equipment_id.category_id.name or ''
            aggregation[key]['equipment_name'] = intervention.equipment_id.name

        row = 1
        grand_total = 0.0
        for (equipment_id, month_key), data in sorted(aggregation.items(), key=lambda x: (x[0][1], x[1]['equipment_name'])):
            worksheet.write(row, 0, data['equipment_name'], cell_format)
            worksheet.write(row, 1, data['category'], cell_format)
            worksheet.write(row, 2, month_key, cell_format)
            worksheet.write(row, 3, data['count'], cell_format)
            worksheet.write(row, 4, round(data['duration'], 2), cell_format)
            worksheet.write(row, 5, data['cost'], money_format)
            grand_total += data['cost']
            row += 1

        worksheet.write(row + 1, 4, 'TOTAL GÉNÉRAL', total_format)
        worksheet.write(row + 1, 5, grand_total, total_format)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'synthese_couts_maintenance_techpark.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }


class ItContract(models.Model):
    _inherit = 'it.contract'

    def action_export_expiring_excel(self):
        """Exporter les contrats expirants dans 60 jours en Excel."""
        today = fields.Date.today()
        alert_date = today + timedelta(days=60)

        expiring_contracts = self.search([
            ('end_date', '<=', alert_date),
            ('end_date', '>=', today),
        ])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Contrats Expirants')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1B4F72',
            'font_color': 'white',
            'border': 1,
        })
        warning_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'border': 1,
        })
        caution_format = workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C6500',
            'border': 1,
        })
        normal_format = workbook.add_format({'border': 1})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})

        headers = ['Référence', 'Fournisseur', 'Type', 'Date fin', 'Jours restants', 'Montant (FCFA)']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 16)

        type_labels = dict(self._fields['type'].selection)
        for row, contract in enumerate(expiring_contracts, start=1):
            if contract.days_remaining <= 7:
                fmt = warning_format
                money_fmt = workbook.add_format({
                    'bg_color': '#FFC7CE', 'font_color': '#9C0006',
                    'border': 1, 'num_format': '#,##0.00',
                })
            elif contract.days_remaining <= 30:
                fmt = caution_format
                money_fmt = workbook.add_format({
                    'bg_color': '#FFEB9C', 'font_color': '#9C6500',
                    'border': 1, 'num_format': '#,##0.00',
                })
            else:
                fmt = normal_format
                money_fmt = money_format

            worksheet.write(row, 0, contract.name or '', fmt)
            worksheet.write(row, 1, contract.supplier_id.name or '', fmt)
            worksheet.write(row, 2, type_labels.get(contract.type, ''), fmt)
            worksheet.write(row, 3, str(contract.end_date or ''), fmt)
            worksheet.write(row, 4, contract.days_remaining or 0, fmt)
            worksheet.write(row, 5, contract.amount or 0, money_fmt)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'contrats_expirants_60j_techpark.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
