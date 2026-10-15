"""Limites de calcul communes au processus Streamlit, sans partage de données étudiantes."""
import threading
from contextlib import contextmanager

# Deux entraînements lourds au maximum, toutes sessions confondues.
_SLOTS = threading.BoundedSemaphore(value=2)

@contextmanager
def computation_slot(wait_seconds=180):
    if not _SLOTS.acquire(timeout=wait_seconds):
        raise TimeoutError('Le serveur traite déjà plusieurs calculs. Réessaie dans quelques instants.')
    try:
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=1):
            yield
    finally:
        _SLOTS.release()
