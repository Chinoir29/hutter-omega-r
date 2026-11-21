# OMÉGA-R v0.18 — Preflight GitHub exécuté et vérifié

- Dépôt projet : Chinoir29/hutter-omega-r
- Branche isolée : research/omr18-production-preflight
- Workflow : .github/workflows/omr18-source-preflight.yml
- Exécution : https://github.com/Chinoir29/hutter-omega-r/actions/runs/44956009000
- Job : 137004182034
- Commit exécuté : 846db4cd0b3f8dfc678095427a01c0e53ecce779
- Statut GitHub : completed / success
- Source tierce effectivement clonée : marwoelk/cmix-neif-2.0, 35d1957a5074db802fc134126afc77b76d931761 (GPL-3.0).
- Tests de contrat source : 7/7 PASS (tests contradictoires sur fixtures synthétiques).
- Contrôle des empreintes, des chemins compresseur et décodeur et du dictionnaire : PASS sur l'arbre réel au commit pinned.
- Création de deux arbres distincts : baseline kQpE3=990 ; candidat kQpE3=999.
- Marqueur exact du log : PINNED_SOURCE_PREFLIGHT_OK; NO_PRODUCTION_BUILD; NO_HUTTER_SCORE
- Archive d'audit de l'exécution : GitHub Actions artifact 14727353950. SHA256 du ZIP artifact : b60fd74b553868cb7de665d8bcdf00fb842dd2b721793db3032038f39b5d2c39.
- Deux binaires comp9 produits dans **cette exécution** : NON.
- enwik9 intégral présent : NON.
- archive9 autonome produite : NON.
- Score admissible/victoire : NON DÉMONTRÉS.

**Décision :** garder le préflight comme instrument fiable ; pas d'acceptation de l'hypothèse de gain. La prochaine mesure structurante est une double construction sur la voie de production puis, quand disponible, deux tests d'archive sur le corpus canonique. Ne pas confondre un succès de CI avec la mesure du concours.
