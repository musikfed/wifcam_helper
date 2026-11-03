# Deutsch · Vollständige Anleitung

Prüfstand für die autonome T23N-Kamera als Robotik-Kopf von Hombo3. Ziel sind messbare Videoeinstellungen sowie der physische Nachweis, dass internes Mikrofon und Lautsprecher funktionieren. Die Cloud ist optional.

## 1. Setup and tests

Zuerst per SSH rvd, rsd, rad, rac sowie microphone/speaker/play prüfen. Danach bestehende RTSP-Kanäle ch0/ch1 mit ffprobe analysieren und TCP/UDP vergleichen. Mikrofontests nur mit Zustimmung; ein leiser Lautsprechertest muss vor Ort gehört werden.


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

RTSP-Verbindungszeit und Dekodier-FPS sind keine echte Objektiv-zu-Bildschirm-Latenz. Messen Sie mit LED/Uhr und zweiter Kamera. Prüfen Sie Schärfe, Bewegung, Dunkelheit, Bitrate und WLAN. YOLO, STT und TTS können lokal auf CORE RTX 3060 laufen.

## 3. Local dashboard, Wiki and security

Dashboard nur auf `http://127.0.0.1:8765` oder SSH-Tunnel. GitHub Wiki: erste Home-Seite manuell erzeugen, Übersetzungen kontrollieren und danach `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`. TLS-Privatschlüssel nicht veröffentlichen.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**

## Echte Bildqualität, Klassifikation und zwei Kamerapositionen

Die Kamera ist entweder **Roboterkopf** von Hombo3 oder **unabhängige Beobachtungskamera**. Remote-Erkennungen dürfen ohne kalibrierte Extrinsik nicht als Roboterkoordinaten behandelt werden. Tag/Nacht/Bewegung messen, nur reale Werte in `profiles/quality_evaluation_template.csv` eintragen und `python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv` ausführen. Lokales YOLO läuft auf CORE, nicht auf T23N.
