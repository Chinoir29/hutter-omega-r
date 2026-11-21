# OMÉGA-R v0.20 — Verrou d'admissibilité du transcodeur global

**Source vérifiée :** [`src/runner.cpp` du dépôt `marwoelk/cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`](https://github.com/marwoelk/cmix-neif-2.0/blob/35d1957a5074db802fc134126afc77b76d931761/src/runner.cpp) (GNU GPL-3.0-only, le fichier source entier n'est pas recopié ici).

## Fait structural

L'encodeur `Compress` et le décodeur `Decompress` synchronisent plusieurs automates **octet par octet** via `AfterStreamByte(Predictor*, c)`. Cette fonction pilote notamment `metablock`, les contextes d'alias, les blocs auteur, les pages census, les états temporels et les articles de début de texte. L'encodeur a aussi un chemin de bits imposés `Tf1ZwangByte` et la grammaire `run_mode::gram`.

**Conséquence :** appliquer directement `split2`, `split4`, `reverse` ou `swap_pairs` à l'intégralité des 501 062 281 octets **avant** `Compress` détruirait l'ordre des marques structurées. Un résultat favorable en zlib ne prouverait alors rien sur la compatibilité de la transformation avec le codeur ni le décodeur amont.

## Statut et décision

La v0.20 teste une propriété plus étroite : une réorganisation entièrement réversible de l'image binaire **hors du modèle contextuel amont**, avec coût explicite de format, témoins identiques et SHA de restitution sur toute la chaîne diagnostique. Elle ne se présente pas comme un patch final du prix.

Même si l'expérience A/B améliore son proxy, la décision correcte reste : **KEEP uniquement comme résultat de laboratoire / HOLD pour intégration réglementaire**.

Prochaine recherche prioritaire :
1. Choisir un composant qui ne modifie pas l'ordre du flux observé par les automates (par exemple adaptation du prédicteur bit-à-bit, conservation de l'historique et de la grammaire).
2. Ou démontrer une région "inert" explicitement balisée, en dérivant le même choix côté encodeur et côté décodeur, sans ajouter de side-data non comptabilisée.
3. Tester un changement sur ce composant et mesurer son impact **dans le vrai codeur arithmétique** en confrontation au même témoin ; ne pas extrapoler d'un proxy zlib au score `S`.

Cette décision est une application des articles 1, 7, 8, 16, 21 et 24 de la constitution originale (intégrité, dépendances, statut de preuve, construction et contradiction).
