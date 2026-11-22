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
