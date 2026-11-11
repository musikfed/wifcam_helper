# Lenya · Deux méthodes (FR)

**Vérifié :** image microSD minimale T23N, Raptor, interface caméra :8090 et station Acer v2.2. Le serveur Brain sur CORE, RAG et l'identification faciale/vocale sont encore à développer.

**A — IMG :** conserver T23N_Lenya_WORKING.zip en privé ; vérifier avec python scripts/lenya-image.py T23N_Lenya_WORKING.zip. Écrire le fichier IMG sur la bonne carte microSD avec un outil d'image disque. Le script ne modifie jamais les disques physiques.

**B — SD active :** extraire localement peginelab.zip. PowerShell scripts/lenya-deploy-camera.ps1 -PackageRoot F:\peginelab est une vérification ; -Apply effectue la copie via SSH et scp -O, avec sauvegarde. Acer : scripts/lenya-install-acer.ps1 -PackageRoot F:\peginelab -Apply. Ne pas publier les mots de passe, clés ni images privées.
