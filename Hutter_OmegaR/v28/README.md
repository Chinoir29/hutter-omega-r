# OMÉGA-R v0.28 — Mélangeur bayésien causal intégré aux deux codeurs

## Objectif de construction

Produire et confronter une vraie modification **symétrique** de la chaîne de
compression de `cmix-neif-2.0` : `comp9` doit encoder un préfixe authentique
du flux `enwik9` avec une nouvelle loi de probabilité ; son `archive9`
doit restituer les mêmes octets dans un **répertoire vide**, sans argument.

Ce travail reste un **test expérimental sur 524 288 octets du flux prétraité**,
pas une restauration de `enwik9` entier, ni un score ou une soumission au jury.

## État vérifié et voies écartées

Le dossier original v0.25 et la constitution intacte sont la base. Les archives
v0.24 et v0.25 sont autonomes sur le préfixe, la v0.25 par le chemin natif
`comp9 → archive9`, GitHub Actions #44971506635. Témoin disponible :
archive de recherche de 4 079 636 octets ; 158 153 octets arithmétiques ;
524 288 octets de sortie ; SHA-256 du préfixe original
`1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf`.

Les corrections EMA (v0.21) et température (v0.22) ont régressé sur les bits
réels ; la permutation globale zlib (v0.20) n'est pas compatible avec les
automates d'origine sans révision de la chaîne. La recompression externe du
conteneur de poids (v0.27) coûte au mieux **9 octets supplémentaires**.
Ces résultats ne sont pas cachés ni réinterprétés.

## Hypothèse constructive nouvelle au sein d'OMÉGA-R

À chaque **bit librement codé** (pas les bits imposés), prendre :
1. `p = SemCorrect(floor.P32(...))`, probabilité originale de `cmix`.
2. `q = (n_1+1/2)/(n_0+n_1+1)`, estimateur
   **Krichevsky–Trofimov** conditionné par le préfixe binaire `bit_context`
   de l'octet courant (255 contextes possibles).
3. Calculer `r = (1-w)p+wq`, avec `w=1/2` au premier bit du contexte.
4. Après le bit, mettre à jour `w` par la vraisemblance bayésienne des deux
   experts et mettre à jour `n_0,n_1`.

Ce mécanisme est **causal** : les deux directions possèdent exactement les
mêmes informations après chaque bit. Aucune donnée annexe, aucune graine
aléatoire, aucun poids téléchargé ; le prétraitement WRT et le découpage
`archive9` natif restent ceux de v0.25.

Toutes les opérations qui affectent le codage sont réalisées en **entiers
Q32 et multiplications 128 bits**, et non par des calculs de vraisemblance
flottants susceptibles de diverger entre encodeur et décodeur. Les pertes
`-log2` servent exclusivement au diagnostic.

### Garantie mathématique dans la représentation idéale

Pour un contexte donné, le mélange bayésien de deux experts attribue à
toute séquence la probabilité
`P_mix = [P_cmix + P_KT]/2`, puisque les poids sont mis à jour après
chaque observation. Donc `P_mix ≥ P_cmix/2`, et
`L_mix ≤ L_cmix + 1 bit` de perte logarithmique par contexte observé.

Avec au plus 255 contextes, la borne idéale est **+255 bits par préfixe**.
C'est un résultat sur la perte logarithmique *idéale*, **pas** une borne
sur la taille finie de `archive9`, ni une garantie exacte pour les arrondis
Q32 utilisés. Un binaire plus gros peut perdre même si cette perte baisse.

Le contrôle indépendant Python énumère toutes les séquences de huit bits
pour vérifier cette identité ; le test C++ exécute 100 000 bits synthétiques
avec une amélioration claire et 250 000 bits de contrôle où le modèle peut
régresser mais reste dans la borne. Aucun de ces tests ne suffit à prouver
un gain sur `enwik9`.

## Code

- `omr28_bayes_bitmix.h` : modèle symétrique en mémoire, Q32/128 bits.
- `prepare_bayesian_pair.py` : applique la même correction à
  `Encoder::Encode` et `Decoder::Decode` des véritables sources
  `cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`,
  **GPL-3.0-only**, sans recopier ces sources dans notre dépôt.
- `test_prepare_bayesian_pair.py`, `bitmix_selftest.cpp` :
  tests de symétrie, dérives de sources, causalité et borne mathématique.
- Sonde de ressources v0.26 recopiée sans modification :
  `Hutter_OmegaR/v26/one_core_resource_meter.py`, épinglage sur **un CPU**,
  compte des fichiers temporaires supprimés mais encore ouverts,
  mesures RSS/disque/temps. Cela ne remplace pas la certification officielle.

## Critères de décision préenregistrés

1. **Préflight** : source amont épinglée, 7 tests Python et deux tests C++
   réussis, incrément des probabilités uniquement via la même routine dans
   les deux sens.
2. **Réalité** : compiler le vrai binaire de production, authentifier
   `enwik9` 1 000 000 000 octets (SHA-256
   `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`),
   coder les 524 288 premiers octets du flux résultant, créer
   `archive9` par `comp9` et la lancer seule dans un dossier vierge.
3. **Restitution** : longueur **524 288** et SHA-256 exact. Échec de l'un des
   deux critères = **REJET / CORRECTION DE SYMÉTRIE**, pas gain.
4. **Performance** : enregistrer séparément variation des octets codés,
   variation des octets d'archive, surcoût du binaire `comp9`,
   perte logarithmique idéale, temps et mémoire. Une économie sur un de ces
   critères ne prouve pas une économie sur le total `S`.
5. **Décision** : conserver comme **amélioration partielle démontrée**
   uniquement un avantage réel net sur comparaison appropriée, en respectant
   l'autonomie. Sinon enregistrer le résultat négatif, et réviser la stratégie.

Aucune variante supplémentaire ne sera choisie après consultation de l'essai
sans enregistrer une hypothèse et un nouveau protocole.

## État présent

[Préflight #44976015823](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44976015823) : **succès**.
Sept tests Python, deux essais C++ répétés, véritable source du concurrent
épinglée et instrumentation encodeur/décodeur validée. La source synthétique
positive fait économiser ~119 990 bits de log-perte ; le témoin pseudoaléatoire
perd ~238,46 bits, en dessous de la borne idéale de 255 bits.

Un succès du vrai codec ou de son score n'est PAS établi par ce préflight.

La constitution originale `CONSTITUTION_ORIGINALE_INTEGRALE.txt` est préservée
intacte. La construction, la confrontation et la consolidation sont gouvernées
par ses articles 1, 3, 8, 13, 16, 21, 24, 26 et 29.
