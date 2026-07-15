# ============================================================
# MovieAI - TMDb Schnittstelle
# ============================================================
#
# Diese Datei übernimmt:
#
# - Kommunikation mit der TMDb API
# - Suche nach Filmen
# - Laden von Genres
# - Laden des TMDb Ratings
# - Erstellen von CSV-Dateien
#
# Serien werden bewusst nicht gesucht.
# MovieAI arbeitet nur mit Filmen.
#
# ============================================================


import os
import time
import requests
import pandas as pd

from dotenv import load_dotenv


# ============================================================
# API Einstellungen laden
# ============================================================

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = ("https://api.themoviedb.org/3")

if not TMDB_API_KEY:

    raise ValueError("TMDB_API_KEY fehlt. Bitte .env Datei prüfen.")


# ============================================================
# TMDb Anfrage
# ============================================================

def tmdb_request(endpoint, params=None):

    if params is None:
        params = {}

    params["api_key"] = TMDB_API_KEY
    params["language"] = "de-DE"

    url = (BASE_URL + endpoint)

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

# ============================================================
# Einzelnen Film suchen
# (wird später genutzt, um Metadaten zu Filmen aus Netflixhistorie zu ergänzen)
# ============================================================

def search_movie(title):
    data = tmdb_request("/search/movie", {"query": title})
    results = data.get("results", [])

    if not results:
        return None

    movie = results[0]
    return {
        "id": movie["id"],
        "title": movie.get("title", title),
        "original_title": movie.get("original_title",title)
    }


# ============================================================
# Filmdetails laden (Genres und Rating)
# ============================================================

def get_movie_details(movie_id):
    data = tmdb_request(f"/movie/{movie_id}")
    genres = []
    for genre in data.get("genres",[]):
        genres.append(genre["name"])

    return {"Genres":"|".join(genres), "Rating":data.get("vote_average", 0)}


# ============================================================
# Netflix Titel in Filmdaten umwandeln
# ============================================================

def create_movies_file(titles, output="data/movies.csv"):
    movies = []     # Liste der Filme (zu Beginn leer)
    print("\nLade Netflix-Filme von TMDb...")

    for title in titles:
        result = search_movie(title)

        if result:
            details = get_movie_details(result["id"])
            movies.append({                     # Filmliste wird erweitert um gefundene Filme
                    "Title": result["title"],
                    "Original_Title": result["original_title"],
                    "Genres": details["Genres"],
                    "Rating": details["Rating"]
                })

        else:   # wenn ein Film nicht auf TMDb gefunden wurde
            print("Nicht gefunden:", title)

        # Kleine Pause verhindert zu viele API-Anfragen
        time.sleep(0.2)

    df = pd.DataFrame(movies)

    # Liste zu CSV konvertieren, damit sie weiterverwendet werden kann
    df.to_csv(output, index=False)
    print("\nGespeichert:", output)
    return df


# ============================================================
# Kandidatenfilme laden
# ============================================================
#
# Für Empfehlungen brauchen wir Filme, die noch nicht gesehen wurden.
#
# TMDb bietet dafür beliebte Filme.
#
# ============================================================

def create_candidates_file(pages=5,    # nur erste 5 Seiten sollen betrachtet werden, um Datenmenge zu reduzieren
    output="data/candidates.csv"):
    movies = []     
    print("\nLade Empfehlungs-Kandidaten...")

    for page in range(1, pages + 1):
        print(f"Lade TMDb-Seite {page}/{pages}...")
        data = tmdb_request("/movie/popular", {"page": page})

        for movie in data.get("results", []):
            details = get_movie_details(movie["id"])
            movies.append({     # Filmliste wird erweitert
                    "Title": movie["title"],
                    "Genres": details["Genres"],
                    "Rating": details["Rating"]
                })

        time.sleep(0.2)

    df = pd.DataFrame(movies)
    df = df.drop_duplicates(subset="Title")     # doppelte Titel löschen

    # Liste zu CSV umwandeln
    df.to_csv(output, index=False)
    print("\nGespeichert:", output)
    return df