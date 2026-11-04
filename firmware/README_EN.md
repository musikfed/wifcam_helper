# WifCam Helper: distinct Ingenic T23N SD firmware flavor

YadroKreator pins both the Helper source SHA and the approved WIFICAM base SHA, stages a safe camera-side firmware overlay into its own isolated build worktree, and builds a separate Thingino SD image.

The target rootfs contains an explicit release marker, an init script, a camera-side executable probe, and a CGI JSON endpoint for audio/video transport readiness. These are actual rootfs components, not host-side Python services. Detection of rad/rac/rvd commands is NOT proof that the camera microphone, speaker amplifier or video sensor works physically.

The multimodal assistant itself (CV, STT, LLM, TTS, visual memory and GPU scheduling) runs on CORE, not on the 64 MB T23N. RTSP/video and audio transport must be hardware tested and integrated with the CORE orchestration separately. No SD flashing occurs automatically; preserve the historical WIFICAM 0.1_test recovery image.
