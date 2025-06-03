# Quiz Game

Un jeu de quiz interactif avec des personnages animés.

## Installation

1. Cloner le repository :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Structure des dossiers

```
characters/
  character_name/
    video/           # Pour les personnages avec vidéos
      intro.mp4
      outro.mp4
      pose1.mp4
      ...
    image/           # Pour les personnages avec images
      intro.png
      outro.png
      question.png
      answer.png
    voice/           # Sons pour tous les personnages
      A.mp3
      B.mp3
      C.mp3
      D.mp3
      intro.mp3
      outro.mp3
common_sounds/       # Sons communs
  timer.mp3
  answer.mp3
```

## Lancement

```bash
python main.py
```

## Contrôles

- Échap : Quitter le jeu 