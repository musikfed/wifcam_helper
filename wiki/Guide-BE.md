# Беларуская · Поўнае кіраўніцтва

Стэнд правярае аўтаномную T23N-камеру і выкарыстанне як галавы Hombo3. Патрэбныя сапраўдныя вынікі для відэа і фізічная праверка ўбудаванага мікрафона ды дынаміка. Воблака не абавязковае.

## 1. Setup and tests

Праверце праз SSH працэсы rvd, rsd, rad, rac, праграмы microphone, speaker, play. Далей выкарыстайце ffprobe для існага RTSP ch0/ch1, параўнайце TCP і UDP. Кароткі аналіз мікрафона толькі пасля згоды, гук дынаміка — у прысутнасці аператара.


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

Час адкрыцця RTSP і FPS не роўныя затрымцы ад аб'ектыва да экрана. Вымерайце яе з дапамогай святлодыёда ці гадзінніка і другой камеры. Параўнайце рух, святло, якасць, бітрэйт і Wi-Fi. YOLO/STT/TTS можна запускаць на CORE RTX 3060.

## 3. Local dashboard, Wiki and security

Панэль адкрываецца на `http://127.0.0.1:8765` або праз SSH-тунэль. Для Wiki спачатку стварыце Home на GitHub, праверце пераклады і запусціце `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`. Сакрэтныя ключы нельга публікаваць.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**
