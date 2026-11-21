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

Une modification du contexte lexical, à huit tables inchangées (minuscules ASCII et chiffres regroupés), a amélioré le score sur **trois tranches authentifiées de 8 Mio d'`enwik8`**, avec **51 218 octets économisés (0,60 % de la somme des scores)**, six reconstructions exactes et des tailles de programmes identiques. Le verdict est publié dans [le registre v0.11](Hutter_OmegaR/results_v11/ENWIK8_ABLATION_GITHUB.json) et [l'exécution GitHub](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44944691842). Le **benchmark intégral `enwik9` de v0.11 est maintenant terminé avec succès** : **282 550 351 octets** (35 040 o de programme + 282 515 311 o d'archive autonome), **2 086 696 octets de moins que v0.6 (−0,7331 %)**. La reconstruction des 1 000 000 000 octets est SHA-256 identique. [Exécution GitHub](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44945151998), [rapport brut](Hutter_OmegaR/results_v11/ENWIK9_FULL_GITHUB.json) et [audit](Hutter_OmegaR/results_v11/ENWIK9_AUDIT_2026-11-21.json). Le score reste non compétitif.

- [Méthode et résultats locaux v0.11](Hutter_OmegaR/v11/README.md)
- [Code de génération de la variante](Hutter_OmegaR/v11/make_candidate.py)

**Décision scientifique :** maintenir v0.6 comme référence expérimentale, explorer les variantes légères sur enwik8 et réserver les ambitions de première place à une amélioration substantielle, validée et admissible d'une architecture compétitive. Ne jamais attribuer à OMÉGA-R le score d'un concurrent.

## Itération v0.12 — canary du compresseur compétitif

La compilation depuis les sources GPL-3.0 de `cmix-neif 2.0` a été reproduite. Pour éviter de mobiliser une compression complète de ~49 heures sans prétest, nous avons construit un banc d'essai **sur un échantillon XML complet extrait du vrai `enwik9` authentifié**. Il reconstruit un fichier source à partir de pages entières, puis teste la compression `-e` et l'archive autonome dans des répertoires isolés.

- [Source et méthode](Hutter_OmegaR/v12/README.md) ; [extracteur vérifié localement](Hutter_OmegaR/v12/extract_wiki_pages.py) ; [banc d'essai testé localement avec un simulateur, pas encore avec le modèle amont](Hutter_OmegaR/v12/run_upstream_canary.py).
- [Workflow en cours de vérification](.github/workflows/omr12-cmix-neif-canary.yml) ; [état du canary](Hutter_OmegaR/results_v12/UPSTREAM_CANARY_GITHUB.json).
- **Aucun score Hutter Prize n'est produit sur cet échantillon**, et aucun gain de compression de ce concurrent n'est attribué à OMÉGA-R.

## v0.12–v0.13 — Instrumentation compétitive (21 novembre 2026)

- **v0.12 — canary sur la référence compétitive :** le code original `cmix-neif-2.0` est extrait à une révision Git épinglée et compilé, puis essayé sur un *petit XML reconstitué* depuis `enwik9` authentifié. Le verdict est [suivi ici](Hutter_OmegaR/results_v12/UPSTREAM_CANARY_GITHUB.json) et [dans GitHub Actions](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44946052561). La tentative sur XML tronqué a **échoué avec E178** ; le binaire de concours requiert les indices de dictionnaire correspondant à l'ensemble de `enwik9`. Le [diagnostic de l'échec](Hutter_OmegaR/results_v12/DIAGNOSTIC_E178_2026-11-21.md) est conservé. Le workflow v0.12 d'origine est désactivé.
- **v0.13 — préparation d'une première ablation sur SEMCACHE :** [source du patch](Hutter_OmegaR/v13/semantic_cache_gate_patch.py), [tests unitaires](Hutter_OmegaR/v13/test_semantic_cache_gate_patch.py) et [protocole](Hutter_OmegaR/v13/README.md). Neuf tests unitaires ont réussi. Les trois seuils `990`, `980` et `970` ont été [compilés avec succès](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44947707113) : binaires non empaquetés de 621 176, 621 240 et 621 240 octets. **Aucune amélioration de compression n'est encore mesurée.**
- **Relevé direct du statut des workflows** : [instantané GitHub Actions](Hutter_OmegaR/status/workflow_status_snapshot.json), produit par un workflow de métadonnées ne relançant ni compression ni benchmark.
- **v0.11 — score complet enwik9 confirmé :** [282 550 351 octets](Hutter_OmegaR/results_v11/ENWIK9_FULL_GITHUB.json), exactement reconstructibles, soit un gain mesuré de 2 086 696 octets sur v0.6 ; l'amélioration reste très inférieure à celle exigée pour une nouvelle récompense.

Rappel : le compresseur amont est GNU GPL-3.0 ; aucune publication de binaire modifié n'a été effectuée et aucune candidature n'a été envoyée aux organisateurs du Hutter Prize.

## v0.14 — laboratoire contrôlé du modèle de prédiction complet

Le [workflow v0.14](.github/workflows/omr14-raw-core-lab.yml) compile une version de laboratoire du moteur concurrent en ouvrant le mode de codage `-c`, habituellement absent du binaire de concours. Il authentifie `enwik9` puis prépare un **flux de 65 536 octets projeté avec perte** dans les 208 symboles admis par le vocabulaire du modèle. Le test ne donne **aucun score officiel**, car le chemin de prétraitement, les octets d'entrée et l'autonomie de l'archive ne sont pas ceux du concours. La seule réussite recherchée est la restitution exacte du flux expérimental. [Méthode et réserves](Hutter_OmegaR/v14/README.md) · [Registre v0.14](Hutter_OmegaR/results_v14/RAW_CORE_LAB_GITHUB.json).

La comparaison de modèles SEMCACHE ne peut commencer qu'après une restitution exacte en laboratoire et une vérification de la présence des composants visés. Les résultats négatifs restent archivés sans répétition stérile.

## v0.14.2 — Diagnostic et contrôle contradictoire du codage brut

Le premier essai v0.14 a échoué à la compilation (fonction auxiliaire `provide_dict_file` non exposée). Le second a **compilé**, authentifié `enwik9` et construit l'échantillon, mais le codage brut a échoué avec **E553** : le modèle attendait les règles textuelles et métadonnées de son flux d'origine. Le [diagnostic vérifiable est archivé](Hutter_OmegaR/results_v14/DIAGNOSTIC_E553_2026-11-21.md).

Une troisième exécution [v0.14.2](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44948698647), à partir d'un patch contrôlé, active le codage brut **et neutralise les transformations de métadonnées pour ce laboratoire uniquement**, sans désactiver le Transformer ni SEMCACHE. Le jeu d'entrée est une **projection avec perte** ; même un aller-retour exact ne serait pas un score de concours. À l'issue du benchmark, le [registre GitHub](Hutter_OmegaR/results_v14/RAW_CORE_LAB_GITHUB.json) donne le seul verdict valide.


## v0.14.3 — Laboratoire opérationnel et prochaine ablation v0.15

Le quatrième essai [v0.14.3](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44949002223) a réussi, après correction du gate Transformer sur une copie GPL du concurrent. Le laboratoire a traité **65 536 octets projetés avec perte** depuis `enwik9` authentifié, codés en **20 533 octets**, puis restitués exactement (SHA-256), en 36,98 s d'encodage et 37,10 s de décodage. **Ce résultat ne constitue ni une compression du véritable enwik9 ni un score Hutter Prize.** Les [preuves](Hutter_OmegaR/results_v14/RAW_CORE_LAB_GITHUB.json) et les échecs E553/E215 précédents sont conservés.

La [v0.15](Hutter_OmegaR/v15/README.md) applique, sur **la même entrée artificielle, les mêmes poids et le même runner**, les seuils SEMCACHE 990, 980 et 970, avec reconstruction exacte exigée à chaque essai. Le [workflow de comparaison](.github/workflows/omr15-semcache-raw-ab.yml) a **réussi** et son [rapport v0.15](Hutter_OmegaR/results_v15/SEMCACHE_LAB_COMPARISON.json) confirme trois reconstructions exactes. Les seuils 980 et 970 dégradent le flux sur cet échantillon ; ils sont rejetés pour cette configuration.


## v0.16 — contre-expérience SEMCACHE sur trois holdouts

À la suite du résultat négatif v0.15, nous testons la direction opposée : augmenter le seuil de recherche SEMCACHE de 990 à **995** ou **999**, sous contrôle de neuf restitutions sans perte sur trois fenêtres disjointes de Wikipédia (32, 96 et 192 Mio). Ces données sont projetées dans le vocabulaire restreint du laboratoire et sont donc **avec perte par rapport au corpus officiel**.

Les sources et les tests locaux ont été publiés après **20 tests unitaires et l'autotest d'extraction réussis**. Le workflow [omr16-semc-upper-holdout.yml](.github/workflows/omr16-semc-upper-holdout.yml) exécute la comparaison A/B depuis un commit amont épinglé et enregistre le verdict dans [SEMCACHE_UPPER_HOLDOUT.json](Hutter_OmegaR/results_v16/SEMCACHE_UPPER_HOLDOUT.json). [Exécution de lancement n° 44951476074](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44951476074).

**Attention :** aucune valeur n'est retenue avant vérification de chaque décompression ; le résultat expérimental n'est pas une archive auto-extractible du concours, et aucun nouvel exploit mondial n'est revendiqué.

## v0.16 — résultat confirmé (21 novembre 2026)

La [comparaison v0.16](Hutter_OmegaR/results_v16/SEMCACHE_UPPER_HOLDOUT.json) a réussi : neuf restitutions de flux de laboratoire exactes, trois fenêtres projetées de 65 536 octets chacune. Le témoin q990 totalise **64 719 octets**, q995 **64 683** (−36), q999 **64 652** (−67, soit −0,1035 %). La variante **q999 améliore les trois fenêtres**, sans changement de taille de l'exécutable non empaqueté dans ce laboratoire. Ces flux sont **avec perte par rapport au corpus officiel**, sans score Hutter Prize.

## v0.17 — suppression de la perte d'information dans les fenêtres expérimentales

La nouvelle [méthode v0.17](Hutter_OmegaR/v17/README.md) code les octets Wikipédia **bruts** dans l'alphabet figé de 208 symboles, grâce à un échappement réversible ; sa [preuve de réversibilité et ses limites](Hutter_OmegaR/v17/FORMAL_CODEC_SPEC.md) sont conservées. Les **33 tests locaux** ont réussi, incluant tests d'octets arbitraires, contrôles négatifs et simulation des deux étapes de restauration.

Le [workflow v0.17](.github/workflows/omr17-reversible-wiki-ab.yml) a été publié au commit `4c35cf4a1ae3d31074ce37a544826d5e79456096` et son [exécution n° 44953624240](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44953624240) compare q990 contre q999 sur de nouvelles fenêtres à 256, 384, 640 Mio. Les critères sont six reproductions exactes du **flux échappé** et des **octets bruts d'origine**, avec manifeste SHA-256 authentifié. Verdict final : consulter le [registre v0.17](Hutter_OmegaR/results_v17/REVERSIBLE_AB_GITHUB.json).

**Important :** le programme expérimental utilise toujours un chemin de codage modifié (`-c/-d`) et ne produit ni une archive auto-extractible ni un score officiel. La source amont GPL-3.0 et les poids sont utilisés dans GitHub Actions, sans redistribution de binaires concurrents.
