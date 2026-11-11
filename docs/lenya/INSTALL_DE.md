# Lenya · Zwei Wege (DE)

**Bestätigt:** minimales T23N-microSD-Abbild, Raptor, Kameraoberfläche :8090 und Acer Station v2.2. CORE Brain Server, RAG sowie Gesichts- und Stimmerkennung sind noch geplant.

**A — IMG:** T23N_Lenya_WORKING.zip privat aufbewahren; mit python scripts/lenya-image.py T23N_Lenya_WORKING.zip prüfen. Mit einem Disk-Imaging-Programm auf die korrekt ausgewählte microSD schreiben. Das Skript schreibt niemals auf physische Datenträger.

**B — laufende SD:** Lokales peginelab.zip entpacken. PowerShell scripts/lenya-deploy-camera.ps1 -PackageRoot F:\peginelab führt eine Prüfung aus; -Apply installiert über SSH und scp -O mit Backup. Acer: scripts/lenya-install-acer.ps1 -PackageRoot F:\peginelab -Apply. Keine Schlüssel, Passwörter oder Roh-Images öffentlich hochladen.
