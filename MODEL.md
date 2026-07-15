# MODELLERKLÄRUNG

# Wie funktioniert das Empfehlungsmodell?

## Übersicht

MovieTasteAI analysiert die eigene Netflix-Wiedergabehistorie und versucht daraus abzuleiten, welche Filme wahrscheinlich gefallen könnten.

Das Programm verwendet keine manuell vergebenen Bewertungen, sondern erzeugt einen einfachen Interessescore aus dem bisherigen Wiedergabeverhalten.

Zusätzlich werden Filminformationen von TMDb verwendet:

- Filmgenres
- allgemeines TMDb Rating

Der Ablauf:

```
Netflix Historie
       |
       v
Filme erkennen und bereinigen
(Serien werden entfernt)
       |
       v
Filmdaten von TMDb laden
       |
       v
Features erstellen
(Genres + Rating)
       |
       v
Random Forest Modell trainieren
       |
       v
Neue Filme aus TMDb bewerten
       |
       v
Top 20 Empfehlungen erzeugen
```

---

# Welche Daten verwendet das Modell?

## 1. Netflix-Wiedergabeverhalten

Die Netflix-Datei enthält:

```
Title,Date
"Inception","6/6/26"
```

Das Programm betrachtet, wie häufig ein Film in der Historie vorkommt.
Da Netflix keine persönliche Bewertung liefert, wird daraus ein einfacher Interessescore erzeugt:

| Anzahl angesehen | Interesse-Wert |
| ---------------- | -------------: |
| 1x gesehen       |              5 |
| 2x gesehen       |              7 |
| 3x gesehen       |              9 |
| 4+ mal gesehen   |             10 |

Die Idee:
Ein Film, der mehrfach angesehen wurde, war vermutlich besonders interessant.

---

# Welche Filmeigenschaften werden analysiert?

Das Modell verwendet zwei Hauptinformationen.
Die Gewichtung ist:
```
Genre-Interesse       50 %
TMDb Rating           50 %
```
Dadurch kombiniert das Modell:
- persönlichen Geschmack
- allgemeine Filmqualität

---
# 1. Genres

Von TMDb werden die Genres eines Films geladen.
Beispiel:

```
Inception
```
wird zu:
```
Action
Science Fiction
Thriller
```
Da ein Computer keine Texte direkt verarbeiten kann, werden Genres in Zahlen umgewandelt.

Beispiel:
| Genre           | Wert |
| --------------- | ---: |
| Action          |    1 |
| Science Fiction |    1 |
| Comedy          |    0 |
| Horror          |    0 |

Dadurch kann das Modell erkennen, welche Genres häufig mit interessanten Filmen verbunden sind.

---

# 2. Allgemeine Filmbewertung
Zusätzlich wird das Rating von TMDb verwendet.
Beispiel:

```
Inception
Rating: 8.4
```
Das Rating wird normalisiert und als zusätzliches Merkmal verwendet.

Ein Film mit hoher Bewertung erhält dadurch einen Vorteil gegenüber einem ähnlich passenden Film mit deutlich schlechterer Bewertung.

---

# Welche Informationen werden nicht verwendet?
Aktuell werden bewusst nicht berücksichtigt:

* Erscheinungsjahr
* Schauspieler
* Regisseur
* Laufzeit
* persönliche Sternebewertungen
* Handlungstexte
* Bewertungen anderer Nutzer

Das Projekt bleibt dadurch einfach und nachvollziehbar.

---
# Wie lernt die KI?
Das Modell verwendet einen Random Forest.
Ein Random Forest besteht aus vielen Entscheidungsbäumen, die gemeinsam eine Vorhersage treffen.
Das Modell bekommt bekannte Filme aus der Netflixhistorie.

Beispiel:
| Film         | Genres         | TMDb Rating | Interesse |
| ------------ | -------------- | ----------: | --------: |
| Interstellar | Sci-Fi, Drama  |         8.6 |         5 |
| Matrix       | Sci-Fi, Action |         8.7 |         7 |
| Film X       | Sci-Fi         |         8.3 |         ? |

Das Modell versucht zu lernen:

> Welche Eigenschaften haben Filme, die der Nutzer interessant findet?

Danach kann es unbekannte Filme bewerten.

---
# Training und Bewertung

Die Daten werden in Trainings- und Testdaten aufgeteilt.
```
80 % Training
20 % Test
```
Mit den Trainingsdaten lernt das Modell.
Die Testdaten werden verwendet, um zu prüfen, ob das Modell auch unbekannte Filme bewerten kann.

---
## Cross Validation
Zusätzlich wird eine 5-fache Cross Validation durchgeführt.
Dabei wird das Modell mehrfach mit unterschiedlichen Daten getestet.
Dadurch erhält man eine stabilere Einschätzung der Modellqualität.

---
# Modellbewertung
Die Bewertung erfolgt über den Mean Absolute Error (MAE).
Der MAE zeigt die durchschnittliche Abweichung zwischen:
- vorhergesagtem Interesse
- tatsächlichem Interesse

Beispiel:
```
MAE = 1.2
```
bedeutet:
Die Vorhersage liegt durchschnittlich etwa 1.2 Punkte vom tatsächlichen Wert entfernt.

---
# Wie entstehen Empfehlungen?
Das Programm lädt eine Liste neuer Filme über TMDb.
Bereits gesehene Filme werden entfernt.
Für jeden neuen Film berechnet das Modell:

> Wie wahrscheinlich gefällt dieser Film diesem Nutzer?

Beispiel:

| Film   | Vorhersage |
| ------ | ---------: |
| Film A |        8.7 |
| Film B |        7.9 |
| Film C |        6.5 |

Die Filme mit den höchsten Werten werden als Empfehlungen ausgegeben.
Aktuell werden die Top 20 Filme gespeichert.

---
# Feature Importance

Der Random Forest kann anzeigen, welche Merkmale besonders wichtig für die Vorhersagen waren.
Beispiele:
- bestimmte Genres
- TMDb Rating

Diese Informationen werden zusätzlich als Grafik gespeichert.
Dadurch kann nachvollzogen werden:

> Welche Eigenschaften beeinflussen die Empfehlungen am stärksten?

---
# Visualisierung
Das Programm erstellt eine grafische Darstellung der Empfehlungen.
Die Grafik zeigt:

- empfohlene Filme
- vorhergesagtes Interesse
- Vergleich zwischen verschiedenen Filmen

Zusätzlich wird die Feature Importance visualisiert.

---
# Grenzen der aktuellen Version

Die aktuelle Version ist ein einfaches Lernprojekt.
Eine echte Streaming-Empfehlungsmaschine würde zusätzliche Informationen verwenden, wie:

* persönliche Wertungen
* Schauspieler und Regisseure
* Handlung und Schlüsselbegriffe
* Ähnlichkeit zwischen Filmen
* Nutzergruppen mit ähnlichem Geschmack
* Zeitpunkte und Situationen beim Anschauen

MovieTasteAI zeigt bewusst eine einfache und nachvollziehbare Machine-Learning-Pipeline (Lernprojekt).