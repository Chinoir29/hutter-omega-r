# OMÉGA-R v0.24 — archive exécutable de préfixe indépendante

**Périmètre :** construire une archive expérimentale qui restaure exactement **524 288 octets du flux Wikipédia prétraité** au moyen du vrai décodeur cmix, en démarrant **sans arguments dans un dossier vierge contenant seulement archive9**. Il ne s'agit ni d'une archive Hutter intégrale ni d'un score réglementaire.

## Preuve préalable v0.23

L'exécution GitHub #44967704622 s'est conclue par success. Le corpus enwik9 intégral a été authentifié (1 000 000 000 octets, SHA-256 159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc). Le flux complet pré-codeur compte 501 062 281 octets. Les 524 288 premiers octets ont été codés en 158 153 octets arithmétiques, puis décodés identiquement dans le même répertoire que le compresseur.

SHA-256 du préfixe source et restauré : 1d5b8c3b6448a8020084f64f5a75028b2ad42ce8434e7ac41979009f4c2932cf.

SHA-256 du flux arithmétique : 836a7f6eb3b439f3f682fe8c16252d5a10d44fcbabfdc053f0053ec217baa0d3.

## Construction et garde-fous

- prepare_selfextract.py : copie éphémère des sources épinglées de cmix-neif-2.0, commit 35d1957a5074db802fc134126afc77b76d931761. Le codeur et le décodeur arithmétiques demeurent intacts. La voie archive9 sans argument est adaptée au préfixe.
- assemble_prefix_archive.py : format binaire exactement conforme à ArchivKopf du concurrent : [stub décodeur][poids Transformer][flux arithmétique][longueur du flux int32][longueur des poids int32]. Tous les octets sont comptés.
- run_isolated.py : lance seulement ./archive9 dans un répertoire neuf où aucun corpus, poids ou autre fichier n'existe avant le démarrage. Il contrôle la sortie par longueur et SHA-256, conserve les mesures et les causes d'échec.
- test_selfcontained_prefix.py : contrôles adversariaux source, format de fichier et isolement d'exécution.

Préflight GitHub #44970270467 : succès, huit tests v0.24 et sept tests v0.23.
Expérience réelle GitHub #44970334096 : résultat à confirmer dans ses journaux, sans présumer de sa réussite.

**KEEP** uniquement si la restauration isolée réussit ; **RECONCEVOIR** sinon. Une restitution de préfixe prétraité ne constitue pas la restauration autonome des 1 000 000 000 octets de enwik9. Aucun S Hutter, aucune victoire, aucune soumission.

## Droit d'auteur et gouvernance

Les sources et exécutables modifiés restent sous GNU GPL-3.0-only (avec attribution, licence et notices originales conservées dans la copie éphémère). Le dépôt du projet ne republie ni sources complètes du concurrent, ni fichiers du corpus, ni poids, ni binaires tiers. Les artefacts GitHub Actions ne comprennent que les empreintes, tailles, mesures, informations de défaillance et protocoles. La constitution OMÉGA-R du dossier de reprise reste strictement inchangée.
