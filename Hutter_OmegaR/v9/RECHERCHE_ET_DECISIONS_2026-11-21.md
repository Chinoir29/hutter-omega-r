# OMÉGA-R — Journal de recherche et décisions (21 novembre 2026)

**Horodatage :** point de contrôle au cours de la soirée du 21 novembre 2026, heure Europe/Paris. Les statuts d'exécution GitHub sont à vérifier à chaque nouvelle consultation ; ils ne sont pas permanents.

## Résultats reproductibles et provenance

1. **Prévol enwik8 réel : réussi** sur trois tranches distinctes de 8 388 608 octets. Reconstruction SHA-256 : 3/3. Rapport détaillé : [enwik8](../results_v8/ENWIK8_GITHUB_PREFLIGHT_2026-11-21.md). Exécution : https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939582235
2. **Mesures enwik8 des flux (sans taille d'exécutable)** : OMÉGA-R = 8 334 770 octets, Zstandard -19 = 7 115 162 octets au total sur les trois tranches. OMÉGA-R est **17,14 % plus volumineux** dans cette comparaison partielle. Aucune généralisation automatique à `enwik9`.
3. **Benchmark enwik9 1 000 000 000 octets** : exécution https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921 ; prévol réussi et entrée officielle téléchargée/authentifiée. Au dernier pointage disponible dans cette session, étape compression-décompression intégrale **en cours**. Aucun score final déclaré.
4. **Référence compétitive à reproduire** : `marwoelk/cmix-neif-2.0` révision `35d1957a5074db802fc134126afc77b76d931761`, GPL-3.0 ; workflow de compilation `.github/workflows/omr9-build-upstream.yml`. Résultat de compilation **pas encore vérifié dans cette session** ; aucune compression de concours du logiciel amont n'a été exécutée par OMÉGA-R.
5. **Auditeur de rapports OMÉGA-R v0.9.1** : `v9/assess_hutter_report.py` et `v9/test_assess_hutter_report.py` ; dix tests locaux réussis, empreintes Git SHA identiques sur GitHub et dans les fichiers locaux. L'auditeur contrôle les rapports, pas les fichiers originaux ni leur authenticité indépendamment.

## Objectif quantifié (valeurs de référence historiques)

- Score officiellement récompensé observé : 100 424 672 octets ; seuil de gain d'au moins 1 % = au plus 99 420 425 octets, sous réserve des conditions du concours.
- Soumission de pointe annoncée `cmix-neif-2.0` : 93 388 956 octets ; si elle devenait la référence récompensée, seuil de gain de 1 % = au plus 92 455 066 octets.
- Toute comparaison doit utiliser **S = |comp9| + |archive9| + octets d'options obligatoires**.
- Ces nombres peuvent changer. Consulter le règlement et le record à la date de candidature.

## Décision méthodologique

- Conserver v0.6/v0.8 comme instrument expérimental à faible mémoire, **pas** comme concurrent reconnu.
- Attendre le rapport complet de l'exécution `enwik9` avant toute décision de soumission et analyser ce rapport avec v0.9.1.
- Reproduire et étudier les vrais compresseurs de tête avec licence et attribution adéquates. Chercher un gain effectivement mesuré sur un témoin inchangé et un corpus authentique.
- Ne pas affirmer de record, ne pas publier le corpus ou l'archive, ne pas lancer de seconde longue exécution sans raison, et ne pas envoyer de candidature au jury.

**Statut selon OMÉGA-R :** R3 pour les instruments reproductibles ; R2 pour les résultats de prévol ; R0 pour la première place mondiale.
