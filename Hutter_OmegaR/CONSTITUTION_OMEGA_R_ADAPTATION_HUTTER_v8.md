# OMÉGA-R — Adaptation opérationnelle Hutter v0.8

**Date :** 21 novembre 2026. **Texte source conservé sans modification :** `Constitution_OMEGA_R_source.txt`. Cette adaptation de travail ne remplace pas la constitution d'origine.

## Mission active

Obtenir une compression sans perte de `enwik9`, avec archive auto-extractible, `data9` rigoureusement identique, et un score `S = comp9 + archive9` strictement inférieur au seuil applicable à la date de la candidature, tout en respectant les limites du règlement officiel.

## Évolution méthodologique v0.8

1. **Interdire les scores fabriqués :** seuls les octets du fichier canonique de 1 milliard d'octets et leur reconstruction SHA-256 autorisent un score *local sur enwik9*. Une soumission n'est officielle qu'après validation du comité.
2. **Tester à deux échelles :** étape de prévol sur `enwik8` de 100 millions d'octets, authentifié par taille + MD5 + SHA-1 du site de Matt Mahoney, puis contrôle de trois tranches indépendantes de 8 MiB (offsets 0, 40, 80 MiB). Ces résultats ne sont jamais un score Hutter ni une extrapolation du score final.
3. **Contrôler l'archive autonome :** le décompresseur s'exécute dans un répertoire isolé, sans original, et doit produire `data9` identique au bloc testé, avec contrôle SHA-256.
4. **Réserver l'essai complet :** autoriser le lancement de l'épreuve `enwik9` seulement après un prévol réussi et une décision explicite d'exécution. Le workflow ne publie ni corpus ni archive, seulement des mesures.
5. **Mesurer le bon objectif :** compter le binaire compresseur et l'archive exécutable ; ne jamais assimiler le débit, le flux intermédiaire ou une comparaison avec `zstd` à ce score.
6. **Conserver l'intégrité scientifique :** une idée sans validation est une hypothèse ; une idée mesurée puis rejetée demeure une connaissance négative réutilisable.
7. **Respecter les ressources et les droits :** ne pas engager de paiement ni publier le projet dans un dépôt public non autorisé, et ne pas modifier des dépôts personnels hors du périmètre Hutter.

## Décision

- R3 : logiciel autonome et instrumentation en local ; workflow de prévol et benchmark distant **préparé mais non exécuté**.
- R2 : expériences partielles non représentatives du corpus officiel, et rejet du double historique v0.7.
- R0 : record mondial non obtenu ; aucune candidature envoyée.

**Prochain verrou :** exécuter d'abord le prévol sur `enwik8` authentique depuis un dépôt GitHub Hutter dédié, puis décider s'il est rationnel de lancer le milliard d'octets.
