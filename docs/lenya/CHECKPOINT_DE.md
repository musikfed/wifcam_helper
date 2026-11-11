# Lenya · gesicherter Entwicklungsstand

**Deutsch · 2026-11-11 · Lenya v2.2**

## Bestätigt
Die Ingenic-T23N-Kamera startet von microSD; Raptor, Kamera-UI :8090 und Acer Lenya Station v2.2 (Ollama-Proxy :11435, Whisper/Piper :11436, Steuerung :11437) wurden praktisch getestet. Gesprochene Antworten mit HTTP 200/PCM wurden bestätigt. Das private Referenz-IMG ist 81 MiB groß. Installationswege: [INSTALL_DE.md](INSTALL_DE.md).

## Kritisch: T23N-Boot-Offsets
SPI NOR ist entfernt; Start von microSD. **Bekannte Partitionsgrenzen:** MBR, FAT16 ab **LBA 2048** (16 MiB), Linux/ext ab **LBA 34816** (64 MiB). Die genauen **MSPL/SPL/U-Boot-/Kernel-Offets sind nicht verifiziert**. MBR und den Bootbereich vor LBA 2048 bytegenau aus dem funktionierenden IMG bewahren. Partitionen und Bootloader nicht blind verschieben. Die IMG-Strukturprüfung beweist keinen erfolgreichen Start.

## Noch offen
Vollständige Übernahme geprüfter Acer/Kamera-Quellen in main; CORE Brain Server mit RAG, Wissensgraph, Szenarien und Planer; Gesichts-/Stimmerkennung mit Qualitätsprüfung, PTZ-Verfolgung, animierter rotgetigerter Katze, Emoji-Filter für TTS und Monitoring der drei Geräte. Sieben zusätzliche Branches bestehen noch; zwei haben offene PRs.

## Nächste Schritte
Privates Referenz-IMG sichern und hashen, genaue Boot-Offsets untersuchen, geprüfte Quellen ohne Geheimnisse übernehmen, Brain Server auf Huananzhi einrichten und Acer anbinden. Bei der Einlernprozedur nur nach erfolgreicher Qualitätsprüfung von Bild und Stimme fortfahren.

## Sprachen
Die technische Oberfläche/Dokumentation unterstützt **RU, EN, BE, SAH, DE, FR, ZH-CN** (7 Sprachen). Neue Einstellungen, Dialoge und Fehlermeldungen müssen in allen sieben Sprachen vorliegen; die Showcase-Seite mit 11 Sprachen ist getrennt.
