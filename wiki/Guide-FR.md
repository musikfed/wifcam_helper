# Français · Guide complet

Le banc d'essai examine la caméra T23N autonome comme tête du robot Hombo3. Il faut mesurer le flux vidéo et prouver physiquement le bon fonctionnement du microphone et du haut-parleur intégrés. Aucun cloud obligatoire.

## 1. Setup and tests

Vérifier d'abord les processus rvd, rsd, rad, rac et les commandes microphone/speaker/play par SSH. Analyser les véritables flux RTSP ch0/ch1 avec ffprobe ; comparer TCP et UDP. Le micro requiert un consentement explicite et le son du haut-parleur doit être entendu à proximité.


### CLI (Ubuntu 24.04 / Python 3.12 / uv)

```bash
sudo apt-get install -y ffmpeg openssh-client
cd /1tbdisk/PegineLab/projects/wifcam_helper
bash scripts/verify-host.sh
uv run --no-project python3 -m wifcam_helper web
# Open http://127.0.0.1:8765 on CORE, or SSH forward from laptop.
python3 -m wifcam_helper inventory --host CAMERA_IP
python3 -m wifcam_helper probe --rtsp-url rtsp://CAMERA_IP:554/ch0
python3 -m wifcam_helper video --rtsp-url rtsp://CAMERA_IP:554/ch0 --transport tcp
python3 -m wifcam_helper microphone --rtsp-url rtsp://CAMERA_IP:554/ch0 --mic-consent
python3 -m wifcam_helper speaker --host CAMERA_IP --speaker-consent
python3 -m wifcam_helper export-preset
```

Use only a verified camera IP and real ch0/ch1 RTSP URL. The microphone test holds PCM in RAM only; the speaker test emits a quiet 0.2-second tone with explicit consent. Never publish Wi-Fi passwords, SSH keys or TLS private keys in Git. Neither test flashes SD, modifies the kernel nor restarts Raptor.


## 2. Video latency and local vision

Le temps de connexion RTSP et les FPS de décodage ne représentent pas la latence objectif-écran. La mesurer avec une LED ou une horloge et une autre caméra. Comparer mouvement, éclairage, débit, détails et stabilité Wi-Fi. YOLO/STT/TTS peuvent fonctionner localement sur CORE RTX 3060.

## 3. Local dashboard, Wiki and security

Le panneau est local : `http://127.0.0.1:8765`, ou tunnel SSH. Pour GitHub Wiki : créer Home dans le site, relire les traductions, exécuter `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`. Ne publier aucune clé TLS privée.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**

## Qualité mesurée, classification et deux positions de caméra

La caméra sert de **tête montée du robot** Hombo3 ou d'**observateur distant indépendant**. Sans calibration de pose, ses détections ne sont pas des coordonnées du robot. Mesurer jour/nuit/mouvement, compléter `profiles/quality_evaluation_template.csv` avec de vraies valeurs, puis lancer `python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv`. Le YOLO optionnel fonctionne sur CORE, pas sur T23N.
