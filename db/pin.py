# db/pin.py - Sécurité Code PIN NOKIROVA 🔒

import hashlib
from db.base import get_connexion


def _hasher_pin(pin: str) -> str:
    """Hash le PIN avec SHA256 pour la sécurité"""
    return hashlib.sha256(pin.encode()).hexdigest()


def set_pin(pin: str) -> bool:
    """Définit ou change le code PIN"""
    if not pin or len(pin) < 4:
        return False
    try:
        pin_hash = _hasher_pin(pin)
        conn = get_connexion()
        cur = conn.cursor()
        cur.execute("""
            UPDATE securite
            SET pin_hash=?, pin_actif=1
            WHERE id=1
        """, (pin_hash,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Erreur set_pin : {e}")
        return False


def verifier_pin(pin: str) -> bool:
    """Vérifie si le PIN entré est correct"""
    try:
        pin_hash = _hasher_pin(pin)
        conn = get_connexion()
        cur = conn.cursor()
        cur.execute("""
            SELECT pin_hash FROM securite
            WHERE id=1 AND pin_actif=1
        """)
        res = cur.fetchone()
        conn.close()
        if not res:
            return False
        return res[0] == pin_hash
    except Exception as e:
        print(f"⚠️ Erreur verifier_pin : {e}")
        return False


def pin_existe() -> bool:
    """Vérifie si un PIN est défini"""
    try:
        conn = get_connexion()
        cur = conn.cursor()
        cur.execute("""
            SELECT pin_actif FROM securite WHERE id=1
        """)
        res = cur.fetchone()
        conn.close()
        return bool(res and res[0] == 1)
    except Exception as e:
        print(f"⚠️ Erreur pin_existe : {e}")
        return False


def supprimer_pin() -> bool:
    """Supprime le code PIN"""
    try:
        conn = get_connexion()
        cur = conn.cursor()
        cur.execute("""
            UPDATE securite
            SET pin_hash=NULL, pin_actif=0
            WHERE id=1
        """)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Erreur supprimer_pin : {e}")
        return False