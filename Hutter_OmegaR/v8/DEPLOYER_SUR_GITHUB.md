# Comment exécuter le prévol officiel depuis GitHub

1. Ouvrir https://github.com/new et créer **un nouveau dépôt dédié**, de préférence nommé `hutter-omega-r`, sans fichier README initial et sans branche existante. Choisir `Public` ou `Private` en connaissance de cause : dépôt public = code accessible ; dépôt privé = consommation de minutes et éventuels coûts selon le compte.
2. Décompresser `Hutter_OmegaR_v0.8_github_ready.zip`. Placer le terminal dans le dossier extrait, à la racine qui contient `README.md`, `Hutter_OmegaR/` et `.github/`.
3. Sur macOS ou Linux :

   ```sh
   git init -b main
   git add .
   git commit -m "Hutter OMÉGA-R v0.8: benchmark preflight"
   git remote add origin https://github.com/VOTRE_COMPTE/hutter-omega-r.git
   git push -u origin main
   ```

   **Remplacer `VOTRE_COMPTE` par le véritable identifiant GitHub.** La connexion à GitHub pourra demander une authentification dans le navigateur. Ne pas transmettre ses mots de passe ou jetons à l'assistant.
4. Dans GitHub : onglet **Actions** → workflow **Hutter OMÉGA-R v0.8 — prévol enwik8 et essai complet enwik9** → **Run workflow** → `phase = preflight` → **Run workflow**.
5. Lire l'artefact `omr8-enwik8-preflight` : les trois JSON doivent indiquer `enwik8_whole_file_verified=true`, `lossless_roundtrip_verified=true`, `hutter_prize_score=null`.
6. Uniquement si ce prévol fonctionne, relancer le workflow avec `phase = full`. Si ce job aboutit, lire l'artefact `omr8-enwik9-local-full`, le champ `score_bytes_LOCAL_only`, les temps et la mémoire. Aucun envoi au jury n'est prévu.

Le workflow a été validé syntaxiquement et testé hors ligne, **pas encore lancé sur GitHub ni sur le corpus officiel**.

**Avertissement :** les GitHub-hosted runners standard sont plafonnés à 6 heures par job ; le test complet est limité à 5 h 30, au maximum 2,5 h par phase de compression ou décompression. Un timeout ne prouve rien quant au score final. Les données officielles ne figurent pas dans le dépôt ni dans les artefacts.