# OMÉGA-R v0.25 — conditionnement natif de l'archive expérimentale

## Objet constructif

La v0.23 a démontré sur GitHub (#44967704622) une restitution bit pour bit des 524 288 premiers octets du véritable flux prétraité de enwik9, en utilisant le même répertoire que le compresseur. Le résultat était reproductible : SHA de source et décodage 1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf, flux arithmétique 158 153 octets avec SHA 836a7f6eb3b439f3f682fe8c16252d5a10d44fcbabfdc053f0053ec217baa0d3.

La v0.24 a construit un conteneur expérimental autonome en assemblage Python, avec le décodeur compact, les poids et le flux arithmétique. Lors de sa première compilation, le garde de section a détecté un appel erroné à getFileSize depuis le décodeur. Ce défaut a été supprimé ; les journaux de diagnostic et le correctif sont conservés dans results_v24. Son verdict d'autonomie ne doit pas être présumé.

**La v0.25 élimine maintenant l'assembleur externe** : son patch remplace uniquement l'arrêt de recherche du compresseur après encodage d'un préfixe par un retour contrôlé, afin de reprendre le chemin de production natif qui construit archive9 depuis les composants déjà produits.

### Invariants

- Sources amont : marwoelk/cmix-neif-2.0, commit 35d1957a5074db802fc134126afc77b76d931761, licence GPL-3.0-only, notices intactes dans la copie temporaire.
- Le codeur et le décodeur arithmétiques originaux restent intacts ; le flux de prétraitement est celui de enwik9 entier, puis une limite de recherche plafonne le codage à 524 288 octets.
- Le compresseur lui-même doit conditionner archive9 au format prévu par son propre code, avec le décodeur compact, les poids, les bits et les longueurs.
- Le décodeur expérimental fixe en interne la longueur du préfixe sur le chemin zéro argument, en sautant les inversions qui exigent l'intégralité du corpus.
- Une archive de préfixe ne reproduit PAS enwik9 entier, et n'est pas une soumission Hutter. Aucun score S réglementaire n'est rapporté.

### Preuves, critères

Préflight #44971140540 : réussite des cinq tests propres à v0.25, des régressions v0.24 et de la préparation des véritables sources GPL épinglées. Le premier préflight a échoué en raison d'une assertion d'indentation incorrecte du test synthétique, corrigée avant la réussite.

**GO pour l'expérience réelle** : une fois le mode zéro argument de v0.24 vérifié, construire comp9 v0.25, encoder exactement le préfixe canonique, faire produire archive9 directement par comp9, puis décoder ce fichier seul dans un répertoire vierge et comparer longueur et SHA.

**HOLD** : source préflight seulement, ou échec du décodage autonome. **REJECT** : compilation impossible, divergences de flux ou d'état, ressources cachées, coût supplémentaire non comptabilisé.

Le but terminal reste comp9 + archive9 autonomes, restitution bit pour bit des 1 000 000 000 octets de enwik9, limites officielles de temps/RAM/disque et validation du jury. La constitution originale n'est pas modifiée.


## Mise à jour des dépendances : v0.24 désormais réussie

Le verrou d'autonomie du décodeur sur 524 288 octets du flux prétraité est **levé en v0.24** par l'expérience #44970630686 : archive assemblée 4 079 649 octets, exécution de ce fichier seul en dossier vierge, sortie 524 288 octets de SHA-256 `1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf`.

La v0.25 teste désormais un objectif matériellement différent : que **le code `comp9` natif lui-même** assemble ce fichier `archive9` sans assembleur Python externe. Son exécution réelle est [#44971506635](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44971506635). Aucun résultat n'est présumé avant contrôle du journal et des SHA.

**Limite :** ces archives ont pour sortie le préfixe du flux déjà prétraité, non le corpus intégral `enwik9`. Pas de score ni de validation réglementaire.


## Résultat terminal de cette expérience — SUCCÈS TECHNIQUE (22 novembre 2026)

[GitHub Actions #44971506635](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44971506635) : toutes les étapes réussies. Le véritable exécutable `comp9` **instrumenté** a prétraité `enwik9` canonique, codé son préfixe de 524 288 octets en 158 153 octets, puis emprunté lui-même son chemin de conditionnement natif pour produire `archive9`. Aucune intervention de l'assembleur Python de la v0.24.

- Archive native **4 079 636 octets**, SHA-256 `50b4c161f524f3464a589ea44d527b7851f524ac03c1379a886376d933e81309` ; décodeur 176 846, poids 3 744 629, flux arithmétique 158 153, en-tête 8 octets.
- Construite par le binaire de recherche `comp9`, SHA-256 `f20fcb1d9f6e967ecfa35b0bbad2b3e7d92edc2c4cc7db0813c24045aa78eb11`. Ce n'est **pas** le compresseur officiel amont non modifié.
- Démarrage de la seule archive dans un nouveau dossier contenant initialement `archive9`, sans argument ni variables d'expérimentation ni fichiers externes. Code retour 0.
- Restitution bit pour bit de **524 288 octets du flux déjà prétraité** ; SHA-256 `1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf`, identique à la référence.
- Temps sur runner GitHub Actions : construction 357,68 s, compression 352,22 s, décompression isolée 64,025 s. Ces durées ne sont **pas normalisées selon les règles du concours**.

Comparée à l'archive préfixe v0.24 assemblée extérieurement (4 079 649 octets), la v0.25 est 13 octets plus petite en décodeur compact. Ce petit écart entre binaires de laboratoire n'implique pas une amélioration de score Hutter.

Dossier de preuve : `Hutter_OmegaR/results_v25/REAL_NATIVE_SELFCONTAINED_PREFIX_44971506635.json` ; artefact de métadonnées GitHub **14734675565**.

**KEEP R3 pour l'instrument natif. R4–R6 ne sont PAS atteints.** Le décompresseur restitue un préfixe du flux de production, et non les 1 000 000 000 octets du corpus original. Aucune archive Hutter complète, aucun score admissible S, aucune reconnaissance du jury. Ne pas extrapoler la vitesse, les ressources ou la compression du préfixe au corpus entier.
