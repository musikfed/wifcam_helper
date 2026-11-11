# Lenya · verified checkpoint and next steps

**English · 2026-11-11 · Lenya v2.2**

## Verified
Physical Ingenic T23N camera booting from microSD, Raptor audio/video, camera web UI :8090 and Acer Lenya Station v2.2 (Ollama proxy :11435, Whisper/Piper :11436, dashboard :11437). Spoken replies were observed with HTTP 200 and PCM output. The private reference image `T23N_Lenya_WORKING.img` is **84,934,656 bytes (81 MiB)**. Two deployment paths are documented in [INSTALL_EN.md](INSTALL_EN.md). Do not publish raw SD images or credentials.

## Critical T23N SD boot offsets
The stock SPI NOR was removed; boot is from microSD. Known **partition** boundaries: MBR; FAT16 type 0x0e at **LBA 2048**, 16 MiB; Linux/ext type 0x83 at **LBA 34816**, 64 MiB. These are **NOT validated MSPL/SPL/U-Boot/kernel offsets**. Preserve all boot bytes before LBA 2048 and the MBR byte for byte from the working image; never blindly repartition or move the loader. The IMG checker only validates partition structure, not actual boot. Confirm the boot component map and test on physical hardware before flashing a new candidate.

## Not yet completed
Reviewed Acer and camera source migration from private `peginelab.zip` into Git `main`, CORE containerized Brain Server (RAG, knowledge graph, planner, scenarios, Ollama tools), face/voice identification, guided quality-gated enrollment, PTZ tracking, animated ginger cat, TTS emoji filtering and three-node telemetry remain pending until individually verified. Seven obsolete branches still exist; two have open PRs; do not delete before reviewing unique changes.

## Next work
Preserve and hash the private reference IMG; safely migrate reviewed sources without secrets; validate the T23 boot-component placement; implement Brain API + PostgreSQL/pgvector on CORE while leaving Ollama on its host; connect Acer perception, speech and PTZ; add T23N/Acer/CORE telemetry; implement verified face/voice enrollment and cat avatar; review old branches and open PRs before cleanup. Never interrupt the currently working camera or voice services for documentation work.

## Languages
Technical UI/docs currently cover **RU, EN, BE, SAH, DE, FR, ZH-CN** (7 languages). Translate every new UI element, error, scenario and setting into all seven and validate completeness in CI. An 11-language project showcase is a separate surface, not evidence of 11 fully localized interfaces.
