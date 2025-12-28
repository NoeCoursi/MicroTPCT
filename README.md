# MicroTPCT
*Noé - 28/12/25*

## Architecture initiale du projet

Voici une petite présentation de l'architecture. Il s'agit d'une sugestion qui pourra être modifiée à votre convenance.

J'ai essayé de faire quelque chose de propre, professionnel et surtout très modulaires pour permettre un développement plus simple et une répartition du travail plus évidente. Je pense qu'au début cette architecture peut paraître un peu complexe mais à terme elle permettra d'aller plus vite dans le travail.
L'idée est de vraiment bien séparer les différents "métiers" (lecture des fichiers, détection d'erreur, alignement de séquences...) du code et les différentes structures de données (fichiers d'input, fichiers d'output, séquences...). L'architecture devrait aussi une bonne reproductibilité et une relecture du code plus simple.

Dans **chaque fichier** (vide pour le moment), **j'ai essayer d'indiquer sont rôle** ainsi qu'une structure du code qui respecte (selon moi, c'est sûrement pas parfait), les conventions et bonnes pratiques.

&nbsp;

**Voici l'arborescence du projet avec un commentaire du rôle de chaque script :**

```
microtpct
├── __init__.py         # Obligatoire pour reconnaitre microtpct comme un package
├── __version__.py      # Informations de version et d'auteurs (pour la reproductibilité)
├── config              # Paramètres par défaults (mismatch max, remplacement de I/L...)
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   └── defaults.yaml   # Liste organisé des paramètres
├── core                # Coeur computationnel
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   ├── alignment.py    # Algorithme d'alignement
│   ├── metrics.py      # Calcul des métriques
│   ├── pipeline.py     # Orchestrateur des différents scripts
│   └── sequences.py    # Défini la forme des séquence bioloogique (protéines, peptides) ensemble de classes
├── interfaces          # Interfaces de l'outil
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   ├── cli.py          # En lignes de commandes
│   └── gui.py          # Interface graphique
├── io                  # Gestion des fichiers d'input et d'output
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   ├── readers.py      # Lit, parse et traite les inputs
│   ├── schema.py       # Défini les formats des inputs et output de façon centralisée, permet la validation
│   ├── validators.py   # Valide les formats d'input/output
│   └── writers.py      # Génère les outputs
└── utils               # Petits scripts utilitaires
    ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
    ├── exeptions.py    # Listes des exeptions propre à MicroTPCT
    ├── helpers.py      # Petites fonctions transverses utilisé partout (ex: time wrapper, gestion des paths)
    └── logging.py      # Génère les logs (pour la reproductibilités)
```