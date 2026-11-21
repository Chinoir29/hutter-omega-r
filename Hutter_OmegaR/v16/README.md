# OMÉGA-R v0.16 — SEMCACHE : contre-expérience de seuil élevé sur jeux tenus à l'écart

**Question falsifiable.** La v0.15 a trouvé que réduire `kQpE3` de 990 à 980 ou 970 dégradait le flux brut de laboratoire de 37 ou 70 octets sur une seule projection de 65 536 octets de Wikipédia. Tester l'hypothèse inverse : **davantage de recherches** dans SEMCACHE, en portant le seuil à **995** ou **999**, peut-il améliorer la longueur du flux ?

## Construction exécutée

- `patch_upper_gate.py` : une modification contrôlée d'un seul entier C++ ; le commit source exact `35d1957a5074db802fc134126afc77b76d931761` et le SHA Git blob `20614538d3ff90906163a6bd9150894cbb7020f1` sont obligatoires. **Ne jamais modifier le dépôt amont** ; opérer sur une copie de travail éphémère.
- `prepare_holdouts.py` : vérifier SHA-256 et taille du vrai `enwik9`, puis construire trois flux **avec perte** de 65 536 octets à partir de fenêtres disjointes situées à **32, 96 et 192 Mio** ; ces fenêtres ne recouvrent pas la zone de v0.15 (0 à 4 Mio).
- `run_holdout_sweep.py` : compiler le même modèle complet avec les seuls seuils 990, 995 et 999. Appliquer ensuite le patch laboratoire v0.14 au parseur et à l'automate ; coder et décoder les trois flux isolément avec un seul CPU. Une compilation et trois restitutions par configuration ; ne publier que des rapports et empreintes SHA-256.
- `summarize_holdouts.py` : refuser les données de provenance ambiguë, les sources différentes, un décodage non identique, les programmes non comparables et les rapports incomplets. Comparer 9 flux par paires sur les mêmes échantillons. Une candidate est **provisoirement appuyée** seulement si son flux total diminue et si au moins deux fenêtres gagnent ; ce n'est pas une victoire ni une acceptation statistique définitive.

## Tests automatiques

```bash
python3 Hutter_OmegaR/v16/test_patch_upper_gate.py
python3 Hutter_OmegaR/v16/test_summarize_holdouts.py
python3 Hutter_OmegaR/v16/prepare_holdouts.py --self-test
```

**Tests préliminaires en environnement local :** 9 tests de patch, 11 tests du contrôle comparatif et un autotest d'extraction ont réussi. Les 9 véritables compressions/décompressions nécessitent GitHub Actions et ses outils Linux.

## Interprétation et limites

**AUCUN** score Hutter Prize ne peut être obtenu avec ces données : la projection élimine des octets, l'échantillon est très petit, le code contient le patch de laboratoire, le flux n'est pas une archive auto-extractible, et l'entrée n'est pas `enwik9`. Le total de flux est comparable **dans cet essai seulement** ; les tailles des exécutables non empaquetés sont documentées séparément. Les taux observés sur ces échantillons ne doivent jamais être extrapolés à l'archive de 1 milliard d'octets.

Une modification qui se dégrade sur la majorité des fenêtres sera **rejetée**. Une modification encourageante restera une **hypothèse expérimentale**, avec nouvelles données indépendantes nécessaires avant tout test de compétition.

## Origine et licence

Le cœur concurrent est `marwoelk/cmix-neif-2.0`, **GPL-3.0**. Son source et ses poids ne sont pas redistribués par ce dépôt ; le workflow clone la révision de l'auteur puis applique un patch vérifiable. Les modifications appartiennent au laboratoire et ne constituent pas un produit de concours.

Workflow : `.github/workflows/omr16-semc-upper-holdout.yml` ; registre attendu : `Hutter_OmegaR/results_v16/SEMCACHE_UPPER_HOLDOUT.json`.
