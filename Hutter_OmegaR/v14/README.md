# OMÉGA-R v0.14 — laboratoire de codage sur le moteur compétitif

**Statut :** protocole expérimental, pas un score Hutter Prize et pas un résultat du moteur de concours inchangé.

## Pourquoi une nouvelle voie ?

Le canary v0.12 a échoué avec **E178** : le binaire `comp9 -e` de `cmix-neif-2.0` utilise une reconstruction de dictionnaire fondée sur des informations de l'intégralité d'`enwik9`. Il ne peut pas être appliqué tel quel à un petit extrait XML.

Il existe cependant un chemin de codage brut `RunCompression()` / `RunDecompression()`, exposé dans le **build auxiliaire** `AUX_BUILD=1`. Celui-ci désactive les composants sémantiques étudiés. Pour étudier SEMCACHE, ce laboratoire active uniquement l'interface `-c` dans une compilation de recherche du moteur complet (`AUX_BUILD=0`), **sans modifier ses tables de prédiction**.

## Composition

- `enable_raw_lab.py` : vérifie le commit et le blob exacts `src/runner.cpp` de `marwoelk/cmix-neif-2.0` et autorise `-c` dans la compilation de laboratoire.
- `prepare_vocabulary_sample.py` : authentifie l'intégralité d'`enwik9`, puis construit un échantillon **avec perte** en ne gardant que les 208 valeurs d'octet autorisées par le vocabulaire gelé du flux interne. L'entrée n'est donc plus une reproduction de Wikipédia ou un sous-corpus XML.
- `run_raw_lab.py` : teste la compression et la décompression du flux expérimental dans des répertoires séparés, avec les mêmes poids et un seul cœur, et compare les empreintes SHA-256.
- `.github/workflows/omr14-raw-core-lab.yml` : compile une seule version témoin avant toute tentative d'optimisation.

## Limites épistémiques

1. L'interface `-c` est une **modification explicitement non compétitive** de l'exécutable ; le programme n'est pas empaqueté en archive autonome.
2. Le corpus d'entrée du laboratoire est **une projection irréversible** des octets de Wikipédia. Les taux ou temps obtenus ne prédisent pas le score admissible sur le fichier officiel `enwik9`.
3. Le codage brut n'exerce pas forcément les mêmes contextes et métadonnées que le chemin normal `-e`, en particulier le dictionnaire, le réordonnancement, les métablocs et leurs signaux connus ; l'activité réelle de SEMCACHE reste à vérifier.
4. Les résultats auront le statut de **faisabilité fonctionnelle**, et seulement ensuite de prétest pour des modifications A/B de composants réellement actifs.
5. Le code du concurrent est GNU GPL-3.0. Le dépôt OMÉGA-R publie uniquement des patchs sur la révision vérifiée, et ne redistribue pas les fichiers tiers ni les poids du modèle.

## Critère de réussite

Un essai valide exige la compilation, une taille non nulle du flux de codage, puis la reconstruction exacte du flux expérimental (SHA-256). En cas d'échec, conserver les logs pour réviser le protocole sans effacer les résultats négatifs.

**Aucune soumission n'est autorisée sur la base de ces résultats.**
