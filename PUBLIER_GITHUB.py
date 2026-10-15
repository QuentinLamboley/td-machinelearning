"""Publication guidée vers un NOUVEAU dépôt GitHub via Git et GitHub CLI.
Ce programme n'extrait aucun identifiant et refuse d'écraser un dépôt existant.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def call(*args, check=True, capture=False):
    return subprocess.run(list(args), cwd=ROOT, text=True, check=check,
                          capture_output=capture)


def run():
    print("\n=== Publication du TD Machine Learning / Master ESMIHA ===\n")
    print("Cette procédure crée un NOUVEAU dépôt ; elle n'écrase jamais le support d'origine.")
    for cmd in ("git", "gh"):
        if not shutil.which(cmd):
            raise RuntimeError(f"La commande {cmd!r} est introuvable. Voir README.md pour installer Git et GitHub CLI.")
    if not (ROOT / 'streamlit_app.py').is_file() or not (ROOT / 'requirements.txt').is_file():
        raise RuntimeError("Le dossier du projet est incomplet.")
    if (ROOT / '.git').exists():
        raise RuntimeError("Un dossier Git existe déjà ici. Publication automatique annulée pour éviter de changer un dépôt existant.")
    auth = call('gh', 'auth', 'status', check=False, capture=True)
    if auth.returncode:
        raise RuntimeError("Aucune connexion GitHub CLI active. Dans le terminal : gh auth login")
    user_result = call('gh', 'api', 'user', '--jq', '.login', capture=True)
    login = user_result.stdout.strip()
    if not login or '/' in login:
        raise RuntimeError("Impossible d'identifier le compte GitHub connecté.")
    print(f"\nCompte GitHub connecté : {login}")
    repo = input("Nom du nouveau dépôt [TD-Machine-Learning-ESMIHA] : ").strip() or 'TD-Machine-Learning-ESMIHA'
    if not re.fullmatch(r'[A-Za-z0-9_.-]{2,100}', repo) or repo.startswith('.'):
        raise RuntimeError("Nom de dépôt invalide. Utiliser lettres, chiffres, tirets, points ou underscores.")
    target = f'{login}/{repo}'
    exists = call('gh', 'repo', 'view', target, check=False, capture=True)
    if exists.returncode == 0:
        raise RuntimeError(f"Le dépôt {target} existe déjà. Choisir un nouveau nom, aucun dépôt n'a été modifié.")
    print("Visibilité : publique (accessible aux étudiants) ou privée (accès limité).")
    visibility = input("Rendre le dépôt public ? [o/N] : ").strip().lower() in {'o', 'oui', 'y', 'yes'}
    state = '--public' if visibility else '--private'
    print(f"\nNouveau dépôt : https://github.com/{target} ({'public' if visibility else 'privé'})")
    if input("Confirmer la création et la publication ? Tapez OUI : ").strip() != 'OUI':
        print("Publication annulée. Aucun changement.")
        return
    if not call('git', 'config', 'user.name', check=False, capture=True).stdout.strip() or \
       not call('git', 'config', 'user.email', check=False, capture=True).stdout.strip():
        raise RuntimeError("Configurer d'abord votre identité Git : git config --global user.name 'Nom' ; git config --global user.email 'email@example.com'")
    call('git', 'init', '-b', 'main')
    call('git', 'add', '.')
    call('git', 'commit', '-m', 'Publier le TD Machine Learning ESMIHA - V5.0')
    # GitHub CLI crée le dépôt distant et publie la branche main.
    call('gh', 'repo', 'create', target, state, '--source=.', '--remote=origin', '--push',
         '--description', 'TD interactif de classification supervisée - Master ESMIHA')
    print(f"\nPublication terminée : https://github.com/{target}")
    print("Déploiement Streamlit : https://share.streamlit.io/ (main / streamlit_app.py)")


if __name__ == '__main__':
    try:
        run()
    except (RuntimeError, subprocess.CalledProcessError, KeyboardInterrupt) as exc:
        print(f"\nPublication non terminée : {exc}", file=sys.stderr)
        print("Voir README.md. Si le dépôt a été créé mais le push a échoué, vérifier GitHub avant de réessayer.", file=sys.stderr)
        sys.exit(1)
