## Benchmark App

## Descriere

Algorithm Benchmark App este o aplicație interactivă realizată în Python, folosind Streamlit, pentru evaluarea comparativă a performanței algoritmilor de sortare și căutare.

Aplicația permite configurarea unui test de benchmark, rularea mai multor algoritmi în aceleași condiții și afișarea rezultatelor sub formă de tabele, grafice și raport PDF.

## Funcționalități principale

* Compararea algoritmilor de sortare
* Compararea algoritmilor de căutare
* Selectarea dimensiunii setului de date
* Selectarea numărului de rulări
* Alegerea a 2 până la 4 algoritmi pentru comparație
* Generarea automată a datelor de intrare
* Afișarea rezultatelor în tabel
* Vizualizarea rezultatelor prin grafice
* Generarea și descărcarea unui raport PDF

## Algoritmi implementați

### Algoritmi de sortare

* Bubble Sort
* Insertion Sort
* Merge Sort
* Quick Sort

### Algoritmi de căutare

* Linear Search
* Binary Search
* Jump Search
* Interpolation Search

## Metrici analizate

Aplicația calculează următoarele metrici:

* timpul total de execuție
* timpul mediu de execuție
* numărul mediu de comparații
* numărul mediu de mutări pentru algoritmii de sortare
* memoria maximă utilizată
* poziția rezultatului pentru algoritmii de căutare

## Tehnologii utilizate

* Python
* Streamlit
* Pandas
* Altair
* Matplotlib
* ReportLab
* tracemalloc
* time / perf_counter

## Instalare

Pentru rularea aplicației este necesar Python instalat pe sistem.

Instalarea bibliotecilor necesare:

pip install streamlit pandas altair matplotlib reportlab

## Rulare aplicație

În terminal, din folderul proiectului, se rulează comanda:

streamlit run BenchmarkApp.py

După pornire, aplicația se deschide în browser la adresa:

http://localhost:8501

## Structura aplicației

Aplicația este organizată în mai multe componente logice:

* generarea datelor de intrare
* implementarea algoritmilor
* rularea benchmark-ului
* calcularea metricilor
* afișarea rezultatelor
* generarea raportului PDF

## Scopul proiectului

Scopul proiectului este de a evidenția diferențele de performanță dintre mai mulți algoritmi clasici, în funcție de dimensiunea și structura datelor de intrare. Aplicația oferă o metodă vizuală și interactivă pentru înțelegerea comportamentului algoritmilor în scenarii experimentale.

## Autor

Bizoi Beniamin
Universitatea din Craiova
Facultatea de Automatică, Calculatoare și Electronică
Specializarea: Inginerie software 1
