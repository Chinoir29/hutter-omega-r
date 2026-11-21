# Hutter OMÉGA-R v0.9.1 — auditeur du rapport enwik9

## Contenu

- `assess_hutter_report.py` : lit le JSON produit par `verified_enwik9_run_v6.py`, contrôle sa cohérence interne et classe son score contre deux seuils **historiques datés du 21 novembre 2026**.
- `test_assess_hutter_report.py` : dix tests unitaires contradictoires, uniquement avec rapports synthétiques ; aucun de ces nombres n'est un résultat Hutter.

## Exécuter les tests

```bash
python3 test_assess_hutter_report.py
```

## Analyser le résultat d'un benchmark complet

```bash
python3 assess_hutter_report.py rapport_enwik9.json --out rapport_audite.json
```

**Limites** : l'auditeur ne lit pas les octets du corpus ni de l'archive, ne vérifie pas les coûts CPU normalisés Geekbench ni les limites de disque, ne peut confirmer aucun travail d'un jury et ne prouve aucune victoire. La compétition impose une vérification externe complète.

## Provenance de l'expérience réelle

- [Prévol enwik8 réussi](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939582235)
- [Benchmark complet enwik9 : suivre ici](https://github.com/Chinoir29/hutter-omega-r/actions/runs/44939882921)
- [Compresseur amont cmix-neif-2.0](https://github.com/marwoelk/cmix-neif-2.0), GPL-3.0, **non copié** dans le projet.
