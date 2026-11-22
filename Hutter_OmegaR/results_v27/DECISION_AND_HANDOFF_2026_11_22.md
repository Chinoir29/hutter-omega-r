# OMÉGA-R — bilan scientifique v0.24 à v0.27 (22 novembre 2026)

## Preuves acquises

**v0.24 — KEEP (autonomie expérimentale).** GitHub Actions #44970630686 : archive auto-extractible de préfixe assemblée à partir du vrai décodeur compact et du conteneur de poids de cmix-neif-2.0, exécutée seule dans un répertoire neuf. 524 288 octets prétraités restitués exactement, SHA-256 1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf. Archive 4 079 649 octets, SHA-256 caf27b2303e0f709f200ca97e6b72fb2661d1aa42bab37e8d7f73c5799325c8a.

**v0.25 — KEEP (conditionnement natif).** GitHub Actions #44971506635 : le vrai compresseur modifié, construit depuis le commit GPL-3.0-only amont 35d1957a5074db802fc134126afc77b76d931761, a produit nativement archive9. Le même préfixe a été restauré sans argument dans un répertoire vierge (code 0, 64,025 s). Archive : 4 079 636 octets, SHA-256 50b4c161f524f3464a589ea44d527b7851f524ac03c1379a886376d933e81309. Le différentiel -13 octets avec v0.24 est un effet de conditionnement, pas un nouveau score.

**v0.26 — KEEP (métrologie).** GitHub Actions #44972422878 : neuf tests sur neuf du banc CPU unique / RSS du groupe de processus / fichiers temporaires alloués sous le répertoire et sous /tmp, y compris tmpfile() sans nom mais toujours ouvert. La mesure reste échantillonnée et non officielle.

**v0.27 — REJECT (reconditionnement des poids).** GitHub Actions #44972762089 : 15 couples réversibles en cinq codecs et trois représentations du conteneur de poids de 3 744 629 octets. Toutes les vérifications de restitution sont exactes ; le meilleur Brotli 11 fait 3 744 638 octets, soit +9 octets par copie. Cette voie ne diminue pas S.

## Frontière scientifique

L'étape v0.25 a établi l'autonomie d'une archive **sur les premiers 524 288 octets du flux prétraité**. Elle ne prouve PAS la restitution des **1 000 000 000 octets de enwik9 originel** ni un temps conforme à la formule 70 000/T heures, mémoire/disque et CPU unique du jury. Aucun score intégral S, première place ou validation officielle n'est revendiqué. Le record officiellement récompensé consulté demeure 100 424 672 octets ; seuil public affiché : S < 99 420 425 octets. cmix-neif-2.0 annonce 93 388 956 octets sans être confondu avec le record récompensé.

## Prochaine opération discriminante

Ne pas réitérer le recodage zlib de v0.20, les calibrations de v0.21–v0.22 ou les wrappers du .c5 de v0.27 sans hypothèse matérielle différente. Le sous-problème prioritaire est de construire une **nouvelle correction du prédicteur contextualisée sur un phénomène du flux**, symétrique et causale, sans poids supplémentaires coûteux, puis de comparer les vrais octets arithmétiques émis sur un témoin identique et des zones distinctes du flux canonique. En cas d'amélioration prouvée de la taille du flux, la porter dans le décodeur autonome v0.25 et compter la variation de taille des DEUX exécutables. Un gain local ne devient admissible qu'après production et restitution de enwik9 entier, ressources normalisées et contrôle indépendant.

Les sources et journaux sont dans les branches de recherche v0.24 à v0.27, sans modification de la constitution originale. Le dossier ZIP remis par conversation conserve la constitution, les sources d'origine v0.17, l'état v0.23, les codes propres v0.24–v0.27 et les preuves officielles des workflows. Aucune donnée de corpus, poids ou binaire tiers n'a été ajoutée au dépôt.
