# Guide d'Installation - Configuration du Chemin du Module

## Emplacements

- **Odoo** : `C:\Users\DELL\OneDrive\Documents\odoo-18.0+e.20241230`
- **Module it_parc** : `D:\PC STANN\Projet fin de module\IT_parc_Odoo\it_parc`

## Méthode 1 : Via la ligne de commande (Recommandée pour le test)

Lors du lancement d'Odoo, ajoutez le paramètre `--addons-path` :

```powershell
cd "C:\Users\DELL\OneDrive\Documents\odoo-18.0+e.20241230"
python odoo-bin --addons-path="addons, D:\PC STANN\Projet fin de module\IT_parc_Odoo\it_parc" -d votre_base
```

## Méthode 2 : Via le fichier de configuration odoo.conf

1. Localisez votre fichier `odoo.conf` (généralement dans `C:\Users\DELL\.odoorc` ou dans le répertoire d'Odoo)
2. Ouvrez-le avec un éditeur de texte
3. Modifiez ou ajoutez la ligne `addons_path` :

```ini
addons_path = addons, D:\PC STANN\Projet fin de module\IT_parc_Odoo\it_parc
```

4. Sauvegardez le fichier
5. Redémarrez Odoo

## Méthode 3 : Via les variables d'environnement (Windows)

1. Appuyez sur `Win + R`, tapez `sysdm.cpl` et appuyez sur Entrée
2. Cliquez sur l'onglet **Avancé**
3. Cliquez sur **Variables d'environnement**
4. Sous **Variables système**, cliquez sur **Nouveau**
5. Nom de la variable : `PYTHONPATH`
6. Valeur de la variable : `D:\PC STANN\Projet fin de module\IT_parc_Odoo\it_parc`
7. Cliquez sur OK pour fermer toutes les fenêtres
8. Redémarrez votre terminal/IDE

## Vérification

Pour vérifier que le module est reconnu :

1. Lancez Odoo avec la configuration choisie
2. Connectez-vous à l'interface web
3. Allez dans **Apps**
4. Cliquez sur **Mettre à jour la liste des applications**
5. Recherchez "IT Parc" ou "it_parc"
6. Le module devrait apparaître dans la liste

## Installation du module

Une fois le module reconnu :

1. Dans Apps, recherchez "IT Parc"
2. Cliquez sur **Installer**
3. Attendez la fin de l'installation
4. Le menu **IT Parc** apparaîtra dans la barre de navigation

## Dépendance Python requise

Avant d'installer, assurez-vous d'avoir installé xlsxwriter :

```bash
pip install xlsxwriter
```

## Dépannage

### Le module n'apparaît pas dans la liste des apps

- Vérifiez que le chemin dans `--addons-path` est correct
- Vérifiez que le fichier `__manifest__.py` existe dans le dossier du module
- Vérifiez qu'il n'y a pas d'erreur de syntaxe dans les fichiers Python/XML
- Consultez les logs Odoo pour les erreurs

### Erreur lors de l'installation

- Vérifiez que la dépendance `xlsxwriter` est installée
- Vérifiez que les modules dépendants (base, mail, web) sont installés
- Consultez les logs Odoo pour les erreurs spécifiques
