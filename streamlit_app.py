import streamlit as st
import openai
import time

import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAI'ye mesaj gönderen fonksiyon
def ask_chatgpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "⚠️ ChatGPT API ile bağlantı kurulamadı: " + str(e)


# Sayfa ayarları
st.set_page_config(page_title="🛍️ Alışveriş Chatbot", layout="centered")

# Görsel Stil
st.markdown("""
    <style>
    .reportview-container {
        margin: auto;
        max-width: 390px;
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 0 8px rgba(0,0,0,0.1);
    }
    .stRadio > div {
        flex-direction: column;
    }
    .stButton > button {
        width: 100%;
        background-color: #4B8BBE;
        color: white;
        border-radius: 10px;
        padding: 0.6rem;
        margin-top: 0.5rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #3771A1;
    }
    </style>
""", unsafe_allow_html=True)

# Oturum değişkenleri
if "state" not in st.session_state:
    st.session_state.state = "start"
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "subtopic" not in st.session_state:
    st.session_state.subtopic = ""
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "message_input" not in st.session_state:
    st.session_state.message_input = ""
if "last_message" not in st.session_state:
    st.session_state.last_message = ""

# Konular
topics = {
    "🛒 Sipariş": {
        "Kargo Durumu": "Siparişiniz hazırlanıyor, 1-2 iş günü içinde kargoya verilecek.",
        "Teslimat Süresi": "Teslimatlar genellikle 3-5 iş günü sürer.",
        "Kargo Firması": "Gönderilerimiz Yurtiçi ve MNG Kargo ile yapılmaktadır.",
        "Sipariş İptali": "Siparişiniz henüz kargoya verilmediyse iptal edebilirsiniz.",
        "Sipariş Geçmişi": "Hesabım > Siparişlerim sayfasından geçmiş siparişlerinizi görüntüleyebilirsiniz."
    },
    "👤 Hesap": {
        "Şifre Değişikliği": "Profil > Hesap Ayarları kısmından şifrenizi değiştirebilirsiniz.",
        "Bilgi Güncelleme": "Profilinizden e-posta, telefon gibi bilgilerinizi güncelleyebilirsiniz.",
        "Giriş Sorunu": "Şifrenizi unuttuysanız 'Şifremi Unuttum' seçeneğini kullanabilirsiniz."
    },
    "📦 Destek": {
        "Yeni Talep": "Destek sayfasından yeni bir destek talebi oluşturabilirsiniz.",
        "Açık Talepler": "Aktif destek taleplerinizi 'Destek Taleplerim' bölümünde görebilirsiniz.",
        "Yanıtlanan Talepler": "Cevaplanmış talepler arşive taşınır, oradan ulaşabilirsiniz."
    },
    "📄 Fatura & Ödeme": {
        "Fatura Al": "Sipariş detay sayfasından faturanızı PDF olarak indirebilirsiniz.",
        "İade Süreci": "14 gün içinde cayma hakkınızı kullanarak ürün iadesi yapabilirsiniz.",
        "Ödeme Sorunu": "Ödeme esnasında hata aldıysanız bankanızla veya bizimle iletişime geçin."
    },
    "🎁 Kampanyalar": {
        "Güncel Kampanyalar": "Anasayfamızda güncel kampanyaları ve fırsatları inceleyebilirsiniz.",
        "Hediye Çeki": "Çek kodunu ödeme ekranında kullanabilirsiniz.",
        "İndirim Şartları": "Bazı indirimler minimum sepet tutarı şartı ile geçerlidir."
    }
}

# Akış
if st.session_state.state == "start":
    st.title("👋 Alışveriş Asistanı")
    st.write("Size nasıl yardımcı olabilirim?")
    st.session_state.state = "select_topic"
    st.rerun()

elif st.session_state.state == "select_topic":
    st.subheader("📌 Konu Seçin")
    topic = st.radio("Bir kategori seçin:", list(topics.keys()))
    if st.button("Devam ➡️"):
        st.session_state.topic = topic
        st.session_state.state = "select_subtopic"
        st.rerun()

elif st.session_state.state == "select_subtopic":
    st.subheader(f"{st.session_state.topic} → Alt Başlık")
    subtopics = list(topics[st.session_state.topic].keys())
    subtopic = st.radio("Alt başlık seçin:", subtopics)
    if st.button("Yanıtı Göster"):
        st.session_state.subtopic = subtopic
        st.session_state.state = "response"
        st.rerun()

elif st.session_state.state == "response":
    yanit = topics[st.session_state.topic][st.session_state.subtopic]
    st.success(f"**{st.session_state.subtopic}**\n\n{yanit}")
    time.sleep(2)
    st.session_state.state = "feedback"
    st.rerun()

elif st.session_state.state == "feedback":
    st.subheader("✅ Yardımcı olabildik mi?")
    feedback = st.radio("Yanıtınızı seçin:", ["Evet", "Hayır"], key="feedback_radio")

    if feedback == "Evet":
        if st.button("Teşekkürler, Ana Menüye Dön"):
            st.success("Teşekkür ederiz! Başka bir konuda yardımcı olabilirsiniz.")
            time.sleep(1)
            st.session_state.state = "start"
            st.rerun()

    elif feedback == "Hayır":
        st.warning("Nasıl devam etmek istersiniz?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👩‍💼 Temsilciyle Sohbet"):
                st.session_state.chat_log = [("bot", "Bir temsilciye bağlanıyorsunuz...")]
                st.session_state.state = "human_chat"
                st.rerun()
        with col2:
            if st.button("🤖 ChatGPT ile Sohbet"):
                st.session_state.chat_log = [("bot", "ChatGPT'ye bağlanıyorsunuz...")]
                st.session_state.state = "gpt_chat"
                st.rerun()

elif st.session_state.state == "human_chat":
    st.subheader("👩‍💬 Temsilciyle Sohbet")

    if st.session_state.message_input and st.session_state.message_input != st.session_state.last_message:
        st.session_state.chat_log.append(("user", st.session_state.message_input))
        st.session_state.chat_log.append(("bot", "📡 Temsilcimize bağlıyız, lütfen bekleyin..."))
        st.session_state.last_message = st.session_state.message_input
        st.session_state.message_input = ""
        st.rerun()

    for sender, msg in st.session_state.chat_log:
        color = "#DCF8C6" if sender == "user" else "#F1F0F0"
        align = "right" if sender == "user" else "left"
        st.markdown(f"<div style='text-align: {align}; background-color: {color}; padding: 8px; border-radius: 8px; margin: 6px 0;'>{msg}</div>", unsafe_allow_html=True)

    st.text_input("Mesajınızı yazın ve Enter’a basın:", key="message_input")

    if st.button("🔙 Ana Menüye Dön"):
        st.session_state.state = "start"
        st.session_state.chat_log = []
        st.rerun()


elif st.session_state.state == "gpt_chat":
    st.subheader("🤖 ChatGPT ile Sohbet")

    if st.session_state.message_input and st.session_state.message_input != st.session_state.last_message:
        user_msg = st.session_state.message_input
        st.session_state.chat_log.append(("user", user_msg))
        gpt_response = ask_chatgpt(user_msg)
        st.session_state.chat_log.append(("bot", gpt_response))
        st.session_state.last_message = user_msg
        st.session_state.message_input = ""
        st.rerun()

    for sender, msg in st.session_state.chat_log:
        color = "#DCF8C6" if sender == "user" else "#F1F0F0"
        align = "right" if sender == "user" else "left"
        st.markdown(f"<div style='text-align: {align}; background-color: {color}; padding: 8px; border-radius: 8px; margin: 6px 0;'>{msg}</div>", unsafe_allow_html=True)

    st.text_input("Mesajınızı yazın ve Enter’a basın:", key="message_input")

    if st.button("🔙 Ana Menüye Dön"):
        st.session_state.state = "start"
        st.session_state.chat_log = []
        st.rerun()