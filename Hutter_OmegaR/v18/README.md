# OMÉGA-R v0.18 — Préflight du chemin de compétition (source épinglée)

## Hypothèse et motivation

La v0.17 a montré une variation de 72 octets **uniquement** sur trois fenêtres de laboratoire. Elle ne démontre rien sur la chaîne d'archive du concours. Pour discriminer le gain hors laboratoire, il faut obtenir **deux exécutables de production** issus du même commit amont : témoin 990 et candidat 999. On ne remplace pas le prétraitement officiel de `cmix-neif-2.0` par l'échappement v0.17.

Le seul changement expérimental est `src/semantic_cache.h: constexpr int kQpE3 = 990;` → `999;`. L'effort nouveau de cette version porte sur **l'intégration et l'identification du véritable score**, pas sur la découverte d'un autre seuil. Le code inspecte les deux constructeurs `Predictor p(vocab)` du chemin de production, les dérivations de dictionnaire et les prétraitements inverses. Les hypothèses négatives E178 de v0.12 sont conservées : une entrée tronquée n'est **pas** un substitut valable à `enwik9` pour `-e`.

## Usage (Python 3.10+, Linux)

Prérequis : copier séparément ou cloner `https://github.com/marwoelk/cmix-neif-2.0` à la révision **exacte** `35d1957a5074db802fc134126afc77b76d931761` (GPL-3.0) ; ne pas modifier ses fichiers, conserver sa licence. L'environnement de construction amont est celui de son README (Ubuntu 24.04, clang-18, lld-18, gcc-13 et fichiers de poids de son dépôt). L'archive de reprise ne distribue pas ces sources ni les poids.

```sh
python3 -m unittest discover -s Hutter_OmegaR/v18 -p 'test_*.py' -v
python3 Hutter_OmegaR/v18/production_ab.py --upstream /chemin/cmix-neif-2.0 --work /tmp/omr18-preflight
# Source seulement : pas de gain mesuré, pas de comp9.

python3 Hutter_OmegaR/v18/production_ab.py --upstream /chemin/cmix-neif-2.0 --work /tmp/omr18-build --build-only --seconds-per-phase 1800
# Construction des deux comp9 emballés : pas d'archive9, pas de score.

python3 Hutter_OmegaR/v18/production_ab.py --upstream /chemin/cmix-neif-2.0 --work /espace/omr18-full --run-full --enwik9 /chemin/enwik9 --seconds-per-phase 210000
# Deux fois le vrai -e embarqué, puis deux restitutions autonomes en répertoire vide.
# NE PAS lancer cette dernière opération sur une machine insuffisante : plusieurs centaines d'heures CPU possibles.
```

Le dernier mode exige **1 000 000 000 octets** et le SHA-256 canonique `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`. Les deux `comp9` s'exécutent sans options ; chaque `archive9` est copiée seule dans un répertoire propre et doit reproduire `enwik9_uncompressed` bit pour bit. Le score local calculé est `S = octets(comp9) + octets(archive9)` (0 octet d'option). Le rapport marque **score officiel et validation externe : non établis**. Il ne certifie pas les contraintes du jury (durée normalisée, pic de RAM, usage disque, portabilité ou absence de communication réseau) : ces contrôles restent indispensables.

## Critères de décision

- **GO technique** : source amont inchangée, les deux binaires construits, deux restitutions complètes exactes, coûts de tous les exécutables et données comptés, tailles comparables.
- **HOLD** : seulement source copiée, deux constructions, ou mesures de laboratoire ; aucune conclusion de gain admissible.
- **REJECT** : dérive de commit, E178 sur un échantillon, build/codec défaillant, restitution différente, ou score total augmenté. Sauvegarder la mesure négative.

Ce protocole ne revendique aucune première mondiale et n'envoie rien au jury. Il ne réutilise aucune source GPL dans le dépôt utilisateur. Tout binaire dérivé de `cmix-neif-2.0` doit conserver ses mentions et obligations de licence GPL-3.0. Les fichiers résultants `comp9` et `archive9` ne sont **pas** automatiquement publiés.
