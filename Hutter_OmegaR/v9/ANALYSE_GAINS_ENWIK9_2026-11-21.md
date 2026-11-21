# OMÉGA-R v0.9 — Carte des économies nécessaires sur le flux réel de cmix-neif 2.0

**Étude rétrospective du 21 novembre 2026 : calcul déterministe à partir des mesures publiques d'un concurrent.** Ce rapport n'est ni un nouvel algorithme ni un résultat de compression d'OMÉGA-R.

## Provenance et vérifications

- Source publiée : [doc/stream_rate.tsv](https://github.com/marwoelk/cmix-neif-2.0/blob/35d1957a5074db802fc134126afc77b76d931761/doc/stream_rate.tsv)
- Révision du code : `35d1957a5074db802fc134126afc77b76d931761`
- SHA Git blob du fichier : `2a042eb0b69a31b9033721485e364de13ee0f093`
- Enregistrements analysés : **1 000**, couvrant **501 062 281 octets** du flux intermédiaire.
- Somme exacte des coûts encodés dans le TSV : **85 417 870 octets**. Ce n'est pas la taille de l'archive auto-extractible.

## Cible mathématique

Le concurrent annonce `S = 93 388 956` octets. Pour améliorer ce score d'au moins 1 % à coût de programme constant, la réduction totale doit être **au moins 933 890 octets** ; la nouvelle somme serait au plus **92 455 066 octets**. C'est une cible hypothétique, applicable si ce score devenait la référence à battre, pas un record officiellement déjà attribué.

Rapportée uniformément au flux intermédiaire de 501 062 281 octets, cette économie représente **0.014911 bit par octet intermédiaire**.

| Portion modifiée | Coût actuel de cette portion | Réduction minimale, si toute l'économie y est obtenue |
|---|---:|---:|
| 1 % des fenêtres les plus coûteuses | 1 411 222 | 66.18 % |
| 5 % des fenêtres les plus coûteuses | 5 717 389 | 16.33 % |
| 10 % des fenêtres les plus coûteuses | 10 938 251 | 8.54 % |
| 20 % des fenêtres les plus coûteuses | 21 039 568 | 4.44 % |
| 50 % des fenêtres les plus coûteuses | 49 147 268 | 1.90 % |
| 100 % des fenêtres les plus coûteuses | 85 417 870 | 1.09 % |

**Limite démontrée :** les quatre premières fenêtres (environ 2 Mo de flux) ne coûtent au total que **725 009 octets**. Même leur compression hypothétique à **zéro octet** ne suffirait pas à économiser 933 890 octets. Une stratégie se limitant aux premières pages ne peut donc pas, à elle seule, fournir 1 % d'amélioration sous ces hypothèses.

Le groupe minimal de fenêtres **les plus coûteuses** atteignant déjà 933 890 octets représente **6 fenêtres** ; cette observation n'indique pas qu'on puisse réellement économiser tous leurs bits. Les dix premières fenêtres consécutives coûtent **1 260 476 octets**.

## Décision expérimentale

1. Priorité aux prédicteurs capables d'apporter un petit gain sur de **nombreuses fenêtres** (environ 1,09 % du coût du flux actuel si gain uniformément réparti) plutôt qu'à une réduction cosmétique sur seulement 2 Mo.
2. Évaluer séparément le coût de chaque ajout : **poids des modèles dans comp9 et archive9**, temps supplémentaire, RAM, changements des prétraitements et coûts du flux codé.
3. Conserver le benchmark original inchangé et traiter chaque variante par comparaison A/B documentée.
4. Refuser les « gains » mesurés uniquement après filtrage artificiel du corpus, sur des fenêtres sélectionnées a posteriori ou en oubliant le poids du programme.
5. Le taux de compression du flux intermédiaire ne permet pas à lui seul de prédire la variation du score total si le modèle, le prétraitement ou la mise en paquet change.

## Périmètre des preuves

C'est un **calcul sur les 1 000 coûts publiés par une équipe concurrente** ; nous n'avons pas reproduit leur mesure. L'analyse ne prouve ni nouveauté mondiale, ni gain technique, ni admissibilité ou victoire au Hutter Prize.
