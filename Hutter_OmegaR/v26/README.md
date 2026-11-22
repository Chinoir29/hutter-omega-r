# OMÉGA-R v0.26 — instrument de ressources à cœur CPU unique

## Portée

Ce banc exécutable n'est pas un compresseur. Il établit un témoin local de ressources pour les prochains binaires candidats. Il épingle le programme sur un seul cœur CPU Linux grâce à sched_setaffinity, échantillonne le RSS additionné des membres du même groupe de processus, et surveille les helpers qui survivent temporairement au lanceur. L'espace disque est compté comme l'augmentation des blocs réellement alloués dans le répertoire de travail.

La mesure n'est **pas une certification Hutter** : les pics très courts peuvent être manqués et les limites de mémoire/disque doivent être validées dans le cadre du jury. Règlement : https://prize.hutter1.net/hrules.htm.

## Usage

~~~bash
mkdir -p /tmp/omr26-clean
python3 Hutter_OmegaR/v26/one_core_resource_meter.py \
    --cwd /tmp/omr26-clean \
    --report /tmp/omr26-mesures.json \
    --timeout-seconds 120 \
    -- /usr/bin/python3 -c 'import time; time.sleep(0.5)'
~~~

Les rapports et journaux sont obligatoirement créés **hors du répertoire testé**. Le programme refuse un CPU non autorisé. Le champ official_hutter_compliance vaut toujours null même quand les métriques se situent sous les budgets configurés.

## Preuves reproduites

- [CI 44972049903](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44972049903) : 7 tests réussis.
- [CI 44972224375](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44972224375) : 8 tests réussis, dont un enfant qui survit à la sortie du processus lanceur.

Les fichiers sont autonomes et n'incluent aucun corpus, poids ni code tiers. La constitution OMÉGA-R originale demeure inchangée, et aucune victoire n'est revendiquée.
