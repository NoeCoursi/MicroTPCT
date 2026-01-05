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
│   └── sequences.py    # Défini la forme des séquence biologique, ensemble de classes propres et immuables
├── interfaces          # Interfaces de l'outil
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   ├── cli.py          # En lignes de commandes
│   └── gui.py          # Interface graphique
├── io                  # Gestion des fichiers d'input et d'output
│   ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
│   ├── converter.py    # Converti les inputs une fois validés en sequences propres pour le core/
│   ├── readers.py      # Lit, parse et traite les inputs
│   ├── schema.py       # Défini les formats des inputs et output de façon centralisée, sans validation
│   ├── validators.py   # Valide les formats d'input
│   └── writers.py      # Génère les outputs
└── utils               # Petits scripts utilitaires
    ├── __init__.py     # Obligatoire utiliser les scripts de ce dossier dans d'autres parties du projet.
    ├── exeptions.py    # Listes des exeptions propre à MicroTPCT
    ├── helpers.py      # Petites fonctions transverses utilisé partout (ex: time wrapper, gestion des paths)
    └── logging.py      # Génère les logs (pour la reproductibilités)
```

&nbsp;

## Quelques pro tips pour travailler proprement

#### Implémenter, modifier ou créer un nouveau script

Au lieu de tous travailler sur la même branche du projet Git, je propose que nous utilisions des branches bien nommée pour chaque étapes du projets/implémentation.

Pour créer un branche :

```
git pull origin main
git checkout -b nom/implémentation
```

*Ici, on récupère le dernier contenu de main (ou de la branche que l'on veut fork) puis on crée la nouvelle branche (option `-b` de `checkout`).*

**Attention :**

- **Vérifiez bien que vous travaillez sur la nouvelle branche** *(en bas à gauche dans VScode)*
- **Nommez bien votre branche** `nom/implémentation` *(exemple : ambre/aligners-fix-bug)*

Pour retourner se balader entre les différentes branche : `git checkout nom/implémentation` **sans le `-b`**


#### Travailler dans un environnement virtuel

- Pour le créer :

Dans un terminal de VScode : 

Pour windows :
```
python -m venv venv
```

Pour Linux (s/o Ambroise) :
```
python3 -m venv venv pour Linux
```

- Pour l'activer :

Pour windows :
```
.\venv\Scripts\Activate
```

Pour Linux (Ambroise RPZ) :
```
source venv/bin/activate
```
*Bien vérifier que l'environnement est actif avec l'inscription (.venv) devant la ligne.*

- Pour configurer VScode à utiliser l’environnement :

Ctrl + Shift + P > écrire Python: Select Interpreter > séléctionner le fichier suggéré

#### Installer le package microtpct en mode editable

Si vous tenter d'utiliser `microtpct` en dehors de `src/` vous risquez de rencontrer l'erreur : `ModuleNotFoundError: No module named 'microtpct'`

Cette erreur vient du fait que Python ne trouve pas `microtpct` dans son `sys.path` qui gère les packages chargés dans l'environnement. *Croyez-moi, ce n'est qu'après une looooongue discussion avec ChatGPT que j'ai compris l'erreur...*

Pour fixer cette erreur, il existe plusieur façon de le faire. La plus simple et la plus pro est sûrement d'nstaller le package `microtpct` en mode editable :

```
pip install -e .
```

Ceci permet de rendre toute modification dans le code immédiatement utilisable. Si tout va bien, **vous n'aurez donc besoin d'exécuter cette commande qu'une fois** après le clone du repo.

*Pour information, le dossier `microtpct.egg-info` qui est créé est ignoré par le `.gitignore`.*


#### Gérer proprement les packages

L'environnement virtuel permet de n'utiliser que les packages nécéssaires au projet.

A la première exécution du programme après un `git pull` ou un `git clone` :

```
pip install -r requirements.txt
```

Pour mettre à jour les packages nécéssaires dans `requirements.txt` après utilisation d'un nouveau package :

```
pip freeze > requirements.txt
```

&nbsp;

## Réflexion sur le traitement des données

En input, on a  :

- Sortie Proline des peptides matchés au protéome alternatif (nécessaire) → **A**
- Fasta du protéome canonique de l'organisme (nécéssaire) → **B**
- Sortie Proline des peptides matchés au protéome canonique (optionnel) → **C**

&nbsp;

On aligne (~ CTRL + F) chaque peptides **A** sur **B**.
Pour chaque peptides **A**, on a alors deux cas :

- Le peptides n'est matché aucune protéine canonique → Appartient vraissemblablement à une microprotéine
- Le peptides est matché sur une ou plusieurs protéines canoniques → On ne peut pas vraiment conclure

&nbsp;

Si on regarde du point de vue accessions du protéome alternatif (PXXXXX, IP_XXXXXXX, II_XXXXXXX) de la liste **A** :

- Si tous les peptides **A** d'une même accession sont matchés au(x) même(s) protéine(s) **B** → Vraissemblablement pas une microprotéine
- Si aucun peptide **A** d'une même accession matché à rien → Vraissemblablement une microprotéine

Si les peptides **A** sont matchés à une protéine qui apparait également dans la liste **C**, alors cela renforce notre niveau de certitude sur le fait que le peptide est issus d'un artéfact de digestion et pas d'une microprotéine.

Si on prend la nomenclature d'openprot (refProt, II_, IP_), il y a fort à parier que les refProt et les II_ match avec le protéome canonique et que les IP_ ne match à rien. Les cas intéressant sont les cas où on observe l'inverse.


En output on pourrait fournir :

- Statistiques globales
    - Nombre de peptides **A** total
    - Nombre de peptides **A** matchés
    - Nombre de peptides **A** non matchés
    - Nombre de protéines alternatives **A** total
    - Nombre de protéines alternatives **A** matché au moins une fois
    - Nombre de protéines alternatives **A** non matchés
    - Nombre de protéines **B** total
    - Nombre de protéines **B** matché au moins une fois
    - Nombre de protéines **B** non matchés
    - Nombre de protéines **C** total
    - Nombre de protéines **C** matché au moins une fois
    - Nombre de protéines **C** non matchés

*Les neufs derniers points peuvent être représentés sous la forme d'un diagramme de Venn pour une meilleurs lisibilités*

- Fichiers de sortie :
    - Liste des peptides **A** avec les matchs éventuels : *accession,peptide_sequence,match,matched_ids,num_matches*


#### Questions :

- Comment est-ce possible que plusieurs peptides d'une même accession match la (les) même(s) protéines ?
- Faudrait-il que l'on prenne en compte la taille des peptides ? Un peptides court à statistiquement plus de chance d'être matché quelque part, qu'un peptides long.