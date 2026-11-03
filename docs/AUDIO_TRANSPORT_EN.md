# Native T23N speaker: local audio transport choices

- **First physical proof:** Hombo3 TTS → authenticated SSH → Raptor `/usr/sbin/play` → `rac` → camera's own speaker. It uses a new SSH process per utterance, but needs no exposed speaker HTTP port or cloud access.
- **Lower handshake overhead:** a persistent, authenticated audio channel or SSH ControlMaster/ControlPersist on Linux; do not blindly add ControlMaster to native Windows OpenSSH used by Hombo3, where Unix socket multiplexing can be unsupported.
- **Future streaming:** tested ONVIF/RTSP audio backchannel, or optional Raptor WebRTC RWD with TLS/signaling; both require real microphone, loudspeaker, codec and backchannel testing.
- **Avoid:** unauthenticated speaker endpoints or raw PCM UDP open to the LAN.

For a valid voice assistant: a person must hear sound from the camera's native speaker and the built-in microphone must capture actual speech. Process exit code or presence of `rac` proves neither. WifCam Helper never changes `ao_enabled`, restarts Raptor or replaces system BusyBox.
