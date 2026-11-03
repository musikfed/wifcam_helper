# PegineLab WifCam Helper · T23N Camera Test Bench

**EN:** Local-first testing of the real Galayou G2 / Ingenic T23N camera, used alone or as Hombo3's robot head. **RU:** Автономный стенд проверки камеры, микрофона, динамика, RTSP и задержек. No cloud, no remote dependency, no uncontrolled flashing.

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

## Camera tools
The pinned Thingino Raptor includes `rad` (mic/audio), `rac` (speaker playback), and `microphone`, `speaker`, `play` wrappers; WIFICAM build requires them in SD rootfs. On the real camera you must verify physical audio, audio input routing/amp GPIO, mic acoustics, and amplifier, then measure the actual latency.

## Boundaries
Repo roles: `wifcam_helper` for **testing only**; `wificam_T23N` for firmware and pinned source; `YadroKreator` for reproducible jobs; `Hombo3_3.0.0` for STT/LLM/TTS/robot. Tests **never** flash SD, restart Thingino, or run a 32-thread build. GPU (RTX 3060 12GB) is for optional offline CV/STT/TTS on the CORE host, not the camera.

Private camera credentials, Wi-Fi keys, SSH keys, certificates (`fullchain.pem`, `privkey.pem`) and reports belong **outside Git**. Web UI binds only to `127.0.0.1`; remote access through SSH tunnel or independently configured authenticated reverse proxy. Do not move TLS private keys into this project.

Instructions: [Русский](wiki/Guide-RU.md) · [English](wiki/Guide-EN.md) · [Беларуская](wiki/Guide-BE.md) · [Саха тыла](wiki/Guide-SAH.md) · [Deutsch](wiki/Guide-DE.md) · [Français](wiki/Guide-FR.md) · [中文](wiki/Guide-ZH-CN.md)

© PegineLab. All external tools and firmware retain their own respective licenses.
