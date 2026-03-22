import streamlit as st
import random
import json
import time
from datetime import datetime
from groq import Groq
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="英國生活英語 🇬🇧 | UK Life English",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Noto+Sans+HK:wght@400;500;700&display=swap');

/* ── Root Variables ── */
:root {
  --red:    #E63946;
  --blue:   #1D3557;
  --sky:    #457B9D;
  --cream:  #F1FAEE;
  --gold:   #FFB703;
  --green:  #2DC653;
  --soft:   #A8DADC;
}

html, body, [class*="css"] {
  font-family: 'Nunito', 'Noto Sans HK', sans-serif;
}

/* ── Background ── */
.stApp {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f4f8 50%, #fff8f0 100%);
}

/* ── Header Banner ── */
.hero-banner {
  background: linear-gradient(135deg, #1D3557 0%, #457B9D 60%, #E63946 100%);
  border-radius: 20px;
  padding: 28px 36px;
  margin-bottom: 24px;
  color: white;
  text-align: center;
  box-shadow: 0 8px 32px rgba(29,53,87,0.25);
  position: relative;
  overflow: hidden;
}
.hero-banner::before {
  content: '🇬🇧';
  position: absolute; top: -20px; right: -10px;
  font-size: 120px; opacity: 0.1;
}
.hero-banner h1 {
  font-size: 2.4rem; font-weight: 900; margin: 0 0 6px 0;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.hero-banner p {
  font-size: 1.1rem; opacity: 0.92; margin: 0;
}

/* ── Level Badges ── */
.level-badge {
  display: inline-block;
  padding: 6px 18px;
  border-radius: 50px;
  font-weight: 800;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}
.level-1 { background:#d4edda; color:#155724; }
.level-2 { background:#fff3cd; color:#856404; }
.level-3 { background:#f8d7da; color:#721c24; }

/* ── Lesson Cards ── */
.lesson-card {
  background: white;
  border-radius: 16px;
  padding: 22px 26px;
  margin: 14px 0;
  border-left: 5px solid var(--sky);
  box-shadow: 0 4px 16px rgba(0,0,0,0.07);
  transition: transform 0.2s;
}
.lesson-card:hover { transform: translateY(-2px); }
.lesson-card.gold  { border-left-color: var(--gold); }
.lesson-card.red   { border-left-color: var(--red); }
.lesson-card.green { border-left-color: var(--green); }

/* ── Dialogue Bubbles ── */
.bubble-uk {
  background: #1D3557;
  color: white;
  border-radius: 18px 18px 18px 4px;
  padding: 14px 20px;
  margin: 10px 0 10px 20px;
  display: inline-block;
  max-width: 85%;
  font-size: 1.05rem;
  box-shadow: 0 3px 10px rgba(29,53,87,0.2);
}
.bubble-hk {
  background: #E63946;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 14px 20px;
  margin: 10px 20px 10px 0;
  display: inline-block;
  max-width: 85%;
  font-size: 1.05rem;
  box-shadow: 0 3px 10px rgba(230,57,70,0.2);
  float: right;
  clear: both;
}
.bubble-label {
  font-size: 0.78rem;
  opacity: 0.7;
  margin-bottom: 4px;
  font-weight: 700;
}
.clear { clear: both; }

/* ── Quiz Cards ── */
.quiz-box {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.09);
  border-top: 6px solid var(--gold);
}
.quiz-q {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1D3557;
  margin-bottom: 18px;
}

/* ── Tip Box ── */
.tip-box {
  background: linear-gradient(135deg, #fff8e1, #fffde7);
  border: 2px solid var(--gold);
  border-radius: 14px;
  padding: 16px 20px;
  margin: 14px 0;
}
.tip-box .tip-icon { font-size: 1.5rem; }
.tip-box strong { color: #856404; }

/* ── Fun Fact ── */
.funfact {
  background: linear-gradient(135deg, #e3f2fd, #e8f5e9);
  border-radius: 14px;
  padding: 16px 20px;
  margin: 12px 0;
  border-left: 4px solid var(--sky);
  font-size: 0.95rem;
}

/* ── Progress Bar custom ── */
.progress-wrap {
  background: #e9ecef;
  border-radius: 50px;
  height: 18px;
  margin: 8px 0;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 50px;
  background: linear-gradient(90deg, #457B9D, #2DC653);
  transition: width 0.5s ease;
}

/* ── Score Display ── */
.score-big {
  text-align: center;
  font-size: 3.5rem;
  font-weight: 900;
  color: #1D3557;
  line-height: 1;
}
.score-label {
  text-align: center;
  font-size: 0.9rem;
  color: #777;
  margin-top: 4px;
}

/* ── Buttons override ── */
.stButton > button {
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-family: 'Nunito', sans-serif !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #1D3557 0%, #457B9D 100%);
}
section[data-testid="stSidebar"] * {
  color: white !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
  background: rgba(255,255,255,0.15) !important;
  border-color: rgba(255,255,255,0.3) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  font-weight: 700;
  font-size: 1rem;
}

/* ── Audio hint ── */
.audio-hint {
  background: #e3f2fd;
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 0.88rem;
  color: #1565C0;
  margin: 8px 0;
}

/* ── Emoji Reactions ── */
.reaction-bar {
  display: flex; gap: 10px; margin: 12px 0;
  flex-wrap: wrap;
}
.reaction {
  font-size: 1.6rem;
  cursor: pointer;
  transition: transform 0.15s;
  display: inline-block;
}
.reaction:hover { transform: scale(1.3); }

/* ── Correct / Wrong flash ── */
.correct-box {
  background: #d4edda; border: 2px solid #28a745;
  border-radius: 12px; padding: 14px 20px;
  font-weight: 700; color: #155724;
}
.wrong-box {
  background: #f8d7da; border: 2px solid #dc3545;
  border-radius: 12px; padding: 14px 20px;
  font-weight: 700; color: #721c24;
}
</style>
""", unsafe_allow_html=True)

# ─── Data ───────────────────────────────────────────────────────────────────

CURRICULUM = {
    "🟢 Level 1：初來乍到": {
        "icon": "🟢",
        "desc": "剛到英國，最基本生存英語",
        "lessons": [
            {
                "title": "超市買嘢 🛒 Supermarket",
                "subtitle": "Tesco / Sainsbury's / Waitrose",
                "dialogues": [
                    {"speaker": "🏪 店員", "en": "Do you need a bag for life?", "cantonese": "你要環保袋嗎？", "tip": "英國超市要收費買袋，叫 'bag for life'（可重用袋）。答 'Yes please' 或 'No thanks' 就夠!"},
                    {"speaker": "🏪 店員", "en": "Have you got a Clubcard / Nectar card?", "cantonese": "你有積分卡嗎？", "tip": "Tesco 叫 Clubcard，Sainsbury's 叫 Nectar card。有就話 'Yes' 然後出示，冇就 'No, I don't'"},
                    {"speaker": "👴 你", "en": "Excuse me, where's the rice?", "cantonese": "唔好意思，米喺邊度？", "tip": "亞洲米通常喺 'World Foods' 或 'International' 走廊。"},
                    {"speaker": "🏪 店員", "en": "That's £12.50 please.", "cantonese": "一共12鎊50便士。", "tip": "英國人讀價錢：'twelve pounds fifty'，唔係 'twelve point five'!"},
                    {"speaker": "👴 你", "en": "Sorry, can I pay by card?", "cantonese": "唔好意思，可唔可以刷卡？", "tip": "英國幾乎無處不接受 contactless（感應付款），50鎊以下直接碰一碰!"},
                ],
                "vocab": [
                    {"en": "Aisle", "cantonese": "走廊/排", "example": "Which aisle is the milk in?"},
                    {"en": "Self-checkout", "cantonese": "自助收銀", "example": "I'll use the self-checkout."},
                    {"en": "On offer", "cantonese": "特價緊", "example": "The biscuits are on offer."},
                    {"en": "Best before", "cantonese": "最佳食用日期", "example": "Check the best before date."},
                    {"en": "Reduced", "cantonese": "減價（快過期）", "example": "The bread is reduced to 20p."},
                ],
                "quiz": [
                    {"q": "店員話 'Do you need a bag for life?' 你想要袋，點答？", "options": ["Yes please!", "No I am fine", "What bag?", "Give me two"], "ans": 0, "explain": "'Yes please!' 係最禮貌又簡單嘅答法。英國人好鍾意加 'please'!"},
                    {"q": "你想問牛奶喺邊度，點問？", "options": ["Where is milk go?", "Excuse me, where's the milk?", "Milk where?", "I find milk please"], "ans": 1, "explain": "用 'Excuse me' 開頭好有禮貌，然後 'where's the [物品]?' 係標準問法。"},
                    {"q": "'That's £8.99 please' 係幾多錢？", "options": ["八百九十九鎊", "八鎊九十九便士", "八點九九鎊", "八十九鎊九"], "ans": 1, "explain": "£8.99 = eight pounds ninety-nine（便士）。'p' 係 'pence'（便士）。"},
                ],
                "funny_note": "😂 真實故事：有位香港阿叔問 'Where is the wonton?' 店員以為係 'want one'，以為佢要一件貨品... 所以記住帶個翻譯 app!",
            },
            {
                "title": "睇家庭醫生 🏥 GP",
                "subtitle": "National Health Service (NHS)",
                "dialogues": [
                    {"speaker": "🏥 接待員", "en": "Have you registered with us before?", "cantonese": "你之前有冇登記喺我哋診所？", "tip": "英國睇醫生要先 register（登記）做該診所 GP 病人，唔係隨便去!"},
                    {"speaker": "🏥 接待員", "en": "Can I take your date of birth?", "cantonese": "請問你出生日期？", "tip": "英國日期格式係 day/month/year，例如 5th March 1965 = 05/03/1965"},
                    {"speaker": "👴 你", "en": "I've had a sore throat for three days.", "cantonese": "我喉嚨痛咗三日。", "tip": "身體不適句型：'I've had [症狀] for [時間]' - 好實用!"},
                    {"speaker": "💊 醫生", "en": "I'll prescribe you some antibiotics.", "cantonese": "我幫你開抗生素。", "tip": "Prescribe = 開藥方。去藥房要話 'I'd like to collect a prescription'"},
                    {"speaker": "👴 你", "en": "Sorry, could you speak a bit slower please?", "cantonese": "唔好意思，可唔可以講慢少少？", "tip": "呢句係最重要嘅句子之一!英國醫生好多時講嘢好快，唔明就要問!"},
                ],
                "vocab": [
                    {"en": "GP (General Practitioner)", "cantonese": "家庭醫生", "example": "I need to see my GP."},
                    {"en": "Appointment", "cantonese": "預約", "example": "I'd like to make an appointment."},
                    {"en": "Prescription", "cantonese": "藥方", "example": "Here's your prescription."},
                    {"en": "Pharmacy / Chemist", "cantonese": "藥房", "example": "Take this to the pharmacy."},
                    {"en": "Referred", "cantonese": "轉介", "example": "You'll be referred to a specialist."},
                ],
                "quiz": [
                    {"q": "你喉嚨痛咗兩日，點樣告訴醫生？", "options": ["My throat hurt two day", "I've had a sore throat for two days.", "Throat pain since two days", "I have throat ache two days ago"], "ans": 1, "explain": "'I've had [症狀] for [時間]' 係標準英語，話你已經痛咗一段時間。"},
                    {"q": "你聽唔明醫生講，應該話？", "options": ["Repeat please!", "Hah?", "Could you speak a bit slower please?", "Talk slow!"], "ans": 2, "explain": "'Could you speak a bit slower please?' 係非常禮貌嘅請求，英國醫生一定會配合!"},
                ],
                "funny_note": "😄 小心!英國人話 'I'm fine' 唔一定係真係好。有次一個阿嫲話 'I'm not feeling too clever' - 唔係話自己唔聰明，係話自己唔舒服!英國人真係好含蓄!",
            },
            {
                "title": "搭巴士 🚌 Bus",
                "subtitle": "London Bus / Local Bus",
                "dialogues": [
                    {"speaker": "🚌 司機", "en": "Where are you heading?", "cantonese": "你去邊度？", "tip": "'Heading' = going。英國巴士有時要告訴司機目的地。"},
                    {"speaker": "👴 你", "en": "One to the town centre, please.", "cantonese": "一張去市中心，謝謝。", "tip": "倫敦巴士用 Oyster card 或 contactless，唔收現金!"},
                    {"speaker": "👴 你", "en": "Excuse me, does this bus stop at Tesco?", "cantonese": "唔好意思，呢架巴士有冇喺Tesco停？", "tip": "唔確定就問!英國人好樂意幫忙，唔問係你蝕底!"},
                    {"speaker": "🚌 司機", "en": "Ring the bell for your stop, love.", "cantonese": "快到站時按鈴，親。", "tip": "'Love' / 'dear' / 'darling' - 英國長者或服務員常用，係友善稱呼，唔係真係叫你做愛人!"},
                    {"speaker": "👴 你", "en": "Sorry, is this seat taken?", "cantonese": "唔好意思，呢個位有人坐嗎？", "tip": "空位就可以坐，但英國人會先問一聲，係禮貌。"},
                ],
                "vocab": [
                    {"en": "Bus stop", "cantonese": "巴士站", "example": "Wait at the bus stop."},
                    {"en": "Single / Return", "cantonese": "單程 / 來回", "example": "A single to Oxford please."},
                    {"en": "Ring the bell", "cantonese": "按鈴", "example": "Ring the bell before your stop."},
                    {"en": "Next stop", "cantonese": "下一站", "example": "The next stop is High Street."},
                    {"en": "Oyster card", "cantonese": "倫敦交通卡", "example": "Tap your Oyster card."},
                ],
                "quiz": [
                    {"q": "你想問個位有冇人坐，點問？", "options": ["This seat free?", "Is this seat taken?", "Anyone sitting here?", "Can I sit?"], "ans": 1, "explain": "'Is this seat taken?' 係最標準有禮嘅問法。"},
                    {"q": "司機叫你 'ring the bell for your stop'，係話你？", "options": ["要你打電話", "快到站時要按鈴", "要你唱歌", "要你站起來"], "ans": 1, "explain": "英國巴士要自己按鈴通知司機停站，唔按就唔停!"},
                ],
                "funny_note": "🤣 有個香港阿伯上倫敦巴士，司機話 'Mind the gap!' 佢以為係 'Mind the Gap' 地鐵廣告，以為搭錯車，立即衝落車!其實係叫你小心落差😂",
            },
        ]
    },
    "🟡 Level 2：融入社區": {
        "icon": "🟡",
        "desc": "銀行、郵局、街坊閒聊",
        "lessons": [
            {
                "title": "銀行開戶 🏦 Bank",
                "subtitle": "Barclays / HSBC / Lloyds",
                "dialogues": [
                    {"speaker": "🏦 職員", "en": "What type of account would you like to open?", "cantonese": "你想開哪種戶口？", "tip": "Current account（往來戶口，有debit card）vs Savings account（儲蓄戶口）"},
                    {"speaker": "👴 你", "en": "I'd like to open a current account please.", "cantonese": "我想開一個往來戶口，謝謝。", "tip": "'I'd like to...' 係非常好用嘅禮貌句型，比 'I want' 客氣好多!"},
                    {"speaker": "🏦 職員", "en": "Can I see two forms of ID?", "cantonese": "我可以看兩份身份證明文件嗎？", "tip": "通常需要：護照 + 住址証明（utility bill 或 council letter）"},
                    {"speaker": "👴 你", "en": "How long will it take to set up?", "cantonese": "需要多長時間設置？", "tip": "英國銀行通常3-5個工作天寄卡，有些 same day!"},
                    {"speaker": "🏦 職員", "en": "You'll receive your card within 5 working days.", "cantonese": "你會在5個工作天內收到卡。", "tip": "Working days = 工作天（唔包括週末同公眾假期）"},
                ],
                "vocab": [
                    {"en": "Current account", "cantonese": "往來戶口", "example": "I have a current account with Barclays."},
                    {"en": "Sort code", "cantonese": "銀行分行代碼", "example": "What's the sort code?"},
                    {"en": "Direct debit", "cantonese": "自動轉帳付款", "example": "Set up a direct debit."},
                    {"en": "Standing order", "cantonese": "定期轉帳", "example": "I have a standing order for rent."},
                    {"en": "Overdraft", "cantonese": "透支", "example": "I went into overdraft."},
                ],
                "quiz": [
                    {"q": "你想開戶口，點禮貌地說？", "options": ["Give me account!", "I want open account", "I'd like to open an account please.", "Account opening now"], "ans": 2, "explain": "'I'd like to...' 係英語中最客氣嘅要求方式，比 'I want' 有禮好多!"},
                    {"q": "'Working days' 係咩意思？", "options": ["任何日子", "工作天（唔包括週末）", "工廠工作", "加班時間"], "ans": 1, "explain": "Working days = Monday to Friday，唔包括Saturday, Sunday 同 Bank Holidays。"},
                ],
                "funny_note": "😂 有位阿嫲去銀行，職員問 'Are you the account holder?' 佢答 'No, my son hold the account!' 職員傻眼了... Account holder = 戶口持有人，唔係真係拿住本戶口!",
            },
            {
                "title": "街坊閒聊 ☁️ Small Talk",
                "subtitle": "最英國的藝術：講天氣!",
                "dialogues": [
                    {"speaker": "🏡 鄰居", "en": "Lovely weather we're having, isn't it?", "cantonese": "天氣真好啊，係咪？", "tip": "英國人永遠講天氣!即使天氣唔好，都可以答 'Yes, for a change!' （難得係!）"},
                    {"speaker": "👴 你", "en": "Dreadful, isn't it? Typical British weather!", "cantonese": "天氣真糟糕，係咪？典型英國天氣!", "tip": "英國人自己都嫌自己國家天氣差，你咁講佢哋會覺得你係自己人!"},
                    {"speaker": "🏡 鄰居", "en": "Have you settled in alright?", "cantonese": "你適應得好嗎？", "tip": "'Settled in' = 安頓好。可以答 'Getting there!' 或 'Slowly but surely!'"},
                    {"speaker": "👴 你", "en": "Slowly but surely! Still getting used to the cold!", "cantonese": "慢慢來!仍然習慣緊寒冷!", "tip": "'Slowly but surely' = 慢慢但肯定地。英國人超喜歡呢個說法!"},
                    {"speaker": "🏡 鄰居", "en": "Let me know if you need anything, won't you?", "cantonese": "如果有需要的話記得告訴我啊!", "tip": "英國鄰居通常都好friendly!可以答 'That's very kind, thank you!'"},
                ],
                "vocab": [
                    {"en": "Lovely / Dreadful", "cantonese": "可愛/好靚 / 糟糕", "example": "Lovely day! / Dreadful weather!"},
                    {"en": "Settled in", "cantonese": "安頓好", "example": "Have you settled in yet?"},
                    {"en": "Typical!", "cantonese": "典型!（帶諷刺）", "example": "Rain again? Typical!"},
                    {"en": "Mustn't grumble", "cantonese": "唔好抱怨（英式幽默）", "example": "How are you? - Mustn't grumble!"},
                    {"en": "Cheers", "cantonese": "謝謝 / 再見（非正式）", "example": "Cheers, mate!"},
                ],
                "quiz": [
                    {"q": "鄰居話 'Lovely weather!' 但係落緊雨，你應該？", "options": ["話 'No it isn't!'", "帶幽默答 'Yes, typical British weather!'", "唔出聲走開", "話 'I hate rain'"], "ans": 1, "explain": "英國人喜歡幽默地談天氣。帶笑意咁答最自然，顯示你融入文化!"},
                    {"q": "'Mustn't grumble' 係咩意思？", "options": ["我係啞巴", "生活還可以，唔好抱怨", "我唔想說話", "我有問題"], "ans": 1, "explain": "呢句係英式幽默，表示生活唔係太差，係一種樂觀低調的態度!"},
                ],
                "funny_note": "🤣 英國人最典型嘅對話：\n'How are you?' - 'Not bad!'\n'Weather's terrible!' - 'Could be worse!'\n'Bit chilly today!' - 'At least it's not raining!'\n\n全部都係負負得正嘅正面主義，真係一種藝術!",
            },
        ]
    },
    "🔴 Level 3：自信表達": {
        "icon": "🔴",
        "desc": "打電話、投訴、看急症",
        "lessons": [
            {
                "title": "致電預約 📞 Phone Calls",
                "subtitle": "打電話係最難的!",
                "dialogues": [
                    {"speaker": "📞 接線員", "en": "Hello, this is [Company], how can I help you?", "cantonese": "你好，呢度係[公司]，請問有咩可以幫到你？", "tip": "聽電話好難!先話 'Sorry, could you repeat that?' 冇問題!"},
                    {"speaker": "👴 你", "en": "Hello, I'd like to make an appointment please.", "cantonese": "你好，我想預約，謝謝。", "tip": "電話開場白：'Hello, my name is [名字], I'm calling about...'"},
                    {"speaker": "📞 接線員", "en": "Can I take your name and date of birth?", "cantonese": "請問你名字同出生日期？", "tip": "準備好：名字（英文）、出生日期（日/月/年）、地址、NHS number"},
                    {"speaker": "👴 你", "en": "Sorry, I didn't catch that. Could you repeat please?", "cantonese": "唔好意思，我聽唔清楚，可以重複一次嗎？", "tip": "'I didn't catch that' = 我聽唔到。比 'What?' 客氣好多!"},
                    {"speaker": "👴 你", "en": "Could you spell that for me please?", "cantonese": "可以幫我逐個字母拼嗎？", "tip": "唔確定對方講緊咩字，就叫佢spell!英國人習慣呢樣。"},
                ],
                "vocab": [
                    {"en": "Hold the line", "cantonese": "請稍等（唔好掛線）", "example": "Please hold the line."},
                    {"en": "Put you through", "cantonese": "幫你轉駁", "example": "I'll put you through to the right department."},
                    {"en": "Leave a message", "cantonese": "留言", "example": "Would you like to leave a message?"},
                    {"en": "Call back", "cantonese": "回電", "example": "I'll ask them to call you back."},
                    {"en": "Press 1 for...", "cantonese": "按1選擇...", "example": "Press 1 for appointments."},
                ],
                "quiz": [
                    {"q": "你聽唔到對方講緊咩，禮貌地說？", "options": ["What?! WHAT?!", "Sorry, I didn't catch that. Could you repeat please?", "Speak up!", "I cannot hear you"], "ans": 1, "explain": "'I didn't catch that' 係非常有禮的說法，顯示係聽力問題，唔係對方問題。"},
                    {"q": "'Hold the line' 係叫你點做？", "options": ["掛線", "繼續等候", "握住電話線", "上網"], "ans": 1, "explain": "'Hold the line' = 請稍等，唔好掛線。通常接線員幫你轉駁或查資料時會用。"},
                ],
                "funny_note": "😅 打電話真係最恐怖!有位阿叔打去NHS，自動語音系統問 'Press 1 for GP'，佢緊張到按了'1111'... 結果去了急症!記住：先深呼吸，再按鍵!",
            },
        ]
    }
}

PRONUNCIATION_TRAPS = [
    {"word": "Worcester", "wrong": "沃-切-斯-特", "right": "Wooster（Wuster）", "note": "🤯 英國地名最tricky!"},
    {"word": "Leicester", "wrong": "李-切-斯-特", "right": "Lester", "note": "😱 縮短到你唔信!"},
    {"word": "Edinburgh", "wrong": "愛丁-堡（burg）", "right": "Edinbra / Edinbruh", "note": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 蘇格蘭人會更正你!"},
    {"word": "Gloucester", "wrong": "格洛-切-斯-特", "right": "Gloster", "note": "🧀 同個芝士同音!"},
    {"word": "Queue", "wrong": "Q-U-E-U-E（5個字母）", "right": "Kyoo（讀'Q'）", "note": "😂 英國人最愛排的東西!"},
    {"word": "Fortnight", "wrong": "四十夜", "right": "兩個星期!", "note": "📅 英國人成日用，唔係奇幻詞彙!"},
    {"word": "Cheers", "wrong": "只係舉杯", "right": "謝謝/再見/好的（萬能詞!）", "note": "🍺 英國人用法超廣!"},
    {"word": "Quite", "wrong": "相當好", "right": "可能係'普通'!", "note": "😐 'Quite good' = 勉強算好，唔係很好!"},
]

CULTURAL_TIPS = [
    {"tip": "排隊係神聖的!", "detail": "英國人對排隊嘅認真程度好過宗教。永遠要排隊，插隊係最大失禮!", "emoji": "🇬🇧"},
    {"tip": "'Sorry' 有N種意思", "detail": "'Sorry' = 對唔住 / 你講咩？/ 讓我過 / 你撞咗我（係你自己道歉!）", "emoji": "😅"},
    {"tip": "茶係解決一切嘅方案", "detail": "有問題？食虧？天災？英國人第一個反應係 'Shall I put the kettle on?'（我燒水啦？）", "emoji": "☕"},
    {"tip": "'Fine' 可能唔係Fine", "detail": "'I'm fine' / 'It's fine' 有時係禮貌假客氣。要留意語調!", "emoji": "🤔"},
    {"tip": "地鐵要 'Mind the Gap'", "detail": "倫敦地鐵每站都會廣播，係指月台同車廂之間嘅空隙，要小心踏空!", "emoji": "🚇"},
    {"tip": "小費文化", "detail": "餐廳通常10-12.5%，有時已包含service charge。Check bill先!Pub通常唔需要小費。", "emoji": "💷"},
]

# ─── Speaking Practice Scenarios ────────────────────────────────────────────

SPEAKING_SCENARIOS = [
    {
        "id": "supermarket",
        "title": "🛒 超市買嘢",
        "subtitle": "Tesco - 同收銀員對話",
        "difficulty": "🟢 初級",
        "scene_desc": "你喺 Tesco 收銀處，收銀員正在掃描你嘅貨品。",
        "ai_role": "friendly Tesco cashier named Sarah",
        "ai_persona_hk": "你係一個友善的Tesco收銀員Sarah",
        "steps": [
            {
                "step": 1,
                "prompt_hk": "收銀員問你要唔要袋",
                "target_en": "Yes please, just one bag.",
                "ai_line": "Hi there! Do you need a bag for life today?",
                "keywords": ["yes", "bag", "please"],
                "hint": "答 'Yes please' 再加要幾多袋",
                "tip": "英國超市袋要收費，一般環保袋 10p-30p",
            },
            {
                "step": 2,
                "prompt_hk": "收銀員問你有冇積分卡",
                "target_en": "No, I don't have one.",
                "ai_line": "Do you have a Clubcard with us?",
                "keywords": ["no", "don't", "have"],
                "hint": "冇積分卡就話 'No, I don't have one'",
                "tip": "Clubcard 係 Tesco 積分卡，免費申請，長期住英國值得辦!",
            },
            {
                "step": 3,
                "prompt_hk": "收銀員報價錢，你問可唔可以用卡付款",
                "target_en": "Can I pay by card please?",
                "ai_line": "That's £15.40 altogether!",
                "keywords": ["card", "pay", "can"],
                "hint": "問 'Can I pay by card?' 或 'Do you take card?'",
                "tip": "英國幾乎全部超市都接受 contactless，50鎊以下直接碰!",
            },
            {
                "step": 4,
                "prompt_hk": "收銀員說謝謝，你道別",
                "target_en": "Thank you, bye bye!",
                "ai_line": "There you go! Have a lovely day!",
                "keywords": ["thank", "bye", "cheers"],
                "hint": "'Thank you, bye!' 或 'Cheers, have a good one!'",
                "tip": "'Cheers' 喺英國係萬能詞：謝謝、再見、好的都可以用!",
            },
        ],
    },
    {
        "id": "gp_appointment",
        "title": "🏥 預約GP",
        "subtitle": "打電話去診所預約",
        "difficulty": "🟡 中級",
        "scene_desc": "你打電話去GP診所，想預約睇醫生。你喉嚨痛咗兩日。",
        "ai_role": "NHS GP receptionist named Emma",
        "ai_persona_hk": "你係一個NHS GP接待員Emma",
        "steps": [
            {
                "step": 1,
                "prompt_hk": "接待員接聽，你介紹自己同說明目的",
                "target_en": "Hello, I'd like to make an appointment please.",
                "ai_line": "Good morning, Riverside Medical Centre, how can I help you?",
                "keywords": ["appointment", "like", "make", "hello"],
                "hint": "'Hello, I'd like to make an appointment please'",
                "tip": "電話開場要清晰：名字 + 目的。唔好只係說 'Hello!'",
            },
            {
                "step": 2,
                "prompt_hk": "接待員問你哪裡不舒服，你說喉嚨痛了兩天",
                "target_en": "I've had a sore throat for two days.",
                "ai_line": "Of course! Can I ask what the problem is?",
                "keywords": ["sore", "throat", "two", "days", "had"],
                "hint": "'I've had a sore throat for two days'",
                "tip": "'I've had [症狀] for [時間]' 係睇醫生最實用嘅句型!",
            },
            {
                "step": 3,
                "prompt_hk": "接待員問你什麼時候方便，你說下午比較好",
                "target_en": "In the afternoon would be better for me.",
                "ai_line": "We have a slot on Thursday - would morning or afternoon suit you?",
                "keywords": ["afternoon", "better", "prefer", "suit"],
                "hint": "'Afternoon would be better' 或 'I prefer afternoon'",
                "tip": "英國人常用 'suit' 問方不方便：'Does that suit you?'",
            },
            {
                "step": 4,
                "prompt_hk": "接待員確認預約，你表示感謝",
                "target_en": "Thank you so much, goodbye.",
                "ai_line": "Perfect! Thursday at 2pm it is. We'll send you a text reminder. Is there anything else?",
                "keywords": ["thank", "bye", "goodbye"],
                "hint": "'Thank you so much, goodbye' 或 'Thanks very much, bye!'",
                "tip": "電話結束要說 'goodbye' 或 'bye'，唔好突然掛線!",
            },
        ],
    },
    {
        "id": "bus",
        "title": "🚌 搭巴士",
        "subtitle": "問路 + 買票",
        "difficulty": "🟢 初級",
        "scene_desc": "你係巴士站，想搭巴士去市中心，唔確定係唔係呢架。",
        "ai_role": "friendly bus driver",
        "ai_persona_hk": "你係一個友善的英國巴士司機",
        "steps": [
            {
                "step": 1,
                "prompt_hk": "問司機呢架巴士去唔去市中心",
                "target_en": "Excuse me, does this bus go to the town centre?",
                "ai_line": "Morning! Hop on then!",
                "keywords": ["town", "centre", "bus", "go", "excuse"],
                "hint": "'Excuse me, does this bus go to the town centre?'",
                "tip": "唔確定就問!英國人好樂意幫忙，唔問係你蝕底!",
            },
            {
                "step": 2,
                "prompt_hk": "司機說係，你買單程票",
                "target_en": "One single to the town centre please.",
                "ai_line": "Yes it does! Where are you heading?",
                "keywords": ["single", "one", "town", "please"],
                "hint": "'One single to [地點] please'",
                "tip": "Single = 單程，Return = 來回。倫敦巴士只收 Oyster/contactless!",
            },
            {
                "step": 3,
                "prompt_hk": "你唔知在哪裡下車，請司機提醒你",
                "target_en": "Could you let me know when we get to the town centre please?",
                "ai_line": "That'll be £2.50 please!",
                "keywords": ["let", "know", "when", "town", "please"],
                "hint": "'Could you let me know when we get to the town centre?'",
                "tip": "唔熟路唔好害羞!司機通常都好好人會提醒你。",
            },
        ],
    },
    {
        "id": "neighbour",
        "title": "☁️ 同鄰居閒聊",
        "subtitle": "講天氣 - 英國必修課!",
        "difficulty": "🟡 中級",
        "scene_desc": "你係門口遇見鄰居 Margaret，一個典型英國老太太。天氣陰陰地但未落雨。",
        "ai_role": "typical friendly British neighbour named Margaret, 70s, loves talking about weather and gardens",
        "ai_persona_hk": "你係一個典型英國老太太Margaret，70歲，愛聊天氣同花園",
        "steps": [
            {
                "step": 1,
                "prompt_hk": "打招呼，評論一下天氣",
                "target_en": "Good morning! Bit cloudy today, isn't it?",
                "ai_line": "Oh hello there, lovely to see you!",
                "keywords": ["morning", "cloudy", "weather", "hello", "good"],
                "hint": "'Good morning! Bit cloudy today, isn't it?'",
                "tip": "英國打招呼必提天氣!'Bit [天氣形容詞] today, isn't it?' 係萬能句!",
            },
            {
                "step": 2,
                "prompt_hk": "鄰居問你喺英國生活怎樣，你說慢慢適應中",
                "target_en": "Getting there slowly! Still getting used to the weather.",
                "ai_line": "Yes, typical isn't it! Are you settling in alright, dear?",
                "keywords": ["getting", "used", "slowly", "settling"],
                "hint": "'Getting there slowly! Still getting used to the weather.'",
                "tip": "'Getting there' = 慢慢進步中，係好正面嘅英式說法!",
            },
            {
                "step": 3,
                "prompt_hk": "鄰居熱情邀請你有需要時找她，你感謝她",
                "target_en": "That's very kind, thank you so much!",
                "ai_line": "Oh don't worry, you'll love it here! Let me know if you ever need anything, won't you?",
                "keywords": ["kind", "thank", "much"],
                "hint": "'That's very kind, thank you so much!'",
                "tip": "'That's very kind of you' 係英國人最愛聽嘅感謝方式!",
            },
        ],
    },
]

# ─── Groq AI helper ──────────────────────────────────────────────────────────

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def groq_score_speech(client, target_en: str, user_said: str, scenario_title: str) -> dict:
    """Ask Groq to score the user's spoken attempt vs target sentence."""
    prompt = f"""你係一個英語老師，專門幫助香港移民學英語。
學生嘗試說："{user_said}"
目標句子係："{target_en}"
情境：{scenario_title}

請用廣東話評分，格式如下（JSON）：
{{
  "score": 0-100的整數分數,
  "verdict": "一句話評語（廣東話，帶鼓勵，可加少少幽默）",
  "pronunciation_tips": "1-2句發音建議（廣東話）",
  "grammar_ok": true或false,
  "grammar_note": "如果語法有問題，簡短說明（廣東話），否則留空",
  "encouragement": "一句鼓勵說話（廣東話，要開心有趣）"
}}

評分標準：
- 90-100：非常接近，意思清晰，發音正確
- 70-89：基本正確，少少問題
- 50-69：意思大致表達到，但有明顯問題
- 50以下：需要再練習

只回答JSON，不要其他文字。"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7,
        )
        raw = response.choices[0].message.content.strip()
        # strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "score": 70,
            "verdict": "唔錯!繼續練習!",
            "pronunciation_tips": "記得清晰發音每個音節。",
            "grammar_ok": True,
            "grammar_note": "",
            "encouragement": "加油!每次開口都係進步!",
        }

def groq_ai_response(client, ai_role: str, ai_line: str, user_said: str, step_context: str) -> str:
    """Get AI (playing UK person) natural follow-up response."""
    prompt = f"""You are playing the role of a {ai_role} in the UK.
The scripted line you just said was: "{ai_line}"
The Hong Kong immigrant learner replied: "{user_said}"
Context: {step_context}

Respond naturally in character (1-2 sentences max). Be warm, friendly, and encouraging.
If their English was unclear, gently respond as if you understood the gist.
Stay in character, keep it simple and natural British English."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except:
        return "Oh lovely, thank you! Have a wonderful day!"




# ─── Google Sheets helpers ────────────────────────────────────────────────────

SHEET_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_NAME = "UK_English_Learning_History"
SHEET_HEADERS = ["timestamp", "user_id", "activity_type", "scenario", "score", "points_earned", "details"]

def get_gsheet():
    """Return (worksheet, error_msg). worksheet is None on failure."""
    creds_dict = st.secrets.get("GOOGLE_CREDS", {})
    if not creds_dict:
        return None, "no_creds"
    try:
        creds = Credentials.from_service_account_info(dict(creds_dict), scopes=SHEET_SCOPES)
        client = gspread.authorize(creds)
        try:
            sh = client.open(SHEET_NAME)
        except gspread.SpreadsheetNotFound:
            sh = client.create(SHEET_NAME)
            sh.share(creds_dict.get("client_email", ""), perm_type="user", role="writer")
        ws = sh.sheet1
        # ensure headers
        if ws.row_count == 0 or ws.cell(1, 1).value != "timestamp":
            ws.insert_row(SHEET_HEADERS, 1)
        return ws, None
    except Exception as e:
        return None, str(e)

def log_activity(activity_type: str, scenario: str, score: int, points: int, details: str = ""):
    """Append one row to the Google Sheet. Silent on failure."""
    ws, err = get_gsheet()
    if ws is None:
        return
    user_id = st.session_state.get("user_id", "unknown")
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_id,
        activity_type,
        scenario,
        score,
        points,
        details,
    ]
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception:
        pass  # never crash the app over logging

def load_history(user_id: str) -> list[dict]:
    """Load all rows for this user_id from the sheet."""
    ws, err = get_gsheet()
    if ws is None:
        return []
    try:
        records = ws.get_all_records()
        return [r for r in records if str(r.get("user_id", "")) == user_id]
    except Exception:
        return []

# ─── Session State ──────────────────────────────────────────────────────────
if "points" not in st.session_state:
    st.session_state.points = 0
if "completed" not in st.session_state:
    st.session_state.completed = set()
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "sp_scenario" not in st.session_state:
    st.session_state.sp_scenario = None
if "sp_step" not in st.session_state:
    st.session_state.sp_step = 0
if "sp_results" not in st.session_state:
    st.session_state.sp_results = []
if "sp_ai_reply" not in st.session_state:
    st.session_state.sp_ai_reply = {}
if "user_id" not in st.session_state:
    import hashlib, socket
    raw = str(datetime.now().date()) + socket.gethostname()
    st.session_state.user_id = hashlib.md5(raw.encode()).hexdigest()[:10]

def add_points(n):
    st.session_state.points += n
    st.session_state.streak += 1

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇬🇧 英國生活英語")
    st.markdown("### 你嘅學習進度")
    
    total_lessons = sum(len(v["lessons"]) for v in CURRICULUM.values())
    done = len(st.session_state.completed)
    pct = int(done / total_lessons * 100) if total_lessons else 0
    
    st.markdown(f"""
    <div style='margin:12px 0;'>
      <div style='font-size:0.88rem; opacity:0.8; margin-bottom:6px;'>完成課程: {done}/{total_lessons}</div>
      <div class='progress-wrap'>
        <div class='progress-fill' style='width:{pct}%;'></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align:center; padding:16px; background:rgba(255,255,255,0.12); border-radius:14px; margin:12px 0;'>
      <div style='font-size:2.5rem; font-weight:900;'>&#11088; {st.session_state.points}</div>
      <div style='font-size:0.85rem; opacity:0.8;'>積分</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.streak > 0:
        st.markdown(f"&#128293; 連勝 {st.session_state.streak} 題!")
    
    st.markdown("---")
    st.markdown("### 📖 選擇模式")
    mode = st.selectbox("學習模式", 
        ["🏠 主頁", "📚 系統課程", "🎤 對話練習", "📊 學習歷史", "🔤 發音陷阱", "🎭 文化小貼士", "🧠 大挑戰"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 💡 今日金句")
    daily_quotes = [
        "'Every day is a school day!' - 每天都是學習日!",
        "'When in Rome, do as the Romans do!' - 入鄉隨俗!",
        "'Practice makes perfect!' - 熟能生巧!",
        "'Better late than never!' - 好過冇!",
    ]
    st.markdown(f"*{random.choice(daily_quotes)}*")

# ─── Main Content ────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero-banner'>
  <h1>🇬🇧 英國生活英語學習班</h1>
  <p>專為香港移民設計 · 輕鬆有趣 · 從零開始征服英倫生活!</p>
</div>
""", unsafe_allow_html=True)

# ── HOME ─────────────────────────────────────────────────────────────────────
if "主頁" in mode:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='lesson-card'>
          <div style='font-size:2rem;'>📚</div>
          <h3 style='margin:8px 0 4px;'>系統課程</h3>
          <p style='color:#666; font-size:0.9rem;'>Level 1-3 漸進式學習<br>超市→醫生→銀行→打電話</p>
          <span class='level-badge level-1'>3個難度</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='lesson-card green'>
          <div style='font-size:2rem;'>🎤</div>
          <h3 style='margin:8px 0 4px;'>開口練習</h3>
          <p style='color:#666; font-size:0.9rem;'>固定劇本 · 聆聽示範<br>AI即時評分你嘅發音!</p>
          <span class='level-badge level-1'>4個場景</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='lesson-card gold'>
          <div style='font-size:2rem;'>🔤</div>
          <h3 style='margin:8px 0 4px;'>發音陷阱</h3>
          <p style='color:#666; font-size:0.9rem;'>英國地名 · 古怪拼音<br>唔知就會出醜嘅發音!</p>
          <span class='level-badge level-2'>8個陷阱</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='lesson-card red'>
          <div style='font-size:2rem;'>&#128202;</div>
          <h3 style='margin:8px 0 4px;'>&#23416;&#32244;&#27511;&#21490;</h3>
          <p style='color:#666; font-size:0.9rem;'>Google Sheets &#20132;&#20856;<br>&#35352;&#37636;&#27599;&#27425;&#20998;&#25976;&#36914;&#27493;!</p>
          <span class='level-badge level-1'>&#33258;&#21205;&#20132;&#20856;</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 今日挑戰")
    
    col_a, col_b = st.columns([3,1])
    with col_a:
        daily_challenges = [
            "💬 學識今日對話：買超市時主動問店員",
            "📞 練習打電話預約醫生",
            "☁️ 同鄰居傾一次天氣",
            "🚌 搭巴士時問站名",
        ]
        today_challenge = daily_challenges[datetime.now().weekday() % len(daily_challenges)]
        st.markdown(f"""
        <div class='lesson-card green'>
          <h4 style='margin:0 0 8px;'>{today_challenge}</h4>
          <p style='color:#666; font-size:0.9rem;'>完成挑戰賺取 +20 積分!</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        if st.button("✅ 完成咗!\n+20分", use_container_width=True):
            add_points(20)
            st.success("🎉 叻仔!+20分!")
            st.balloons()
    
    st.markdown("---")
    st.markdown("### 😂 今日笑話")
    jokes = [
        {"joke": "香港人去英國餐廳，問服務員 'Do you have dim sum?'\n服務員：'Some what?'\n阿叔：'Not some what, DIM SUM!'", "punchline": "😂 其實可以話 'Do you have Chinese dishes?' 更清楚!"},
        {"joke": "阿嫲入銀行想問 'Can I see the manager?'\n但係緊張到講咗 'Can I see the monster?'", "punchline": "😂 幸好英國銀行職員唔介意!記住：Manager = 經理"},
        {"joke": "在英國超市，阿伯問 'Where is the fish ball?'\n店員搵了5分鐘，最後話 'Sorry we don't sell sports equipment here.'", "punchline": "😂 魚蛋 = fish ball，英國人以為係運動用品!"},
        {"joke": "阿叔搭地鐵，廣播 'This is a Piccadilly line train.' 佢問身邊人：'皮卡啲利係咩？係口袋嗎？'", "punchline": "😄 Piccadilly = 地鐵線名，唔係 'piccolo' 嘅意思!"},
    ]
    joke_of_day = jokes[datetime.now().day % len(jokes)]
    st.markdown(f"""
    <div class='lesson-card' style='background:linear-gradient(135deg,#fff8e1,#fff3e0);'>
      <pre style='font-family:inherit; white-space:pre-wrap; margin:0; font-size:0.95rem;'>{joke_of_day['joke']}</pre>
      <div style='margin-top:12px; color:#856404; font-size:0.9rem;'>{joke_of_day['punchline']}</div>
    </div>
    """, unsafe_allow_html=True)

# ── CURRICULUM ───────────────────────────────────────────────────────────────
elif "系統課程" in mode:
    st.markdown("## 📚 系統課程")
    
    selected_level = st.selectbox("選擇難度", list(CURRICULUM.keys()))
    level_data = CURRICULUM[selected_level]
    
    st.markdown(f"""
    <div class='funfact'>
      {level_data['icon']} <strong>{selected_level.split('：')[1]}</strong> - {level_data['desc']}
    </div>
    """, unsafe_allow_html=True)
    
    for li, lesson in enumerate(level_data["lessons"]):
        lesson_key = f"{selected_level}_{li}"
        done_marker = "✅ " if lesson_key in st.session_state.completed else ""
        
        with st.expander(f"{done_marker}{lesson['title']} - {lesson['subtitle']}", expanded=(li==0)):
            
            # Dialogues
            st.markdown("### 💬 對話練習")
            st.markdown("<div class='audio-hint'>🔊 建議：大聲讀出每句英文，練習開口!</div>", unsafe_allow_html=True)
            
            for d in lesson["dialogues"]:
                if "店員" in d["speaker"] or "醫生" in d["speaker"] or "接待員" in d["speaker"] or "接線員" in d["speaker"] or "職員" in d["speaker"] or "鄰居" in d["speaker"] or "司機" in d["speaker"]:
                    st.markdown(f"""
                    <div>
                      <div class='bubble-label' style='margin-left:20px;'>{d['speaker']}</div>
                      <div class='bubble-uk'>
                        <strong>&#128266; {d['en']}</strong><br>
                        <span style='opacity:0.8; font-size:0.9rem;'>{d['cantonese']}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align:right;'>
                      <div class='bubble-label' style='margin-right:20px;'>{d['speaker']}</div>
                      <div class='bubble-hk'>
                        <strong>&#128483;&#65039; {d['en']}</strong><br>
                        <span style='opacity:0.8; font-size:0.9rem;'>{d['cantonese']}</span>
                      </div>
                      <div class='clear'></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='tip-box'>
                  <span class='tip-icon'>&#128161;</span> {d['tip']}
                </div>
                """, unsafe_allow_html=True)
            
            # Vocab
            st.markdown("### 📖 重點詞彙")
            vcols = st.columns(len(lesson["vocab"]) if len(lesson["vocab"]) <= 3 else 3)
            for vi, v in enumerate(lesson["vocab"]):
                with vcols[vi % 3]:
                    st.markdown(f"""
                    <div style='background:white; border-radius:12px; padding:14px; text-align:center; box-shadow:0 3px 10px rgba(0,0,0,0.07); margin:6px 0;'>
                      <div style='font-size:1.1rem; font-weight:800; color:#1D3557;'>{v['en']}</div>
                      <div style='color:#E63946; font-weight:700; margin:4px 0;'>{v['cantonese']}</div>
                      <div style='font-size:0.82rem; color:#888; font-style:italic;'>"{v['example']}"</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Funny note
            st.markdown(f"""
            <div class='lesson-card' style='background:linear-gradient(135deg,#ffeaa7,#fdcb6e10); border-left-color:#fdcb6e;'>
              {lesson['funny_note']}
            </div>
            """, unsafe_allow_html=True)
            
            # Quiz
            st.markdown("### 🧠 小測驗")
            all_correct = True
            for qi, q in enumerate(lesson["quiz"]):
                qkey = f"{lesson_key}_q{qi}"
                st.markdown(f"""
                <div class='quiz-box'>
                  <div class='quiz-q'>Q{qi+1}. {q['q']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                choice = st.radio(
                    f"選擇答案 (問題 {qi+1})",
                    q["options"],
                    key=qkey,
                    label_visibility="collapsed"
                )
                
                if st.button(f"確認答案 ✓", key=f"btn_{qkey}"):
                    chosen_idx = q["options"].index(choice)
                    if chosen_idx == q["ans"]:
                        st.markdown(f"""<div class='correct-box'>&#9989; 答對了!+10分<br><small>{q['explain']}</small></div>""", unsafe_allow_html=True)
                        if qkey not in st.session_state.quiz_answers:
                            add_points(10)
                            st.session_state.quiz_answers[qkey] = True
                            log_activity("quiz", lesson["title"], 100, 10, q["q"][:80])
                    else:
                        st.markdown(f"""<div class='wrong-box'>&#10060; 差少少!答案係：<strong>{q['options'][q['ans']]}</strong><br><small>{q['explain']}</small></div>""", unsafe_allow_html=True)
                        all_correct = False
                        if qkey not in st.session_state.quiz_answers:
                            st.session_state.quiz_answers[qkey] = False
            
            # Complete lesson
            col1, col2 = st.columns([2,1])
            with col1:
                if st.button(f"&#9989; 完成呢課!+15分", key=f"complete_{lesson_key}", use_container_width=True):
                    if lesson_key not in st.session_state.completed:
                        st.session_state.completed.add(lesson_key)
                        add_points(15)
                        st.success("🎉 叻仔!完成咗!繼續加油!")
                        st.balloons()
                    else:
                        st.info("已完成過呢課!")

# ── VOICE PRACTICE ───────────────────────────────────────────────────────────
elif "對話練習" in mode:
    st.markdown("## 🎤 開口練習：跟住講!")

    # ── CSS for voice practice ──
    st.markdown("""
    <style>
    .scene-card {
      background: linear-gradient(135deg, #1D3557 0%, #2a4a7f 100%);
      color: white; border-radius: 20px; padding: 24px 28px;
      margin-bottom: 20px; position: relative; overflow: hidden;
    }
    .scene-card::after {
      content: attr(data-emoji);
      position: absolute; right: 20px; top: 50%; transform: translateY(-50%);
      font-size: 5rem; opacity: 0.15;
    }
    .scene-card h2 { margin: 0 0 6px; font-size: 1.6rem; }
    .scene-card p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

    .step-row {
      display: flex; align-items: flex-start; gap: 14px;
      background: white; border-radius: 16px;
      padding: 18px 20px; margin: 10px 0;
      box-shadow: 0 3px 12px rgba(0,0,0,0.07);
    }
    .step-num {
      background: #1D3557; color: white;
      border-radius: 50%; width: 32px; height: 32px;
      display: flex; align-items: center; justify-content: center;
      font-weight: 900; font-size: 0.9rem; flex-shrink: 0;
    }
    .step-content { flex: 1; }
    .step-role { font-size: 0.78rem; color: #888; font-weight: 700; margin-bottom: 4px; }
    .step-en { font-size: 1.12rem; font-weight: 800; color: #1D3557; margin-bottom: 4px; }
    .step-zh { font-size: 0.9rem; color: #666; }
    .step-mine { border-left: 4px solid #E63946; }
    .step-theirs { border-left: 4px solid #457B9D; }

    .score-pill {
      display: inline-block; padding: 4px 14px;
      border-radius: 50px; font-weight: 800; font-size: 0.88rem;
    }
    .score-great { background: #d4edda; color: #155724; }
    .score-ok    { background: #fff3cd; color: #856404; }
    .score-try   { background: #f8d7da; color: #721c24; }

    .hint-chip {
      display: inline-block; background: #e3f2fd; color: #1565C0;
      border-radius: 20px; padding: 3px 12px; font-size: 0.82rem;
      font-weight: 700; margin: 3px 3px 0 0; cursor: default;
    }
    .tts-bar {
      background: #f0f4ff; border-radius: 12px; padding: 12px 16px;
      margin: 8px 0; font-size: 0.9rem; color: #1D3557;
      border: 1px solid #d0d9ff;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Scene data ──
    VOICE_SCENES = [
        {
            "id": "supermarket",
            "title": "超市結帳 🛒",
            "subtitle": "Tesco · Sainsbury's · Waitrose",
            "emoji": "🛒",
            "intro": "你推住購物車去收銀台，準備好用英語結帳!",
            "steps": [
                {"role": "theirs", "speaker": "🏪 收銀員", "en": "Hi there! Do you need a bag for life?",        "zh": "你好!你需要環保袋嗎？",           "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Yes please, just one.",                       "zh": "好的，一個就夠。",                 "yours": True,
                 "hints": ["Yes please", "just one", "thank you"],
                 "keywords": ["yes", "please", "one", "bag"]},
                {"role": "theirs", "speaker": "🏪 收銀員", "en": "Have you got a Clubcard?",                     "zh": "你有Clubcard積分卡嗎？",           "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "No, I don't. Sorry.",                         "zh": "沒有，對不起。",                   "yours": True,
                 "hints": ["No I don't", "Sorry", "I'm afraid not"],
                 "keywords": ["no", "don't", "sorry", "afraid"]},
                {"role": "theirs", "speaker": "🏪 收銀員", "en": "That's twelve pounds fifty, please.",          "zh": "一共十二鎊五十便士，謝謝。",       "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Can I pay by card please?",                   "zh": "可以刷卡嗎？",                     "yours": True,
                 "hints": ["Can I pay by card", "contactless", "please"],
                 "keywords": ["card", "pay", "contactless", "please"]},
                {"role": "theirs", "speaker": "🏪 收銀員", "en": "Of course! Just tap here.",                   "zh": "當然!在這裡感應就可以了。",       "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Thank you. Have a good day!",                 "zh": "謝謝，祝你有美好的一天!",         "yours": True,
                 "hints": ["Thank you", "Have a good day", "Cheers"],
                 "keywords": ["thank", "good", "day", "cheers"]},
            ],
        },
        {
            "id": "gp",
            "title": "預約家庭醫生 🏥",
            "subtitle": "NHS GP Receptionist",
            "emoji": "🏥",
            "intro": "你打電話去GP診所預約，接待員接聽了……",
            "steps": [
                {"role": "theirs", "speaker": "🏥 接待員", "en": "Good morning, Riverside Medical Centre.",     "zh": "早安，Riverside醫療中心。",        "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Hello, I'd like to make an appointment please.", "zh": "你好，我想預約看診。",            "yours": True,
                 "hints": ["I'd like to", "make an appointment", "please"],
                 "keywords": ["appointment", "like", "make", "please", "book"]},
                {"role": "theirs", "speaker": "🏥 接待員", "en": "Of course. Can I take your name and date of birth?", "zh": "當然。可以告訴我你的名字和出生日期嗎？", "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Yes, it's [your name]. Born fifth of March, nineteen sixty-five.", "zh": "是的，我叫[你的名字]，一九六五年三月五日出生。", "yours": True,
                 "hints": ["My name is", "Born", "nineteen sixty-five"],
                 "keywords": ["name", "born", "march", "nineteen", "sixty", "fifth"]},
                {"role": "theirs", "speaker": "🏥 接待員", "en": "What seems to be the problem?",              "zh": "請問有什麼問題？",                  "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "I've had a sore throat for three days.",     "zh": "我喉嚨痛了三天。",                  "yours": True,
                 "hints": ["I've had", "sore throat", "for three days"],
                 "keywords": ["throat", "sore", "three", "days", "pain", "had"]},
                {"role": "theirs", "speaker": "🏥 接待員", "en": "Can you come in tomorrow at ten fifteen?",   "zh": "你明天十點十五分可以來嗎？",        "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Yes, that's perfect. Thank you so much.",   "zh": "好的，非常好。非常感謝你!",         "yours": True,
                 "hints": ["Yes", "that's perfect", "thank you so much"],
                 "keywords": ["yes", "perfect", "thank", "fine", "good"]},
            ],
        },
        {
            "id": "bus",
            "title": "搭巴士問路 🚌",
            "subtitle": "Local Bus · London Bus",
            "emoji": "🚌",
            "intro": "你喺巴士站，唔確定要搭邊架車去市中心……",
            "steps": [
                {"role": "yours",  "speaker": "👴 你",      "en": "Excuse me, does this bus go to the town centre?", "zh": "唔好意思，這輛巴士去市中心嗎？", "yours": True,
                 "hints": ["Excuse me", "does this bus go to", "town centre"],
                 "keywords": ["excuse", "bus", "town", "centre", "go"]},
                {"role": "theirs", "speaker": "🚌 乘客",   "en": "Yes it does! It stops right outside Tesco.",  "zh": "是的!它停在Tesco正門外面。",       "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Oh lovely, thank you! Is this seat taken?",  "zh": "太好了，謝謝!這個座位有人嗎？",   "yours": True,
                 "hints": ["Oh lovely", "Is this seat taken", "thank you"],
                 "keywords": ["seat", "taken", "lovely", "thank"]},
                {"role": "theirs", "speaker": "🚌 乘客",   "en": "No, go ahead! Where are you from originally?", "zh": "沒有，請坐!你原本是哪裡人？",     "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "I'm from Hong Kong. I moved here last year.", "zh": "我來自香港，去年搬來的。",           "yours": True,
                 "hints": ["I'm from Hong Kong", "I moved here", "last year"],
                 "keywords": ["hong", "kong", "moved", "year", "from"]},
                {"role": "theirs", "speaker": "🚌 乘客",   "en": "How wonderful! Are you settling in alright?", "zh": "太棒了!你適應得好嗎？",            "yours": False},
                {"role": "yours",  "speaker": "👴 你",      "en": "Slowly but surely! Still getting used to the weather!", "zh": "慢慢來!還在適應天氣!",      "yours": True,
                 "hints": ["Slowly but surely", "getting used to", "weather"],
                 "keywords": ["slowly", "surely", "weather", "used", "getting"]},
            ],
        },
        {
            "id": "neighbour",
            "title": "同鄰居閒聊 ☁️",
            "subtitle": "British Small Talk",
            "emoji": "☁️",
            "intro": "你係花園澆花，鄰居 Margaret 走過來打招呼……",
            "steps": [
                {"role": "theirs", "speaker": "🏡 Margaret", "en": "Morning! Lovely day for it, isn't it?",    "zh": "早安!今天天氣真好，對吧？",         "yours": False},
                {"role": "yours",  "speaker": "👴 你",        "en": "Good morning! Yes, finally some sunshine!", "zh": "早安!是啊，終於出太陽了!",        "yours": True,
                 "hints": ["Good morning", "finally some sunshine", "Yes!"],
                 "keywords": ["morning", "sunshine", "yes", "finally", "lovely"]},
                {"role": "theirs", "speaker": "🏡 Margaret", "en": "Have you settled in alright? It's been a few months now.", "zh": "你適應得好嗎？已經幾個月了。", "yours": False},
                {"role": "yours",  "speaker": "👴 你",        "en": "Getting there! Everyone's been very kind.", "zh": "慢慢適應!大家都很友善。",          "yours": True,
                 "hints": ["Getting there", "Everyone's been very kind", "slowly"],
                 "keywords": ["getting", "kind", "everyone", "nice", "lovely"]},
                {"role": "theirs", "speaker": "🏡 Margaret", "en": "Do let me know if you need anything, won't you?", "zh": "如果需要任何幫助請告訴我。",       "yours": False},
                {"role": "yours",  "speaker": "👴 你",        "en": "That's very kind of you, thank you Margaret.", "zh": "你真好，謝謝你Margaret。",         "yours": True,
                 "hints": ["That's very kind", "thank you", "so kind of you"],
                 "keywords": ["kind", "thank", "very", "appreciate"]},
            ],
        },
    ]

    # ── Session state for voice practice ──
    if "vp_scene"    not in st.session_state: st.session_state.vp_scene    = 0
    if "vp_step"     not in st.session_state: st.session_state.vp_step     = 0
    if "vp_scores"   not in st.session_state: st.session_state.vp_scores   = {}
    if "vp_attempts" not in st.session_state: st.session_state.vp_attempts = {}
    if "vp_done"     not in st.session_state: st.session_state.vp_done     = set()

    # ── Scene selector ──
    scene_names = [s["title"] for s in VOICE_SCENES]
    col_sel, col_prog = st.columns([3, 1])
    with col_sel:
        chosen = st.selectbox("選擇練習場景", scene_names,
                              index=st.session_state.vp_scene,
                              key="vp_scene_sel")
        idx = scene_names.index(chosen)
        if idx != st.session_state.vp_scene:
            st.session_state.vp_scene = idx
            st.session_state.vp_step  = 0
            st.rerun()
    with col_prog:
        done_scenes = len(st.session_state.vp_done)
        st.markdown(f"""
        <div style='text-align:center; background:white; border-radius:14px; padding:12px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-top:4px;'>
          <div style='font-size:1.7rem; font-weight:900; color:#1D3557;'>{done_scenes}/{len(VOICE_SCENES)}</div>
          <div style='font-size:0.78rem; color:#888;'>場景完成</div>
        </div>""", unsafe_allow_html=True)

    scene = VOICE_SCENES[st.session_state.vp_scene]
    your_steps = [s for s in scene["steps"] if s["yours"]]
    total_your = len(your_steps)

    # ── Scene header ──
    st.markdown(f"""
    <div class='scene-card' data-emoji='{scene["emoji"]}'>
      <h2>{scene["title"]}</h2>
      <p>📍 {scene["subtitle"]}</p>
      <p style='margin-top:10px; font-size:1rem; background:rgba(255,255,255,0.12);
                border-radius:10px; padding:10px 14px; display:inline-block;'>
        &#128214; {scene["intro"]}
      </p>
    </div>""", unsafe_allow_html=True)

    # ── How it works banner ──
    st.markdown("""
    <div class='tts-bar'>
      🎤 <strong>點樣練習：</strong>
      ① 按 <strong>「▶ 聆聽示範」</strong> 聽正確發音 →
      ② 大聲讀出句子 →
      ③ 按 <strong>「✅ 我講咗!評分」</strong> 輸入你講嘅內容讓AI評分
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Replay full script toggle ──
    with st.expander("📜 睇完整對話劇本", expanded=False):
        for s in scene["steps"]:
            mine_style = "color:#E63946;" if s["yours"] else "color:#457B9D;"
            align = "text-align:right;" if s["yours"] else ""
            st.markdown(f"""
            <div style='{align} margin:6px 0;'>
              <span style='font-size:0.78rem; color:#999;'>{s["speaker"]}</span><br>
              <span style='font-weight:800; font-size:1rem; {mine_style}'>{s["en"]}</span>
              <span style='font-size:0.85rem; color:#888;'> - {s["zh"]}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎬 開始練習!逐句過關")

    # ── Step-by-step practice ──
    current_step = st.session_state.vp_step
    steps = scene["steps"]

    for si, step in enumerate(steps):
        step_key  = f"{scene['id']}_{si}"
        is_mine   = step["yours"]
        past      = si < current_step
        active    = si == current_step
        future    = si > current_step

        border_col = "#E63946" if is_mine else "#457B9D"
        bg         = "white" if not future else "#f8f9fa"
        opacity    = "1" if not future else "0.45"

        st.markdown(f"""
        <div class='step-row step-{"mine" if is_mine else "theirs"}'
             style='opacity:{opacity}; background:{bg};'>
          <div class='step-num' style='background:{"#E63946" if is_mine else "#457B9D"};'>
            {si+1}
          </div>
          <div class='step-content'>
            <div class='step-role'>{step["speaker"]} {"👈 你嘅回合!" if is_mine and active else ""}</div>
            <div class='step-en'>{"🔒 待解鎖" if future else ("&#128483;&#65039; " if is_mine else "&#128266; ") + step["en"]}</div>
            {"" if future else f'<div class="step-zh">{step["zh"]}</div>'}
          </div>
        </div>""", unsafe_allow_html=True)

        if not future:
            # TTS button (browser Web Speech API via st.components)
            tts_col, hint_col = st.columns([1, 2])
            with tts_col:
                _tts_text = step['en'].replace("'", "&#39;")
                tts_html = (
                    "<button onclick=\"var voices=speechSynthesis.getVoices();"
                    "var gb=voices.find(function(v){return v.lang==='en-GB';});"
                    "var u=new SpeechSynthesisUtterance('" + _tts_text + "');"
                    "u.lang='en-GB';u.rate=0.82;if(gb)u.voice=gb;"
                    "speechSynthesis.cancel();speechSynthesis.speak(u);\" "
                    "style=\"background:#1D3557;color:white;border:none;"
                    "border-radius:10px;padding:8px 18px;cursor:pointer;"
                    "font-size:0.9rem;font-weight:700;font-family:inherit;\">"
                    "&#9654; &#32085;&#32202;&#31034;&#31684;</button>"
                )
                import streamlit.components.v1 as components
                components.html(tts_html, height=46)

            with hint_col:
                if is_mine and "hints" in step:
                    hints_html = " ".join(
                        f'<span class="hint-chip">"{h}"</span>'
                        for h in step["hints"]
                    )
                    st.markdown(f"&#128161; 關鍵詞：{hints_html}", unsafe_allow_html=True)

            # ── If it's the user's turn and it's active ──
            if is_mine and active:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#fff8e1,#fffde7);
                            border:2px dashed #FFB703; border-radius:14px;
                            padding:16px 20px; margin:8px 0;'>
                  <strong style='color:#856404;'>&#127908; 你嘅回合!</strong>
                  大聲讀出上面句子，然後喺下面輸入你講嘅內容（或者盡力打出你以為講咗嘅嘢）
                </div>""", unsafe_allow_html=True)

                spoken = st.text_input(
                    "你講咗咩？（用英文輸入）",
                    placeholder=f"e.g. {step['en'][:30]}...",
                    key=f"spoken_{step_key}"
                )

                c1, c2 = st.columns([2, 1])
                with c1:
                    if st.button("&#9989; 我講咗!AI評分", key=f"eval_{step_key}",
                                 use_container_width=True):
                        if spoken.strip():
                            # ── Keyword-based scoring (no API needed) ──
                            spoken_lower = spoken.lower()
                            target_kw    = step.get("keywords", [])
                            hits         = sum(1 for kw in target_kw if kw in spoken_lower)
                            ratio        = hits / len(target_kw) if target_kw else 0.5

                            if ratio >= 0.6:
                                score_label = "優秀 🌟"
                                score_class = "score-great"
                                feedback    = "非常好!發音同內容都正確!繼續下一句!"
                                pts_earn    = 15
                            elif ratio >= 0.3:
                                score_label = "唔錯 👍"
                                score_class = "score-ok"
                                feedback    = f"好有進步!試試包含更多關鍵詞。正確版本：\"{step['en']}\""
                                pts_earn    = 8
                            else:
                                score_label = "再試一次 💪"
                                score_class = "score-try"
                                feedback    = f"唔緊要!正確版本係：\"{step['en']}\"  再聽一次示範，大聲練習!"
                                pts_earn    = 3

                            st.session_state.vp_scores[step_key]   = score_label
                            st.session_state.vp_attempts[step_key] = spoken

                            st.markdown(f"""
                            <div style='background:white;border-radius:14px;padding:16px 20px;
                                        box-shadow:0 3px 12px rgba(0,0,0,0.1); margin:8px 0;'>
                              <span class='score-pill {score_class}'>{score_label}</span>
                              <span style='font-size:0.82rem; color:#888; margin-left:8px;'>
                                +{pts_earn} 分
                              </span>
                              <p style='margin:10px 0 6px; color:#333;'>{feedback}</p>
                              <p style='margin:0; font-size:0.85rem; color:#888;'>
                                你講：「{spoken}」<br>
                                標準：「{step['en']}」
                              </p>
                            </div>""", unsafe_allow_html=True)

                            add_points(pts_earn)

                            if ratio >= 0.3:
                                st.session_state.vp_step = si + 1
                                st.rerun()
                        else:
                            st.warning("請先輸入你講嘅內容再評分!")

                with c2:
                    if st.button("&#9197;️ 跳過呢句", key=f"skip_{step_key}",
                                 use_container_width=True):
                        st.session_state.vp_step = si + 1
                        st.rerun()

            elif is_mine and past:
                # Show historical score
                if step_key in st.session_state.vp_scores:
                    sc = st.session_state.vp_scores[step_key]
                    sc_class = ("score-great" if "優秀" in sc
                                else "score-ok" if "唔錯" in sc else "score-try")
                    st.markdown(
                        f"<span class='score-pill {sc_class}'>✓ {sc}</span>",
                        unsafe_allow_html=True
                    )

        st.markdown("")  # spacing

    # ── Scene complete ──
    if current_step >= len(steps):
        scene_id = scene["id"]
        st.markdown("---")
        # Tally scores
        great = sum(1 for k, v in st.session_state.vp_scores.items()
                    if scene_id in k and "優秀" in v)
        ok    = sum(1 for k, v in st.session_state.vp_scores.items()
                    if scene_id in k and "唔錯" in v)

        if great + ok >= total_your * 0.7:
            medal, msg, bonus = "🏅", "完美過關!", 30
        else:
            medal, msg, bonus = "✅", "成功完成!", 15

        st.markdown(f"""
        <div style='text-align:center; background:linear-gradient(135deg,#1D3557,#457B9D);
                    color:white; border-radius:20px; padding:30px; margin:10px 0;'>
          <div style='font-size:4rem;'>{medal}</div>
          <div style='font-size:1.8rem; font-weight:900; margin:8px 0;'>{msg}</div>
          <div style='font-size:1rem; opacity:0.85;'>
            優秀：{great}句 · 唔錯：{ok}句 · 完成!
          </div>
          <div style='font-size:2rem; font-weight:900; margin-top:12px;'>
            +{bonus} 積分獎勵!
          </div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🎊 收取完成獎勵!", use_container_width=True):
                if scene_id not in st.session_state.vp_done:
                    st.session_state.vp_done.add(scene_id)
                    add_points(bonus)
                    st.balloons()
                    st.success(f"&#127881; +{bonus}分!")
        with c2:
            if st.button("🔄 再練一次", use_container_width=True):
                for k in list(st.session_state.vp_scores.keys()):
                    if scene_id in k:
                        del st.session_state.vp_scores[k]
                st.session_state.vp_step = 0
                st.rerun()

# ── PRONUNCIATION TRAPS ───────────────────────────────────────────────────────
elif "發音陷阱" in mode:
    st.markdown("## 🔤 發音陷阱：你唔知就會出醜!")
    st.markdown("""
    <div class='funfact'>
      😂 英國地名同日常詞彙有好多陷阱。呢度整理咗最常見嘅，出口前先要練!
    </div>
    """, unsafe_allow_html=True)
    
    for i, trap in enumerate(PRONUNCIATION_TRAPS):
        with st.container():
            st.markdown(f"""
            <div class='lesson-card {"gold" if i%3==1 else "red" if i%3==2 else ""}'>
              <div style='display:flex; justify-content:space-between; align-items:start; flex-wrap:wrap; gap:10px;'>
                <div>
                  <div style='font-size:1.6rem; font-weight:900; color:#1D3557;'>{trap['word']}</div>
                  <div style='margin:6px 0;'>
                    <span style='color:#dc3545;'>&#10060; 錯：</span> <span style='font-size:0.95rem;'>{trap['wrong']}</span>
                  </div>
                  <div>
                    <span style='color:#28a745;'>&#9989; 正：</span> <strong style='font-size:1.05rem; color:#1D3557;'>{trap['right']}</strong>
                  </div>
                </div>
                <div style='font-size:1.5rem;'>{trap['note']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 發音快測")
    st.markdown("以下邊個係 'Leicester' 嘅正確讀音？")
    pron_q = st.radio("", ["Lee-ches-ter", "Lester", "Lie-ces-ter", "Ligh-chester"], label_visibility="collapsed")
    if st.button("確認"):
        if pron_q == "Lester":
            st.markdown("<div class='correct-box'>✅ 正確!Leicester = Lester。+10分!</div>", unsafe_allow_html=True)
            add_points(10)
        else:
            st.markdown("<div class='wrong-box'>❌ Leicester 讀 'Lester'!英國地名太tricky了!</div>", unsafe_allow_html=True)

# ── CULTURAL TIPS ─────────────────────────────────────────────────────────────
elif "文化小貼士" in mode:
    st.markdown("## 🎭 英國文化小貼士")
    st.markdown("""
    <div class='funfact'>
      🏴󠁧󠁢󠁥󠁮󠁧󠁿 英國文化有很多獨特之處，了解文化背景可以幫你更自然地溝通，避免誤會!
    </div>
    """, unsafe_allow_html=True)
    
    for tip in CULTURAL_TIPS:
        st.markdown(f"""
        <div class='lesson-card'>
          <h3 style='margin:0 0 8px;'>{tip['emoji']} {tip['tip']}</h3>
          <p style='color:#444; margin:0; font-size:1rem;'>{tip['detail']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🤔 文化小測驗")
    st.markdown("""
    <div class='quiz-box'>
      <div class='quiz-q'>英國人話 'Quite good'，係咩意思？</div>
    </div>
    """, unsafe_allow_html=True)
    
    culture_q = st.radio("", ["非常好!", "普通，勉強算好", "完全唔好", "我唔知"], label_visibility="collapsed", key="culture_quiz")
    if st.button("確認答案", key="culture_btn"):
        if culture_q == "普通，勉強算好":
            st.markdown("<div class='correct-box'>✅ 正確!英國人講 'quite' 通常係降低評價，唔係加強!+10分</div>", unsafe_allow_html=True)
            add_points(10)
        else:
            st.markdown("<div class='wrong-box'>❌ 英國人講 'Quite good' 通常係 '普通，勉強算好'，不是讚美!小心呢個文化陷阱!</div>", unsafe_allow_html=True)

# ── MEGA CHALLENGE ────────────────────────────────────────────────────────────
elif "大挑戰" in mode:
    st.markdown("## 🧠 大挑戰!綜合考核")
    st.markdown("""
    <div class='lesson-card gold'>
      <strong>⚡ 規則：</strong>答對一題 +15分，答錯扣5分!考驗你嘅學習成果!
    </div>
    """, unsafe_allow_html=True)
    
    mega_quiz = [
        {"q": "你想要環保袋，怎樣回應店員 'Do you need a bag for life?'", "options": ["Yes please!", "I want bag", "Give bag", "Bag please give"], "ans": 0},
        {"q": "你想問座位有冇人坐", "options": ["Sit here?", "Is this seat taken?", "Anyone here?", "Can I?"], "ans": 1},
        {"q": "'Fortnight' 係幾耐？", "options": ["一星期", "兩星期", "四十天", "一個月"], "ans": 1},
        {"q": "去GP睇病要先做咩？", "options": ["直接去", "Register（登記）做病人", "打急症", "買藥先"], "ans": 1},
        {"q": "打電話聽唔明，禮貌地說：", "options": ["What!?", "Louder please", "Sorry, I didn't catch that. Could you repeat?", "Say again!"], "ans": 2},
        {"q": "'Cheers' 係咩意思（非酒杯）？", "options": ["只係舉杯", "謝謝/再見/好的（萬能詞）", "再見", "好的"], "ans": 1},
        {"q": "英國超市 'On offer' 係話？", "options": ["有優惠/特價", "有提供服務", "新到貨", "限量版"], "ans": 0},
        {"q": "Leicester 點讀？", "options": ["Lee-ches-ter", "Lester", "Lie-ster", "Lay-cester"], "ans": 1},
    ]
    
    total_score = 0
    answered = 0
    
    for i, q in enumerate(mega_quiz):
        mkey = f"mega_q{i}"
        st.markdown(f"""
        <div class='quiz-box' style='margin:12px 0;'>
          <div class='quiz-q'>問題 {i+1}. {q['q']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ans = st.radio("", q["options"], key=mkey, label_visibility="collapsed")
        
        if st.button(f"確認 #{i+1}", key=f"mega_btn_{i}"):
            idx = q["options"].index(ans)
            if idx == q["ans"]:
                st.markdown("<div class='correct-box'>✅ 正確!+15分</div>", unsafe_allow_html=True)
                if f"mega_{mkey}" not in st.session_state.quiz_answers:
                    add_points(15)
                    st.session_state.quiz_answers[f"mega_{mkey}"] = True
            else:
                correct = q["options"][q["ans"]]
                st.markdown(f"<div class='wrong-box'>&#10060; 答案係：<strong>{correct}</strong> -5分</div>", unsafe_allow_html=True)
                if f"mega_{mkey}" not in st.session_state.quiz_answers:
                    st.session_state.points = max(0, st.session_state.points - 5)
                    st.session_state.quiz_answers[f"mega_{mkey}"] = False
    
    st.markdown("---")
    if st.button("🎊 睇我嘅最終成績!", use_container_width=True):
        pts = st.session_state.points
        if pts >= 200:
            medal = "🥇 金牌英語達人!"
            msg = "你係香港移英英語精英!去同英國人傾偈啦!"
        elif pts >= 100:
            medal = "🥈 銀牌學員!"
            msg = "好有進步!繼續練習就可以升金牌!"
        else:
            medal = "🥉 銅牌學員"
            msg = "唔緊要，繼續練習!羅馬唔係一日建成嘅!"
        
        st.markdown(f"""
        <div style='text-align:center; padding:30px; background:linear-gradient(135deg,#1D3557,#457B9D); border-radius:20px; color:white;'>
          <div style='font-size:4rem;'>{medal.split()[0]}</div>
          <div style='font-size:1.8rem; font-weight:900; margin:10px 0;'>{medal}</div>
          <div style='font-size:3rem; font-weight:900;'>&#11088; {pts} 分</div>
          <div style='font-size:1.1rem; opacity:0.9; margin-top:12px;'>{msg}</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

# ── SPEAKING PRACTICE ────────────────────────────────────────────────────────
elif "對話練習" in mode:
    st.markdown("## 🎤 對話練習 - 開口講英文!")

    # Check Groq API
    groq_client = get_groq_client()
    if not groq_client:
        st.warning("⚠️ 請在 Streamlit Secrets 設定 `GROQ_API_KEY` 先可以使用 AI 評分功能。")

    st.markdown("""
    <div class='funfact'>
      🎯 <strong>點樣練習：</strong>睇住情境，聽AI英國人講話，然後<strong>用麥克風錄音</strong>說出你的英文回應，AI即時評分!
    </div>
    """, unsafe_allow_html=True)

    # ── Scenario selection ──
    if st.session_state.sp_scenario is None:
        st.markdown("### 選擇練習情境")
        cols = st.columns(2)
        for si, sc in enumerate(SPEAKING_SCENARIOS):
            with cols[si % 2]:
                st.markdown(f"""
                <div class='lesson-card {"gold" if "中級" in sc["difficulty"] else ""}'>
                  <div style='font-size:1.6rem;'>{sc["title"].split()[0]}</div>
                  <div style='font-weight:800; font-size:1.05rem; color:#1D3557; margin:6px 0;'>{sc["title"]}</div>
                  <div style='color:#666; font-size:0.9rem; margin-bottom:8px;'>{sc["subtitle"]}</div>
                  <span class='level-badge {"level-2" if "中級" in sc["difficulty"] else "level-1"}'>{sc["difficulty"]}</span>
                  <div style='font-size:0.85rem; color:#888; margin-top:8px;'>{len(sc["steps"])} 個回合</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"開始練習", key=f"start_sc_{si}", use_container_width=True):
                    st.session_state.sp_scenario = si
                    st.session_state.sp_step = 0
                    st.session_state.sp_results = []
                    st.session_state.sp_ai_reply = {}
                    st.rerun()

    # ── Active scenario ──
    else:
        sc = SPEAKING_SCENARIOS[st.session_state.sp_scenario]
        current_step = st.session_state.sp_step
        total_steps = len(sc["steps"])

        # Header
        col_title, col_exit = st.columns([4, 1])
        with col_title:
            st.markdown(f"### {sc['title']} - {sc['subtitle']}")
            st.markdown(f"""
            <div class='funfact' style='margin-bottom:8px;'>
              &#127916; <strong>情境：</strong>{sc['scene_desc']}
            </div>
            """, unsafe_allow_html=True)
        with col_exit:
            if st.button("← 返回選擇", use_container_width=True):
                st.session_state.sp_scenario = None
                st.rerun()

        # Progress bar
        pct_done = int(current_step / total_steps * 100)
        st.markdown(f"""
        <div style='margin:8px 0 16px;'>
          <div style='font-size:0.85rem; color:#666; margin-bottom:4px;'>進度：{current_step}/{total_steps} 回合</div>
          <div class='progress-wrap'><div class='progress-fill' style='width:{pct_done}%;'></div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Show completed steps summary ──
        if st.session_state.sp_results:
            with st.expander("📊 已完成回合", expanded=False):
                for r in st.session_state.sp_results:
                    score_color = "#28a745" if r["score"] >= 70 else "#dc3545"
                    st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; padding:8px 12px;
                         background:white; border-radius:10px; margin:4px 0; font-size:0.9rem;'>
                      <span>回合 {r["step"]}：<em>{r["user_said"]}</em></span>
                      <strong style='color:{score_color};'>{r["score"]}分</strong>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Current step or completion ──
        if current_step >= total_steps:
            # All done!
            total_score = sum(r["score"] for r in st.session_state.sp_results)
            avg = total_score // len(st.session_state.sp_results) if st.session_state.sp_results else 0
            if avg >= 85:
                grade, grade_emoji = "英語達人!", "🥇"
            elif avg >= 65:
                grade, grade_emoji = "好有進步!", "🥈"
            else:
                grade, grade_emoji = "繼續加油!", "🥉"

            st.markdown(f"""
            <div style='text-align:center; padding:32px; background:linear-gradient(135deg,#1D3557,#457B9D);
                 border-radius:20px; color:white; margin:16px 0;'>
              <div style='font-size:4rem;'>{grade_emoji}</div>
              <div style='font-size:2rem; font-weight:900; margin:8px 0;'>練習完成!{grade}</div>
              <div style='font-size:3rem; font-weight:900;'>平均 {avg} 分</div>
              <div style='opacity:0.85; margin-top:10px;'>完成 {len(st.session_state.sp_results)} 個回合</div>
            </div>
            """, unsafe_allow_html=True)

            pts_earned = max(10, avg // 5)
            if st.button(f"&#127882; 領取 +{pts_earned} 積分!", use_container_width=True):
                add_points(pts_earned)
                st.success(f"&#11088; +{pts_earned} 分!繼續練習!")
                st.balloons()

            if st.button("🔄 再練一次", use_container_width=True):
                st.session_state.sp_step = 0
                st.session_state.sp_results = []
                st.session_state.sp_ai_reply = {}
                st.rerun()

        else:
            step_data = sc["steps"][current_step]
            step_key = f"sc{st.session_state.sp_scenario}_s{current_step}"

            # AI speaks first
            st.markdown(f"""
            <div style='margin:8px 0 4px; font-size:0.8rem; color:#888; margin-left:20px;'>
              &#127468;&#127463; {sc['ai_role'].split()[0].title()} 說：
            </div>
            <div class='bubble-uk'>
              &#128266; <strong>{step_data['ai_line']}</strong>
            </div>
            """, unsafe_allow_html=True)

            # Show AI reply from previous input if exists
            if step_key in st.session_state.sp_ai_reply:
                st.markdown(f"""
                <div style='margin:4px 0 4px; font-size:0.8rem; color:#888; margin-left:20px;'>
                  &#128172; AI 回應：
                </div>
                <div class='bubble-uk' style='opacity:0.85; font-size:0.95rem;'>
                  {st.session_state.sp_ai_reply[step_key]}
                </div>
                """, unsafe_allow_html=True)

            # Task prompt
            st.markdown(f"""
            <div class='tip-box' style='margin:16px 0 10px;'>
              <span class='tip-icon'>&#127919;</span>
              <strong>你的任務：</strong>{step_data['prompt_hk']}<br>
              <span style='font-size:0.85rem; color:#666;'>&#128161; 提示：{step_data['hint']}</span>
            </div>
            """, unsafe_allow_html=True)

            # TTS button - read the target aloud for reference
            tts_html = f"""
            <div style='margin:8px 0;'>
              <button onclick="speakText()" style='
                background:#1D3557; color:white; border:none; border-radius:10px;
                padding:10px 20px; font-size:0.95rem; cursor:pointer; font-weight:700;'>
                &#128266; 聽示範讀音
              </button>
              <span id="tts-status" style='margin-left:12px; font-size:0.85rem; color:#666;'></span>
            </div>
            <script>
            function speakText() {{
              const text = {json.dumps(step_data['target_en'])};
              const utter = new SpeechSynthesisUtterance(text);
              utter.lang = 'en-GB';
              utter.rate = 0.85;
              const voices = window.speechSynthesis.getVoices();
              const gbVoice = voices.find(v => v.lang === 'en-GB');
              if (gbVoice) utter.voice = gbVoice;
              document.getElementById('tts-status').textContent = '▶ 播放中...';
              utter.onend = () => document.getElementById('tts-status').textContent = '✓ 完成';
              window.speechSynthesis.speak(utter);
            }}
            // preload voices
            window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
            </script>
            """
            components.html(tts_html, height=60)

            # ── Speech recording via Web Speech API ──
            stt_html = f"""
            <style>
              .mic-btn {{
                background: linear-gradient(135deg, #E63946, #c1121f);
                color: white; border: none; border-radius: 50px;
                padding: 14px 28px; font-size: 1rem; font-weight: 800;
                cursor: pointer; transition: all 0.2s; font-family: 'Nunito', sans-serif;
                box-shadow: 0 4px 14px rgba(230,57,70,0.35);
              }}
              .mic-btn:hover {{ transform: scale(1.04); }}
              .mic-btn.recording {{
                background: linear-gradient(135deg, #c1121f, #800f1a);
                animation: pulse 1s infinite;
              }}
              @keyframes pulse {{
                0%,100% {{ box-shadow: 0 4px 14px rgba(230,57,70,0.35); }}
                50% {{ box-shadow: 0 4px 28px rgba(230,57,70,0.7); }}
              }}
              #transcript-box {{
                margin-top: 14px;
                background: #f0f7ff;
                border: 2px solid #457B9D;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 1rem;
                min-height: 44px;
                color: #1D3557;
                font-family: 'Nunito', sans-serif;
              }}
              #submit-wrap {{ margin-top:10px; }}
              #submit-btn {{
                background: #2DC653; color:white; border:none;
                border-radius:10px; padding:10px 24px;
                font-size:0.95rem; font-weight:800; cursor:pointer;
                display:none; font-family:'Nunito',sans-serif;
              }}
            </style>

            <div id="stt-container">
              <button class="mic-btn" id="mic-btn" onclick="toggleRecording()">
                &#127908; 按住錄音 開始說話
              </button>
              <div id="transcript-box">（錄音後你說的話會出現在這裡）</div>
              <div id="submit-wrap">
                <button id="submit-btn" onclick="submitTranscript()">&#9989; 提交答案</button>
              </div>
            </div>

            <script>
            let recognition = null;
            let isRecording = false;
            let finalTranscript = '';

            function toggleRecording() {{
              if (isRecording) {{
                stopRecording();
              }} else {{
                startRecording();
              }}
            }}

            function startRecording() {{
              if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                document.getElementById('transcript-box').innerHTML =
                  '&#10060; 你的瀏覽器唔支援語音識別。請用 Chrome 瀏覽器!';
                return;
              }}
              const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
              recognition = new SR();
              recognition.lang = 'en-GB';
              recognition.continuous = false;
              recognition.interimResults = true;

              recognition.onstart = () => {{
                isRecording = true;
                finalTranscript = '';
                const btn = document.getElementById('mic-btn');
                btn.classList.add('recording');
                btn.textContent = '&#9209; 錄音中... 點擊停止';
                document.getElementById('transcript-box').textContent = '🎙 聆聽中...';
                document.getElementById('submit-btn').style.display = 'none';
              }};

              recognition.onresult = (event) => {{
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                  if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript;
                  }} else {{
                    interim += event.results[i][0].transcript;
                  }}
                }}
                document.getElementById('transcript-box').textContent =
                  finalTranscript || interim || '🎙 聆聽中...';
              }};

              recognition.onend = () => {{
                isRecording = false;
                const btn = document.getElementById('mic-btn');
                btn.classList.remove('recording');
                btn.textContent = '&#127908; 再錄一次';
                if (finalTranscript.trim()) {{
                  document.getElementById('transcript-box').textContent = '你說：「' + finalTranscript + '」';
                  document.getElementById('submit-btn').style.display = 'inline-block';
                  // pass to Streamlit
                  const event = new CustomEvent('speech-result', {{detail: finalTranscript}});
                  window.parent.document.dispatchEvent(event);
                  window.parent.postMessage({{type:'speech-result', text: finalTranscript}}, '*');
                  // store in sessionStorage for Streamlit to pick up
                  sessionStorage.setItem('speech_{step_key}', finalTranscript);
                }}
              }};

              recognition.onerror = (e) => {{
                isRecording = false;
                document.getElementById('transcript-box').textContent = '&#10060; 錄音錯誤：' + e.error + '。請再試。';
                document.getElementById('mic-btn').classList.remove('recording');
                document.getElementById('mic-btn').textContent = '&#127908; 按住錄音 開始說話';
              }};

              recognition.start();
            }}

            function stopRecording() {{
              if (recognition) recognition.stop();
            }}

            function submitTranscript() {{
              if (finalTranscript.trim()) {{
                // Write into a hidden input so Streamlit form can pick it
                const ta = window.parent.document.querySelector('textarea[data-speech-key="{step_key}"]');
                document.getElementById('transcript-box').innerHTML =
                  '&#9989; 已提交：「' + finalTranscript + '」<br><small style="color:#666">請點擊下方「提交錄音答案」按鈕</small>';
              }}
            }}
            </script>
            """
            components.html(stt_html, height=200)

            # Manual text input as fallback / for users without mic
            st.markdown("<div style='font-size:0.85rem; color:#888; margin:8px 0 4px;'>或者手動輸入（冇麥克風時用）：</div>", unsafe_allow_html=True)
            typed_input = st.text_input(
                "手動輸入你的英文回應",
                placeholder=f"例：{step_data['target_en']}",
                key=f"text_input_{step_key}",
                label_visibility="collapsed"
            )

            col_submit, col_skip = st.columns([3, 1])
            with col_submit:
                submit_clicked = st.button("&#128308; 提交答案 + AI評分", key=f"submit_{step_key}", use_container_width=True)
            with col_skip:
                skip_clicked = st.button("&#9197; 跳過", key=f"skip_{step_key}", use_container_width=True)

            if submit_clicked and typed_input.strip():
                user_said = typed_input.strip()
                with st.spinner("🤔 AI緊評分緊..."):
                    if groq_client:
                        result = groq_score_speech(groq_client, step_data["target_en"], user_said, sc["title"])
                        ai_reply = groq_ai_response(groq_client, sc["ai_role"], step_data["ai_line"], user_said, step_data["prompt_hk"])
                    else:
                        # Fallback scoring without API
                        target_words = set(step_data["target_en"].lower().split())
                        user_words = set(user_said.lower().split())
                        kw_hits = sum(1 for k in step_data["keywords"] if k.lower() in user_said.lower())
                        score = min(95, 40 + kw_hits * 15)
                        result = {
                            "score": score,
                            "verdict": "不錯!（需要GROQ_API_KEY才能精確評分）",
                            "pronunciation_tips": "記得清楚發音每個音節。",
                            "grammar_ok": True,
                            "grammar_note": "",
                            "encouragement": "繼續練習!加油!💪",
                        }
                        ai_reply = "Lovely, thank you! Have a great day!"

                # Save result
                st.session_state.sp_results.append({
                    "step": current_step + 1,
                    "user_said": user_said,
                    "target": step_data["target_en"],
                    "score": result["score"],
                })
                log_activity("speaking", sc["title"], result["score"], max(5, result["score"]//10), step_data["prompt_hk"][:80])
                st.session_state.sp_ai_reply[step_key] = ai_reply

                # Display score
                score = result["score"]
                score_color = "#28a745" if score >= 70 else "#FFB703" if score >= 50 else "#dc3545"
                score_emoji = "🥳" if score >= 85 else "😊" if score >= 65 else "💪"

                st.markdown(f"""
                <div style='background:white; border-radius:16px; padding:20px 24px;
                     box-shadow:0 4px 16px rgba(0,0,0,0.09); margin:14px 0;
                     border-top: 5px solid {score_color};'>
                  <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                      <div style='font-size:0.85rem; color:#888;'>你說：</div>
                      <div style='font-size:1.05rem; font-weight:700; color:#1D3557; margin:4px 0;'>「{user_said}」</div>
                    </div>
                    <div style='text-align:center;'>
                      <div style='font-size:2.8rem; font-weight:900; color:{score_color}; line-height:1;'>{score}</div>
                      <div style='font-size:0.8rem; color:#888;'>分</div>
                    </div>
                  </div>
                  <hr style='border-color:#f0f0f0; margin:12px 0;'>
                  <div style='font-size:1rem;'>{score_emoji} <strong>{result["verdict"]}</strong></div>
                  <div style='margin-top:8px; font-size:0.9rem; color:#555;'>&#128292; {result["pronunciation_tips"]}</div>
                  {"<div style='margin-top:6px; font-size:0.9rem; color:#856404; background:#fff3cd; padding:6px 10px; border-radius:8px;'>&#128221; " + result["grammar_note"] + "</div>" if not result.get("grammar_ok") and result.get("grammar_note") else ""}
                  <div style='margin-top:10px; font-size:0.9rem; color:#2DC653; font-weight:700;'>✨ {result["encouragement"]}</div>
                  <div style='margin-top:10px; font-size:0.85rem; color:#888;'>
                    &#9989; 參考答案：<em>{step_data["target_en"]}</em>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Tip for this step
                st.markdown(f"""
                <div class='tip-box'>
                  <span class='tip-icon'>&#128161;</span> {step_data['tip']}
                </div>
                """, unsafe_allow_html=True)

                add_points(max(5, score // 10))

                if st.button("&#10145;&#65039; 下一回合", key=f"next_{step_key}", use_container_width=True):
                    st.session_state.sp_step += 1
                    st.rerun()

            elif skip_clicked:
                st.session_state.sp_results.append({
                    "step": current_step + 1,
                    "user_said": "（跳過）",
                    "target": step_data["target_en"],
                    "score": 0,
                })
                st.session_state.sp_step += 1
                st.rerun()

            elif submit_clicked and not typed_input.strip():
                st.warning("請先輸入你的答案，或用麥克風錄音!")


# -- HISTORY PAGE ---------------------------------------------------------------
elif "學習歷史" in mode:
    st.markdown("## 📊 學習歷史")

    ws, err = get_gsheet()
    if err == "no_creds":
        st.warning("""
⚠️ 尚未設定 Google Sheets。請喺 Streamlit Secrets 加入 `GOOGLE_CREDS`。
詳見下方設定教學。
        """)
        with st.expander("📋 如何設定 Google Sheets？", expanded=True):
            st.markdown("""
**步驟 1：建立 Service Account**
1. 去 [Google Cloud Console](https://console.cloud.google.com)
2. 建立新 Project → 啟用 **Google Sheets API** 同 **Google Drive API**
3. 去 IAM → Service Accounts → 建立新帳號
4. 下載 JSON 金鑰檔案

**步驟 2：加入 Streamlit Secrets**

喺 Streamlit Cloud → App Settings → Secrets 加入：

```toml
[GOOGLE_CREDS]
type = "service_account"
project_id = "你的project_id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "你的service_account@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

**步驟 3：分享 Sheet 俾 Service Account**

App 首次運行時會自動建立 Sheet，並分享俾 `client_email`。
            """)
    else:
        uid = st.session_state.get("user_id", "unknown")
        history = load_history(uid)

        if not history:
            st.info("未有歷史記錄。完成練習或測驗後記錄會自動儲存！")
        else:
            # ── Summary metrics ──
            total_sessions = len(history)
            quiz_rows  = [r for r in history if r["activity_type"] == "quiz"]
            speak_rows = [r for r in history if r["activity_type"] == "speaking"]
            total_pts  = sum(int(r.get("points_earned", 0)) for r in history)
            avg_score  = int(sum(int(r.get("score", 0)) for r in history) / total_sessions) if total_sessions else 0

            c1, c2, c3, c4 = st.columns(4)
            for col, label, val, emoji in [
                (c1, "總活動次數", total_sessions, "📝"),
                (c2, "測驗完成", len(quiz_rows), "🧠"),
                (c3, "對話練習", len(speak_rows), "🎤"),
                (c4, "累計積分", total_pts, "⭐"),
            ]:
                col.markdown(f"""
                <div style="background:white;border-radius:14px;padding:18px;text-align:center;
                     box-shadow:0 3px 12px rgba(0,0,0,0.08);margin:4px;">
                  <div style="font-size:2rem;">{emoji}</div>
                  <div style="font-size:1.6rem;font-weight:900;color:#1D3557;">{val}</div>
                  <div style="font-size:0.8rem;color:#888;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Score trend chart (pure Python, no plotly needed) ──
            if len(history) >= 2:
                st.markdown("### 📈 分數趨勢")
                scores = [int(r.get("score", 0)) for r in history[-20:]]
                dates  = [r.get("timestamp", "")[:10] for r in history[-20:]]

                # Build simple bar chart with HTML
                max_s = max(scores) if scores else 100
                bars_html = ""
                for i, (s, d) in enumerate(zip(scores, dates)):
                    h = int(s / max_s * 80)
                    color = "#2DC653" if s >= 80 else "#FFB703" if s >= 60 else "#E63946"
                    bars_html += f"""
                    <div style="display:inline-flex;flex-direction:column;align-items:center;
                         margin:0 3px;vertical-align:bottom;">
                      <div style="font-size:0.7rem;color:#666;margin-bottom:2px;">{s}</div>
                      <div style="width:28px;height:{h}px;background:{color};
                           border-radius:4px 4px 0 0;"></div>
                      <div style="font-size:0.6rem;color:#aaa;margin-top:3px;
                           writing-mode:vertical-lr;transform:rotate(180deg);height:40px;
                           overflow:hidden;">{d[5:]}</div>
                    </div>"""

                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:20px 16px 8px;
                     box-shadow:0 3px 12px rgba(0,0,0,0.08);overflow-x:auto;">
                  <div style="display:flex;align-items:flex-end;min-width:300px;height:120px;
                       border-bottom:2px solid #eee;padding-bottom:4px;">
                    {bars_html}
                  </div>
                  <div style="font-size:0.75rem;color:#aaa;margin-top:8px;">最近 {len(scores)} 次活動分數</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Per-scenario breakdown ──
            st.markdown("### 🎯 各情境表現")
            scenario_map = {}
            for r in history:
                sc_name = r.get("scenario", "其他")
                if sc_name not in scenario_map:
                    scenario_map[sc_name] = []
                scenario_map[sc_name].append(int(r.get("score", 0)))

            sc_cols = st.columns(min(len(scenario_map), 3))
            for i, (sc_name, sc_scores) in enumerate(scenario_map.items()):
                avg = int(sum(sc_scores) / len(sc_scores))
                best = max(sc_scores)
                color = "#2DC653" if avg >= 80 else "#FFB703" if avg >= 60 else "#E63946"
                with sc_cols[i % 3]:
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:16px;
                         border-left:5px solid {color};box-shadow:0 3px 10px rgba(0,0,0,0.07);
                         margin:6px 0;">
                      <div style="font-weight:800;font-size:0.95rem;color:#1D3557;
                           margin-bottom:6px;">{sc_name[:25]}</div>
                      <div style="font-size:1.5rem;font-weight:900;color:{color};">{avg}分</div>
                      <div style="font-size:0.8rem;color:#888;">平均 · 最高 {best}分 · {len(sc_scores)}次</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Recent activity log ──
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🕐 最近活動記錄")
            recent = list(reversed(history[-15:]))
            for r in recent:
                score = int(r.get("score", 0))
                pts   = int(r.get("points_earned", 0))
                ts    = r.get("timestamp", "")[:16]
                atype = "🧠 測驗" if r.get("activity_type") == "quiz" else "🎤 對話"
                color = "#2DC653" if score >= 80 else "#FFB703" if score >= 60 else "#E63946"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                     padding:10px 14px;background:white;border-radius:10px;
                     margin:4px 0;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                  <div>
                    <span style="font-size:0.85rem;">{atype}</span>
                    <span style="font-size:0.82rem;color:#666;margin-left:8px;">{r.get("scenario","")[:30]}</span>
                  </div>
                  <div style="display:flex;gap:12px;align-items:center;">
                    <span style="font-size:0.8rem;color:#aaa;">{ts}</span>
                    <span style="font-weight:800;color:{color};">{score}分</span>
                    <span style="font-size:0.8rem;color:#2DC653;">+{pts}&#11088;</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Export button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📥 下載歷史 CSV", use_container_width=False):
                import csv, io
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=SHEET_HEADERS)
                writer.writeheader()
                writer.writerows(history)
                st.download_button(
                    "⬇️ 確認下載",
                    buf.getvalue().encode("utf-8-sig"),
                    file_name="learning_history.csv",
                    mime="text/csv",
                )

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; font-size:0.85rem; padding:16px;'>
  🇬🇧 英國生活英語學習班 · 專為香港移民設計<br>
  加油!你已經踏出最重要嘅一步 - 學習! 💪
</div>
""", unsafe_allow_html=True)
