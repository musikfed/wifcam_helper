# 简体中文 · 完整说明

本地测试平台用于研究独立工作的 T23N 摄像头，也可以将其作为 Hombo3 机器人的头部。需要实际测量视频性能，并验证摄像头自带麦克风与扬声器确实可用。不强制使用云服务。

## 1. Setup and tests

先通过 SSH 检查 rvd、rsd、rad、rac 及 microphone/speaker/play 程序。然后用 ffprobe 检测实际存在的 RTSP ch0/ch1 流，比较 TCP 和 UDP。分析麦克风必须明确授权；扬声器测试需要操作员在现场听到短暂低音量提示音。


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

RTSP 建连时间和解码 FPS 不等于镜头到屏幕的端到端延迟。请使用 LED 或时钟与第二台摄像机进行真实测量，并比较清晰度、低光画质、运动、码率和 Wi-Fi 稳定性。YOLO/STT/TTS 可以运行在 CORE 的 RTX 3060 上。

## 3. Local dashboard, Wiki and security

本地页面：`http://127.0.0.1:8765`，或者通过 SSH 隧道访问。发布 GitHub Wiki 前先在网站创建 Home 页面，检查翻译后执行 `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`。不要提交 TLS 私钥。

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**

## 实测画质、分类以及两种摄像头位置

摄像头既可以安装为 Hombo3 的**机器人头部**，也可以作为**独立远程观察者**。未经外参标定，远程目标识别结果不能当作机器人本地坐标。请在白天、夜间、运动场景中实测，将真实数值写入 `profiles/quality_evaluation_template.csv`，运行 `python3 -m wifcam_helper quality-evaluate --csv /private/measurements.csv`。可选 YOLO 在 CORE 上运行，不在 T23N 上运行。
