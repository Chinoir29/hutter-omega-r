# OMÉGA-R v0.8 — Authenticité des données et banc d'essai déporté

**Statut : instrument opérationnel local ; validation GitHub et `enwik8` authentique encore à réaliser. Aucune candidature au Hutter Prize.**

## Pourquoi deux phases ?

L'environnement local ne résout pas le DNS du serveur officiel `mattmahoney.net`. L'ancien workflow v0.7 ne testait que `enwik9` (1 Go). La v0.8 ajoute un prévol rapide sur `enwik8` authentique, de 100 Mo. L'archive officielle `enwik8.zip` fait ~36,4 Mo. Ce prévol n'est pas un score Hutter Prize.

Le workflow `.github/workflows/hutter-omega-v8.yml` contient deux jobs :

- **preflight**, par défaut, télécharge `enwik8.zip`, contrôle nom/longueur/MD5/SHA-1 et teste trois tranches de 8 MiB prises à 0, 40 et 80 MiB, avec SHA-256 intégral de la restitution. Il mesure `comp9+archive9` pour chaque tranche, et `zstd -19` comme référence en taille de flux uniquement.
- **full_enwik9**, exécuté uniquement si l'option manuelle `phase=full` est choisie et si le prévol a réussi, récupère `enwik9`, contrôle la taille et le SHA-256 connus, puis exécute le validateur v0.6 sur un cœur. Le résultat, s'il est obtenu, reste *local* et non homologué.

Les artefacts GitHub contiennent les rapports JSON et l'environnement, sans aucun corpus ni archive compressée. Les opérations ne contactent pas le jury.

## Test hors ligne (déjà exécuté ici)

```sh
python3 Hutter_OmegaR/v8/prefix_benchmark_v8.py \
  --self-test Hutter_OmegaR/results_mixed/synthetic_wiki.xml \
  --prefix-mib 2 \
  --out Hutter_OmegaR/results_v8/local_synthetic_smoke.json
```

Ce mode se nomme explicitement `NONOFFICIAL_LOCAL_SMOKE`. Le code *refuse* si le même fichier est présenté sous `--enwik8`, avant toute compression.

## Exécution déportée

1. Créer sur GitHub un **dépôt dédié** au Hutter Prize ; ne pas utiliser un dépôt personnel sans rapport. Choisir sa visibilité en connaissance de cause (public = sources publiques ; privé = quota de minutes et facturation possibles).
2. Décompresser `Hutter_OmegaR_v0.8_github_ready.zip` à la racine et transférer le contenu dans le dépôt, y compris le répertoire caché `.github/workflows`.
3. Ouvrir **Actions → Hutter OMÉGA-R v0.8 → Run workflow**, choisir `phase=preflight` et lancer.
4. Consulter l'artefact **omr8-enwik8-preflight** ; vérifier les trois rapports `report_offset_*.json` et le statut `AUTHENTIC_ENWIK8_PREFIX`.
5. Le cas échéant, lancer **une seconde fois** le workflow avec `phase=full` ; le score réel de `enwik9` sera dans `omr8-enwik9-local-full/report.json` sous `score_bytes_LOCAL_only`, à condition que le job aboutisse.

**Limite :** GitHub impose 6 h maximum par job standard. Une interruption ne prouve pas que le compresseur est invalide, mais montre que cet environnement ne suffit pas pour cette configuration. Les machines GitHub publiques standard ont 16 Go de RAM et 14 Go de stockage annoncé ; les spécifications des dépôts privés diffèrent.

## Références

- https://www.hutter1.net/prize/hrules.htm
- https://mattmahoney.net/dc/textdata.html
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits
