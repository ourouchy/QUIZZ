# Quiz Game

Un jeu de quiz prêt à la personnalisation. But : contenu en masse.

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/ourouchy/QUIZZ.git
cd QUIZZ/
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

## Structure des personnages

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
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
python main.py
```

## Contrôles

- Échap : Quitter le jeu 
