# Lenya · 已确认基线与后续计划

**简体中文 · 2026-11-11 · Lenya v2.2**

## 已验证
Ingenic T23N 通过 microSD 启动；Raptor 音视频、摄像头界面 :8090、Acer Lenya Station v2.2（Ollama 代理 :11435、Whisper/Piper :11436、管理界面 :11437）均已实际测试。HTTP 200 和 PCM 语音回复已确认。私有参考 IMG 大小为 81 MiB。两种安装方法见 [INSTALL_ZH-CN.md](INSTALL_ZH-CN.md)。

## 关键：T23N SD 启动偏移
原 SPI NOR 已拆除，系统从 microSD 启动。**已知分区起始位置：**MBR、FAT16 从 **LBA 2048** 开始（16 MiB），Linux/ext 从 **LBA 34816** 开始（64 MiB）。这些是**分区偏移，并非已经验证的 MSPL/SPL/U-Boot/内核偏移**。必须逐字节保留工作镜像的 MBR 和 LBA 2048 之前的启动区域；禁止未经验证的重新分区或移动加载程序。IMG 结构检查不代表真实硬件一定能够启动。

## 尚未完成
将私有包中经过验证的 Acer/摄像头源代码安全整理到 main；Huananzhi 上的 Brain Server、RAG、知识图谱、场景引擎与规划器；人脸和声纹识别、质量控制的注册流程、PTZ 跟踪、橘猫动画、TTS 表情符号过滤以及三节点资源监控。当前仍有 7 个额外分支，其中 2 个关联未关闭 PR。

## 接下来
私密备份并校验参考 IMG；确认 T23N 启动组件的真实位置；仅合并无敏感信息的已验证源码；在 CORE 部署 Brain Server 并连接 Acer。新用户注册需要每个角度的照片和语音样本通过质量检测后才能进入下一步骤。

## 语言
技术文档与 UI 支持 **RU、EN、BE、SAH、DE、FR、ZH-CN**（共 7 种语言）。所有新增设置、场景和错误信息必须提供七种翻译。展示页的 11 种语言与完整产品界面本地化是两回事。
