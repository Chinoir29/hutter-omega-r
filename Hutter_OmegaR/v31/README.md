# OMÉGA-R v0.31 — Cartographie causale des phases du vrai flux pré-codeur

## Mission sous la Méta-Constitution OMÉGA-R

La constitution originale de 540 lignes reste intacte, SHA-256 `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`. Application opérationnelle des articles 1, 3, 6–12, 18, 20, 21, 24, 26–30 : **construire une donnée discriminante exacte** pour savoir où investir les modifications du modèle et comment éviter la sélection sur un préfixe non représentatif.

Il ne s'agit pas d'une simple revue de conformité. Le projet a bâti une chaîne native `comp9 → archive9` autonome sur 524 288 octets prétraités (v0.25), puis plusieurs algorithmes symétriques de calibration (v0.28, v0.29, v0.30). Les mesures réelles ont rejeté comme gains nets la v0.28 (+940 octets) et la v0.29 (+596 octets). La v0.30 (remplacement de 11 264 cellules par 16) est en essai natif distinct, #45075993000.

### Problème expérimental identifié

Le flux WRT réel généré à partir des 1 000 000 000 octets de `enwik9` mesure 501 062 281 octets. Toutes les comparaisons du codeur exécutées jusqu'à v0.30 s'arrêtent après **524 288 octets**, soit environ un millième de ce flux.

L'amont découpe le flux en un métabloc, des sous-articles de dictionnaire/auteurs/census, puis les premières pages. Le cache sémantique du concurrent traite certains types d'octets différemment selon la phase. Une optimisation qui semble défavorable dans le métabloc peut être excellente ailleurs, et réciproquement. Sans localiser les phases réelles, sélectionner des politiques par ce premier préfixe constitue un biais de recherche.

### Construction : localisation exacte par marqueur gelé

Le `src/text_start_pack.h` de `cmix-neif-2.0`, commit GPL-3.0-only `35d1957a5074db802fc134126afc77b76d931761`, définit un marqueur de fin de page de huit octets `20 20 4c 2f df 98 4e 0a`. Cette séquence intervient **après** WRT, dans le même espace d'octets que le vrai codeur.

La v0.31 s'appuie sur le harnais v0.19 de prétraitement d'enwik9 : il passe par le véritable `-e`, vérifie le milliard d'octets et s'arrête après `text_start::Pack`, *avant* le codeur arithmétique. Le fichier temporaire réel `archive9.cmix.temp` est analysé en lecture seule par `phase_map.py`.

L'outil ne conserve et ne publie que :
- les SHA-256 exacts du corpus canonique et du flux pré-codeur ;
- le nombre et les offsets des dix premiers et dix derniers marqueurs de page ;
- le nombre de marqueurs dans chacune des 60 fenêtres de 8 Mio ;
- la première fenêtre contenant le marqueur ;
- des propositions de fenêtres d'expérience, avec la condition explicite de conserver tout l'historique du prédicteur si l'on commence à coder après le métabloc.

Les octets du texte, la liste des pages, les poids, les binaires de production tiers et l'archive compressée ne sont pas redistribués. Le motif de huit octets provient du code source déjà public du concurrent, non d'une extraction du corpus.

**Limite scientifique :** trouver un marqueur exact ne prouve pas à lui seul la frontière officielle de zone du modèle. Une mesure de `metablock::Grenze` serait nécessaire pour l'affirmer ; cette version nomme honnêtement « premier marqueur de page » ce qu'elle constate, sans inférer davantage.

### Expérience

- [Workflow de preuve #45077280163](https://github.com/Chinoir29/hutter-omega-r/actions/runs/45077280163) : construire le harnais sur le commit exact, authentifier `enwik9`, produire le vrai flux de 501 062 281 octets et construire la carte, sans coder d'archive de concours.
- Tests adversariaux : marqueur exact traversant une fenêtre, absence de marqueur, refus de taille/empreinte erronées, séquence constante.
- **Critère de conservation :** 1) SHA authentique du flux identique à v0.19 ; 2) 60 fenêtres couvrant exactement les 501 062 281 octets ; 3) fréquence/offsets reproduisibles ; 4) aucune publication de données du corpus.
- **Critère de rejet :** empreinte différente, flux issu d'une autre voie ou marqueur de source non identique. Pas d'invention de localisation.

### Voies de construction ensuite

1. **Voie A — prétraitement réversible :** chercher des substitutions compactes réellement autonomes dans les structures abondantes, sans réduire le contexte observé par le prédicteur.
2. **Voie B — véritable modèle :** évaluer les améliorations de haute confiance dans les fenêtres effectivement utilisées par le modèle, plutôt que le début du métabloc uniquement.
3. **Voie C — coût total :** vérifier chaque variante au niveau de `comp9 + archive9`, poids et coût binaire inclus, puis sur l'intégralité du corpus lorsque les ressources le permettent.

Les fenêtres de données centrales **ne sont pas des préfixes indépendants** : relancer un prédicteur initialisé à un offset central n'est pas une reproduction du flux de l'amont. Toute véritable comparaison devra conserver l'historique du codeur et du décodeur, ou annoncer clairement un benchmark à états réinitialisés.

**Aucune soumission, aucune victoire, aucun S réglementaire.** Le record officiel récompensé actuellement référencé est 100 424 672 octets ; le candidat externe à 93 388 956 est une déclaration tierce, non un prix déjà validé.
