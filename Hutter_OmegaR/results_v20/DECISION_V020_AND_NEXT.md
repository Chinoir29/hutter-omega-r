# OMÉGA-R v0.20 — Décision scientifique après exécution réelle du 21 novembre 2026

## Sources, intégrité et reproductibilité

- Constitution originale conservée intacte, SHA-256 : `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`.
- Source tierce `marwoelk/cmix-neif-2.0`, GPL-3.0-only, commit `35d1957a5074db802fc134126afc77b76d931761` ; aucune copie de poids ou corpus n'est publiée.
- v0.19 : GitHub Actions [#44957604937](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44957604937) a produit le véritable flux pré-codeur de 501 062 281 octets : SHA-256 `c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718`.
- **v0.20 :** GitHub Actions [#44959605545](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44959605545) = completed/success ; source au commit `899cd30d591937b7e5bb5863d708cc0b848f14e6`. Archive originale des métriques : [artefact 14729043487](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44959605545/artifacts/14729043487).
- Comparaison indépendante des deux artefacts v0.19/v0.20 : le SHA du flux est identique ; **les 60 tailles zlib3 témoins correspondent exactement une à une**, et non seulement en somme.

## Expérience

Sur un seul et même flux de 60 fenêtres de 8 Mio au plus, cinq modes purement réversibles ont été confrontés à zlib niveau 3. Sélection **préenregistrée** : les 12 fenêtres d'indice multiple de 5 choisissent un mode global, sans connaître les résultats des 48 fenêtres de contrôle. Résultat : `reverse`.

| Grandeur | Témoin | Candidat |
|---|---:|---:|
| Coût zlib3 apprentissage | 50 311 835 B | 49 699 361 B |
| Coût zlib3 contrôle | 201 864 593 B | 199 666 966 B |
| Archive indépendante complète et en-têtes | 252 176 752 B | 249 366 651 B |
| Diminution sur contrôle | — | 2 197 627 B |
| Diminution intégrale | — | **2 810 101 B (1,114 %)** |
| Réinversion 501 062 281 B | exacte | exacte |

Le coût structurel est de 324 B dans chaque archive. Les deux archives ont été relues avec l'implémentation inverse et ont restitué exactement le flux original (SHA-256 identique). 60/60 fenêtres améliorées en zlib. Les empreintes des archives diagnostiques et les 60 mesures figurent dans `REMOTE_AB_44959605545.json`.

Le temps A/B rapporté est 40,61 s ; l'extraction du flux a demandé 311,40 s, après construction de la sonde en 353,66 s (machine GitHub Actions, **non calibrée** pour le règlement Hutter).

## Contradiction : ce gain n'est pas encore transférable à cmix

Le flux est zippé par un codec **zlib indépendant**, pas par le modèle arithmétique du concurrent. La transformation globale `reverse` brise l'ordre des octets attendu dans `AfterStreamByte()`, par la grammaire et par les octets imposés, qui opèrent en séquence et doivent être synchrones entre les deux sens. Un simple ajout de l'inverse après le décodeur ne répare pas ces automates. Le gain 1,114 % de ce **proxy** ne doit jamais être présenté comme 1,114 % du Hutter Prize.

Le fichier officiel de coûts du modèle `doc/stream_rate.tsv` publie 85 417 870 octets de codeur pour ce flux ; la carte des coûts `REFERENCE_CMIX_COST_MAP.json` est alignée sur les 60 fenêtres (agrégation approximative). La fenêtre zéro est la plus chère pour `cmix` mais 55e pour zlib, d'où la nécessité d'utiliser les coûts **réels** de prédiction pour choisir une cible.

## Décision en application de la constitution

- **CONSERVER** : instrument de production v0.19, nouveau codec de diagnostic v0.20, preuve de gain zlib sur données complètes avec contrôle hors apprentissage, deux restitutions SHA-256 ; statut R3 **uniquement** pour l'instrument de laboratoire.
- **RECONCEVOIR** : l'intégration de `reverse` au chemin de production. La version présente n'est ni un `comp9` gagnant, ni un `archive9` Hutter, ni une preuve de conformité ou de gain au concours.
- **PROCHAINE OPÉRATION** : développer une ablation côté **prédicteur bit-à-bit**, sans toucher l'ordre du flux sémantique ; cibler d'abord le bloc de métadonnées initial à coût `cmix` élevé. Mesurer les vrais bits émis sur un même préfixe authentique ; obliger la symétrie encodeur-décodeur, avant toute tentative sur la totalité de `enwik9`.

Il n'y a eu aucune soumission au jury, publication de corpus/poids ou dépense autorisée par cette recherche.
