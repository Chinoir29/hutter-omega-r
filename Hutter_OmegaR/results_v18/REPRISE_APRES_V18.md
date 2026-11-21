# OMÉGA-R — reprise opérationnelle après v0.18 (21 novembre 2026)

## Périmètre et constitution

Le projet a été repris à partir de l'archive HUTTER_OMEGA_R_REPRISE_AUTONOME_v0.17(1).zip, sans supposer exactes les données historiques. 203/203 empreintes de son MANIFESTE_SHA256.txt vérifiées. Constitution originale INTACTE : SHA-256 b56b689584c01943aca8127b7f0b09745a5abe6fd17c2b9e6d27c1cca8453e9f.

Dépôt : Chinoir29/hutter-omega-r ; branche de travail non fusionnée research/omr18-production-preflight ; main au début de session 3b525be7f5dc5ba7800df793cf78138ea2644761.

## État et preuve

- Antérieur : v0.11 S intégral **annoncé dans les artefacts antérieurs** 282 550 351 B ; non reproduit sur enwik9 pendant cette session.
- Antérieur : v0.17 six restitutions laboratoire sur trois fenêtres authentifiées ; 72 B de gain de flux face au témoin 990 pour 999 ; **aucune archive9 officielle**.
- Local : 33/33 tests v0.17 ; 7/7 tests contradictoires v0.18 ; 8 restitutions v0.11 sur témoins synthétiques, aucune différence de taille entre les quatre modes pour chaque entrée.
- Réel amont : workflow GitHub #44956009000, succès au commit 846db4cd0b3f8dfc678095427a01c0e53ecce779 : checkout GPL-3.0 cmix-neif-2.0 au commit 35d1957a5074db802fc134126afc77b76d931761, empreintes source exactes, chemin compresseur/décompresseur/dictionnaire confirmé, arbres A/B séparés.
- Réel corpus de 1 Go : workflow #44956405083, succès au commit f9ed680fca3608ac4c5651aef47e67238456a586 : SHA-256 canonique enwik9 authentifié, dict_derive C++ compilé puis exécuté sur ce vrai fichier, dictionnaire dérivé 520 804 B et identique à la référence, SHA-256 0ab9f2d2733003577b53b206791f382fd31b91eff9975041b2173bb5585c5535. Aucun octet du corpus, dictionnaire ni poids redistribué.
- Construction du couple de comp9 de production : workflow #44956092485, en cours au dernier contrôle ; ne pas présumer du résultat.

## Source, licence et décisions

Source en propre : Hutter_OmegaR/v18/production_ab.py ; test_production_ab.py ; README.md. Les codes GPL-3.0 de marwoelk ne sont PAS recopiés dans le dépôt projet, mais clonés au moment des validations dans leur révision figée.

E178 est **levé pour la dérivation du dictionnaire sur enwik9 intégral** ; ce résultat ne prouve pas la chaîne de compression/décompression.

Verdict : **KEEP** contrat source et sous-composant dictionnaire, **HOLD** hypothèse de gain 999 et score admissible. Résultat de mission R2 pour le sous-problème du dictionnaire, R3 pour le nouvel instrument d'intégration au sens de la constitution (pas de revendication de nouveauté mondiale). Aucune solution R4/R5/R6 au prix n'est établie.

## Action suivante, concrète

1. Lire et archiver le rapport du build #44956092485 ; comparer exactement tailles et SHA-256 des deux comp9, à environnement identique. En cas d'échec, corriger la cause source/outillage sans répéter une stratégie inchangée.
2. Si les deux comp9 sont construits, exécuter les deux chaînes `comp9 → archive9 → enwik9_uncompressed` sur le seul enwik9 canonique, décodeur autonome en répertoire neuf et SHA-256 obligatoire ; inclure tailles de TOUS les composants, mesures CPU/RAM/disque, et limites de temps normalisé avant de prétendre à un résultat admissible.
3. En parallèle, ouvrir une voie algorithmiquement distincte du seul seuil SEMCACHE : extension **strictement réversible** du traitement des résidus des modèles de pages census et de leurs métadonnées, sans corpus externe au décodeur. N'adopter qu'après réduction mesurée du score S complet par rapport au témoin.
4. Ne pas soumettre au jury, engager de dépense, diffuser corpus ou poids, ni annoncer de première place sans autorisation et validation officielle.
