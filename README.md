# Hutter OMÉGA-R — recherche sur la compression sans perte

**Objectif :** développer un système conforme au Hutter Prize capable de comprimer `enwik9` mieux que les records internationaux. **Aucune victoire ni soumission n'est actuellement revendiquée.**

## Deux voies distinctes

| Piste | État | Traçabilité |
|---|---|---|
| **OMÉGA-R v0.6/v0.8**, prédicteur et archive auto-extractible originaux | Tests sans perte réussis sur `enwik8` et `enwik9` authentiques ; **score local enwik9 = 284 637 047 octets** — non compétitif | [Rapport des mesures enwik8](Hutter_OmegaR/results_v8/ENWIK8_GITHUB_PREFLIGHT_2026-11-21.md), [workflow v0.8](.github/workflows/hutter-omega-v8.yml) |
| **OMÉGA-R v0.9**, reproduction d'une base haut de gamme amont | **Compilation terminée et réussie** à partir d'un commit épinglé de `cmix-neif-2.0` (4 042 424 octets). Aucune compression enwik9 par le binaire amont | [Protocole v0.9](Hutter_OmegaR/v9/BASELINE_COMPETITIF.md), [workflow build-only](.github/workflows/omr9-build-upstream.yml) |

Le compresseur amont `cmix-neif-2.0` est sous **GNU GPL-3.0** ; tout éventuel travail dérivé doit conserver les notices, droits et conditions de redistribution. Le dépôt OMÉGA-R ne reproduit pas son code : le workflow clone une révision épinglée et compile sans exécuter la compression complète.

## Évaluation

Un résultat Hutter Prize exige la reconstruction exacte de `enwik9` (1 milliard d'octets), un compresseur plus une archive autonome (et arguments) de taille inférieure au seuil, la conformité temporelle et matérielle, puis une vérification externe.

Les tests sur des extraits, les benchmarks locaux et la compilation de logiciels tiers **ne sont pas** des soumissions gagnantes.

- [Règles du Hutter Prize](https://prize.hutter1.net/)
- [Exécution enwik9 terminée](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921)
- [Constitution de recherche originale](Hutter_OmegaR/Constitution_OMEGA_R_source.txt)

**Sécurité opérationnelle :** aucun corpus officiel ni aucune archive gigantesque ne sont téléversés dans les artefacts de CI ; seuls les rapports et diagnostics sont conservés. Aucune soumission au jury, souscription ou location de serveur n'est effectuée par les workflows.

## Nouvelles expériences reproductibles — 21 novembre 2026

- **Compilation réussie de la référence compétitive** `cmix-neif-2.0` : binaire construit de **4 042 424 octets** depuis le commit épinglé `35d1957...`, en 478,33 secondes, pic mémoire de 4 557 388 Kio. [Preuves GitHub](Hutter_OmegaR/v9/upstream_build_status.json) · [Exécution n° 44942316594](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44942316594). Différence de 140 octets avec le binaire publié par le concurrent, **sans démonstration de gain de compression**.
- **Abandon d'une variante v0.10** : deux contextes textuels supplémentaires testés sur sept corpus réels ou artificiels, avec reconstruction exacte. Chaque essai a donné un **score total plus élevé** que le témoin v0.6. [Code et compte rendu v0.10](Hutter_OmegaR/v10/README.md) · [mesures](Hutter_OmegaR/v10/local_results_v10.json). La version gagnante du protocole reste le témoin v0.6.
- **Benchmark intégral v0.8** : [exécution n° 44939882921](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921), résultat local exact **284 637 047 octets**, reconstruction SHA-256 conforme, mais trop élevé pour la première place.

Une compilation réussie, un modèle issu d'un concurrent ou un score sur `enwik8` ne constituent pas une soumission victorieuse au Hutter Prize. La référence `cmix-neif-2.0` est GPL-3.0, distribuée par son auteur ; elle n'est pas rebaptisée invention d'OMÉGA-R.

## Résultat intégral et contrôle contradictoire — 21 novembre 2026

Le programme OMÉGA-R v0.6 a traité les **1 000 000 000 octets** de `enwik9` sous Linux avec un seul cœur CPU : 35 040 octets de `comp9`, 284 602 007 octets d'archive autonome, soit **284 637 047 octets au total**. Reconstruction exacte vérifiée par SHA-256 ; compression en 1 151,27 secondes, décompression en 1 205,18 secondes, pic RAM 56 952 Kio.

Le score officiel récompensé consulté le 21 novembre 2026 était de 100 424 672 octets. Le seuil de 1 % correspondant est de **99 420 425 octets**. Il faudrait réduire notre score de **185 216 622 octets** au minimum pour atteindre ce seuil : le prototype n'est **pas** une candidature compétitive.

- [Rapport complet extrait des journaux GitHub](Hutter_OmegaR/results_v8/ENWIK9_GITHUB_FULL_2026-11-21.json)
- [Audit indépendant de cohérence du rapport (R3 instrument, pas validation externe)](Hutter_OmegaR/results_v8/ENWIK9_ASSESSMENT_2026-11-21.json)
- [Exécution GitHub Actions complète](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921)

## Expérience v0.11 — normalisation des contextes lexicaux

Une modification du contexte lexical, à huit tables inchangées (minuscules ASCII et chiffres regroupés), a amélioré le score sur **trois tranches authentifiées de 8 Mio d'`enwik8`**, avec **51 218 octets économisés (0,60 % de la somme des scores)**, six reconstructions exactes et des tailles de programmes identiques. Le verdict est publié dans [le registre v0.11](Hutter_OmegaR/results_v11/ENWIK8_ABLATION_GITHUB.json) et [l'exécution GitHub](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44944691842). Un **nouveau benchmark intégral `enwik9`**, distinct de la mesure v0.6 à 284 637 047 octets, est configuré dans [le workflow v0.11 complet](.github/workflows/omr11-enwik9-full.yml). Son score n'est pas encore confirmé : aucune victoire revendiquée.

- [Méthode et résultats locaux v0.11](Hutter_OmegaR/v11/README.md)
- [Code de génération de la variante](Hutter_OmegaR/v11/make_candidate.py)

**Décision scientifique :** maintenir v0.6 comme référence expérimentale, explorer les variantes légères sur enwik8 et réserver les ambitions de première place à une amélioration substantielle, validée et admissible d'une architecture compétitive. Ne jamais attribuer à OMÉGA-R le score d'un concurrent.

## Itération v0.12 — canary du compresseur compétitif

La compilation depuis les sources GPL-3.0 de `cmix-neif 2.0` a été reproduite. Pour éviter de mobiliser une compression complète de ~49 heures sans prétest, nous avons construit un banc d'essai **sur un échantillon XML complet extrait du vrai `enwik9` authentifié**. Il reconstruit un fichier source à partir de pages entières, puis teste la compression `-e` et l'archive autonome dans des répertoires isolés.

- [Source et méthode](Hutter_OmegaR/v12/README.md) ; [extracteur vérifié localement](Hutter_OmegaR/v12/extract_wiki_pages.py) ; [banc d'essai testé localement avec un simulateur, pas encore avec le modèle amont](Hutter_OmegaR/v12/run_upstream_canary.py).
- [Workflow en cours de vérification](.github/workflows/omr12-cmix-neif-canary.yml) ; [état du canary](Hutter_OmegaR/results_v12/UPSTREAM_CANARY_GITHUB.json).
- **Aucun score Hutter Prize n'est produit sur cet échantillon**, et aucun gain de compression de ce concurrent n'est attribué à OMÉGA-R.

## v0.12–v0.13 — Instrumentation compétitive (21 novembre 2026)

- **v0.12 — canary sur la référence compétitive :** le code original `cmix-neif-2.0` est extrait à une révision Git épinglée et compilé, puis essayé sur un *petit XML reconstitué* depuis `enwik9` authentifié. Le verdict est [suivi ici](Hutter_OmegaR/results_v12/UPSTREAM_CANARY_GITHUB.json) et [dans GitHub Actions](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44946052561). Cette expérience n'a **pas** de score officiel et son aller-retour exact doit être confirmé.
- **v0.13 — préparation d'une première ablation sur SEMCACHE :** [source du patch](Hutter_OmegaR/v13/semantic_cache_gate_patch.py), [tests unitaires](Hutter_OmegaR/v13/test_semantic_cache_gate_patch.py) et [protocole](Hutter_OmegaR/v13/README.md). Neufs tests unitaires ont réussi et les sources publiées ont les mêmes Git blobs que les fichiers testés. Valeurs envisagées du seuil de confiance : `990` (témoin), `980` et `970`. **Aucune amélioration de compression n'est encore mesurée.**
- **Relevé direct du statut des workflows** : [instantané GitHub Actions](Hutter_OmegaR/status/workflow_status_snapshot.json), produit par un workflow de métadonnées ne relançant ni compression ni benchmark.
- **v0.11 — score complet enwik9 :** le [registre dédié](Hutter_OmegaR/results_v11/ENWIK9_FULL_GITHUB.json) est distinct de la réussite déjà vérifiée sur trois tranches enwik8 ; un résultat absent n'est pas une victoire.

Rappel : le compresseur amont est GNU GPL-3.0 ; aucune publication de binaire modifié n'a été effectuée et aucune candidature n'a été envoyée aux organisateurs du Hutter Prize.
