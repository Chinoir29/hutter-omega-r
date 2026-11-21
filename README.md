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

Une modification à huit tables constantes (minuscules ASCII et chiffres regroupés) améliore localement le score total de 898 octets sur les fichiers de développement et 801 octets sur les fichiers de validation, avec 28/28 reconstructions exactes et une taille de programme identique au témoin. Le test A/B sur trois tranches authentiques d'`enwik8` est défini dans le workflow [omr11-enwik8-ablation.yml](.github/workflows/omr11-enwik8-ablation.yml). Aucun gain sur `enwik9` n'est revendiqué.

- [Méthode et résultats locaux v0.11](Hutter_OmegaR/v11/README.md)
- [Code de génération de la variante](Hutter_OmegaR/v11/make_candidate.py)

**Décision scientifique :** maintenir v0.6 comme référence expérimentale, explorer les variantes légères sur enwik8 et réserver les ambitions de première place à une amélioration substantielle, validée et admissible d'une architecture compétitive. Ne jamais attribuer à OMÉGA-R le score d'un concurrent.
