# OMÉGA-R v0.27 — Réduire le coût de distribution des poids

## Hypothèse

Le codeur du concurrent GPL-3.0-only cmix-neif-2.0 doit embarquer des poids Transformer dans comp9 puis dans archive9. Le fichier comprimé de poids mesure **3 744 629 octets**, donc il est compté **deux fois**. Une amélioration substantielle de sa représentation *sans perte* pourrait diminuer S, à condition que l'implémentation de la décompression des poids, ses métadonnées et son temps soient inclus dans les deux exécutables.

Ce n'est **pas** une optimisation démontrée : le fichier .c5 est déjà compressé et pourrait être incompressible au moyen de codecs externes.

## Expérience construite

Le programme weight_repack_probe.py exige le commit amont 35d1957a5074db802fc134126afc77b76d931761 et valide le SHA-256 729694cba4969b7d833686ed3f597ff04d3b226da849d5f8004ec020a0ed9563 du fichier de poids de référence.

Quinze essais strictement réversibles : cinq codecs (gzip-9, bzip2-9, xz-9e, zstd-19, brotli-11) appliqués à trois représentations (octets originaux, différence XOR avec l'octet précédent, regroupement des indices modulo quatre). Après chaque compression, la sortie est décompressée puis réinversée et doit restituer le SHA de poids source. Des contrôles adversariaux rejettent les poids incorrects, les transformations non inversibles et l'absence de codec.

Le programme n'émet que des **tailles, empreintes, temps et décisions** ; il ne téléverse aucun poids ni aucune version du corpus. La compression avec ces outils n'est **pas** admissible tant que le coût de leur décodeur réellement embarqué n'a pas été compté. Le champ official_hutter_S est null.

## Seuil de décision

Si cmix-neif-2.0 à S = 93 388 956 devenait une référence officiellement récompensée, l'objectif de 1 % serait S au maximum 92 455 066, soit au moins **933 890 octets d'économie totale**. En supposant que cette économie provienne uniquement d'un conteneur de poids présent en double, il faudrait retirer **466 945 octets par copie** avant le coût de l'algorithme de décompression. Cette valeur est un budget théorique conditionnel, pas un résultat obtenu.

- Rejeter les wrappers qui augmentent la taille ou ne dégagent aucune marge pratique pour un décodeur embarqué.
- Conserver une piste seulement après restitution intégrale des poids et estimation du coût du code.
- Toute piste conservée devra ensuite produire un vrai comp9 et archive9 sur enwik9 entier, avec autonomie, temps, RAM, disque et score S vérifiés.

Exécution : [GitHub Actions #44972762089](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44972762089). La constitution originale n'est pas altérée.
