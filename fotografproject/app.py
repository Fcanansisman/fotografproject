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
def fetch_images(query, per_page=200, max_pages=5):
    all_images = []  # Tüm fotoğrafları tutacak liste
    
    for page in range(1, max_pages + 1):  # max_pages kadar döngüye giriyoruz
        params = {
            'key': API_KEY,
            'q': query,
            'image_type': 'photo',  # Yalnızca fotoğraflar
            'per_page': per_page,   # Sayfada gösterilecek resim sayısı
            'page': page,           # Sayfa numarası
            'orientation': 'horizontal'  # Resim yönü
        }

        response = requests.get(URL, params=params)

        if response.status_code == 200:
            try:
                data = response.json()  # JSON verisini döndür
                for image in data['hits']:
                    # Etiketleri işlerken sadece ilk iki kelimeyi al
                    image['tags'] = get_first_two_words(image['tags'])
                all_images.extend(data['hits'])  # Fotoğrafları birleştir
                
                # MinIO'ya her bir fotoğrafı yükle
                for image in data['hits']:
                    image_url = image['largeImageURL']
                    
                    # Fotoğraf daha önce yüklenmişse atla
                    if image_url in uploaded_images:
                        continue
                    
                    # Fotoğrafı yüklemeden önce URL'yi set'e ekle
                    uploaded_images.add(image_url)
                    
                    # Fotoğraf adı, URL'den son kısmı alınarak oluşturulur
                    image_name = image_url.split('/')[-1]
                    upload_image_to_minio(image_url, image_name)
            except ValueError:  # JSONDecodeError'dan önce
                print("JSON hatası oluştu.")
        else:
            print(f"Hata: {response.status_code}")
            break  # Eğer hata alınırsa döngüden çık
        
    return all_images  # Tüm fotoğrafları döndür

# Ana sayfa
@app.route('/')
def index():
    # Manzara fotoğraflarını çek
    result = fetch_images('manzara', per_page=40, max_pages=1)  # Test için 40 fotoğraf, 1 sayfa

    if result:
        # Fotoğrafları ve başlıkları template'e gönder
        return render_template('index.html', images=result)
    else:
        return "Veri çekilemedi."

if __name__ == '__main__':
    app.run(debug=True)