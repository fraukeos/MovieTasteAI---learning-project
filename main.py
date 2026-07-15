# ============================================================
# MovieTasteAI - Hauptprogramm
# ============================================================
#
# Dieses Programm:
#
# 1. liest die Netflix-Historie
# 2. entfernt Serienfolgen (es sollen nur Filme bewertet werden)
# 3. berechnet einen persönlichen Interesse-Score (basierend auf Re-Watches)
# 4. lädt Filmdaten von TMDb
# 5. erstellt Machine Learning Features
# 6. trainiert ein Random Forest Modell
# 7. bewertet das Modell
# 8. erstellt Filmempfehlungen
# 9. speichert Visualisierungen
#
# ============================================================


import os

from pathlib import Path

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

from sklearn.model_selection import train_test_split, cross_val_score

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Import aus selbst erstelltem Modul tmdb.py
from tmdb import create_movies_file, create_candidates_file

# Warnungen bzgl. unbekannter Genres unterdrücken (stattdessen wird Liste angezeigt)
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.preprocessing._label")


# ============================================================
# Ordner vorbereiten
# ============================================================

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)


# ============================================================
# Netflix Historie laden
# ============================================================

print("\n[1/8] Netflix-Historie laden")

history = pd.read_csv("data/netflix_history.csv")
print("Anzahl Einträge in Historie:", len(history))


# ============================================================
# Serien entfernen
# ============================================================
#
# Netflix exportiert Serienfolgen einzeln.
#
# Beispiel:
#
# The Boroughs: Folge 1
# The Boroughs: Folge 2
#
# Diese würden das Modell verzerren.
#
# Serien werden entfernt, wenn mehrere Titel denselben Anfang vor ":" besitzen.
#
# ============================================================

print("\n[2/8] Serien entfernen")

def remove_series(titles):
    prefixes = {}
    for title in titles:
        if ":" in title:
            prefix = title.split(":")[0]    # schaut sich den Teil vor dem : an
            prefixes[prefix] = (prefixes.get(prefix, 0) + 1) # zählt wie oft Präfix vorkommt

    movies = []
    for title in titles:
        remove = False
        if ":" in title:
            prefix = title.split(":")[0]
            if prefixes.get(prefix, 0) >= 3:
                remove = True   # entferne Titel, wenn Präfix >= 3 Mal vorkommt

        if not remove:
            movies.append(title)

    return movies

movie_titles = remove_series(history["Title"].unique().tolist())

print("Anzahl Filme nach Einsatz des Serienfilters:", len(movie_titles))


# ============================================================
# Interesse-Score berechnen
# ============================================================
#
# Da Netflix kein eigenes Rating liefert, wird Häufigkeit des Sehens genutzt.
## Ein Film, der mehrfach gesehen wurde, wird als stärkeres Interesse interpretiert.
#
# ============================================================

print("\n[3/8] Interesse berechnen")

watch_count = (history.groupby("Title").size().reset_index(name="Views"))

def calculate_interest(views):
    if views == 1:
        return 5

    elif views == 2:
        return 7

    elif views == 3:
        return 9

    elif views >3:
        return 10
    
    else:
        return 0

watch_count["Interest"] = (watch_count["Views"].apply(calculate_interest))


# ============================================================
# TMDb Daten laden
# ============================================================

print("\n[4/8] TMDb Filmdaten laden")

# API abfragen reduzieren
if Path("data/movies.csv").exists():
    movies = pd.read_csv("data/movies.csv")

else:
    movies = create_movies_file(movie_titles)

movies = movies.merge(watch_count, on="Title", how="inner")


# ============================================================
# Trainingsdaten vorbereiten
# ============================================================

print("\n[5/8] Features erstellen")

movies["GenreList"] = (movies["Genres"].fillna("").str.split("|"))

encoder = MultiLabelBinarizer()

# Genre-Liste in Zahlenwerte transformieren
genre_features = encoder.fit_transform(movies["GenreList"])
genre_features = pd.DataFrame(genre_features, columns=encoder.classes_)

# 50% Gewichtung Genre
genre_features = (genre_features * 0.5)

# 50% Gewichtung TMDb Rating
rating_feature = (movies["Rating"] / 10 * 0.5)
rating_feature = pd.DataFrame({"TMDb_Rating": rating_feature})

# Alle Features zusammenführen
X = pd.concat([genre_features, rating_feature], axis=1)
y = movies["Interest"]


# ============================================================
# Train/Test Split
# ============================================================
print("\n[6/8] Modell trainieren")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)


# ============================================================
# Modell bewerten
# ============================================================
prediction = model.predict(X_test)

mae = mean_absolute_error(y_test, prediction)

cv_scores = cross_val_score(model, X, y, cv=5, scoring="neg_mean_absolute_error")
cv_mae = (-cv_scores.mean())

print("\nModellbewertung")

print("Test MAE:", round(mae, 2))
print("Cross Validation MAE:", round(cv_mae, 2))


# ============================================================
# Feature Importance speichern
# ============================================================
importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_})

importance = importance.sort_values("Importance", ascending=False)

# Feature Impportance als CSV speichern
importance.to_csv("output/feature_importance.csv", index=False)


# ============================================================
# Empfehlungen ermitteln laden
# ============================================================
print("\n[7/8] Empfehlungen erstellen")

if Path("data/candidates.csv").exists():
    try:
        reload_candidates = input("Kandidatenliste neu von TMDb laden? (j/n): ").lower()
        if reload_candidates not in ["j", "n"]:
            raise ValueError("Ungültige Eingabe")

    except ValueError:
        print("Ungültige Eingabe. Vorhandene Kandidatenliste wird verwendet.")
        reload_candidates = "n"

else:
    reload_candidates = "j"     # falls Pfad nicht existiert, wird reload_candidates automatisch auf j gesetzt

if reload_candidates == "j":
    candidates = create_candidates_file(pages=5)

else:
    print("Vorhandene Kandidatenliste wird verwendet.")
    candidates = pd.read_csv("data/candidates.csv")
        
# bereits gesehene Filme entfernen
candidates = candidates[~candidates["Title"].isin(movies["Title"])]

# Index zurücksetzen, um Fehler zu vermeiden
candidates = candidates.reset_index(drop=True)

# Genres ergänzen (Gewichtung 50%)
candidates["GenreList"] = (candidates["Genres"].fillna("").str.split("|"))


# Prüfen, ob Kandidaten unbekannte Genres enthalten:
#
# Einige TMDb Genres können in den Netflix-Daten nicht vorkommen. #
# Diese Features kennt das Modell dann nicht und kann sie nicht verwenden.

# Genres aus Netflixhistorie
known_genres = set(encoder.classes_)

# alle TMDb Genres
candidate_genres_all = set(
    genre
    for genres in candidates["GenreList"]
    for genre in genres
)

# TMDb Genres die Modell nicht bekannt sind, da mit Netflixhistorie trainiert wurde
unknown_genres = (candidate_genres_all - known_genres)

if unknown_genres:
    print("\nHinweis: Folgende TMDb Genres werden nicht berücksichtigt:")
    
    for genre in sorted(unknown_genres):
        print("-", genre)

candidate_genres = encoder.transform(candidates["GenreList"])

candidate_genres = pd.DataFrame(candidate_genres, columns=encoder.classes_)
candidate_genres = (candidate_genres * 0.5)

# TMDb Rating ergänzen (Gewichtung 50%)
candidate_rating = pd.DataFrame({"TMDb_Rating": candidates["Rating"] / 10 * 0.5})

# Features kombinieren
candidate_features = pd.concat([candidate_genres, candidate_rating], axis=1)

# Vorhersage für Kandidatenfilme
candidates["Prediction"] = (model.predict(candidate_features))

# Top 20 ermitteln
recommendations = (candidates.sort_values("Prediction",ascending=False).head(20))

# Empfehlungen als CSV speichern
recommendations.to_csv("output/recommendations.csv", index=False)


# ============================================================
# Feature Importance visualisieren
# ============================================================
#
# Diese Grafik zeigt:
# Welche Genres und Features das Modell besonders stark beeinflussen.
#
# ============================================================

# Nur die wichtigsten 10 Features anzeigen,
# damit die Grafik lesbar bleibt.

top_features = (importance.head(10).sort_values("Importance", ascending=True))

plt.figure(figsize=(10, 7))

# automatische Farbskala
norm = colors.Normalize(
    top_features["Importance"].min(),
    top_features["Importance"].max()
)

bar_colors = cm.viridis(norm(top_features["Importance"]))

plt.barh(
    top_features["Feature"],
    top_features["Importance"],
    color=bar_colors
)

plt.xlabel("Einfluss auf Modellentscheidung")
plt.ylabel("Feature")
plt.title("MovieAI - Feature Importance")

plt.tight_layout()

# Grafik speichern
plt.savefig("output/feature_importance.png", dpi=300)

# Grafik schließen
plt.close()

print("\nFeature Importance gespeichert:")
print("output/feature_importance.png")


# ============================================================
# Visualisierung der Empfehlungen
# ============================================================


print("\n[8/8] Visualisierungen erstellen")

plt.figure(figsize=(10,8))

# automatische Farbskala
norm = colors.Normalize(
    recommendations["Prediction"].min(),
    recommendations["Prediction"].max()
)

bar_colors = cm.viridis(norm(recommendations["Prediction"]))

plt.barh(
    recommendations["Title"],
    recommendations["Prediction"],
    color=bar_colors
)

plt.xlabel("Vorhergesagtes persönliches Interesse")
plt.title("MovieAI Empfehlungen")
plt.gca().invert_yaxis()
plt.tight_layout()

# Grafik speichern
plt.savefig("output/recommendations.png", dpi=300)

# Grafik schließen
plt.close()


print("\nFertig!")
print("Dateien befinden sich im output Ordner.")
