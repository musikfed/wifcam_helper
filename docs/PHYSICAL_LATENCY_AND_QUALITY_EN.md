# T23N physical latency & image quality field protocol

`ffprobe` reports stream metadata and `video` measures host decode throughput/startup, **not lens-to-display latency**. For real glass-to-glass timing, film an LED/clock and the Hombo3 monitor in one 120/240 fps smartphone shot. Measure the same event's delay across multiple samples; compare *day*, *night* and *motion* scenes under controlled lighting and Wi-Fi. Assign manual image-quality scores 1–5 and actual dropout percentages (never invent values).

Fill a private copy of `profiles/quality_evaluation_template.csv` and run `python3 -m wifcam_helper quality-evaluate --csv /path/to/measurements.csv`. Recommendations require all three scenes, minimum average quality 3/5 and max dropout 3%. The helper never changes camera settings, kernel or SD.

For already validated URLs, compare RTSP transports with `python3 -m wifcam_helper compare --rtsp-url rtsp://CAMERA_IP:554/ch0 --alt-rtsp-url rtsp://CAMERA_IP:554/ch1`. Never assume ch1 exists.

An optional single-frame local YOLO test on CORE is `python3 -m wifcam_helper classification --rtsp-url rtsp://CAMERA_IP:554/ch0 --model /trusted/models/yolo11n.pt --device cpu --vision-consent`. It only works when **operator-supplied trusted local** weights and optional ultralytics are installed; nothing is downloaded. `--device cuda:0` may be used if the RTX 3060 is online, without automatic power control. PyTorch weights must be trusted.

A passing CI job means code/tests passed, not that native mic, speaker, physical latency or image quality passed. Keep SSH recovery and the SD reference.
