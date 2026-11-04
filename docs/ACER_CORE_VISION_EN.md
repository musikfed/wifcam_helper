# Acer CPU object detection and opt-in Ollama vision on CORE

## Roles

Camera (Galayou G2 / T23N) supplies RTSP video; physical RAD microphone and RAC speaker testing is required. Acer Swift 3 (Windows 11 Pro, Ryzen 5 3500U, 20 GB RAM, Vega 8) runs YOLO nano on CPU, not CUDA. Huananzhi CORE (Ubuntu 24.04, RTX 3060 12 GB) runs the pre-installed qwen2.5vl:7b or granite3.2-vision:2b in Ollama on demand.

## Windows PowerShell setup

Install trusted FFmpeg and verify ffmpeg -version, then:

    git clone https://github.com/musikfed/wifcam_helper.git
    cd wifcam_helper
    uv venv --python 3.12 .venv
    uv pip install --python .venv\Scripts\python.exe ultralytics pillow
    .\.venv\Scripts\python.exe -m wifcam_helper observe --rtsp-url "rtsp://CAMERA_IP:554/ch0" --model "C:\models\yolo11n.pt" --device cpu --samples 3 --vision-consent
    .\.venv\Scripts\python.exe -m wifcam_helper web

Obtain locally trusted YOLO weights yourself before running. The helper never downloads model files. Untrusted .pt weights can execute code. Compatible .onnx weights require an appropriate runtime. Web interface: http://127.0.0.1:8765, Video tab.

## One private CORE visual question

Keep Ollama bound to its server loopback and open a separate Windows PowerShell tunnel:

    ssh -N -L 11434:127.0.0.1:11434 user@192.168.0.100

In a second Acer terminal:

    .\.venv\Scripts\python.exe -m wifcam_helper observe --rtsp-url "rtsp://CAMERA_IP:554/ch0" --model "C:\models\yolo11n.pt" --samples 2 --device cpu --vision-consent --ollama-endpoint "http://127.0.0.1:11434" --ollama-model "qwen2.5vl:7b" --question "What objects can you see and count?" --ollama-consent

Only the final in-memory JPEG is transferred, exclusively with --ollama-consent, to a private IP address. No image is persisted. Avoid exposing Ollama on the Internet; HTTP is not encrypted, so prefer SSH or protected VPN.

Each RTSP sample is a real frame. visible_counts are per-frame YOLO boxes, current_visible is the last frame's count, and peak_visible is the maximum per class. These are not unique identities accumulated across time, not full tracking and not proof of accuracy. There is no continuous service or automatic learning.

CPU YOLO on Acer uses no CORE GPU memory. Ollama is invoked once with stream=false, keep_alive=0 and num_ctx=2048; it requests model unload after response. This does not control unrelated Ollama requests. Operators may consider OLLAMA_MAX_LOADED_MODELS=1 and OLLAMA_NUM_PARALLEL=1 plus a shared server scheduler, after checking other projects and ollama ps. Helper never toggles GPU power, restarts systemd services or flashes firmware.

Real microphone/speaker testing must precede Hombo3 VAD/STT → LLM → TTS → play/rac integration. Human-approved dataset collection and training will be separate future tasks.
