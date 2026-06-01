# notifications.py - Popups animés pour les récompenses 🎁

import customtkinter as ctk


def notification_xp(parent, points: int, message: str = ""):
    """
    Affiche un popup de récompense XP qui disparaît automatiquement.
    """
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("350x120+800+50")
    popup.configure(fg_color="#FFD93D")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)
    popup.attributes("-alpha", 0.95)
    
    # Contenu
    frame = ctk.CTkFrame(popup, fg_color="#FFD93D", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    ctk.CTkLabel(frame, text=f"🎁  +{points} XP !",
                 font=ctk.CTkFont(size=24, weight="bold"),
                 text_color="#374151").pack(pady=(15, 5))
    
    if message:
        ctk.CTkLabel(frame, text=message,
                     font=ctk.CTkFont(size=12),
                     text_color="#374151").pack()
    
    # Disparaît après 2 secondes
    popup.after(2000, popup.destroy)


def notification_badge(parent, badge_emoji: str, badge_nom: str, badge_desc: str):
    """
    Popup spécial pour un nouveau badge débloqué.
    """
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("400x180+700+100")
    popup.configure(fg_color="#A855F7")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)
    
    frame = ctk.CTkFrame(popup, fg_color="#A855F7", corner_radius=18)
    frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    ctk.CTkLabel(frame, text="🏆 NOUVEAU BADGE !",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 5))
    
    ctk.CTkLabel(frame, text=badge_emoji,
                 font=ctk.CTkFont(size=40)).pack()
    
    ctk.CTkLabel(frame, text=badge_nom,
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(0, 2))
    
    ctk.CTkLabel(frame, text=badge_desc,
                 font=ctk.CTkFont(size=11),
                 text_color="#FFFFFF").pack(pady=(0, 15))
    
    popup.after(3500, popup.destroy)


def notification_succes(parent, titre: str, message: str):
    """
    Popup de succès générique.
    """
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("380x100+750+60")
    popup.configure(fg_color="#00C853")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)
    
    frame = ctk.CTkFrame(popup, fg_color="#00C853", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    ctk.CTkLabel(frame, text=f"✅ {titre}",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 3))
    
    ctk.CTkLabel(frame, text=message,
                 font=ctk.CTkFont(size=11),
                 text_color="#FFFFFF").pack()
    
    popup.after(2500, popup.destroy)