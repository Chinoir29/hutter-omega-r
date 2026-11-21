# OMÉGA-R v0.21 — Prédiction réelle, calibrateur fantôme et contrôle arithmétique A/B

## Objet et statut

Cette version reprend les preuves v0.20, **sans utiliser son résultat zlib comme résultat du concours**. Le laboratoire v0.20 a démontré que `reverse` réduisait la taille d'une archive zlib diagnostique de 2 810 101 octets sur le véritable flux de production (501 062 281 octets, SHA-256 `c35d3073eeba70f22a2e08a50202b53eb95466e3e9f1f2702f6f9b3f96fd8718`). Les automates de production interdisent d'en déduire immédiatement un gain sur le codeur de `cmix`.

La v0.21 introduit une voie **matériellement distincte** : examiner des corrections en ligne de la probabilité des **vrais bits effectivement codés** par `Encoder::Encode`, sans réordonner le flux et sans modifier la probabilité du codeur réel lors de ce diagnostic.

La constitution originale est préservée. Aucune soumission au jury, aucune revendication de première place.

## Sources et licence

- Dépôt utilisateur autorisé : `Chinoir29/hutter-omega-r` ; branche `research/omr21-cmix-shadow-calibration`.
- Sources tierces : `marwoelk/cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`, **GPL-3.0-only** ; `prepare_shadow.py` exige les blob Git exacts et ne modifie que des copies temporaires en préservant les notices amont. Aucune source tierce intégrale ni aucun poids n'est republé.
- Fichiers nouveaux : `prepare_shadow.py`, `omr21_shadow.h`, `test_prepare_shadow.py`, `shadow_selftest.cpp` ; permis sous GPL-3.0-only pour la compatibilité avec la base instrumentée.

## Expérience préenregistrée et falsifiable

Sur **deux arbres exactement identiques pour les prétraitements, le décodage et la limite de préfixe** :

- Contrôle : source amont et seul arrêt de recherche à 524 288 octets pré-codeur, après `e.Flush()`.
- Sonde : même préfixe, même source, **un seul ajout d'observation** au niveau de la probabilité `P32` produite par `floor_stage` et `SemCorrect`. La fonction `Before` rend exactement son argument `p32`. Les états du modèle et les bits émis ne sont pas changés.
- Exigence 1 : le flux arithmétique brut de la sonde et du témoin a **la même taille et le même SHA-256**. Le fichier temporaire s'appelle `omr21-coded-prefix.bin`, et ne doit jamais être confondu avec `archive9`.
- Exigence 2 : les vrais bits librement codés (pas les bits connus ou imposés) alimentent une calibration résiduelle en ligne, déterministe et entière. Quatre coefficients préenregistrés sont confrontés : 0, 1/4, 1/2, 3/4 (la valeur `variant` allant de 0 à 3). Le correcteur repose sur une EMA d'erreur en Q16 dans 32 groupes (8 positions de bit × 4 niveaux de confiance) ; toutes ses informations proviennent de bits **déjà observés**.
- Sélection du coefficient : la perte logarithmique sur les **262 144 premiers bits codés** (témoin 0 gagnant les égalités). Validation : **tous les bits codés ultérieurs** du préfixe, sans sélection rétrospective.
- Important : le calibrateur s'entraîne en ligne sur les bits passés, comme un compresseur causal. Ce test n'est pas un estimateur statistique i.i.d. de généralisation et ne mesure pas directement la taille finale d'archive.
- Exigence 3 : même corpus public `enwik9` authentifié par les **1 000 000 000 octets** et SHA-256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`, prétraitement par le vrai chemin de `comp9`, pas un fichier XML abrégé (E178).

## Exécution

Préflight déjà exécuté avec succès : [GitHub Actions #44963090336](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44963090336) : Python, C++ synthétique et empreintes source réelles, deux arbres de build clonés.

Expérience réelle : [GitHub Actions #44963170463](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44963170463). Le workflow génère les deux exécutables séquentiellement, authentifie `enwik9`, contrôle les deux SHA-256 arithmétiques, retient les résultats numériques et supprime le corpus, le dictionnaire, les poids et les fichiers codés bruts. Aucun binaire dérivé GPL ni aucun corpus n'est publié.

## Critère de décision

**KEEP comme piste de production** uniquement si la sonde est strictement non intrusive *et* si le coefficient sélectionné sur la première période améliore la perte logarithmique sur la période ultérieure. Ensuite seulement, construire le **vrai** ajustement symétrique encodeur/décodeur, vérifier le décodage exact de la totalité des métadonnées et finalement l'autonomie de `archive9`.

**REJECT** si la calibration dégrade la perte ultérieure ou si le témoin 0 est sélectionné. **FAILED** si la compilation, le traitement canonique ou l'égalité des SHA entre témoin et sonde échoue. Aucun résultat n'est transformé en score Hutter avant un binaire candidat intégral, le calcul des coûts admissibles et la validation officielle.

### Invariants de coût et de sûreté

Cette expérience mesure des bits de code prédictif en **préfixe**, non un score définitif. Elle ne réclame ni dépense, ni soumission, ni infrastructure payante. Le workflow s'arrête en cas d'échec d'un seul contrôle et conserve ses journaux. La constitution originale et ses hiérarchies de sûreté, d'exactitude et de reproductibilité restent applicables.
