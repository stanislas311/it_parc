# IT Parc — Module de Gestion du Parc Informatique pour Odoo 18

**TECHPARK CI** — Direction des Systèmes d'Information — Abidjan, Côte d'Ivoire

Module Odoo 18 pour la gestion complète du parc informatique : équipements, interventions, contrats, alertes, rapports et dashboard OWL.

## Fonctionnalités

| # | Fonctionnalité | Description |
|---|----------------|-------------|
| 01 | Équipements | Workflow Brouillon → Affecté → En maintenance → Retiré |
| 02 | Affectations | Wizard de réaffectation avec motif et historique |
| 03 | Interventions | Corrective/préventive, calendrier, durée auto, coûts |
| 04 | Contrats | Maintenance/licences, jours restants, renouvellement |
| 05 | Alertes | Garanties et contrats, cron + scan manuel |
| 06 | Import CSV | Import en masse avec détection de doublons |
| 07 | Rapports PDF | Fiche équipement, inventaire filtré, historique maintenance |
| 08 | Exports Excel | Inventaire, coûts par asset/mois, contrats expirants |
| 09 | Dashboard OWL | 4+ KPIs, graphiques, RPC Python (`it.dashboard`) |

## Prérequis

- Odoo 18 Enterprise
- Python 3.11+
- `pip install xlsxwriter`
- Modules : `base`, `mail`, `web`, `hr`, `stock`, `purchase`, `account`, `maintenance`, `contacts`

## Installation

```bash
pip install xlsxwriter
python odoo-bin --addons-path="addons,CHEMIN_VERS/it_parc" -d votre_base -u it_parc --stop-after-init
```

Puis dans Odoo : **Apps → Mettre à jour la liste → Installer "IT Parc"**.

Assignez les utilisateurs aux groupes **IT Technicien** ou **IT Manager** (Paramètres → Utilisateurs).

## Sécurité

| Groupe | Droits |
|--------|--------|
| **IT Technicien** | Lecture parc + création/modification interventions |
| **IT Manager** | Accès complet au module |

Droits : `security/ir.model.access.csv` + `security/it_parc_security.xml` (ir.rule).

## Données de démo

- 10 équipements (PC, serveurs, imprimantes, téléphones IP)
- 3 contrats fournisseurs
- 5 interventions de maintenance
- Sites : Cocody, Plateau (Abidjan), antenne Bouaké

## Import CSV

```csv
serial_number,category,brand,model,purchase_date,warranty_end_date,purchase_price,location
DELL-LAT-003,Ordinateur Portable,Dell,Latitude 7420,2024-01-15,2026-01-15,1200.00,Site Cocody — Bureau 103
```

## Tâches planifiées

- Vérification des garanties expirantes (quotidien)
- Vérification des contrats expirants (quotidien)

Paramètres configurables : `it_parc.warranty_alert_threshold`, `it_parc.contract_alert_threshold`.

## Licence

LGPL-3
