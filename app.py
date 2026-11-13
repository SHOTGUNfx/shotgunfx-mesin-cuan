import streamlit as st
from biquote import Biquote
import pandas as pd
from datetime import datetime, timezone
import feedparser

# ================== BRANDING ==================
BRAND_NAME = "SHOTGUNfx"
BRAND_TAGLINE = "MESIN CUAN"
BRAND_COLOR = "#FF3B3B"  # merah senapan
BRAND_ACCENT = "#FFD700"  # gold

st.set_page_config(
    page_title=f"{BRAND_NAME} {BRAND_TAGLINE} | XAUUSD Fundamental",
    page_icon="🥇",
    layout="wide",
)

# Custom CSS branding
st.markdown(f"""
<style>
    .brand-header {{
        background: linear-gradient(90deg, #111 0%, {BRAND_COLOR} 100%);
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 10px;
    }}
    .brand-title {{
        color: white;
        font-size: 34px;
        font-weight: 900;
        letter-spacing: 1px;
        margin: 0;
    }}
    .brand-title span {{ color: {BRAND_ACCENT}; }}
    .brand-sub {{
        color: #ddd;
        font-size: 13px;
        letter-spacing: 3px;
        margin: 0;
    }}
    .brand-footer {{
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #333;
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="brand-header">
    <p class="brand-title">{BRAND_NAME} <span>{BRAND_TAGLINE}</span></p>
    <p class="brand-sub">XAUUSD FUNDAMENTAL DASHBOARD</p>
</div>
""", unsafe_allow_html=True)

bq = Biquote()

# --- Sidebar ---
st.sidebar.markdown(f"### 🎯 {BRAND_NAME}")
st.sidebar.caption(BRAND_TAGLINE)
st.sidebar.divider()
st.sidebar.header("Filter")
show_news = st.sidebar.checkbox("Tampilkan Berita", value=True)
news_count = st.sidebar.slider("Jumlah berita", 3, 10, 5)

# --- Harga ---
try:
    tick = bq.tick("XAUUSD")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Harga XAUUSD (mid)", f"${tick['mid']:,.2f}")
    with col2:
        st.metric("Perubahan Hari Ini", f"{tick.get('dayDiffPercent', 0):+.2f}%")
except Exception as e:
    st.warning(f"Gagal ambil harga XAUUSD: {e}")

st.divider()

# --- Kalender ---
st.subheader("📅 Kalender High-Impact (US) — Fokus Gold")
try:
    events = bq.calendar(importance="high", countries="US", limit=10)
    if events:
        rows = []
        for ev in events:
            time_str = ev.get("time", "")
            if ev.get("timeMode") != "exact":
                time_str = time_str[:10] + " (tanggal saja)"
            else:
                try:
                    dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    time_str = dt.strftime("%d %b %H:%M UTC")
                except:
                    pass
            rows.append({
                "Waktu": time_str,
                "Event": ev.get("name", "-"),
                "Actual": f"{ev.get('actual')}" if ev.get("actual") is not None else "—",
                "Forecast": f"{ev.get('forecast')}" if ev.get("forecast") is not None else "—",
                "Previous": f"{ev.get('previous')}" if ev.get("previous") is not None else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Actual vs Forecast: selisih jauh = volatilitas tinggi.")
    else:
        st.info("Tidak ada event high-impact US minggu ini.")
except Exception as e:
    st.error(f"Gagal ambil kalender: {e}")

st.divider()

# --- Berita ---
if show_news:
    st.subheader("📰 Berita Terkait Gold & Fed")
    try:
        feed = feedparser.parse("https://www.forexlive.com/feed/news")
        keywords = ["gold", "xau", "fed", "inflation", "rate", "dollar", "usd", "fomc", "cpi", "nfp"]
        filtered = []
        for entry in feed.entries:
            combined = (entry.title + " " + entry.get("summary", "")).lower()
            if any(kw in combined for kw in keywords):
                filtered.append({
                    "Judul": entry.title,
                    "Link": entry.link,
                    "Waktu": entry.get("published", "")[:25] if entry.get("published") else "-"
                })
        if filtered:
            for item in filtered[:news_count]:
                st.markdown(f"**[{item['Judul']}]({item['Link']})**")
                st.caption(item["Waktu"])
        else:
            st.info("Tidak ada berita relevan saat ini.")
    except Exception as e:
        st.error(f"Gagal ambil berita: {e}")

# --- Footer ---
st.markdown(f"""
<div class="brand-footer">
    <b>{BRAND_NAME} {BRAND_TAGLINE}</b> © {datetime.now().year}<br>
    Data: biquote + ForexLive RSS · Bukan saran trading · Trading risiko sendiri.
</div>
""", unsafe_allow_html=True)
