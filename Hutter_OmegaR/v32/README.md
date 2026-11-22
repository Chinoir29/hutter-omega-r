# OMÉGA-R v0.32 — Extension du vrai chemin natif au-delà du premier métabloc

## Problème réellement résolu par cette construction

Jusqu'à v0.30, les essais comparables de `comp9 → archive9` ne codaient
que les premiers 524 288 octets du flux `enwik9` **déjà prétraité**.
Cela correspond à environ 0,105 % du flux complet (501 062 281 octets)
et ne permet pas de départager des hypothèses visant le traitement des pages.

La v0.31 construit une carte des marqueurs de pages et la confronte aux
coûts publiés du codeur, sans réinitialiser fictivement le modèle au
milieu des données. La v0.32 construit la **capacité logicielle manquante** :
un vrai `comp9` et son `archive9` autonome sur un préfixe beaucoup plus
long, capable de traverser les premières phases tout en maintenant
**l'intégralité de l'historique causal antérieur**.

## Source et méthode

Point de départ : le chemin natif v0.25, prouvé par GitHub Actions
#44971506635, conservant les codeurs arithmétiques et les transformées WRT
d'origine de `marwoelk/cmix-neif-2.0`, commit
`35d1957a5074db802fc134126afc77b76d931761` (GPL-3.0-only).

Le programme `prepare_extended_prefix.py` applique des patchs
source-pinnés à la copie **temporaire** de `src/runner.cpp` :

1. Remplace exactement les **trois** plafonds de laboratoire
   `1048576ull` par `67108864ull` dans l'encodeur de préfixe,
   la copie de référence et le décodeur de préfixe.
2. Change exactement une fois la longueur injectée en interne par la
   voie auto-extractible zéro argument de `archive9`.
3. Conserve le `RunCompression` original en amont et le
   conditionnement natif `[décodeur][poids][payload][trailer]`.
4. Conserve `omr23-reference-prefix.bin`, écrit **avant**
   l'arithmétique depuis le flux WRT authentique. Le décodeur autonome
   doit produire `omr24-decoded-prefix.bin` de même longueur et
   de même SHA-256.
5. Exige un multiple de 524 288 octets, entre 524 288 et 67 108 864
   octets (64 Mio). Aucune donnée secondaire n'est ajoutée à l'archive.

Les transformées d'origine parcourent le **milliard d'octets canonique**
de Wikipédia avant la limite du codage arithmétique. Une archive de préfixe
plus long ne restaure **toujours pas** le fichier `enwik9` original :
les inverses du corpus complet restent hors de portée de cette sonde.

## Contre-épreuves et limites

Les tests sources refusent un changement du commit amont, des trois bornes,
du décodeur zéro argument, de l'assembleur natif et de la référence exacte.
Le préflight compare les copies GPL originale, 8 Mio et 32 Mio tout en
s'assurant que les moteurs arithmétiques restent inchangés.

Un benchmark réel plus long n'est autorisé qu'après avoir fixé la longueur
en fonction de la première page effective mesurée par v0.31. Si la phase
recherchée est au-delà de 64 Mio, ce plafond devra être réévalué en
expliquant explicitement le nouveau coût.

La longueur supérieure augmente linéairement le calcul arithmétique,
les besoins de référence, les temps de décodage et la probabilité
d'un problème de ressources. Tout essai réel devra utiliser la sonde
de ressources à CPU unique v0.26 et vérifier le SHA-256 de la référence
et de la sortie **hors du répertoire de l'encodeur**.

## Statut épistémique

Cette v0.32 est d'abord une **construction de harnais source**.
Une compilation réussie, le codage réel de plusieurs dizaines de Mio
et l'identité autonome ne sont acquis **qu'après exécution effective**.
Aucun score réglementaire Hutter, aucun gain de taille, aucune victoire,
aucune soumission.

Constitution originale de recherche conservée intacte :
SHA-256 `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`.

Suite constructive : sélectionner la première longueur couvrant des
pages vraies (v0.31), mesurer les deux voies à capacité identique et
comparer le total `comp9 + archive9`, puis tester de véritables
optimisations au-delà du métabloc.
