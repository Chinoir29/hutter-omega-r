# OMÉGA-R v0.23 — Premier test bidirectionnel sur le vrai codeur cmix

## Objet

La v0.21 a démontré une vérité trop faible pour viser le Hutter Prize : un préfixe authentique de 524 288 octets du flux de production peut être codé sans modifier les probabilités du concurrent (158 153 octets, SHA-256 `836a7f6eb3b439f3f682fe8c16252d5a10d44fcbabfdc053f0053ec217baa0d3`). La v0.22 explore une nouvelle famille de températures en lecture seule.

**La v0.23 construit la capacité manquante : vérifier un véritable décodage symétrique du flux arithmétique préfixé**, avec tous les automates de métadonnées, de grammaire, de prédiction et d'injection actifs dans les deux directions.

## Intégration

`prepare_roundtrip.py` importe le préparateur *épinglé aux sources* `../v21/prepare_shadow.py` et crée une copie de travail séparée de `cmix-neif-2.0` (commit `35d1957a5074db802fc134126afc77b76d931761`, **GPL-3.0-only**).

Le code natif `src/coder/encoder.cpp` et `src/coder/decoder.cpp` du concurrent sont laissés **intacts**, après validation de leurs empreintes. Seul `src/runner.cpp` est instrumenté pour :

1. Prétraiter le **vrai corpus complet** `enwik9` (1 000 000 000 octets, SHA-256 canonique `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`).
2. Copier **en local uniquement** les premiers 524 288 octets du fichier pré-codeur post-WRT dans `omr23-reference-prefix.bin`, avec une lecture intégrale strictement comptée. Le fichier est éphémère et ne doit jamais être publié.
3. Encoder les mêmes 524 288 octets avec le vrai `comp9` en mode `-e` plafonné, puis finaliser le codeur arithmétique et conserver les octets dans `omr21-coded-prefix.bin` pour le contrôle immédiat.
4. Exécuter le **même binaire** en mode `-d` dans le **même répertoire de travail** avec les ressources déjà extraites par le compresseur ; lire l'en-tête du flux complet (501 062 281 octets) mais arrêter le décodage du codeur à la position 524 288, sans appeler les inversions externes qui exigent la fin du corpus.
5. Mesurer la restitution octet pour octet entre `omr23-reference-prefix.bin` et `omr23-decoded-prefix.bin`, vérifier leurs tailles et leurs SHA-256, ainsi que le SHA historique du codeur **158 153 octets**, puis supprimer les données d'essai.

Les réglages de zone, du module PPMd et des champs ISBN de la voie de décodage normale sont reproduits pour que la sonde ne crée pas une fausse dissymétrie. La symétrie réelle n'est acquise qu'après **la comparaison SHA exécutée** et non par la simple présence des patchs.

## Résultats et statut

- [Préflight GitHub n° 44967635859](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44967635859) : terminé avec succès, quatre tests adversariaux et applications des véritables ancres du commit tiers.
- [Expérience d'exécution n° 44967704622](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44967704622) : confronte le codeur et le décodeur authentiques sur le préfixe canonique. Elle doit enregistrer les SHA, tailles, durées et limites mémoire, et garder les échecs éventuels.
- Aucun fichier de corpus, dictionnaire dérivé, poids Transformer ou binaire tiers ne doit entrer dans les artefacts publics.

## Limites volontairement conservées

Le préfixe de sortie n'est pas le corpus original : c'est le flux de **production transformé** qui a alimenté `Compress`. Le test utilise des ressources temporaires extraites par le compresseur dans le répertoire courant ; il **ne prouve donc pas l'autonomie** d'un exécutable `archive9`.

**Ni le Hutter Prize, ni le score réglementaire `S`, ni la restitution des 1 000 000 000 octets de `enwik9` ne sont démontrés à ce stade.** La constitution originale reste intacte.

Décision préenregistrée : si les deux SHA coïncident, **KEEP** cette capacité comme banc d'intégration pour une prochaine modification symétrique du prédicteur. Sinon **RECONCEVOIR**, enregistrer le premier décalage, la cause d'initialisation du modèle ou les états de grammaire divergents et ne pas relancer à l'identique.
