from flask import Flask, render_template
import requests
from minio import Minio
from io import BytesIO

app = Flask(__name__)

# Pixabay API Anahtarı
API_KEY = '48202519-2adc2007eb6344bb9de46c0f1'

# API URL'si
URL = "https://pixabay.com/api/"

# MinIO client ayarları
client = Minio(
    "localhost:9000",  # MinIO'nun adresi
    access_key="minioadmin",  # MinIO access key
    secret_key="minioadmin",  # MinIO secret key
    secure=False  # HTTPS kullanmıyorsanız False
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
            "fotograf-bucket",  # Bucket adı
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
def fetch_images(query, per_page=200, max_pages=1):
    all_images = []  # Tüm fotoğrafları tutacak liste

    for page in range(1, max_pages + 1):
        params = {
            'key': API_KEY,
            'q': query,
            'image_type': 'photo',
            'per_page': per_page,
            'page': page,
            'orientation': 'horizontal'
        }

        response = requests.get(URL, params=params)
        print("API Yanıtı:", response.text)

        if response.status_code == 200:
            try:
                data = response.json()  # JSON verisini döndür
                print(f"Toplam Resim Sayısı: {data['totalHits']}")

                if data['totalHits'] == 0:
                    print("Yeni resimler bulunamadı.")
                    break

                for image in data['hits']:
                    image_url = image['largeImageURL']

                    if image_url in uploaded_images:
                        continue  # Zaten yüklendiyse atla

                    uploaded_images.add(image_url)  # Fotoğrafı ekle

                    image_name = image_url.split('/')[-1]  # Fotoğraf adını oluştur
                    upload_image_to_minio(image_url, image_name)  # Yükle

                    minio_url = f"http://localhost:9000/fotograf-bucket/{image_name}"

                    image['tags'] = get_first_two_words(image['tags'])  # Etiketleri işle

                    all_images.append({
                        'minio_url': minio_url,
                        'tags': image['tags']
                    })
            except ValueError:
                print("JSON hatası oluştu.")
        else:
            print(f"Hata: {response.status_code}")
            break

    return all_images  # Tüm fotoğrafları döndür
