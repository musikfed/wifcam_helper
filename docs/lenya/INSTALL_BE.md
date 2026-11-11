# Лёня · Два спосабы ўсталявання (BE)

**Ужо працуе:** мінімальны вобраз T23N microSD, Raptor, вэб-інтэрфейс :8090 і галасавая станцыя Acer v2.2. Brain Server, RAG і распазнаванне людзей — пакуль планы.

**A — вобраз:** захоўвайце T23N_Lenya_WORKING.zip прыватна. Праверце яго праз python scripts/lenya-image.py T23N_Lenya_WORKING.zip, потым запішыце IMG на правільную карту праграмай для дыскавых вобразаў. Скрыпт не змяняе фізічныя дыскі.

**B — жывая SD:** распакуйце лакальны peginelab.zip. Выканайце scripts/lenya-deploy-camera.ps1 -PackageRoot F:\peginelab (праверка), затым дадайце -Apply. Станцыю Acer усталюйце праз scripts/lenya-install-acer.ps1 -PackageRoot F:\peginelab -Apply. Не публікуйце паролі, ключы і асабістыя вобразы на GitHub.
