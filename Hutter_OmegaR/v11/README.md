# Hutter OMÉGA-R v0.11 — normalisation contextuelle sans coût de modèle

**Statut :** variante expérimentale améliorant les tests locaux **et trois extraits authentifiés d'enwik8** ; validation intégrale enwik9 en cours. Ce n'est pas une candidature Hutter Prize ni une invention mondiale revendiquée.

## Construction et paramètres
À partir du source de référence `../v6/omr6_sfx.cpp`, `make_candidate.py` remplace **une seule opération** de calcul de contexte lexical. La normalisation change uniquement ce que le prédicteur apprend de l'historique déjà décodé ; elle ne change aucun octet dans le texte reconstruit.

Le programme utilise toujours **huit tables de contexte** (pas dix), sans nouveaux dictionnaires, poids de réseau neuronal ou fichiers externes. Mode 0 : contrôle inchangé ; mode 1 : majuscules ASCII vers minuscules ; mode 2 : majuscules vers minuscules **et** chiffres 0-9 vers '#'; mode 3 : chiffres seuls. La sélection du mode se fait à la compilation et ne nécessite aucun argument au lancement.

## Reproduire

```bash
python3 make_candidate.py
bash build.sh
python3 benchmark.py
```

La génération doit produire le SHA-256 de source : `6dd3a2d7b28851552223118c9abf27fe9be8a28d223f96b15fd49553a3910c39`. En compilation locale avec les paramètres fixés, le mode 0 correspond **octet pour octet** au binaire v0.6 (`17cf52eab65e73c4db8f8b6e6006d8ac81c0f2e02bfc29f9da57d8192ffd5780`). Chaque programme pèse **35 192 octets** sur cette machine.

## Tests locaux (source et archives séparées)

| Jeu | Groupe | Contrôle (mode 0) | Candidat (mode 2) | Économie locale |
|---|---|---:|---:|---:|
| Code Pandas frame.py | développement | 168 068 | 167 609 | 459 |
| XML synthétique (1,25 Mo) | développement | 213 756 | 213 317 | 439 |
| Code Pandas generic.py | validation | 166 106 | 165 621 | 485 |
| Code NumPy numeric.py | validation | 93 385 | 93 244 | 141 |
| Code scikit-learn validation.py | validation | 98 077 | 97 958 | 119 |
| Constitution OMÉGA-R | validation | 80 176 | 80 120 | 56 |
| Octets aléatoires, 128 Kio | validation | 201 666 | 201 666 | 0 |
| **Somme développement** | | **381 824** | **380 926** | **898** |
| **Somme validation** | | **639 410** | **638 609** | **801** |

Chaque score correspond à `taille(comp9) + taille(archive9)`, et le binaire est compté séparément pour chaque fichier de test. Les 28 restitutions (quatre modes × sept entrées) ont été vérifiées exactement par SHA-256.

Le candidat est retenu **pour un prétest**, pas comme amélioration prouvée sur Wikipédia. Le prétest est défini dans [omr11-enwik8-ablation.yml](../../.github/workflows/omr11-enwik8-ablation.yml) et effectue une authentification de `enwik8` suivie de six restitutions exactes (trois tranches disjointes, deux modes). Il n'envoie rien au jury et ne lance pas `enwik9`.

## Limites

Les données de développement et de validation sont principalement du code source, pas des articles Wikipédia. Les scores ne sont pas transférables au concours. Une amélioration de l'ordre de 0,1 % dans un moteur encore peu compétitif ne permet pas de déduire que l'on battra `cmix-neif 2.0` ou le record officiellement récompensé. Pour le prix, il faut intégrer une amélioration dans une architecture du niveau mondial et démontrer l'intégralité des contraintes.

## Résultat sur Wikipédia authentifié — 21 novembre 2026

Le workflow GitHub [n° 44944691842](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44944691842) a téléchargé et vérifié le corpus `enwik8` officiel (100 millions d'octets), puis comparé **trois tranches disjointes de 8 Mio** à modèles réinitialisés. Les six reconstructions ont réussi.

| Début de tranche | Contrôle v0.6, score total | Candidat v0.11, score total | Économie |
|---:|---:|---:|---:|
| 0 Mio | 2 839 188 | 2 822 811 | 16 377 |
| 40 Mio | 2 839 292 | 2 821 434 | 17 858 |
| 80 Mio | 2 866 626 | 2 849 643 | 16 983 |
| **Somme des 3 expériences** | **8 545 106** | **8 493 888** | **51 218** |

Économie mesurée : **0,60 % de la somme de trois scores locaux**, compresseur compté séparément à chaque essai. La taille du binaire sur Linux GitHub est **35 040 octets dans les deux modes**.

- [Rapport brut publié automatiquement](../results_v11/ENWIK8_ABLATION_GITHUB.json)
- [Benchmark intégral candidat v0.11](../../.github/workflows/omr11-enwik9-full.yml) : lancé pour mesurer l'effet sur `enwik9`, sans extrapolation à partir des tranches et sans soumission au jury.

Ce résultat ne démontre **aucune amélioration d'une soumission de premier rang**. Il démontre une amélioration d'OMÉGA-R v0.6 par v0.11 sur des extraits de Wikipédia. L'objectif de la première place exige une architecture de niveau `cmix-neif 2.0`, et sa propre validation indépendante.
