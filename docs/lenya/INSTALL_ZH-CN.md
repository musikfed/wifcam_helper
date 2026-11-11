# Lenya（Лёня）· 两种部署方式（简体中文）

**已验证：** T23N 最小 microSD 镜像、Raptor、摄像头网页 :8090，以及 Acer Station v2.2。CORE Brain Server、RAG、人脸和声纹识别仍是未来计划。

**A — IMG：** 将 T23N_Lenya_WORKING.zip 保存在本地，不要公开。通过 python scripts/lenya-image.py T23N_Lenya_WORKING.zip 检查结构，然后使用磁盘镜像工具写入确认过的 microSD。此脚本不会访问物理磁盘。

**B — 正在运行的 SD：** 本地解压 peginelab.zip。PowerShell 命令 scripts/lenya-deploy-camera.ps1 -PackageRoot F:\peginelab 默认只读检查；添加 -Apply 后通过 SSH 和 scp -O 部署并备份。Acer 运行 scripts/lenya-install-acer.ps1 -PackageRoot F:\peginelab -Apply。不要将密码、密钥或私有镜像提交到公开 GitHub。
