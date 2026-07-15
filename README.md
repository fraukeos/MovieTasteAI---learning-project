# MovieTasteAI (Lernprojekt)

Einfaches Machine-Learning-Projekt, das eine Netflix-Wiedergabehistorie analysiert und daraus persönliche Filmempfehlungen erstellt.

> Der konkrete Modellablauf wird in `MODEL.md` erklärt.
> Diese Datei beschreibt nur die Rahmenbedingungen, Architektur und Projektstruktur.

---


## Architektur
```text
                    Netflix Export
                         |
                         v
              +-------------------+
              | netflix_history   |
              +-------------------+
                         |
                         v
              Gesehene Filme + Score
                         |
                         |
                         v
              +-------------------+
              | Datenaufbereitung |
              +-------------------+
                         |
                         v
              +-------------------+
              | Random Forest     |
              | Modell            |
              +-------------------+
                         |
                         |
        +----------------+----------------+
        |                                 |
        v                                 v

  Gesehene Filme                 Neue Filme aus TMDb
  (Training)                     (Kandidaten)

                                        |
                                        v

                              KI bewertet jeden Film

                                        |
                                        v

                              Top 20 Empfehlungen
```
## Features
- Liest den exportierten Netflix-Verlauf ein (`Title`, `Date`)
- Entfernt Serienfolgen aus der Historie (aktuell nur Filmempfehlungen)
- Berechnet einen impliziten Interesse-Score aus der Wiedergabehäufigkeit
- Analysiert bevorzugte Genres
- Holt Filmdaten und Ratings über TMDb
- Trainiert ein Random-Forest-Modell
- Nutzt Train/Test Split zur Modellbewertung
- Nutzt Cross Validation zur stabileren Bewertung
- Erstellt Filmempfehlungen
- Erstellt Visualisierungen:
  - Empfehlungen
  - Feature Importance


## Modell
Das Modell verwendet zwei Hauptinformationen:
```text
# 1. Persönliche Interessen
Aus der Netflix-Historie werden bevorzugte Genres abgeleitet.
Gewichtung: 50 %

# 2. Allgemeine Filmqualität
Das TMDb Rating wird ebenfalls berücksichtigt.
Gewichtung: 50 %
```
## Input
Netflix Titelverlauf (muss von Netflix exportiert werden):
> Beispiel:
> ```text
> Title,Date
>"The Boroughs: Die Graue Rebellion","6/6/26"
>"Inception","5/5/26"
> ```

## Installation
Benötigte Bibliotheken installieren:
pip install -r requirements.txt

## TMDb API Key ergänzen
1. Erstelle eine Datei `.env`
2. Füge deinen Schlüssel ein: TMDB_API_KEY=dein_api_key

## Programm starten
python main.py

## Technologien
- Python
- pandas
- matplotlib
- scikit-learn
- requests
- python-dotenv

## Ergebnisse
Nach erfolgreichem Durchlauf werden Dateien im Ordner output erzeugt:
```text
Datei | Zweck
recommendations.csv | Liste der empfohlenen Filme
recommendations.png | Grafische Darstellung der Empfehlungen
feature_importance.csv | Wichtigkeit der Modellmerkmale
feature_importance.png | Visualisierung der wichtigsten Features
```
> Beispieldaten können als Referenz unter "output_example" eingesehen werden

### Projektstruktur
```text
MovieTasteAI/
│
├── data/
│   ├── netflix_history.csv     (Netflix-Historie, muss manuell eingefügt werden, Beispiel vorhanden)
│   ├── movies.csv              (wird automatisch erzeugt)
│   └── candidates.csv          (wird automatisch erzeugt)
│
├── output/                     (wird bei erfolgreichem Durchlauf erzeugt)
│   ├── recommendations.csv
│   ├── recommendations.png
│   ├── feature_importance.csv
│   └── feature_importance.png
│
├── main.py
├── tmdb.py
├── MODEL.md
├── README.md
├── .env.example
├── .env                        (eigener TMDb API Key)
├── requirements.txt
└── .gitignore
```

### Beschreibung der Ordner und Dateien
```text
Datei/Ordner  |      Zweck
data/	       |      Eingabedaten und automatisch erzeugte Filmdaten
output/	|      Empfehlungen und Visualisierungen
.env.example	|      Vorlage für die TMDb API Konfiguration
tmdb.py	|      Kommunikation mit der TMDb API
main.py	|      Hauptprogramm und Machine-Learning-Ablauf
MODEL.md	|      Erklärung des verwendeten Modells
requirements.txt|	Benötigte Python-Bibliotheken
.gitignore	|      Dateien, die nicht veröffentlicht werden sollen
```
