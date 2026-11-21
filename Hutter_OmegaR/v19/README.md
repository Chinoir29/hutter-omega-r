# OMÉGA-R v0.19 — Capturer le véritable flux de production avant codage

## Résultat préalable (v0.18)
GitHub Actions #44956092485 : les **deux vrais `comp9`** ont été compilés avec succès au commit GPL-3.0 amont `35d1957a5074db802fc134126afc77b76d931761`.
- Témoin kQpE3=990 : 4 042 424 B ; SHA-256 `333b183e88a71064da31606e0a3e78dfc3006cc7095c183fb50ee6f43d509531`.
- Candidat kQpE3=999 : 4 042 433 B ; SHA-256 `74418b6329eee1767791ae5501dfa0a4319ae927bd55ddfe48fcb529ac44968b`.
- Delta binaire : candidat **+9 B**, sans archive9 ni compression intégrale. Verdict sur le score total : **HOLD**.
- Métadonnées : https://github.com/Chinoir29/hutter-omega-r/actions/runs/44956092485/artifacts/14728461421.

## Nouveau verrou à lever

Les mesures des laboratoires `-c/-d` ne portent pas sur les octets effectivement présentés au codeur arithmétique du chemin de production `-e`. Une opération distincte est nécessaire : produire le flux normalisé authentique (métadonnées, census, ordre, dictionnaire, règles de texte et post-traitements) **sans attendre les dizaines d'heures de calcul du modèle final**.

`production_stream_probe.py` effectue une instrumentation source **après** `text_start::Pack` dans `RunCompression`, donc après les transformations du chemin `-e` et **avant** la création de `Predictor` et l'appel `Compress`.

Garde-fous :
- commit Git, propreté et SHA du fichier source exigés ;
- modification uniquement dans une copie de travail (licences conservées) ;
- variable d'environnement de recherche `OMR19_PROBE_PRODUCTION_STREAM` ;
- arrêt avec code d'erreur si l'appel ne provient pas de `-e` canonique ;
- **aucune archive9 admissible n'est générée** dans ce mode ;
- aucun corpus, fichier de dictionnaire ou poids ne doit être publié ;
- analyse par fenêtres zlib 3 de **diagnostic uniquement**. Le proxy n'est pas un score du concours ou du modèle cmix.

## Protocole

```bash
python3 -m unittest discover -s Hutter_OmegaR/v19 -p 'test_*.py' -v
python3 Hutter_OmegaR/v19/production_stream_probe.py \
    --upstream /scratch/cmix-neif-2.0 --output /scratch/cmix-neif-instrumented
(cd /scratch/cmix-neif-instrumented && bash build.sh)
(cd /scratch/run &&
    ln -s /protected/enwik9 enwik9 &&
    OMR19_PROBE_PRODUCTION_STREAM=1 /scratch/cmix-neif-instrumented/comp9)
python3 Hutter_OmegaR/v19/profile_true_stream.py \
    /scratch/run/archive9.cmix.temp --output /scratch/profile.json
```

Le corpus `enwik9` doit avoir 1 000 000 000 octets et SHA-256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`. Le workflow GitHub inclut cette authentification avant tout calcul.

### Réfutation et suites

Si le flux ne se construit pas sous les ressources GitHub, consigner la cause exacte ; ne pas modifier arbitrairement la limite de 10 GiB du jury et ne pas attribuer une faute au code concurrent. Si le flux est extrait, conserver taille, SHA, profil par blocs et coût de temps/RSS. Comparer ensuite des algorithmes **réversibles** sur ce flux avec le même témoin et intégrer le meilleur dans les appels encode/décode **avant** de revendiquer la moindre économie sur S.

Niveau actuel : instrument R3 en construction, résultat officiel non démontré. Constitution originale du dossier inchangée.
