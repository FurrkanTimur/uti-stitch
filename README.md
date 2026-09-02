# Stitch

Component for NOVAVISION.

`uti-stitch-images` ve `uti-stitch-ocr` component'lerini tek çatı altında toplayan, birden fazla executor sunan bir NovaVision component'idir. Kullanıcı, `Task` (executor) alanından üç görevden birini seçer:

- **StitchImages**: İki görüntüyü kendi içinde SIFT ile keypoint/descriptor çıkarıp (BFMatcher + homography) tek bir panoramaya birleştirir. Dışarıdan hazır keypoint/descriptor gerekmez, sadece `inputImageA`/`inputImageB` yeterlidir (`uti-stitch-images`'in `develop` branch'inden taşındı).
- **OnEdge**: Bir görüntü listesini satır/sütun grid'ine dizip tek bir kolaj görüntüsü üretir (`uti-stitch-images`'in `develop` branch'inden taşındı).
- **StitchOcr**: OCR tarafından üretilen metin kutularını kümeleyip okuma yönüne göre sıralayarak birleşik metin blokları üretir (`uti-stitch-ocr`'dan taşındı).

Her executor kendi `Request`/`Response`/`Inputs`/`Outputs`/`Configs` şemasını korur; seçim en üst seviyedeki `ConfigExecutor.value` (`Union[StitchImagesExecutor, StitchOcrExecutor, OnEdgeExecutor]`) üzerinden yapılır.
