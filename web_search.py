# web_search.py - Recherche Web gratuite via DuckDuckGo 🌐

from duckduckgo_search import DDGS


def rechercher_web(query: str, max_results: int = 5) -> list:
    """
    Effectue une recherche web et retourne les résultats.

    Args:
        query: La requête de recherche.
        max_results: Nombre maximum de résultats (défaut 5).

    Returns:
        Une liste de dictionnaires avec 'titre', 'url', 'extrait'.
    """
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "titre": r.get("title", ""),
                    "url": r.get("href", ""),
                    "extrait": r.get("body", "")
                })
            return results
    except Exception as e:
        print(f"⚠️ Erreur recherche web : {e}")
        return []


def enrichir_prompt_web(question: str) -> str:
    """
    Enrichit une question avec des informations du web.
    Retourne la question enrichie avec le contexte web.
    """
    resultats = rechercher_web(question)
    if not resultats:
        return question

    contexte = "\n\n".join([
        f"🌐 {r['titre']}\n{r['extrait']}\n🔗 {r['url']}"
        for r in resultats
    ])
    return f"{question}\n\n📖 **Informations récentes du web :**\n{contexte}"