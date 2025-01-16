from flask import Flask, render_template
from views import fetch_images  # views.py dosyasından fetch_images fonksiyonunu import ediyoruz

app = Flask(__name__)

# Ana sayfa
@app.route('/')
def index():
    # Birden fazla anahtar kelime (query) kullanarak resimler çekmek
    query = 'wallpaper beautiful flower'  
    
    # Fotoğrafları çek
    result = fetch_images(query, per_page=20, max_pages=1)

    if result:
        # Fotoğrafları ve başlıkları template'e gönder
        return render_template('index.html', images=result)
    else:
        return "Veri çekilemedi."

if __name__ == '__main__':
    app.run(debug=True)
