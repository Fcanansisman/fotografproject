Fotograf Project
Bu proje, Pixabay API'si aracılığıyla manzara fotoğrafları çeker ve bu fotoğrafları MinIO (yerel bir nesne depolama sunucusu) ile depolar. Ayrıca, projede yer alan fotoğraflar, Flask tabanlı bir web uygulamasında kullanıcıya sunulur.

Özellikler
Pixabay API'si kullanarak manzara fotoğraflarını arar ve getirir.
Fotoğrafları MinIO nesne depolama sistemine yükler.
Web uygulaması ile fotoğrafları görüntülemek için bir kullanıcı arayüzü sağlar.
Her fotoğraf için yalnızca ilk iki etiketi gösterir.
MinIO üzerinde depolanan fotoğraflar, kullanıcıların her seferinde yeniden yüklemelerini önler.
Gereksinimler
Bu projeyi çalıştırabilmek için aşağıdaki yazılımların kurulu olması gerekmektedir:

Python 3.7+
Flask: Web uygulamasını oluşturmak için.
Requests: Pixabay API'den fotoğraf verilerini almak için.
MinIO Python SDK: MinIO ile etkileşimde bulunmak için.
