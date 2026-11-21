# OMÉGA-R v0.17 — Proposition et preuve du transcodeur réversible

**Statut :** preuve mathématique de propriété du **transcodeur**, non du compresseur de compétition. Le programme et les tests constituent les vérifications de l'implémentation.

## Objet

Notons `Σ = {0,...,255}` l'alphabet des octets originaux et `A ⊂ Σ` le vocabulaire de 208 octets du moteur `cmix-neif-2.0`, fixé par le Git blob `da5ffe84fb7e3d9a5061b43da5970f7c9f728e19`. On fixe `e = 94` (caractère ASCII `^`), qui appartient à `A`. Il existe exactement 48 valeurs de `Σ` absentes de `A`. L'ensemble des exceptions est donc `E = (Σ \ A) ∪ {e}`, de cardinal 49.

On fixe une fois pour toutes une liste `C` de **49 symboles distincts** de `A \ {e}` : `abcdefghijklmnopqrstuvwxyz0123456789JKLMNOPQRSX_+`, et une bijection `c : E → C` selon l'ordre croissant des éléments de `E`.

Définissons le transcodeur `T : Σ* → A*` octet par octet :

- pour `b ∈ A \ {e}`, écrire le seul octet `b` ;
- pour `b ∈ E`, écrire les deux octets `e c(b)`.

La transformation inverse `U : T(Σ*) → Σ*` lit un flux de gauche à droite : chaque octet différent de `e` est rendu tel quel ; lorsqu'elle rencontre `e`, elle exige un octet suivant dans `C` et rend l'unique préimage `c^{-1}` correspondante. Elle rejette toute séquence tronquée et tout code invalide.

## Propriétés établies

1. **Alphabet d'arrivée.** Toute sortie de `T` appartient à `A*` : soit `b ∈ A \ {e}`, soit `e ∈ A` suivi de `c(b) ∈ C ⊂ A`.
2. **Déchiffrabilité sans ambiguïté.** Les images des symboles de `A \ {e}` commencent par un octet autre que `e`, tandis que toutes les images de `E` commencent par `e`. Les 49 seconds octets des séquences échappées sont distincts. Il existe donc un unique découpage des sorties de `T` en images d'octets.
3. **Réversibilité pour toute entrée.** Par le point 2, `U(T(b))=b` pour chaque octet, et par induction sur les concaténations de mots, `U(T(x))=x` pour tout `x ∈ Σ*`.
4. **Coût exact et bornes.** En notant `n_E(x)` le nombre d'octets de `x` appartenant à `E`, `|T(x)| = |x| + n_E(x)`. Par conséquent `|x| ≤ |T(x)| ≤ 2|x|` et la mémoire requise par le décodeur naïf est `O(|x|)` ; un décodeur en flux peut utiliser `O(1)` de mémoire, hors sortie et table de 49 entrées.
5. **Aucune donnée auxiliaire dépendante du corpus.** L'ensemble `A`, le marqueur `e` et la bijection `c` sont déterminés par la version épinglée. Pour interpréter le flux, le décodeur a seulement besoin de ces constantes et du flux reçu. Aucune table statistique entraînée et aucun état caché de Wikipédia ne sont nécessaires.

Ces propriétés sont générales, et ne dépendent ni de `enwik9`, ni des fenêtres retenues, ni du seuil de recherche sémantique.

## Limites importantes

- Cette preuve ne démontre pas que le prédicteur de `cmix-neif-2.0` peut traiter tout flux de `A*` : ses modèles et automates peuvent imposer des contraintes **au-delà** du vocabulaire.
- Les essais de la v0.17 utilisent le chemin `-c/-d` du **laboratoire modifié**, pas les exécutables `comp9/archive9` de concours. Leur score Hutter Prize est **indéfini**.
- Une taille de flux arithmétique plus courte sur des fenêtres ne signifie pas nécessairement une archive auto-extractible plus courte sur le milliard d'octets. Le coût du transcodeur, de la reconstruction et des contraintes de l'exécutable final doit être compté si cette méthode était intégrée dans une candidature.
- La transformation est **réversible**, à la différence des projections avec perte v0.15 et v0.16. Une restitution des seuls octets transcodés ne suffit pas pour un verdict v0.17 : le test exige également `SHA-256(U(flux_restauré)) = SHA-256(fenêtre_Wikipédia_originale)`.

**Validation logicielle locale :** 33 tests unitaires réussis sur l'encodeur, les 256 valeurs d'octet, des entrées aléatoires et contrôles négatifs, le banc d'essai à compresseur simulé, et le vérificateur de rapports. L'essai distant sur le vrai modèle doit être jugé séparément.
