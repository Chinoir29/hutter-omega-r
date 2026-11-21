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
