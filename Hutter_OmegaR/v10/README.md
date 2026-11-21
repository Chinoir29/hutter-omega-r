# Hutter OMÉGA-R v0.10 — hypothèse rejetée (contextes supplémentaires)

**Résultat : aucune amélioration démontrée.** L'architecture d'essai conserve la base v0.6 et ajoute deux contextes : dernières lettres normalisées en minuscules et chiffres regroupés, puis historique de mots normalisé. Les deux branches sont déterministes, et le décompresseur est autonome.

## Reproduire

```bash
bash build.sh
python3 compare.py --out comparison_reproduced.json
python3 compare.py --file /path/to/your_input.xml --out your_results.json
```

Les bibliothèques de développement Linux et `g++` C++17 sont nécessaires. En plus des jeux intégrés, des essais locaux ont utilisé le code source de bibliothèques tierces installées dans l'environnement; ces fichiers tiers ne sont **pas redistribués**. Les tailles exactes et les empreintes des jeux sont conservées dans `local_results_v10.json`. Sur toutes les entrées testées, la variante 1 a été moins performante que la variante 0 en taille totale `(programme + archive)`.

| Jeu de données (local) | Contrôle v0.6 | Contextes supplémentaires | Différence |
|---|---:|---:|---:|
| Pandas `frame.py` (447 104 o) | 168 068 | 184 153 | +16 085 |
| Pandas `generic.py` (474 370 o) | 166 106 | 182 122 | +16 016 |
| NumPy `numeric.py` | 93 385 | 109 689 | +16 304 |
| XML synthétique 1,25 Mo | 213 756 | 228 376 | +14 620 |
| Fichier vide | 70 417 | 86 801 | +16 384 |
| Aléatoire 256 Kio | 332 873 | 349 257 | +16 384 |
| Répétition simple | 70 771 | 87 155 | +16 384 |

- `comp9_variant0`: 35 192 octets; `comp9_variant1`: 43 384 octets.
- *Différence de score* inclut l'exécutable de **chaque** mode et son archive.
- Le modèle additionnel est prédit uniquement des octets déjà décodés ; pas de fichier auxiliaire ni de dépendance réseau.
- Toutes les archives ont restitué le fichier initial exactement.
- Aucun benchmark sur `enwik9`, aucune conformité au jury et aucune nouveauté mondiale ne sont établis par cet essai.

**Décision :** rejet de l'hypothèse et non-intégration à la version de référence. L'expérimentation constitue un résultat négatif utile au titre de l'article 13 de la Constitution OMÉGA-R.
