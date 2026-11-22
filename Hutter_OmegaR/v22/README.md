# OMÉGA-R v0.22 — Calibrage par température du véritable prédicteur cmix

## Point de départ : résultat négatif v0.21 reproductible

La v0.21, sur **524 288 octets réels** du flux pré-codeur de `cmix-neif-2.0`, a confirmé un témoin et une sonde **strictement identiques** : chacun produit **158 153 octets**, SHA-256 `836a7f6eb3b439f3f682fe8c16252d5a10d44fcbabfdc053f0053ec217baa0d3`. La correction EMA entraînée par le passé a régressé de **+1 869,43, +4 690,31 et +8 791,83 bits** sur les **3 808 903 bits de contrôle** ; elle est donc **REJETÉE** pour ce préfixe. Source : GitHub Actions [#44963170463](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44963170463).

Une vérification mathématique supplémentaire, faite à partir des chiffres du journal original, donne : code réel `158153 × 8 = 1265224` bits ; longueur de Shannon mesurée sur la probabilité **vraiment utilisée** `60929.7547637539 + 1204252.1152591682 = 1265181.870022922` bits. L'écart de **42,129977 bits** (dont l'en-tête et la finalisation arithmétique) démontre que le compteur de perte logarithmique est cohérent avec les octets effectivement émis pour ce préfixe, **sans garantir** cet écart pour tout autre code.

## Hypothèse et instrument nouveau

v0.22 ne répète pas l'EMA : la probabilité conditionnelle est recalibrée **hors de la chaîne du codeur** par la famille **statique** de températures du logit :

\[
q_t = \operatorname{sigmoid}(t\,\log(p/(1-p))).
\]

Les facteurs choisis **avant** l'accès aux résultats de ce test sont `[1.00, 0.93, 0.97, 1.03, 1.07, 0.85, 1.15]`. Le facteur 1.00 est le témoin exact. Les autres testent une confiance moins forte ou plus forte que l'original. Aucun octet du flux n'est déplacé et `Before(p, context)` renvoie **toujours p inchangé**.

Deux hypothèses préenregistrées, sans les fusionner par sélection rétrospective du contrôle :
1. **Globale :** un facteur choisi uniquement par minimisation de la perte sur les 262 144 premiers **bits réellement codés**.
2. **Spécialisée :** un facteur choisi séparément pour chacune des 8 positions de bit, sur ce même ensemble d'entraînement.

Les choix sont gelés au début du contrôle. Chaque facteur fournit sa perte cumulée sur les **3 808 903 bits codés restants** du même préfixe. Les facteurs restent entraînés / sélectionnés sur le premier segment uniquement : ce test ne doit pas être présenté comme une validation indépendante au niveau d'une nouvelle région de texte.

## Contrôles contradictoires

Les deux programmes autonomes dans `Hutter_OmegaR/v22` ont été compilés et exécutés localement :
- `test_temperature_biased.cpp` : exemple volontairement mal calibré, les températures peuvent améliorer la perte.
- `test_temperature_calibrated.cpp` : sur des observations exactement calibrées à 3/4, la méthode choisit **le facteur neutre (1.0)** dans les huit positions.

Ils valident la sélection et sa capacité à accepter ou refuser une transformation ; ils ne remplacent pas un test du vrai codeur.

## Intégration source épinglée et exécution en cours

- Dépôt autorisé `Chinoir29/hutter-omega-r`, branche `research/omr22-logit-temperature`.
- Sources originales du concurrent : `marwoelk/cmix-neif-2.0`, commit `35d1957a5074db802fc134126afc77b76d931761`, **GPL-3.0-only** ; ses sources et notices restent uniquement dans des clones de travail temporaire.
- Réutilisation contrôlée du préparateur `v21/prepare_shadow.py` avec le fichier d'interface `v22/omr22_temperature.h`. La sonde conserve strictement les mêmes positions d'insertion dans `Encoder::Encode` et renvoie la probabilité du codeur **sans la modifier**.
- GitHub Actions [#44967001401](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44967001401) : exécute les deux contrôles, compile le vrai codeur, vérifie SHA-256 de `enwik9`, code 524 288 octets réels et exige **exactement le même SHA-256 et les mêmes 158 153 octets** que v0.21. Seules les métadonnées du test sont publiées.

Si la sonde modifie le moindre octet codé, l'expérience est invalidée. Si elle échoue à améliorer la perte sur le contrôle, la piste température est **REJETÉE pour ce préfixe**. Si une des deux stratégies préenregistrées économise plus de **512 bits théoriques** sur le contrôle, la piste reste **exploratoire** et exige une confirmation sur une nouvelle région, puis une réelle intégration **symétrique encodeur/décodeur** et une mesure du score `S` incluant le code et le décodeur.

**Aucune archive autonome `archive9`, restitution du fichier complet `enwik9`, victoire ou score Hutter ne sont revendiqués par cette expérience.**

## Reproduction

```sh
g++ -O2 -std=c++17 -Wall -Wextra -Werror -I Hutter_OmegaR/v22 Hutter_OmegaR/v22/test_temperature_biased.cpp -o /tmp/t_biased
g++ -O2 -std=c++17 -Wall -Wextra -Werror -I Hutter_OmegaR/v22 Hutter_OmegaR/v22/test_temperature_calibrated.cpp -o /tmp/t_calibrated
/tmp/t_biased
/tmp/t_calibrated
```

La constitution originale reste **inchangée**, SHA-256 `b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f`. Niveaux de résultat : instrument de laboratoire, pas de candidat admissible.
