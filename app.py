import os
import pickle
import re

from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# ---------------------------------------------------------------------------
# Aplikasi Flask
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ---------------------------------------------------------------------------
# Memuat model & sumber daya (sekali saat startup)
# ---------------------------------------------------------------------------
model_fraud = pickle.load(open(os.path.join(BASE_DIR, "model_deteksi_pesan.sav"), "rb"))
vocab = pickle.load(open(os.path.join(BASE_DIR, "new_selected_feature_tf-idf.sav"), "rb"))
loaded_vec = TfidfVectorizer(decode_error="replace", vocabulary=set(vocab))

key_norm = pd.read_csv(os.path.join(BASE_DIR, "key_norm.csv"))

stopwords_ind = stopwords.words("indonesian")
more_stopword = ["tsel", "gb", "rb", "btw"]
stop_words = stopwords_ind + more_stopword

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# ---------------------------------------------------------------------------
# Fungsi-fungsi Preprocessing NLP
# ---------------------------------------------------------------------------

def casefolding(text):
    """Mengubah teks ke huruf kecil, menghapus URL, angka, dan karakter non-alfanumerik."""
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[-+]?[0-9]+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = text.strip()
    return text


def text_normalize(text):
    """Menormalisasi kata-kata singkatan menjadi bentuk lengkap berdasarkan kamus normalisasi."""
    text = " ".join(
        [
            key_norm[key_norm["singkat"] == word]["hasil"].values[0]
            if (key_norm["singkat"] == word).any()
            else word
            for word in text.split()
        ]
    )
    text = str.lower(text)
    return text


def remove_stop_word(text):
    """Menghapus stopword dari teks untuk menyaring kata-kata yang tidak informatif."""
    clean_words = []
    for word in text.split():
        if word not in stop_words:
            clean_words.append(word)
    return " ".join(clean_words)


def stemming(text):
    """Mengubah kata ke bentuk dasar menggunakan stemmer Bahasa Indonesia (Sastrawi)."""
    return stemmer.stem(text)


def text_preprocessing_process(text):
    """Menjalankan seluruh pipeline preprocessing: casefolding, normalisasi, stopword removal, dan stemming."""
    text = casefolding(text)
    text = text_normalize(text)
    text = remove_stop_word(text)
    text = stemming(text)
    return text

# ---------------------------------------------------------------------------
# Rute / Endpoint
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    sms_text = data.get("text", "").strip()

    if not sms_text:
        return jsonify({
            "prediction": -1,
            "label": "Input Kosong",
            "description": "Silakan masukkan teks SMS terlebih dahulu.",
            "icon": "❌",
        })

    try:
        cleaned_text = text_preprocessing_process(sms_text)
        vector = loaded_vec.fit_transform([cleaned_text])
        prediction = int(model_fraud.predict(vector)[0])

        label_map = {
            0: ("PESAN AMAN", "Tidak terdeteksi indikasi penipuan. Tetap waspada terhadap tautan dan permintaan data pribadi.", "✅"),
            1: ("PESAN PENIPUAN/SCAM!", "Berpotensi penipuan. Jangan membalas pesan, jangan klik tautan, dan jangan bagikan kode OTP.", "⚠️"),
            2: ("PESAN PROMO", "Pesan terdeteksi sebagai promosi. Pastikan berasal dari pengirim resmi sebelum menindaklanjuti.", "💬"),
        }

        label, description, icon = label_map.get(prediction, ("TIDAK DIKETAHUI", "Klasifikasi tidak dikenali.", "📋"))

        return jsonify({
            "prediction": prediction,
            "label": label,
            "description": description,
            "icon": icon,
        })

    except Exception as e:
        return jsonify({
            "prediction": -1,
            "label": "Terjadi Kesalahan",
            "description": str(e),
            "icon": "❌",
        }), 500


# ---------------------------------------------------------------------------
# Menjalankan Aplikasi
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
