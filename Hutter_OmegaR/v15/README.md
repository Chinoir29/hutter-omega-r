# OMÉGA-R v0.15 — ablation SEMCACHE sur un laboratoire fonctionnel

**Question falsifiable :** en codage brut du moteur complet `cmix-neif-2.0` modifié pour le laboratoire, réduire le seuil `kQpE3` de 990 à 980 ou 970 modifie-t-il la longueur du flux arithmétique, l'empreinte du flux ou la durée CPU ? Si oui, dans quel sens et de combien ?

## Références préalables vérifiées

- [v0.11 — véritable enwik9, score intégral 282 550 351 o](../results_v11/ENWIK9_FULL_GITHUB.json), gain de 2 086 696 o sur le prototype v0.6, mais non compétitif.
- [v0.12 — échec E178 sur XML tronqué](../results_v12/DIAGNOSTIC_E178_2026-11-21.md) : dictionnaire spécifique au corpus complet.
- [v0.13 — les trois changements de seuil sont constructibles](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44947707113) : 990, 980 et 970.
- [v0.14.3 — laboratoire encode/décode validé](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44949002223) : 65 536 octets projetés avec perte, flux arithmétique brut de 20 533 o, reconstruction SHA-256 exacte.
- Référence amont `marwoelk/cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`, licence **GPL-3.0**. Les poids ne sont pas redistribués.

## Protocole A/B

1. Télécharger puis authentifier le vrai `enwik9` (taille 1 milliard et SHA-256 officiel).
2. Générer **une seule fois** la projection irréversible de 65 536 octets, SHA-256 attendu `c7fdfc7a3f1249269ec25541155b50a88ce8fcb06643198074cb06fd61daa604`, selon les 208 octets du vocabulaire amont.
3. Compiler successivement les valeurs **990**, **980**, **970** du seul paramètre `kQpE3`, après remise à zéro exacte des sources épinglées, avec le même patch laboratoire v0.14.3. Refuser les empreintes de source inattendues.
4. Exécuter `-c` et `-d` dans des répertoires distincts avec les mêmes poids et une seule affinité CPU. Rejeter chaque résultat sans reconstruction SHA-256 identique.
5. Comparer les tailles **du flux codé brut** et les empreintes des flux pour identifier l'effet des seuils. Documenter les variations de RAM et de durée, sans les confondre avec une mesure normalisée du prix.
6. Refuser de considérer comme une amélioration les variations de binaire seul ou des résultats sur des jeux d'entrée différents.
7. Inscrire les gains ET les échecs dans [le registre v0.15](../results_v15/SEMCACHE_LAB_COMPARISON.json).

## Limites fondamentales

La projection de l'entrée est **avec perte** par rapport au vrai `enwik9`, les sources comportent un **patch de laboratoire de deux fichiers**, et les flux n'ont **pas de décompresseur autonome**. Aucun chiffre de cet essai n'est un score Hutter Prize. Une économie sur le petit échantillon n'est pas un gain garanti sur la compétition. Un débit plus rapide dans GitHub n'est pas une preuve de conformité à la limite de ≲50 h sur une machine à un seul cœur.

**Seuil scientifique :** les 3 restitutions doivent réussir. Un flux compressé différent prouve un effet de la modification sur cette expérience, non une supériorité compétitive mondiale.

## Résultat distant vérifié — rejet de la réduction du seuil

GitHub Actions [n° 44949569634](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44949569634), source JSON [SEMCACHE_LAB_COMPARISON.json](../results_v15/SEMCACHE_LAB_COMPARISON.json). **Trois reconstructions exactes et vérifiées**. Le résultat est négatif pour l'hypothèse testée :

| Seuil QpE3 | Flux de laboratoire (octets) | Surcoût au témoin | Compression mesurée |
|---:|---:|---:|---:|
| 990 (origine) | 20 533 | — | 36,38 s |
| 980 | 20 570 | +37 | 36,71 s |
| 970 | 20 603 | +70 | 37,20 s |

Les tailles du programme *non empaqueté* sont identiques (**621 432 octets**) et la RAM rapportée est d'environ **6,95 Gio** à la compression. Réduire ce seuil ne diminue pas le temps total dans cet essai, même si la différence d'environ une seconde reste trop faible pour constituer un benchmark de vitesse stable.

**Décision :** conserver le seuil original **990** dans ce laboratoire et rejeter les valeurs 980 et 970 sur cet échantillon. Le test ne démontre pas que 990 serait optimal dans tous les corpus. La [v0.16](../v16/README.md) contrôle la direction inverse (995 et 999), sur trois fenêtres tenues à l'écart de v0.15. Ce sont toujours des projections avec perte et jamais un score Hutter Prize.
