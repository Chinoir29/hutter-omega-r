# Hutter OMÉGA-R — recherche sur la compression sans perte

**Objectif :** développer un système conforme au Hutter Prize capable de comprimer `enwik9` mieux que les records internationaux. **Aucune victoire ni soumission n'est actuellement revendiquée.**

## Deux voies distinctes

| Piste | État | Traçabilité |
|---|---|---|
| **OMÉGA-R v0.6/v0.8**, prédicteur et archive auto-extractible originaux | Prétest sur trois tranches du véritable `enwik8` : réussites de décompression ; essai intégral `enwik9` déclenché, résultat à confirmer | [Rapport des mesures enwik8](Hutter_OmegaR/results_v8/ENWIK8_GITHUB_PREFLIGHT_2026-11-21.md), [workflow v0.8](.github/workflows/hutter-omega-v8.yml) |
| **OMÉGA-R v0.9**, reproduction d'une base haut de gamme amont | Étude de faisabilité de compilation épinglée sur `cmix-neif-2.0` ; ce n'est pas un score produit par OMÉGA-R | [Protocole v0.9](Hutter_OmegaR/v9/BASELINE_COMPETITIF.md), [workflow build-only](.github/workflows/omr9-build-upstream.yml) |

Le compresseur amont `cmix-neif-2.0` est sous **GNU GPL-3.0** ; tout éventuel travail dérivé doit conserver les notices, droits et conditions de redistribution. Le dépôt OMÉGA-R ne reproduit pas son code : le workflow clone une révision épinglée et compile sans exécuter la compression complète.

## Évaluation

Un résultat Hutter Prize exige la reconstruction exacte de `enwik9` (1 milliard d'octets), un compresseur plus une archive autonome (et arguments) de taille inférieure au seuil, la conformité temporelle et matérielle, puis une vérification externe.

Les tests sur des extraits, les benchmarks locaux et la compilation de logiciels tiers **ne sont pas** des soumissions gagnantes.

- [Règles du Hutter Prize](https://prize.hutter1.net/)
- [Exécution enwik9 en cours / historique](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921)
- [Constitution de recherche originale](Hutter_OmegaR/Constitution_OMEGA_R_source.txt)

**Sécurité opérationnelle :** aucun corpus officiel ni aucune archive gigantesque ne sont téléversés dans les artefacts de CI ; seuls les rapports et diagnostics sont conservés. Aucune soumission au jury, souscription ou location de serveur n'est effectuée par les workflows.

## Nouvelles expériences reproductibles — 21 novembre 2026

- **Compilation réussie de la référence compétitive** `cmix-neif-2.0` : binaire construit de **4 042 424 octets** depuis le commit épinglé `35d1957...`, en 478,33 secondes, pic mémoire de 4 557 388 Kio. [Preuves GitHub](Hutter_OmegaR/v9/upstream_build_status.json) · [Exécution n° 44942316594](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44942316594). Différence de 140 octets avec le binaire publié par le concurrent, **sans démonstration de gain de compression**.
- **Abandon d'une variante v0.10** : deux contextes textuels supplémentaires testés sur sept corpus réels ou artificiels, avec reconstruction exacte. Chaque essai a donné un **score total plus élevé** que le témoin v0.6. [Code et compte rendu v0.10](Hutter_OmegaR/v10/README.md) · [mesures](Hutter_OmegaR/v10/local_results_v10.json). La version gagnante du protocole reste le témoin v0.6.
- **Benchmark intégral v0.8** : [exécution n° 44939882921](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921), résultat à déterminer à partir de ses rapports; aucune publication de première place.

Une compilation réussie, un modèle issu d'un concurrent ou un score sur `enwik8` ne constituent pas une soumission victorieuse au Hutter Prize. La référence `cmix-neif-2.0` est GPL-3.0, distribuée par son auteur ; elle n'est pas rebaptisée invention d'OMÉGA-R.
