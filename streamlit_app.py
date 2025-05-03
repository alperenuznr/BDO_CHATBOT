import streamlit as st
import openai
import time

# API anahtarını doğrudan buraya yazıyoruz
openai.api_key = "sk..."  # ← buraya kendi API key'inizi yazın

# OpenAI üzerinden mesaj gönderme fonksiyonu
def ask_chatgpt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen kibar, çözüm odaklı bir müşteri temsilcisisin. Bu kodda yazılmış olan konularda kullanıcıya destek veriyorsun. Kullanıcıya samimi ama profesyonel bir dille yardımcı ol."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "⚠️ ChatGPT API ile bağlantı kurulamadı: " + str(e)

# Sayfa başlığı ve düzeni
st.set_page_config(page_title="🛍️ Alışveriş Chatbot", layout="centered")

# Stil tanımı (geliştirilmiş buton görünümü)
st.markdown("""
    <style>
    .reportview-container {
        margin: auto;
        max-width: 420px;
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 0 12px rgba(0,0,0,0.08);
    }
    .stRadio > div {
        flex-direction: column;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(to right, #4B8BBE, #3771A1);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.6rem;
        margin-top: 0.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        background: linear-gradient(to right, #5CA4EA, #4B8BBE);
    }
    </style>
""", unsafe_allow_html=True)

# Oturum değişkenlerinin başlatılması
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

# Konular sözlüğü (uzatılmış açıklamalar)
topics = {
    "🛒 Sipariş": {
        "Kargo Durumu": "Siparişiniz şu anda hazırlanıyor. Genellikle siparişlerimiz 1-2 iş günü içinde kargoya verilmektedir. Siparişiniz kargoya verildiğinde SMS ve e-posta ile bilgilendirme yapılır.",
        "Teslimat Süresi": "Siparişinizin teslimat süresi bulunduğunuz lokasyona göre değişmekle birlikte, genellikle 3-5 iş günü içerisinde teslim edilmektedir.",
        "Kargo Firması": "Gönderilerimiz Yurtiçi ve MNG Kargo ile yapılmaktadır. Kargo firması tercihi sipariş sırasında belirtilebilir.",
        "Sipariş İptali": "Eğer siparişiniz henüz kargoya verilmemişse, iptal işlemi mümkündür. İptal için Hesabım > Siparişlerim kısmından işlem yapabilirsiniz.",
        "Sipariş Geçmişi": "Geçmiş siparişlerinizi görüntülemek için Hesabım > Siparişlerim sayfasını ziyaret edebilirsiniz. Buradan ayrıca fatura ve kargo bilgilerine de ulaşabilirsiniz."
    },
    "👤 Hesap": {
        "Şifre Değişikliği": "Profil sayfanızda bulunan Hesap Ayarları bölümünden mevcut şifrenizi değiştirerek yeni şifrenizi belirleyebilirsiniz.",
        "Bilgi Güncelleme": "E-posta, telefon numarası ve adres gibi kişisel bilgilerinizi profil sayfanızdan kolayca güncelleyebilirsiniz.",
        "Giriş Sorunu": "Hesabınıza giriş yapamıyorsanız, 'Şifremi Unuttum' seçeneğini kullanarak yeni bir şifre oluşturabilirsiniz."
    },
    "📦 Destek": {
        "Yeni Talep": "Karşılaştığınız herhangi bir sorun için destek sayfasından yeni bir talep oluşturabilirsiniz. Destek ekibimiz en kısa sürede dönüş sağlayacaktır.",
        "Açık Talepler": "Devam eden destek taleplerinizi 'Destek Taleplerim' bölümünde görüntüleyebilirsiniz.",
        "Yanıtlanan Talepler": "Cevaplanan destek talepleriniz arşive taşınır ve geçmiş talepleriniz kısmında erişilebilir."
    },
    "📄 Fatura & Ödeme": {
        "Fatura Al": "Faturanıza sipariş detay sayfasından PDF formatında ulaşabilir, çıktısını alabilirsiniz.",
        "İade Süreci": "Üründen memnun kalmadığınız takdirde, teslim tarihinden itibaren 14 gün içinde iade işlemi başlatabilirsiniz.",
        "Ödeme Sorunu": "Ödeme sırasında hata alırsanız, öncelikle bankanızla görüşebilir ya da bizimle iletişime geçebilirsiniz."
    },
    "🎁 Kampanyalar": {
        "Güncel Kampanyalar": "Anasayfamızda yılın farklı dönemlerinde düzenlediğimiz kampanyaları görebilirsiniz. Hafta sonu indirimleri, sepet kampanyaları ve sürpriz hediye çeki fırsatlarını takip edin.",
        "Hediye Çeki": "Kampanya dönemlerinde size özel tanımlanan hediye çeklerini ödeme ekranında kullanabilirsiniz. Çek kodunu girmeniz yeterlidir.",
        "İndirim Şartları": "Bazı indirimler belirli bir sepet tutarının üzerine çıktığınızda otomatik olarak tanımlanır. Detaylar kampanya koşullarında belirtilmektedir."
    }
}

# Uygulama durumu akışı (FSM)
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
    time.sleep(4)
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
        st.warning("Üzgünüz, daha iyi yardımcı olabilmemiz için bir temsilciye yönlendiriyoruz.")
        if st.button("👩‍💼 Temsilciyle Sohbet"):
            st.session_state.chat_log = [("bot", "Yapay Zeka temsilcimize bağlanıyorsunuz...")]
            st.session_state.state = "gpt_chat"
            st.rerun()

# GPT ile konuşma (Müşteri Temsilcisi)
elif st.session_state.state == "gpt_chat":
    st.subheader("🤖 Müşteri Temsilcisi ile Sohbet")

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
        st.markdown(
            f"<div style='text-align: {align}; background-color: {color}; padding: 8px; border-radius: 8px; margin: 6px 0;'>{msg}</div>",
            unsafe_allow_html=True
        )

    st.text_input("Mesajınızı yazın ve Enter’a basın:", key="message_input")

    if st.button("🔙 Ana Menüye Dön"):
        st.session_state.state = "start"
        st.session_state.chat_log = []
        st.rerun()