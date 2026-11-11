# Lenya · point de reprise vérifié

**Français · 2026-11-11 · Lenya v2.2**

## Vérifié
Caméra Ingenic T23N démarrant sur microSD, Raptor, interface :8090 et Acer Lenya Station v2.2 (proxy Ollama :11435, Whisper/Piper :11436, console :11437). Réponse vocale HTTP 200/PCM confirmée en situation réelle. L'IMG de référence privé fait 81 Mio. Deux méthodes : [INSTALL_FR.md](INSTALL_FR.md).

## Critique : décalages de démarrage T23N
La puce SPI NOR a été retirée, le système démarre sur microSD. **Débuts de partitions connus :** MBR, FAT16 à **LBA 2048** (16 Mio), Linux/ext à **LBA 34816** (64 Mio). Les offsets exacts **MSPL/SPL/U-Boot/noyau ne sont pas confirmés**. Préserver octet pour octet le MBR et la zone de démarrage avant LBA 2048 de l'IMG fonctionnel ; ne pas repartitionner ni déplacer le chargeur au hasard. Le contrôle de structure IMG ne prouve pas le démarrage physique.

## À faire
Importer les sources vérifiées Acer/caméra dans main sans secrets ; Brain Server CORE, RAG, graphe, scénarios et planificateur ; reconnaissance visage/voix avec contrôle de qualité, suivi PTZ, chat roux animé, filtre emoji TTS et supervision des trois machines. Sept branches supplémentaires restent présentes, dont deux liées à des PR ouvertes.

## Suite
Protéger et hacher l'IMG de référence ; vérifier la carte des composants de démarrage ; intégrer uniquement les sources testées ; déployer Brain Server sur Huananzhi et relier Acer. Lors de la présentation d'une personne, ne passer à l'étape suivante qu'après validation de chaque photo et enregistrement vocal.

## Langues
L'interface et les guides techniques couvrent **RU, EN, BE, SAH, DE, FR, ZH-CN** (7 langues). Les nouveautés doivent être traduites dans les sept langues ; la vitrine en 11 langues est distincte.
