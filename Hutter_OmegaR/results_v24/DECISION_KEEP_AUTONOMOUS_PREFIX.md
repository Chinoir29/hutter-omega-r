# Décision OMÉGA-R v0.24 — autonomie du décompresseur sur préfixe prouvée

## Vérification exécutée
GitHub Actions #44970630686 (terminé : success), avec source tierce marwoelk/cmix-neif-2.0 à commit 35d1957a5074db802fc134126afc77b76d931761 et GPL-3.0-only.

Le compresseur a utilisé le vrai corpus canonique enwik9 pour produire le flux prétraité et coder ses 524 288 premiers octets. Une archive expérimentale [stub décodeur][poids][bits arithmétiques][trailer] a été assemblée, puis exécutée **seule** sous le nom archive9 dans un répertoire initialement vierge avec seulement le fichier archive9 et sans argument ni enwik9. Elle a produit 524 288 octets de données prétraitées, avec le même SHA-256 que la référence v0.23.

- Taille de l'archive expérimentale : 4 079 649 octets.
- Décodeur : 176 859 ; poids intégrés : 3 744 629 ; bits codés : 158 153 ; trailer : 8 octets.
- SHA-256 archive : caf27b2303e0f709f200ca97e6b72fb2661d1aa42bab37e8d7f73c5799325c8a.
- SHA-256 des 524 288 octets restitués : 1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf.
- Sortie du programme : code 0 ; délai 85,923 secondes ; aucun dépassement déclaré par ce test.
- Identité du fichier de sortie : vérifiée par taille et SHA-256 ; aucune ressource annexe de l'encodeur préexistante au lancement.

Registre machine lisible : results_v24/REMOTE_ISOLATED_44970630686.json.
Artefact GitHub : https://github.com/Chinoir29/hutter-omega-r/actions/runs/44970630686/artifacts/14733828330.
SHA-256 ZIP d'audit : 8a5c60cb4c6e39517bf1d53922338226423872652991d23d43c943284f06ce7d.

## Verdict constitutionnel

**KEEP** : autonomie de décodage sur le préfixe de données **prétraitées** et format de décodeur autonome. Niveau partiel R3 pour le sous-problème expérimental (outil fonctionnel, reproduisible).

**NON DÉMONTRÉ** : restitution du 1 000 000 000 octets original, inversions post-prétraitement complètes, temps normalisé, RSS/disque sur toute la durée et score total S admissible. R4/R5/R6 au Hutter Prize non atteints.

**Opération suivante** : v0.25 fait construire archive9 par le compresseur natif au lieu d'un assembleur Python. Ensuite seulement, élargir le protocole au chemin complet et chercher un gain de score de modèle. Aucune soumission ni publication de poids/corpus/exécutables tiers, ni dépense autorisée.
