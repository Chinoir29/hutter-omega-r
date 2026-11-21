# OMÉGA-R v0.8 — prévol sur enwik8 officiel (21 novembre 2026)

**Statut : résultat d'expérience réel, sans statut de score Hutter Prize.**

- Exécution GitHub Actions : https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939582235
- `preflight` : **success** ; `full_enwik9` : **skipped**.
- Source : `https://mattmahoney.net/dc/enwik8.zip`, vérifiée par taille 100 000 000 octets, MD5 et SHA-1.
- SHA-256 du corpus décompressé : `2b49720ec4d78c3c9fabaee6e4179a5e997302b3a70029f30f2d582218c024a8`
- SHA-256 de `comp9` compilé sous GitHub Linux : `c84baabb466228a477bc24e9ee2569ad0245874a5dace06a53060143a87a7082`
- Taille binaire `comp9` : **35 040 octets**.
- Longueur de chacune des trois tranches : **8 388 608 octets** ; modèle réinitialisé pour chaque tranche.

| Début dans enwik8 | OMR6 flux estimé (o) | Zstd -19 flux (o) | OMR6 score local comp9 + archive (o) | Restitution SHA-256 |
| ---: | ---: | ---: | ---: | :---: |
| 0 Mio | 2 769 076 | 2 365 824 | 2 839 188 | PASS |
| 40 Mio | 2 769 180 | 2 361 943 | 2 839 292 | PASS |
| 80 Mio | 2 796 514 | 2 387 395 | 2 866 626 | PASS |
| **Somme** | **8 334 770** | **7 115 162** | **8 545 106** | **3/3** |

Pour les trois tranches, le flux OMÉGA-R est **17,14 % plus volumineux** que le flux Zstandard -19, ce dernier ne comprenant ni le programme de décompression ni le format auto-extractible. Cette comparaison ne constitue donc **pas un classement au Hutter Prize**.

- Compression d'une tranche : ~14 secondes ; décompression : ~14 à 16 secondes.
- Mémoire maximale relevée durant les phases : **56 888 Kio** (environ 55,6 Mio).
- Les sommes de scores locaux représentent trois expériences distinctes et ne sont **pas** le score de l'archive intégrale.
- Le véritable `enwik9` (1 milliard d'octets) n'a **pas** été mesuré lors de l'exécution 44939582235.

**Décision :** conserver la correction du modèle comme prototype et mesurer le score intégral avant toute candidature. Priorité de recherche ultérieure : architecture d'un niveau supérieur à celui de ce prototype, dont le rendement reste inférieur à Zstandard sur ces extraits.

**Provenance :** journaux et artefact `omr8-enwik8-preflight` de l'exécution GitHub ci-dessus, archive d'artefact ID `14720669567`.
