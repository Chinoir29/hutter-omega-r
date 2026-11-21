# OMÉGA-R v0.17 — Échantillons réellement réversibles pour le laboratoire SEMCACHE

## Verrou supprimé

La v0.15/v0.16 filtrait les octets que le vocabulaire figé du concurrent ne reconnaissait pas. Cette projection était **avec perte** : son décodeur ne pouvait pas restaurer les octets Wikipédia d'origine. La v0.17 construit un **transcodeur déterministe et bijectif** entre les 256 valeurs possibles du flux brut et des séquences de symboles appartenant toutes au vocabulaire figé de 208 valeurs. Il n'utilise aucun octet secret ni dictionnaire statistique entraîné sur les échantillons.

### Encodage

- Vocabulaire amont de la révision exacte `35d1957a5074db802fc134126afc77b76d931761`, fichier `src/vocab_frozen.h` identifié par son Git blob `da5ffe84fb7e3d9a5061b43da5970f7c9f728e19`.
- Marqueur d'échappement : `^`, valeur 94, appartenant au vocabulaire amont.
- Si un octet est autorisé et différent de `^`, il est émis directement.
- Sinon, on émet **deux** octets : `^` suivi d'un caractère d'un codebook **fixe de 49 symboles autorisés**. Les 49 cas représentent les **48 valeurs exclues** et le marqueur `^` lui-même.
- Le décodeur reconstruit exactement la suite brute, rejetant les codes mal formés et les séquences tronquées.
- La surcharge **non compressée** est exactement le nombre d'octets bruts qui ne sont pas autorisés ou correspondent au marqueur. Elle est mesurée par échantillon.

## Expérience prospective

Les trois fenêtres de **65 536 octets bruts** commencent à 256, 384 et 640 Mio du vrai corpus `enwik9` (1 milliard d'octets). Ces positions sont distinctes des précédentes mesures v0.15/v0.16. Chaque entrée brute est authentifiée à partir du corpus vérifié SHA-256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`.

Comparer deux variantes du **même laboratoire** de `cmix-neif-2.0` : `kQpE3=990` contre `kQpE3=999`. Pour chaque fenêtre, deux contrôles distincts sont obligatoires :

1. Le flux arithmétique doit décompresser en **exactement le flux échappé encodé** (SHA-256 et longueur).
2. La transformation inverse du flux échappé doit redonner **exactement les 65 536 octets Wikipédia bruts**, vérifiés par SHA-256 d'origine.

Cela n'utilise **ni le prétraitement officiel de `cmix-neif 2.0`, ni son binaire de concours, ni une archive auto-extractible**. Le score Hutter Prize reste `null`, même en cas de réussite. L'objectif est de disposer d'un laboratoire à entrée réversible, sans prétendre que l'expérience traduit directement la qualité du compresseur de compétition. L'impact du codebook et du décodeur sur la taille de l'exécutable final n'est pas encore évalué.

## Reproduction locale

```bash
cd Hutter_OmegaR/v17
python3 -m unittest discover -p 'test_*.py' -v
python3 reversible_sample.py --self-test
```

Pour la chaîne distante, utiliser `.github/workflows/omr17-reversible-wiki-ab.yml`. Elle clone le concurrent depuis sa révision figée sous GPL-3.0, authentifie `enwik9`, crée les trois échantillons, compile les deux variantes du laboratoire et exige les six **doubles** restitutions, puis conserve uniquement les rapports. Le code et les poids du concurrent ne sont **pas redistribués** dans ce dépôt.

## Décisions pré-enregistrées

- Candidat provisoirement intéressant : gain cumulé sur les trois nouvelles fenêtres, avec au moins **deux succès individuels** et **aucun échec de restitution** ; pas de score officiel revendiqué.
- Candidat rejeté sur ce protocole : taille plus grande ou restitution incorrecte.
- Toute erreur liée à la grammaire ou au vocabulaire vaut **limite méthodologique**, et non échec intrinsèque du compresseur concurrent.
- Le temps et la mémoire sont suivis, mais ne constituent pas la limite de calcul normalisée par le jury.

**Niveau de preuve recherché :** instrument reproductible de laboratoire plus fidèle, résultat expérimental A/B local, sans invention brevetée ni première place mondiale revendiquée.
