# Acer Swift 3 + WifCam Helper + Ollama на CORE

## Разделение задач

* Камера Galayou G2 / T23N: захватывает реальное видео RTSP. Микрофон RAD и динамик RAC должны пройти физические тесты.
* Acer Swift 3 / Windows 11 Pro: Ryzen 5 3500U, 20 ГБ памяти, Vega 8. YOLO nano работает только на CPU ноутбука. Это не CUDA.
* Huananzhi CORE / Ubuntu 24.04: RTX 3060 12 ГБ, Ollama с установленными qwen2.5vl:7b или granite3.2-vision:2b. VLM получает только один кадр по отдельному запросу.
* Протокол между хостами: доверенная локальная сеть/VPN, предпочтительно SSH-туннель, без публикации Ollama в Интернет.

## Acer PowerShell: установка

Установить ffmpeg из доверенного источника и проверить команду ffmpeg -version. Python 3.12.9 и uv 0.11.15 подходят.

    git clone https://github.com/musikfed/wifcam_helper.git
    cd wifcam_helper
    uv venv --python 3.12 .venv
    uv pip install --python .venv\Scripts\python.exe ultralytics pillow
    .\.venv\Scripts\python.exe -m wifcam_helper --help

Получить и проверить доверенный локальный файл весов YOLO11n, например C:\models\yolo11n.pt (или совместимый ONNX с соответствующим runtime). Helper сам модели не скачивает. Не открывать случайные .pt файлы: PyTorch может выполнять код во время загрузки.

Команда локального подсчёта (подставить фактический IP и RTSP-путь камеры):

    .\.venv\Scripts\python.exe -m wifcam_helper observe --rtsp-url "rtsp://192.168.1.55:554/ch0" --model "C:\models\yolo11n.pt" --samples 3 --device cpu --vision-consent

Веб-интерфейс на Acer:

    .\.venv\Scripts\python.exe -m wifcam_helper web

Открыть http://127.0.0.1:8765 → Видео → «Посчитать объекты на реальных кадрах».

## Разговор с Ollama на CORE

Сервер Ollama лучше оставить на 127.0.0.1:11434, на Acer PowerShell открыть отдельный SSH-туннель до CORE:

    ssh -N -L 11434:127.0.0.1:11434 user@192.168.0.100

Точный адрес CORE должен работать через VPN; SSH не включает видеокарту. Затем в другом окне Acer:

    .\.venv\Scripts\python.exe -m wifcam_helper observe --rtsp-url "rtsp://192.168.1.55:554/ch0" --model "C:\models\yolo11n.pt" --device cpu --samples 2 --vision-consent --ollama-endpoint "http://127.0.0.1:11434" --ollama-model "qwen2.5vl:7b" --question "Что я показываю и сколько предметов?" --ollama-consent

Последний JPEG отправляется на собственный CORE только при отдельном согласии --ollama-consent. Образ на диск не сохраняется. Ответ VLM и YOLO-счёт выведены раздельно и могут не совпасть. Обычный HTTP не шифрует трафик — используйте SSH-туннель или защищённый VPN.

## Что именно считает и сколько занимает VRAM

Тест читает 1–5 реальных кадров, на каждом выполняет YOLO предсказание и возвращает список рамок, классы и confidence. current_visible — по последнему кадру, peak_visible — максимальный счёт по выбранным кадрам. **Числа НЕ суммируются по кадрам:** это не уникальные предметы за всё время наблюдения и не непрерывный трекер. Точность проверяется на реальных предметах.

YOLO на Acer использует device=cpu и не занимает RTX VRAM. Ollama вызывается лишь один раз, с keep_alive=0 и num_ctx=2048. keep_alive=0 запрашивает выгрузку после ответа, но НЕ гарантирует отсутствие других процессов на видеокарте. Для общего сервера можно отдельно и с учётом других проектов задать OLLAMA_MAX_LOADED_MODELS=1 и OLLAMA_NUM_PARALLEL=1 и общую очередь запросов; проверить ollama ps. Helper ничего не меняет в systemd, не подаёт питание на GPU, не запускает бесконечный агент.

После подтверждения аудиоканалов Hombo3 сможет делать VAD/STT → понимание сцены/LLM → TTS → проверенный вывод через play/rac. Обучение новому предмету потребует отдельного датасета с метками, подтверждёнными человеком, обучения и проверки. В текущем Helper автоматического обучения нет.

Тесты не прошивают SD, не меняют конфигурацию камеры и не сохраняют изображения.
