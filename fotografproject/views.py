import random
import requests
from minio import Minio
from io import BytesIO
from config import Config  # config.py dosyasındaki ayarları import ediyoruz

# MinIO client ayarları
client = Minio(
    Config.MINIO_HOST,  # MinIO'nun adresi
    access_key=Config.MINIO_ACCESS_KEY,  # MinIO access key
    secret_key=Config.MINIO_SECRET_KEY,  # MinIO secret key
    secure=Config.MINIO_SECURE  # HTTPS kullanmıyorsanız False
)

# Daha önce yüklenen fotoğrafların URL'lerini saklamak için bir set
uploaded_images = set()

# Fotoğrafı MinIO'ya yükleyen fonksiyon
def upload_image_to_minio(image_url, image_name):
    try:
        # Fotoğrafı URL'den çekiyoruz
        response = requests.get(image_url)
        img_data = BytesIO(response.content)  # Resmi binary formatta okuyoruz

        # Fotoğrafı MinIO'ya yükle
        client.put_object(
            Config.MINIO_BUCKET_NAME,  # Bucket adı
            image_name,  # Fotoğrafın adı
            img_data,  # Fotoğraf verisi
            len(response.content)  # Fotoğraf boyutu
        )
        print(f"Resim {image_name} MinIO'ya başarıyla yüklendi.")
    except Exception as e:
        print(f"Hata: {e}")

# Etiketleri sadece ilk iki kelimeye indirgeyen fonksiyon
def get_first_two_words(tags):
    return ' '.join(tags.split()[:2])  # İlk iki kelimeyi al ve birleştir

# Pixabay API'den fotoğraf çekme fonksiyonu
def fetch_images(query, per_page=20, max_pages=1):
    all_images = []  # Tüm fotoğrafları tutacak liste

    # Sayfa numarasını rastgele seç
    page_number = random.randint(1, 5)  # 1 ile 5 arasında rastgele bir sayfa numarası

    params = {
        'key': Config.API_KEY,
        'q': query,
        'image_type': 'photo',
        'per_page': per_page,
        'page': page_number,
        'orientation': 'horizontal'
    }

    response = requests.get(Config.URL, params=params)
    print("API Yanıtı:", response.text)

    if response.status_code == 200:
        try:
            data = response.json()  # JSON verisini döndür
            print(f"Toplam Resim Sayısı: {data['totalHits']}")

            if data['totalHits'] == 0:
                print("Yeni resimler bulunamadı.")
                return []

            for image in data['hits']:
                image_url = image['largeImageURL']

                if image_url in uploaded_images:
                    continue  # Zaten yüklendiyse atla

                uploaded_images.add(image_url)  # Fotoğrafı ekle, bu URL'nin bir daha işlenmesini engeller.

                image_name = image_url.split('/')[-1]  # Fotoğraf adını oluştur
                upload_image_to_minio(image_url, image_name)  # Yükle

                minio_url = f"http://{Config.MINIO_HOST}/{Config.MINIO_BUCKET_NAME}/{image_name}"

                image['tags'] = get_first_two_words(image['tags'])  # Etiketleri işle

                # Her resme benzersiz bir ID ekleyelim (image_url'yi ID olarak kullanabiliriz)
                all_images.append({
                    'minio_url': minio_url,
                    'tags': image['tags'],
                    'id': image_url  # ID olarak URL kullanılıyor
                })

        except ValueError:
            print("JSON hatası oluştu.")
    else:
        print(f"Hata: {response.status_code}")

    # Resimleri 'id' (image_url) değerine göre sıralıyoruz
    all_images = sorted(all_images, key=lambda x: x['id'])

    return all_images  # Tüm fotoğrafları döndür
