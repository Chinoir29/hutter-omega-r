# OMÉGA-R v0.20 — comparaison réversible sur les 501 062 281 octets du vrai flux de production

## Point de départ vérifié

GitHub Actions [#44957604937](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44957604937) a exécuté la chaîne complète de prétraitement du logiciel GPL-3.0 `marwoelk/cmix-neif-2.0` (commit épinglé `35d1957a5074db802fc134126afc77b76d931761`) sur le vrai `enwik9` (1 000 000 000 octets, SHA-256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`). Son instrument a capturé le flux juste avant `Predictor` / le codeur arithmétique :

- **501 062 281 octets**, SHA-256 `c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718` ;
- 60 fenêtres de 8 Mio au maximum, avec 252 176 428 octets au total en zlib niveau 3 (une compression indépendante par fenêtre) ;
- dépense calcul relevée pour la construction de l'instrument : 350,46 s ; pour le prétraitement : 302,63 s ;
- **aucun `archive9` du Hutter Prize** ; ces mesures ne sont pas un score de compétition.

Le registre détaillé des 60 fenêtres est dans `Hutter_OmegaR/results_v19/REMOTE_STREAM_44957604937.json` et les métadonnées de l'artefact GitHub `14728164398`.

## Construction expérimentale nouvelle

`reversible_stream_ab.py` offre un format d'archive binaire de laboratoire indépendant, `OMR20`, avec cinq modes **de même longueur** et inverses exacts :

| Mode | Transformée | Inverse |
|---|---|---|
| identity | conserver les octets | identique |
| split2 | octets de rang pair puis impair | redistribution aux rangs pairs et impairs |
| split4 | répartir les octets selon leur indice modulo 4 | entrelacement modulo 4 |
| reverse | renverser l'ordre des octets | renversement |
| swap_pairs | échanger chaque paire adjacente | même opération |

Chaque bloc est compressé par **zlib niveau 3** après transformation. L'archive contient un en-tête de 24 octets et 5 octets par bloc (1 pour le mode, 4 pour la longueur compressée). Sur 60 blocs, le coût structurel est **324 octets dans chacune des deux archives**. Les deux archives sont construites et relues, et chacune doit reproduire exactement les **501 062 281 octets** et leur SHA canonique.

### Préenregistrement et décision

Une fenêtre sur cinq (indices multiples de cinq) forme l'ensemble d'apprentissage, soit 12 blocs. Elle sert **seule** à choisir **un mode global** par minimisation de la somme des tailles zlib, identité gagnante en cas d'égalité. Les 48 autres fenêtres servent à la validation indépendante du choix ; les données de ces fenêtres ne décident pas du mode.

Une variante n'est conservée pour exploration que si elle améliore le résultat zlib sur les 48 fenêtres de contrôle. Si elle échoue, son résultat négatif est conservé et **la piste est rejetée pour ce proxy**. Ni la compression zlib, ni les deux restaurations de flux intermédiaire ne démontrent la restauration autonome de `enwik9`, l'amélioration de la taille `S`, la conformité temporelle ou l'admissibilité au prix.

Les deux archives de laboratoire de plusieurs centaines de mégaoctets et les restaurations restent **temporaires sur GitHub Actions** et sont détruites une fois leurs empreintes vérifiées. Seules les sommes de contrôle, tailles, profils et journaux sont publiés. Aucun corpus, modèle, poids ou logiciel tiers n'est redistribué.

### Reproduire

```bash
python3 -m unittest discover -s Hutter_OmegaR/v20 -p 'test_*.py' -v

# Prérequis : reconstruire le même flux avec le workflow v0.19
python3 Hutter_OmegaR/v20/reversible_stream_ab.py \
  /scratch/archive9.cmix.temp \
  --work /scratch/omr20-ab \
  --result /scratch/omr20-results.json
```

La valeur SHA-256 du flux exact est imposée par défaut, afin de refuser les données non canoniques. Le workflow `.github/workflows/omr20-real-stream-ab-once.yml` reproduit d'abord les prétraitements amont sur `enwik9` canonique, puis exécute ce test et conserve uniquement les métadonnées.

## Prochaine étape après décision

Si le proxy zlib montre un effet reproductible sur contrôle : porter la transformation dans le chemin de production **des deux côtés** (avant l'arithmétique et après sa restitution), mesurer la taille **réelle** de `comp9 + archive9` et exiger la restauration bit pour bit de `enwik9`. Une amélioration de zlib sans gain sur le compresseur réglementaire n'est **pas** une avancée de score Hutter. Si le proxy régresse, pivoter vers un mécanisme structurel des métadonnées census au lieu de rechercher des paramètres voisins.

Constitution originale inchangée ; état de recherche : instrument reproductible et mesure de laboratoire, sans solution admissible.
