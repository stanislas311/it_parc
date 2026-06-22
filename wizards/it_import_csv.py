# -*- coding: utf-8 -*-

import csv
import io
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItImportCsv(models.TransientModel):
    _name = 'it.import.csv'
    _description = 'Import CSV d\'équipements'

    csv_file = fields.Binary('Fichier CSV', required=True)
    csv_filename = fields.Char('Nom du fichier')
    import_result = fields.Text('Résultat de l\'import', readonly=True)
    
    def action_import(self):
        """Importer les équipements depuis le fichier CSV"""
        self.ensure_one()
        
        if not self.csv_file:
            raise ValidationError(_('Veuillez sélectionner un fichier CSV.'))
        
        # Décoder le fichier
        csv_data = self.csv_file.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        created_count = 0
        ignored_count = 0
        error_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                serial_number = row.get('serial_number') or row.get('name')
                if not serial_number:
                    errors.append(f"Ligne manquante: numéro de série absent")
                    error_count += 1
                    continue
                
                # Vérifier les doublons
                existing = self.env['it.equipment'].search([
                    ('name', '=', serial_number)
                ], limit=1)
                
                if existing:
                    ignored_count += 1
                    continue
                
                # Créer ou récupérer la catégorie
                category_name = row.get('category', 'Standard')
                category = self.env['it.equipment.category'].search([
                    ('name', '=', category_name)
                ], limit=1)
                
                if not category:
                    category = self.env['it.equipment.category'].create({
                        'name': category_name
                    })
                
                # Créer l'équipement
                self.env['it.equipment'].create({
                    'name': serial_number,
                    'category_id': category.id,
                    'brand': row.get('brand', ''),
                    'model': row.get('model', ''),
                    'purchase_date': row.get('purchase_date') or False,
                    'warranty_end_date': row.get('warranty_end_date') or False,
                    'purchase_price': float(row.get('purchase_price', 0)) if row.get('purchase_price') else 0,
                    'location': row.get('location', ''),
                    'state': 'draft',
                })
                
                created_count += 1
                
            except Exception as e:
                errors.append(f"Erreur sur la ligne: {str(e)}")
                error_count += 1
        
        # Générer le rapport
        result = f"""Rapport d'import CSV
=====================
Équipements créés: {created_count}
Équipements ignorés (doublons): {ignored_count}
Erreurs: {error_count}
"""
        if errors:
            result += "\nDétails des erreurs:\n"
            result += "\n".join(errors[:10])  # Limiter à 10 erreurs
        
        self.import_result = result
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.import.csv',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
