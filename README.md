# PegineLab WifCam Helper · T23N Camera-Head Firmware + Test Bench

**EN:** Local-first testing of the real Galayou G2 / Ingenic T23N camera, used alone or as Hombo3's robot head. **RU:** Автономный стенд проверки камеры, микрофона, динамика, RTSP и задержек. No cloud, no remote dependency, no uncontrolled flashing.

## Отдельная прошивка WifCam Helper (T23N / SD)

Открой в YadroKreator **WifCam Helper** (третья сборочная линия, рядом с WIFICAM и Irila). Кнопка **«Создать прошивку Helper»** фиксирует два SHA: `musikfed/wifcam_helper/main` и `musikfed/wificam_T23N/mymarrchWFcam`, добавляет `firmware/overlay` в изолированный исходник WIFICAM и запускает настоящий Thingino/Buildroot SD-билдер с `PUBLISH=0`. Выходной IMG, лог, проверка и удаление находятся внутри этой вкладки — отдельно от WIFICAM 0.1_test. См. [инструкцию прошивки](firmware/README_RU.md) и [схему проекта](peginelab.project.json).

На камере: `/etc/wifcam-helper-release`, `S92wifcam-helper`, `wifcam-helper-probe`, `/cgi-bin/helper-capabilities`. Доступность команд rad/rac/rvd — **не** гарантия физической работы микрофона, динамика и SC2336. CV/STT/LLM/TTS и визуальная память выполняются на CORE, не на 64 МБ ОЗУ T23N. Голосовой диалог и маршрутизация аудио/видео требуют отдельной аппаратной и интеграционной проверки после первой прошивки.

## Диагностический стенд на CORE (Python)

## Quick start · Ubuntu 24.04 / Python 3.12 / uv 0.12
```sh
sudo apt-get install -y ffmpeg openssh-client
cd /1tbdisk/PegineLab/projects
git clone https://github.com/musikfed/wifcam_helper.git
cd wifcam_helper
uv run --no-project python3 -m wifcam_helper web
# Then open http://127.0.0.1:8765 on the server (or ssh tunnel).
```
`uv` is optional. The CLI/test bench uses Python standard library; optional ML classifiers, Whisper and GPU services are external, never part of firmware. Run `python3 -m wifcam_helper --help`.

**No remote administrative action occurs just from opening the UI.** Diagnostics are read-only except an explicit short, low-amplitude speaker test, requiring a separate consent flag. Camera speaker and microphone must pass **physical tests**. `ffprobe` detects an audio track but does not prove sound from the microphone. Time to first decoded frame is **not** glass-to-glass latency.

## Safe standalone structure
- `wifcam_helper/bench.py`: SSH inventory, RTSP probes, mic capture analysis (no audio saved), supervised speaker PCM test, recommendations / JSON results.
- `wifcam_helper/web.py`: localhost-only dashboard with seven complete menu translations.
- `locales/*.json`: RU, EN, BE, SAH, DE, FR, ZH-CN.
- `wiki/*.md`: ready-to-publish GitHub Wiki source in all seven languages.
- `scripts/publish-wiki.sh`: explicit opt-in Git wiki git-push after the initial wiki page has been enabled.
- `profiles/t23n_lean.json`: **allowlisted, conservative build profile**, staged for YadroKreator (does not modify the kernel).
- `tests/`: hardware-free CI exercises for security, UTF-8 locale completeness and recommendation schema.

## Comparison, real latency and optional AI
```sh
# Compare up to two existing RTSP streams across TCP and UDP:
python3 -m wifcam_helper compare --rtsp-url rtsp://CAMERA_IP:554/ch0 --alt-rtsp-url rtsp://CAMERA_IP:554/ch1
# Only after physically measuring day/night/motion scenes and filling the CSV:
python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv
# Optional LOCAL object classifier, on CORE (not on the camera):
python3 -m wifcam_helper classification --rtsp-url rtsp://CAMERA_IP:554/ch0 --model /trusted/models/yolo11n.pt --device cpu --vision-consent
```

- **Decode throughput is not glass-to-glass latency.** Use a separate high-speed phone recording both a direct LED/clock and the delayed Hombo3 display; record real measurements in `profiles/quality_evaluation_template.csv`.
- The quality scorer considers daylight, night and motion quality together. If measurements are absent it returns **no recommendation**, not imaginary FPS/latency numbers.
- Optional Ultralytics/YOLO needs a user-supplied and **trusted local** model file, and explicit consent to analyze one frame. No automatic model downloads, stored video or always-on GPU jobs. PyTorch `.pt` weights can execute code during loading: never use untrusted files.
- Available device choices are `cpu` and `cuda:0` if the RTX 3060 is actually powered/available; the helper never toggles GPU power.
- Instructions: [Physical latency and image quality RU](docs/PHYSICAL_LATENCY_AND_QUALITY_RU.md) · [EN](docs/PHYSICAL_LATENCY_AND_QUALITY_EN.md).

## YadroKreator integration

**Firmware lane:** Helper owns independent `t23n_helper_sd` Buildroot image, own jobs, SHA pins, preflight, log and artifact store. Rootfs includes allowlisted camera-side shell/CGI overlay; no host Python in the camera rootfs. Normal WIFICAM stays a separate standard firmware.

**Optional legacy host-side preset:** `profiles/t23n_lean.json` is kept for compatibility, but it does not replace the dedicated camera-head firmware. New builds should use the separate Helper tab, not a WIFICAM checkbox.

`scripts/check-factory-integration.sh` is a read-only compatibility audit; it does not compile or flash.

## Independent Helper service & SQLite history / Отдельная служба и БД

**RU:** Python-стенд Helper — часть проекта, но не прошивка. Диагностика стенда сохраняется в своей SQLite `~/.local/state/wifcam-helper/history.sqlite3`, включая однократный импорт старого `last-report.json`. База фабрики `factory-state/factory.sqlite3` **не используется**. В «Отчётах» доступна история последних 20 запусков, на `/api/history-summary` — общее количество. Порт Helper — только `127.0.0.1:8765`.

После обновления собственного Git checkout на Ubuntu CORE можно зарегистрировать **только его** пользовательскую службу:

```bash
cd /1tbdisk/PegineLab/projects/wifcam_helper
bash scripts/install-user-service.sh --start
bash scripts/helper-service.sh status
# Только Helper:
bash scripts/helper-service.sh restart
bash scripts/helper-service.sh stop
```

С Acer Windows доступ через SSH-туннель `ssh -N -L 8765:127.0.0.1:8765 user@192.168.0.100` и браузер `http://127.0.0.1:8765`. Не публикуй порт наружу. Никаких контейнеров, ключей Wi-Fi, GPU, прошивок или сервисов ACHEWIW установка не трогает. YadroKreator показывает состояние этого сервиса во вложенном блоке **«Аппаратный испытательный стенд»** внутри сборочной вкладки Helper.

**EN:** All diagnostic reports now persist in a private Helper-only SQLite DB and remain separate from factory build history. Existing legacy last-report JSON is preserved. A dedicated loopback-only user systemd unit can be installed explicitly; its lifecycle is independent of the firmware builder and all other containers.

## Camera tools
The pinned Thingino Raptor includes `rad` (mic/audio), `rac` (speaker playback), and `microphone`, `speaker`, `play` wrappers; WIFICAM build requires them in SD rootfs. On the real camera you must verify physical audio, audio input routing/amp GPIO, mic acoustics, and amplifier, then measure the actual latency.

## Boundaries
Repo roles: `wifcam_helper` for **the distinct camera-head firmware overlay and physical testing**; `wificam_T23N` for the pinned generic camera firmware base; `YadroKreator` for reproducible per-project SD jobs; `Hombo3_3.0.0` for off-device STT/LLM/TTS/robot. Tests **never** flash SD, restart Thingino, or run a 32-thread build. GPU (RTX 3060 12GB) is for optional offline CV/STT/TTS on the CORE host, not the camera.

Private camera credentials, Wi-Fi keys, SSH keys, certificates (`fullchain.pem`, `privkey.pem`) and reports belong **outside Git**. Web UI binds only to `127.0.0.1`; remote access through SSH tunnel or independently configured authenticated reverse proxy. Do not move TLS private keys into this project.

Instructions: [Русский](wiki/Guide-RU.md) · [English](wiki/Guide-EN.md) · [Беларуская](wiki/Guide-BE.md) · [Саха тыла](wiki/Guide-SAH.md) · [Deutsch](wiki/Guide-DE.md) · [Français](wiki/Guide-FR.md) · [中文](wiki/Guide-ZH-CN.md)

© PegineLab. All external tools and firmware retain their own respective licenses.


## Project showcase · Презентация · 11 languages

[**Visual workflow, international descriptions and contacts**](docs/showcase/README.md)

