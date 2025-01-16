from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

class Config:
    # Pixabay API Anahtarı
    API_KEY = os.getenv('PIXABAY_API_KEY')  # .env dosyasından alınır
    
    if not API_KEY:
        print("PIXABAY_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
    else:
        print("PIXABAY_API_KEY başarıyla yüklendi.")
    
    # API URL'si
    URL = "https://pixabay.com/api/"

    # MinIO client ayarları
    MINIO_HOST = os.getenv('MINIO_HOST', 'localhost:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET_NAME = "fotograf-bucket"
    MINIO_SECURE = False  # HTTPS kullanmıyorsanız False

    # Fotoğraf Yükleme Ayarları
    UPLOAD_PATH = "uploads"
