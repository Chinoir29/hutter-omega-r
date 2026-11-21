# OMÉGA-R v0.13 — Abolition contrôlée d'un seuil fixe de recherche sémantique

**Étape atteinte :** construction d'un outil d'ablation de **source**, pas encore d'une amélioration de compression. L'expérience ne doit être exécutée sur le compresseur concurrent que si la v0.12 a démontré un aller-retour autonome exact sur un extrait de Wikipédia.

## Hypothèse falsifiable

Le compresseur amont `cmix-neif-2.0` utilise une mémoire sémantique (`SEMCACHE`) qui consulte les états antérieurs lorsque la probabilité du meilleur octet du Transformer est inférieure à `kQpE3/1000`. La valeur amont est `990`. Un seuil plus bas (`980` ou `970`) évitera certaines consultations coûteuses. Cela peut **réduire le temps** mais peut aussi **augmenter la taille compressée** si les consultations écartées étaient utiles. Aucun gain ne doit être présumé.

## Construction, provenance et licence

- Amont : `marwoelk/cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`, GNU GPL-3.0.
- Fichier amont modifié : `src/semantic_cache.h`, Git blob original `20614538d3ff90906163a6bd9150894cbb7020f1`.
- **Unique différence permise** : la valeur de `constexpr int kQpE3 = 990;`, en `980` ou `970`. Tout autre contenu inattendu conduit à un refus.
- Le témoin `990` conserve exactement l'original. Les règles internes `kSpE3 = 950` et `kCalqE3 = 900` sont contrôlées pour éviter de violer les invariants.
- Ce dépôt ne copie pas le code GPL tiers ; le script modifie localement le clone exact de l'amont. Toute distribution ultérieure du code modifié doit conserver les obligations GPL.

## Reproduction des tests déjà exécutés

```bash
cd Hutter_OmegaR/v13
python3 test_semantic_cache_gate_patch.py
```

## Étape A/B conditionnelle (non exécutée)

Après réussite confirmée de la v0.12, comparer `990` (témoin), `980` et `970` sur **le même** extrait authentifié de `enwik9`, avec le même environnement, la même architecture, la même reconstitution SHA-256 et la taille du programme incluse. Faire mesurer au minimum la taille totale du compresseur et de l'archive, la durée de chaque phase et le pic de RAM. Les tests sur extrait ne sont **pas** des scores officiels.

Rejeter toute variante dont la décompression diverge, qui ne respecte pas les limites, ou dont la perte en taille ne justifie pas le gain de calcul; retenir les résultats négatifs aussi. Un avantage sur extrait ne prouve pas un avantage sur `enwik9` complet ni une première place au concours.
