# Lenya: image or live-script deployment (EN)

**Working:** T23N minimal SD image, Raptor, camera UI :8090, Acer Station v2.2 with proxy :11435, Whisper/Piper :11436 and local dashboard :11437. CORE Brain Server, RAG, graph, face/voice recognition and PTZ tracking are **planned**, not installed.

**A — IMG:** Keep T23N_Lenya_WORKING.zip private. Verify with python scripts/lenya-image.py T23N_Lenya_WORKING.zip. Its IMG has MBR, FAT16 and ext partitions, total 84,934,656 bytes. Flash to a carefully selected microSD using a dedicated imaging application, then test physical boot. To compact a new full dump: python scripts/lenya-image.py full-card.img --compact-to NEXT.img. The script never writes physical disks.

**B — running SD:** Extract peginelab.zip locally. PowerShell scripts/lenya-deploy-camera.ps1 -PackageRoot F:\peginelab performs a dry-run; add -Apply to copy the overlay via SSH / scp -O with a camera-side backup. Install the Acer sources with scripts/lenya-install-acer.ps1 -PackageRoot F:\peginelab -Apply and run the existing station. No passwords or personal SD images go into GitHub.
