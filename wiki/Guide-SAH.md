# Саха тыла · Толору инструкция

T23N камераны бэйэтэ үлэлиир IP-камера уонна Hombo3 робот төбөтө быһыытынан тургутуу. Сүрүн сорук — видео кэтэһиитин өлчөө, камера бэйэтин микрофона уонна динамига чахчы үлэлииллэрин тургутуу. Cloud наадата суох.

## 1. Setup and tests

SSH көмөтүнэн rvd, rsd, rad, rac процесстары уонна microphone, speaker, play утилиталарын көр. Онтон баар RTSP ch0/ch1 ағымын ffprobe-нан тургут, TCP уонна UDP тэҥнээ. Микрофон тыаһын хомуйуу туһанааччы сөбүлэһиитин эрэ кытта. Динамик кыра тыаһын камера кытыытыгар истэн бигэргэт.


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

RTSP холбонуута уонна FPS объективтан экранҥа кэтэһиини толору көрдөрбөт. LED эбэтэр чаас уонна атын камера көмөтүнэн өлчөө. Качество, сырдык, хамсааһын, Wi-Fi туруғун тэҥнээ. YOLO/STT/TTS CORE RTX 3060-ҥа үлэлиэхтэрин сөп.

## 3. Local dashboard, Wiki and security

Панель `http://127.0.0.1:8765`, атын сиртэн SSH-туннель. Wiki-га бастакы Home GitHub-ка оҥор; Markdown тургутан кэннэ `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh` сал. Приватнай ключтар Git-кэ суруллубат.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**

## Видео качество, классификация уонна камера икки уруктааһына

Камера Hombo3 **робот төбөтө** эбэтэр **атынан байыы камера** буолуон сөп. Атын камера координататын робот координататыгар калибровка суох кыайбат. Day/night/motion тургутууну `profiles/quality_evaluation_template.csv`-га чахчы өлчөмнөрүнэн толор уонна `python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv` сал. YOLO классификатор CORE-га үлэлиир, T23N-ҥа суох.
