# OMÉGA-R v0.30 — Remplacement structurel de l'étage de calibration

## Objectif

Poursuivre le **Hutter Prize** en construisant une modification réellement
exécutable des deux chemins de `cmix-neif-2.0`, plutôt qu'en empilant des
vérifications. La constitution originale est conservée **inchangée**,
SHA-256 `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`.

## Fait de départ : v0.29 rejetée sur préfixe réel

GitHub Actions [#45061877899](https://github.com/Chinoir29/hutter-omega-r/actions/runs/45061877899)
a terminé avec succès technique. Les deux archives expérimentales ont restitué
exactement **524 288 octets prétraités** de `enwik9` après compression dans
le vrai modèle sur un cœur et décompression indépendante sans argument.

Le candidat v0.29 économise 9 octets arithmétiques, mais ajoute 306 octets
au compresseur et 290 octets à l'archive : **+596 octets au total**.
Le candidat v0.28 déjà testé ajoutait 940 octets malgré 18 octets économisés
dans le flux. Les voies précédemment négatives (EMA v0.21, température v0.22,
recompression externe des poids v0.27) restent rejetées dans leur périmètre.

## Construction nouvelle : 11 264 cellules → 16 pools

Le composant initial `floor_stage::Stage` contient 11 264 cellules de
calibration fine (8 octets chacune) ; il adapte les probabilités de bits
dont le prédicteur est quasiment certain de la valeur.

La v0.29 **ajoutait** 16 parents aux 11 264 cellules d'origine, avec un
correcteur multiplicatif. Sa précision pouvait augmenter, mais au coût
d'un nouvel état et de code supplémentaire.

La v0.30 **supprime les 11 264 cellules** et les remplace par 16 états :
`side` prédit (0 ou 1) × position du bit dans l'octet (0 à 7). Chaque
pool mémorise la somme des probabilités d'erreur prévues en Q16 et le
nombre de vraies erreurs observées dans les bits codés précédents.

À chaque bit à haute confiance, utiliser la probabilité originale
`f/65536` puis la multiplier par un ratio causal de fiabilité :

`ratio_Q16 = ((errors+16) << 32)/(expected_q16+(16 << 16))`,

borné à [1/4,4]. L'erreur corrigée reste contrainte à [1,32768] en Q16.
Le codeur et le décodeur utilisent **le même `floor_stage.h`**, et
l'encodeur conserve toutes les règles de grammaire, de WRT, de bits imposés,
de poids et de prétraitement. Aucune donnée annexe à l'archive.

Il ne s'agit pas d'un simple balayage de seuil. La représentation de
l'état et la règle d'agrégation ont été remplacées.

## Preuves disponibles

**Préflight [#45075871377](https://github.com/Chinoir29/hutter-omega-r/actions/runs/45075871377) : success.**

- 9 tests de source v0.30 et 8 tests de régression v0.29 ;
- source `src/floor_stage.h` vérifiée par son blob Git
  `cfdedf819ddeae4aeebf1a91e9dbb6942c8be03c`,
  dépôt amont GPL-3.0-only au commit
  `35d1957a5074db802fc134126afc77b76d931761` ;
- compilation C++ des deux composants isolés ;
- **taille effective de Stage : 90 120 → 272 octets** (-89 848 octets),
  mesure `sizeof()`, soit 99,7 % de cette structure ;
- deux implémentations distinctes (C++ et Python bigint) ont reproduit
  **exactement chaque empreinte de probabilité Q32 sur 1,6 million de bits**
  synthétiques ;
- contradiction : sur un contrôle volontairement surconfiant, le candidat
  **régresse de 737,0956 bits** ; sur un contrôle correctement calibré, il
  **gagne 1,6224 bit**. Ces tests sont artificiels et n'établissent aucun
  résultat de compression Wikipédia.

Les deux préflights initiaux ont échoué en raison du fixture synthétique,
puis d'une expansion Bash incompatible avec `set -u` ; les erreurs sont
conservées dans les journaux et corrigées sans modifier le critère de succès.

## Expérience complète sur préfixe canonique

**[GitHub Actions #45075993000](https://github.com/Chinoir29/hutter-omega-r/actions/runs/45075993000)** :
deux builds de production comparables, même version GPL-3.0-only,
corpus d'un milliard d'octets authentifié par SHA
`159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`,
codage de **524 288 octets** du flux après prétraitement,
deux archives natives autoextractibles, deux décodages indépendants et
vérification SHA du préfixe
`1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf`.

Mesurer au minimum séparément : taille `comp9`, taille `archive9`,
octets arithmétiques, RAM/disque et temps sur CPU unique. Seul un gain net
sur **`comp9 + archive9`**, accompagné de la restitution exacte, permet
de conserver cette modification comme amélioration de préfixe. Un gain
hypothétique sur tout `enwik9` n'est pas déductible du préfixe.

**Pas d'archive Hutter admissible, pas de score S officiel, pas de jury
contacté.** Statut de compétition R4/R5/R6 non atteint.

## Dossiers

- `prepare_compact_stage.py` : transformation source stricte et sourcée.
- `compact_reference.py` : oracle Python indépendant.
- `test_prepare_compact_stage.py` : tests contradictoires.
- `run_real_compact_pair.py` : mesure native A/B et double restitution.
- `results_v29/REAL_PAIRED_45061877899.json` : échec v0.29 conservé.
- `results_v30/PREFLIGHT_45075871377.json` : résultats v0.30 sans données protégées.

Les fichiers de corpus, les poids, les binaires GPL dérivés et les archives
expérimentales ne sont pas téléversés dans le dépôt. La licence, les
attributions et les limites d'autonomie sont préservées.
