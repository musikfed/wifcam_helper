# Русский · Полное руководство

Стенд исследует автономную Galayou G2 / T23N и её место как головы Hombo3. Цель: выбрать лучший по реальным измерениям видеотракт и доказать, что штатные микрофон и динамик работают физически. Никакого обязательного облака.

## 1. Setup and tests

Начинайте с SSH-инвентаризации: процессы rvd, rsd, rad, rac, команды speaker/microphone/play. Далее проверьте аудио- и видеодорожки RTSP через ffprobe. Сравните TCP и UDP на существующих ch0/ch1. Короткий тест микрофона потребует согласия, динамика — присутствия человека рядом. Наличие команд не подтверждает качество и громкость.


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

Время соединения и FPS декодирования **не являются** задержкой кадра от объектива до экрана. Измерьте настоящую задержку внешней камерой, снимайте LED/часы вместе с монитором. Сравнивайте освещение, движение, резкость, битрейт, шум и потерю кадров. Для STT/YOLO/TTS используйте CORE RTX 3060; для голоса обязательно штатное аудио T23N.

## 3. Local dashboard, Wiki and security

Откройте `http://127.0.0.1:8765` на CORE или используйте SSH-туннель `ssh -L 8765:127.0.0.1:8765 user@192.168.0.100`. В GitHub Wiki сначала создайте Home вручную; затем после проверки всех переводов `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`. `~/crt-cert/privkey.pem` не переносить в проект.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**

## Измеренное качество, классификация, две позиции камеры

Кадры с камеры могут поступать в Hombo3 как с **головы робота** или как с **независимой стационарной камеры**. Во втором случае не приписывайте обнаруженные объекты координатам робота без калибровки внешней позиции. Для минимальной задержки проверяйте day/night/motion и заполняйте `profiles/quality_evaluation_template.csv` только реальными значениями. Выполните `python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv`. Классификатор YOLO запускается отдельно на CORE, использует свою доверенную локальную модель и не заставляет T23N выполнять нейросеть.
