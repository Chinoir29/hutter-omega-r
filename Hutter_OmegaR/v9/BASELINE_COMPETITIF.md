# OMÉGA-R v0.9 — passage à une base compétitive

**Objectif :** établir la faisabilité d'une construction et d'une expérimentation reproductibles à partir d'un compresseur concurrent de pointe, sans présenter son score comme un résultat OMÉGA-R.

## Référence scientifique

- Dépôt amont : https://github.com/marwoelk/cmix-neif-2.0
- Révision exacte : `35d1957a5074db802fc134126afc77b76d931761`.
- Licence amont : GNU GPL-3.0. Tout code repris et redistribué doit respecter ses obligations et notices.
- Score annoncé (non vérifié par nous) : 93 388 956 octets, correspondant à 89 346 392 octets d'archive et 4 042 564 octets de compresseur.
- Source : README amont, soumission du 30 octobre 2026.

## Expérience 9.0 — compilation de la référence

Le workflow `.github/workflows/omr9-build-upstream.yml` vérifie les dépendances sur Ubuntu 24.04, télécharge la révision épinglée, effectue une compilation sans privilèges puis sauvegarde les mesures, les empreintes et les journaux.

**N'est PAS effectué :** compression et décompression de `enwik9`, validation du score, soumission au jury, transfert des poids/modèles dans ce dépôt, entraînement sur GPU ou exécution sous conditions de compétition.

Un écart de version des compilateurs ou bibliothèques peut modifier le binaire malgré un fonctionnement identique. Les tests de conformité au temps d'exécution (~50 heures sur un seul cœur pour l'amont) exigent une autre infrastructure : les jobs GitHub standards ont une limite de durée plus courte.

## Décision de recherche

- Si la compilation fonctionne : conserver une référence reproductible et étudier UNE modification justifiable contre un témoin inchangé avant toute prétention de gain.
- Si elle échoue : documenter et corriger la dépendance bloquante.
- Si le benchmark officiel du prototype OMÉGA-R v0.6 montre un écart considérable au seuil : cesser de le considérer comme une candidature et réserver ses petites expériences au laboratoire.
- Vérifier systématiquement `S = taille(comp9) + taille(archive9) + longueur(options)`, restitution exacte, RAM, disque, temps CPU, puis reconnaissance externe.

**Statut :** infrastructure de recherche, pas une victoire au Hutter Prize.
