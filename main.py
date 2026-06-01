# main.py - NOKIROVA : Programme principal 🟡

from ia_handler import demander_ia, expliquer_simplement, creer_resume
from document_parser import lire_document
from audio_generator import generer_audio
from exercice_generator import generer_qcm, generer_questions_cours, generer_exercices_examen
import os


def afficher_menu():
    """Affiche le menu principal stylé"""
    print("\n" + "🟡" * 30)
    print("       🎓 NOKIROVA - Ton Prof Intelligent 🎓")
    print("🟡" * 30)
    print("│ 1. 📥 Importer un cours (PDF/Word/PPT)")
    print("│ 2. 📝 Créer un résumé")
    print("│ 3. 💡 Expliquer simplement")
    print("│ 4. 🎯 Générer des QCM")
    print("│ 5. ❓ Générer des questions de cours")
    print("│ 6. 📚 Générer des exercices examen")
    print("│ 7. 🎧 Créer un audio (texte → voix)")
    print("│ 8. 💬 Poser une question libre à l'IA")
    print("│ 0. 👋 Quitter")
    print("🟡" * 30)
    return input("👉 Ton choix : ").strip()


def sauvegarder_texte(texte: str, nom_fichier: str):
    """Sauvegarde un texte dans outputs/"""
    chemin = os.path.join("outputs", nom_fichier)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    print(f"💾 Sauvegardé : {chemin}")


def main():
    """Programme principal de NOKIROVA"""
    print("\n🎉 Bienvenue dans NOKIROVA !")
    print("✨ Ton professeur intelligent personnel ✨\n")
    
    cours_actuel = ""
    
    while True:
        choix = afficher_menu()
        
        # ════════ 1. IMPORTER UN COURS ════════
        if choix == "1":
            print("\n📥 IMPORTER UN COURS")
            chemin = input("Chemin du fichier (ex: C:/Users/HP/Desktop/mon_cours.pdf) : ").strip().strip('"')
            
            if os.path.exists(chemin):
                print("⏳ Lecture en cours...")
                cours_actuel = lire_document(chemin)
                print(f"✅ Cours chargé ! ({len(cours_actuel)} caractères)")
                print(f"📖 Aperçu : {cours_actuel[:300]}...")
            else:
                print("❌ Fichier introuvable. Vérifie le chemin.")
        
        # ════════ 2. RÉSUMÉ ════════
        elif choix == "2":
            if not cours_actuel:
                print("⚠️ Importe d'abord un cours (option 1)")
                continue
            print("\n📝 Création du résumé en cours... ⏳")
            resume = creer_resume(cours_actuel[:5000])
            print("\n" + "="*60)
            print(resume)
            print("="*60)
            sauvegarder_texte(resume, "resume.txt")
        
        # ════════ 3. EXPLIQUER SIMPLEMENT ════════
        elif choix == "3":
            if not cours_actuel:
                print("⚠️ Importe d'abord un cours (option 1)")
                continue
            print("\n💡 Explication simplifiée en cours... ⏳")
            explication = expliquer_simplement(cours_actuel[:5000])
            print("\n" + "="*60)
            print(explication)
            print("="*60)
            sauvegarder_texte(explication, "explication.txt")
        
        # ════════ 4. QCM ════════
        elif choix == "4":
            if not cours_actuel:
                print("⚠️ Importe d'abord un cours")
                continue
            try:
                nb = int(input("Combien de QCM ? (1-20) : "))
            except ValueError:
                nb = 5
            print(f"\n🎯 Génération de {nb} QCM... ⏳")
            qcm = generer_qcm(cours_actuel[:5000], nb)
            print("\n" + "="*60)
            print(qcm)
            print("="*60)
            sauvegarder_texte(qcm, "qcm.txt")
        
        # ════════ 5. QUESTIONS DE COURS ════════
        elif choix == "5":
            if not cours_actuel:
                print("⚠️ Importe d'abord un cours")
                continue
            try:
                nb = int(input("Combien de questions ? : "))
            except ValueError:
                nb = 5
            print(f"\n❓ Génération de {nb} questions... ⏳")
            questions = generer_questions_cours(cours_actuel[:5000], nb)
            print("\n" + "="*60)
            print(questions)
            print("="*60)
            sauvegarder_texte(questions, "questions.txt")
        
        # ════════ 6. EXERCICES EXAMEN ════════
        elif choix == "6":
            if not cours_actuel:
                print("⚠️ Importe d'abord un cours")
                continue
            print("\nNiveaux disponibles :")
            print("  🟢 1. debutant")
            print("  🟡 2. intermediaire")
            print("  🟠 3. difficile")
            print("  🔴 4. ultra_difficile")
            niveau_choix = input("Niveau (1-4) : ").strip()
            niveaux = {"1": "debutant", "2": "intermediaire", "3": "difficile", "4": "ultra_difficile"}
            niveau = niveaux.get(niveau_choix, "intermediaire")
            
            try:
                nb = int(input("Combien d'exercices ? : "))
            except ValueError:
                nb = 3
            
            print(f"\n📚 Génération de {nb} exercices niveau {niveau}... ⏳")
            exos = generer_exercices_examen(cours_actuel[:5000], niveau, nb)
            print("\n" + "="*60)
            print(exos)
            print("="*60)
            sauvegarder_texte(exos, f"examen_{niveau}.txt")
        
        # ════════ 7. AUDIO ════════
        elif choix == "7":
            print("\n🎧 CRÉER UN AUDIO")
            print("1. Audio du résumé du cours actuel")
            print("2. Audio d'un texte personnalisé")
            sous_choix = input("Choix : ").strip()
            
            if sous_choix == "1" and cours_actuel:
                print("⏳ Création du résumé puis audio...")
                texte = creer_resume(cours_actuel[:3000])
                generer_audio(texte, "cours_audio.mp3", "jeune_femme")
            elif sous_choix == "2":
                texte = input("Texte à transformer : ")
                generer_audio(texte, "mon_audio.mp3", "jeune_femme")
            else:
                print("⚠️ Importe d'abord un cours")
        
        # ════════ 8. QUESTION LIBRE ════════
        elif choix == "8":
            question = input("\n💬 Ta question : ")
            print("\n⏳ NOKIROVA réfléchit...")
            reponse = demander_ia(question)
            print("\n" + "="*60)
            print(reponse)
            print("="*60)
        
        # ════════ 0. QUITTER ════════
        elif choix == "0":
            print("\n👋 À bientôt sur NOKIROVA ! Bon courage pour tes études ! 💪🟡")
            break
        
        else:
            print("❌ Choix invalide. Essaie un chiffre entre 0 et 8.")


if __name__ == "__main__":
    main()