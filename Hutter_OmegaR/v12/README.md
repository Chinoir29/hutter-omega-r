# OMÉGA-R v0.12 — canary de compression sur base compétitive

## Problème traité

Le moteur expérimental OMÉGA-R v0.6, même amélioré en v0.11, est encore loin du record mondial. Une compilation de `cmix-neif-2.0` depuis le commit public `35d1957a5074db802fc134126afc77b76d931761` a déjà réussi. Cette itération vérifie **la chaîne compression + décompression sans perte** du compresseur amont, en utilisant un *petit échantillon XML complet* extrait d'`enwik9` authentifié. Elle n'apporte pas encore de modification de l'algorithme.

## Exactitude et licences

- Le code de `cmix-neif-2.0` appartient à ses auteurs et est disponible sous GNU GPL-3.0 ; l'exécutable n'est ni distribué ni revendiqué comme une invention OMÉGA-R.
- L'extracteur `extract_wiki_pages.py` vérifie d'abord le fichier entier `enwik9` (1 milliard d'octets ; SHA-256 canonique), puis crée un **échantillon XML complet** avec un nombre entier de pages et le même préfixe `<siteinfo>`.
- Le test local `--self-test` de l'extracteur passe. Le banc d'essai `run_upstream_canary.py` a été vérifié sur un exemple auto-extracteur *simulé*, à ne pas confondre avec un vrai résultat de `cmix-neif-2.0`.
- Le vrai compresseur amont doit être exécuté avec `-e input output` ; son binaire de production n'accepte pas le mode générique `-c`. Le décompresseur autonome est exécuté dans un autre répertoire temporaire, sans accès au fichier source du test.
- Toutes les ressources (temps réel, RSS, SHA-256, tailles) seront mesurées par GitHub Actions sur un seul cœur CPU.

## Critère R3

Valider la compression puis la décompression d'un échantillon issu des données officielles avec **correspondance SHA-256 exacte**, dans la limite de 1 200 secondes *par phase*. Le résultat ne deviendra R3 que si le pipeline réel réussit. En cas d'échec, conserver l'information négative et la cause.

## Interdiction de généraliser

Une taille obtenue sur cet échantillon, même avec le vrai `cmix-neif-2.0`, **n'est pas un score Hutter Prize sur `enwik9`** et ne permet aucune extrapolation de l'archive entière. Pour améliorer le record, il faudra ensuite construire puis tester une modification compétitive A/B avec contraintes RAM, disque et temps.

## Rapport

- Workflow : `.github/workflows/omr12-cmix-neif-canary.yml`.
- Rapport attendu : `Hutter_OmegaR/results_v12/UPSTREAM_CANARY_GITHUB.json`.
- Aucune soumission au jury, aucune location de serveur, aucune archive contenant le corpus officiel transférée dans GitHub.
