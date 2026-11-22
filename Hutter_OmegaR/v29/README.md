# OMÉGA-R v0.29 — Calibration hiérarchique des erreurs de bits à haute confiance

## Cadre constitutionnel et objectif terminal

Le but terminal reste une paire **comp9 + archive9 admissible au Hutter Prize** qui restitue bit pour bit le milliard d'octets de `enwik9`, sous CPU unique, ressources et temps prescrits, avec au moins 1 % d'amélioration du score total récompensé, et validation par le jury.

Cette version construit **un sous-modèle précis**, qui ne modifie ni `enwik9`, ni l'ordre des articles, ni la grammaire de codage, ni les poids intégrés. Elle préserve la constitution originale intacte (SHA-256 `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`). Elle adapte seulement son application opérationnelle aux nouveaux résultats, selon les articles 3, 8, 10, 13, 16, 21, 24, 26, 27 et 29.

## Résultat de référence v0.28 — enwik9 authentique, test préfixe

[GitHub Actions #44976256308](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44976256308) **success**, deux véritables archives autonomes, chacune restituant 524 288 octets du flux prétraité au SHA-256 exact `1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf`.

L'expert bayésien v0.28 réduit la longueur idéale de 131,72 bits et le flux arithmétique de 18 octets, mais ajoute 531 octets à `comp9` et 409 à `archive9` : **régression de 940 octets pour l'ensemble expérimental**. Décision : **REJECT comme gain net**. Voir `Hutter_OmegaR/results_v28/REAL_PAIRED_44976256308.json`.

Autres voies négatives conservées : EMA v0.21, température v0.22, poids externes v0.27. Le succès d'autonomie v0.25 n'est pas une restitution intégrale de `enwik9`.

## Construction algorithmique v0.29

L'implémentation de référence [`src/floor_stage.h` de `cmix-neif-2.0`](https://github.com/marwoelk/cmix-neif-2.0/blob/35d1957a5074db802fc134126afc77b76d931761/src/floor_stage.h) estime déjà une probabilité d'erreur par **case fine** de logit, position du bit et côté prédit. Pour les bits sautés par le modèle à profondeur adaptative, elle combine :
- le nombre d'erreurs (k) déjà observées dans cette case ;
- un nombre de pseudo-observations (C=4096) ;
- la probabilité d'erreur d'origine (f/65536) ;
- le nombre (n) de bits de cette case.

Sa formule produit un coût de calibration important si (n) est très faible, car la pseudo-distribution domine. La v0.29 met en commun **le facteur multiplicatif entre erreurs réellement observées et erreurs déjà prévues par le modèle**, sans remplacer la structure fine.

Pour chacun des **16 parents** (côté prédit 0/1 × position de bit 0…7) :
- `expected_f` : somme causale, en unités Q16, des probabilités d'erreur originales (f) ;
- `mistakes` : nombre des surprises précédemment observées ;
- `ratio_Q16 = ((mistakes+16) << 32) // (expected_f+(16<<16))`, borné à [1/4, 4] ;
- `f_prior = clamp(round(f * ratio_Q16 / 65536),1,32768)` ;
- le calcul original `P32` de la case fine reste intact, sauf que son **a priori** utilise `f_prior`.

Après chaque bit **effectivement codé**, le parent enregistre (f) et l'erreur réelle ; les deux directions reconstruisent les mêmes compteurs en entiers. Aucun état n'est communiqué par l'archive. Le seuil de confiance du concurrent, la taille de l'historique et les cases fines ne sont pas changés.

Le facteur de correction ne peut pas être considéré comme une probabilité démontrée optimale ; sa borne [1/4,4] évite les extrapolations les plus extrêmes, mais **ne garantit aucune économie**.

## Confrontations vérifiées

**Préflight #45061700701 : success.** Les huit tests contradictoires de protection des sources ont réussi ; les véritables `floor_stage.h` de l'amont et du candidat ont été préparés au commit épinglé `35d1957a5074db802fc134126afc77b76d931761` (GPL-3.0-only). Quatre expériences C++ (témoin/candidat × source artificiellement biaisée ou correctement calibrée) ont été confrontées indépendamment à des calculs Python en entiers arbitraires sur **1 600 000 transitions**, avec empreinte exacte des probabilités Q32.

- Source volontairement surconfiante : économie **1 016,004831 bits** de perte de prédiction sur 400 000 bits ;
- Source correctement calibrée : surcoût **0,307015 bit** sur 400 000 bits.

Ces chiffres sont **strictement synthétiques** ; ni les données du corpus ni son score ne sont représentés ici.

## Expérience sur données réelles

[GitHub Actions #45061877899](https://github.com/Chinoir29/hutter-omega-r/actions/runs/45061877899) : construction de deux copies du véritable moteur au même commit GPL, avec le chemin natif validé v0.25. L'une est intacte ; l'autre ne modifie que `floor_stage.h`. Pour les deux :
- corpus d'1 milliard d'octets téléchargé, vérifié par SHA-256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc` ;
- les 524 288 premiers octets de **la sortie prétraitée** sont codés ;
- une `archive9` de laboratoire est créée par `comp9` puis décodée seule dans un dossier vierge ;
- le résultat doit avoir le SHA-256 de référence ;
- le CPU unique, le RSS, le disque, les octets de `comp9`, du flux arithmétique et de `archive9` sont mesurés.

**Critère préenregistré :** aucune économie n'est attribuée à la version candidate tant que les deux décodages autonomes n'ont pas réussi ; même en cas de gain, seul le différentiel `comp9 + archive9` sur ce préfixe est retenu comme indicateur expérimental. La taille totale pour le corpus officiel, le temps Geekbench normalisé, la restitution `enwik9` entière et la validation du jury resteront non établis.

Décisions après résultat : **KEEP** si amélioration nette et restitution identique ; **RECONCEVOIR** si le codeur/décodeur échoue ; **REJECT sous ces conditions de préfixe** si la variante augmente le coût total. Aucune extrapolation mécanique d'un préfixe initial riche en métadonnées à tout le corpus.

## Protection du projet

Constitution originale et acquis conservés ; sources tierces issues du dépôt GPL-3.0-only jamais redistribuées, tout comme les poids, extraits du corpus et binaires dérivés. Seuls les scripts originaux de recherche, protocoles, tailles, empreintes et journaux de test sont publiés. Aucune candidature ni dépense engagée.
