"""
Indian AI Tax Assistant - Main Streamlit Application
Complete web application with Tax Calculator + AI Chatbot
"""

import streamlit as st
import json
import time
from backend.tax_calculator import TaxCalculator
from backend.chatbot import TaxChatbot

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaxSaathi - AI Indian Tax Assistant",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --saffron: #FF9933;
    --navy: #000080;
    --green: #138808;
    --gold: #C9A84C;
    --bg: #0A0A14;
    --card: #12121E;
    --border: rgba(255,153,51,0.2);
    --text: #E8E4DC;
    --muted: #9A9A9A;
}

* { font-family: 'DM Sans', sans-serif; }
.stApp { background: var(--bg); color: var(--text); }

/* Header */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    background: linear-gradient(135deg, #FF9933 0%, #C9A84C 50%, #138808 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    text-align: center;
    color: var(--muted);
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* Cards */
.tax-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.result-highlight {
    background: linear-gradient(135deg, rgba(255,153,51,0.1), rgba(19,136,8,0.1));
    border: 1px solid var(--saffron);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.regime-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}
.badge-better { background: rgba(19,136,8,0.2); color: #4CAF50; border: 1px solid #4CAF50; }
.badge-old { background: rgba(201,168,76,0.2); color: #C9A84C; border: 1px solid #C9A84C; }
.badge-new { background: rgba(0,0,128,0.3); color: #6699FF; border: 1px solid #6699FF; }

/* Chat */
.chat-bubble-user {
    background: rgba(255,153,51,0.15);
    border: 1px solid rgba(255,153,51,0.3);
    border-radius: 12px 12px 4px 12px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0 0.5rem auto;
    max-width: 80%;
    float: right;
    clear: both;
}
.chat-bubble-bot {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    max-width: 85%;
    float: left;
    clear: both;
}
.chat-container { overflow: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 { color: var(--saffron) !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #FF9933, #C9A84C) !important;
    color: #000 !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.95rem !important;
}
.stButton > button:hover { opacity: 0.9 !important; }

/* Input fields */
.stNumberInput > div > div > input,
.stSelectbox > div > div > select,
.stTextInput > div > div > input {
    background: #1A1A2E !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* Metric styling */
[data-testid="metric-container"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem;
}

/* Section headers */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: var(--saffron);
    margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

.flag-stripe {
    height: 4px;
    background: linear-gradient(90deg, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
    border-radius: 2px;
    margin-bottom: 2rem;
}

.info-box {
    background: rgba(0,0,128,0.15);
    border-left: 3px solid #6699FF;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.warning-box {
    background: rgba(255,153,51,0.1);
    border-left: 3px solid var(--saffron);
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Initialize State ─────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = TaxChatbot()
if "calc_result" not in st.session_state:
    st.session_state.calc_result = None

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇮🇳 TaxSaathi")
    st.markdown("*Your AI Indian Tax Assistant*")
    st.markdown("---")
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "🧮 Tax Calculator", "💬 AI Tax Chatbot", "📚 Tax Guide"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📅 AY 2024-25")
    st.markdown("Based on Union Budget 2023-24 rules")
    
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown(
        "<small style='color:#9A9A9A'>This tool provides general tax information only. "
        "Please consult a qualified CA for professional advice.</small>",
        unsafe_allow_html=True
    )

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">TaxSaathi AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">India\'s Intelligent Tax Assistant · Old vs New Regime · AI-Powered Guidance</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="tax-card" style="text-align:center;">
            <div style="font-size:2.5rem">🧮</div>
            <h3 style="color:#FF9933">Tax Calculator</h3>
            <p style="color:#9A9A9A;font-size:0.9rem">Compare Old vs New regime. Get exact tax breakdowns, deduction analysis, and regime recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="tax-card" style="text-align:center;">
            <div style="font-size:2.5rem">🤖</div>
            <h3 style="color:#C9A84C">AI Tax Chatbot</h3>
            <p style="color:#9A9A9A;font-size:0.9rem">Ask any Indian tax question. Powered by domain-specific AI trained on official tax documents.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="tax-card" style="text-align:center;">
            <div style="font-size:2.5rem">📚</div>
            <h3 style="color:#4CAF50">Tax Guide</h3>
            <p style="color:#9A9A9A;font-size:0.9rem">Comprehensive guide to Indian income tax, deductions, ITR forms, and filing procedures.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Quick Facts — AY 2024-25")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-box">
            <b>New Tax Regime (Default from FY 2023-24)</b><br>
            ₹0–3L: Nil · ₹3–6L: 5% · ₹6–9L: 10% · ₹9–12L: 15% · ₹12–15L: 20% · Above ₹15L: 30%<br>
            <small>Rebate u/s 87A: Tax nil if income ≤ ₹7 Lakh</small>
        </div>
        <div class="info-box">
            <b>Old Tax Regime</b><br>
            ₹0–2.5L: Nil · ₹2.5–5L: 5% · ₹5–10L: 20% · Above ₹10L: 30%<br>
            <small>Rebate u/s 87A: Tax nil if income ≤ ₹5 Lakh</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="warning-box">
            <b>Key Deductions (Old Regime Only)</b><br>
            • 80C: Up to ₹1.5L (PPF, ELSS, LIC, etc.)<br>
            • 80D: Health Insurance up to ₹25,000–₹1L<br>
            • HRA: Partially exempt (LTA, Standard Deduction ₹50,000)<br>
            • Home Loan Interest: Up to ₹2L (Section 24)
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAX CALCULATOR PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🧮 Tax Calculator":
    st.markdown('<div class="section-header">🧮 Income Tax Calculator — AY 2024-25</div>', unsafe_allow_html=True)
    
    calc = TaxCalculator()
    
    with st.expander("ℹ️ How to use this calculator", expanded=False):
        st.markdown("""
        1. Enter your **annual gross income** and applicable deductions
        2. We'll calculate tax under both **Old** and **New** regimes
        3. The tool will **recommend the better regime** and show you how much you save
        4. All calculations follow **Income Tax Act rules for AY 2024-25**
        """)
    
    st.markdown("### 📥 Income Details")
    col1, col2 = st.columns(2)
    
    with col1:
        gross_salary = st.number_input("Annual Gross Salary (₹)", min_value=0, max_value=10_00_00_000, 
                                        value=8_00_000, step=10_000, format="%d",
                                        help="Total CTC or annual salary before any deductions")
        other_income = st.number_input("Other Income (Interest, Rent, etc.) (₹)", 
                                        min_value=0, max_value=10_00_00_000, value=0, step=1000)
        hra_received = st.number_input("HRA Received (₹/year)", 
                                        min_value=0, max_value=10_00_00_000, value=0, step=1000,
                                        help="House Rent Allowance received from employer")
        rent_paid = st.number_input("Actual Rent Paid (₹/year)", 
                                     min_value=0, max_value=10_00_00_000, value=0, step=1000)
        city_type = st.selectbox("City Type (for HRA)", ["Metro (Delhi, Mumbai, Kolkata, Chennai)", "Non-Metro"])
    
    with col2:
        age = st.selectbox("Age Category", 
                           ["Below 60 years", "60–80 years (Senior Citizen)", "Above 80 years (Super Senior Citizen)"])
        sec_80c = st.number_input("Section 80C Investments (₹)", 
                                   min_value=0, max_value=1_50_000, value=0, step=1000,
                                   help="PPF, ELSS, LIC, NSC, EPF, ELSS, Sukanya Samriddhi, etc. Max ₹1.5L")
        sec_80d = st.number_input("Section 80D - Health Insurance Premium (₹)", 
                                   min_value=0, max_value=1_00_000, value=0, step=1000,
                                   help="Self/family: ₹25,000 | Parents (senior): additional ₹50,000")
        home_loan_interest = st.number_input("Home Loan Interest - Sec 24(b) (₹)", 
                                              min_value=0, max_value=2_00_000, value=0, step=1000,
                                              help="Max ₹2L for self-occupied property")
        other_deductions = st.number_input("Other Deductions (80E, 80G, NPS etc.) (₹)", 
                                            min_value=0, max_value=5_00_00_000, value=0, step=1000)
    
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        calculate = st.button("⚡ Calculate Tax", use_container_width=True)
    
    if calculate:
        is_metro = "Metro" in city_type
        age_val = 60 if "60–80" in age else (80 if "Above 80" in age else 0)
        
        inputs = {
            "gross_salary": gross_salary,
            "other_income": other_income,
            "hra_received": hra_received,
            "rent_paid": rent_paid,
            "is_metro": is_metro,
            "sec_80c": sec_80c,
            "sec_80d": sec_80d,
            "home_loan_interest": home_loan_interest,
            "other_deductions": other_deductions,
            "age": age_val
        }
        
        result = calc.calculate(inputs)
        st.session_state.calc_result = result
        
        # ── Results Display ──────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 Tax Calculation Results")
        
        # Recommendation banner
        if result["better_regime"] == "new":
            st.markdown(f"""
            <div class="result-highlight">
                <div style="font-size:0.9rem;color:#9A9A9A">RECOMMENDATION</div>
                <div style="font-size:1.6rem;font-weight:700;color:#4CAF50">✅ New Tax Regime is Better for You</div>
                <div style="font-size:1rem;color:#E8E4DC">You save <b style="color:#FF9933">₹{result['savings']:,}</b> annually by choosing the New Regime</div>
            </div>
            """, unsafe_allow_html=True)
        elif result["better_regime"] == "old":
            st.markdown(f"""
            <div class="result-highlight">
                <div style="font-size:0.9rem;color:#9A9A9A">RECOMMENDATION</div>
                <div style="font-size:1.6rem;font-weight:700;color:#C9A84C">✅ Old Tax Regime is Better for You</div>
                <div style="font-size:1rem;color:#E8E4DC">You save <b style="color:#FF9933">₹{result['savings']:,}</b> annually by choosing the Old Regime</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-highlight">
                <div style="font-size:1.6rem;font-weight:700;color:#6699FF">⚖️ Both Regimes are Equal</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            old = result["old_regime"]
            better_old = result["better_regime"] == "old"
            st.markdown(f"""
            <div class="tax-card" style="border-color:{'#C9A84C' if better_old else 'rgba(255,153,51,0.2)'}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <h3 style="color:#C9A84C;margin:0">Old Tax Regime</h3>
                    {'<span class="regime-badge badge-better">✓ RECOMMENDED</span>' if better_old else ''}
                </div>
                <hr style="border-color:rgba(201,168,76,0.3)">
                <table style="width:100%;font-size:0.9rem">
                    <tr><td style="color:#9A9A9A">Gross Income</td><td style="text-align:right">₹{old['gross_income']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Standard Deduction</td><td style="text-align:right">- ₹{old['standard_deduction']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">HRA Exemption</td><td style="text-align:right">- ₹{old['hra_exemption']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">80C Deductions</td><td style="text-align:right">- ₹{old['deduction_80c']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">80D Deductions</td><td style="text-align:right">- ₹{old['deduction_80d']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Home Loan Interest</td><td style="text-align:right">- ₹{old['home_loan_interest']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Other Deductions</td><td style="text-align:right">- ₹{old['other_deductions']:,}</td></tr>
                    <tr style="font-weight:600"><td>Taxable Income</td><td style="text-align:right">₹{old['taxable_income']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Tax Before Cess</td><td style="text-align:right">₹{old['tax_before_cess']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Rebate u/s 87A</td><td style="text-align:right">- ₹{old['rebate_87a']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Health & Ed. Cess (4%)</td><td style="text-align:right">₹{old['cess']:,}</td></tr>
                    <tr style="font-size:1.1rem;color:#C9A84C;font-weight:700"><td>Total Tax Payable</td><td style="text-align:right">₹{old['total_tax']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Effective Rate</td><td style="text-align:right">{old['effective_rate']:.2f}%</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            new = result["new_regime"]
            better_new = result["better_regime"] == "new"
            st.markdown(f"""
            <div class="tax-card" style="border-color:{'#6699FF' if better_new else 'rgba(255,153,51,0.2)'}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <h3 style="color:#6699FF;margin:0">New Tax Regime</h3>
                    {'<span class="regime-badge badge-better">✓ RECOMMENDED</span>' if better_new else '<span class="regime-badge" style="background:rgba(100,100,100,0.2);color:#666;border:1px solid #444">DEFAULT</span>'}
                </div>
                <hr style="border-color:rgba(102,153,255,0.3)">
                <table style="width:100%;font-size:0.9rem">
                    <tr><td style="color:#9A9A9A">Gross Income</td><td style="text-align:right">₹{new['gross_income']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Standard Deduction</td><td style="text-align:right">- ₹{new['standard_deduction']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Other Deductions</td><td style="text-align:right">₹0 (Not allowed)</td></tr>
                    <tr style="font-weight:600"><td>Taxable Income</td><td style="text-align:right">₹{new['taxable_income']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Tax Before Cess</td><td style="text-align:right">₹{new['tax_before_cess']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Rebate u/s 87A</td><td style="text-align:right">- ₹{new['rebate_87a']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Health & Ed. Cess (4%)</td><td style="text-align:right">₹{new['cess']:,}</td></tr>
                    <tr style="font-size:1.1rem;color:#6699FF;font-weight:700"><td>Total Tax Payable</td><td style="text-align:right">₹{new['total_tax']:,}</td></tr>
                    <tr><td style="color:#9A9A9A">Effective Rate</td><td style="text-align:right">{new['effective_rate']:.2f}%</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        # Tax slab breakdown
        st.markdown("### 📈 Tax Slab Breakdown")
        regime_to_show = st.radio("Show breakdown for:", ["New Regime", "Old Regime"], horizontal=True)
        
        slab_data = result["new_regime"]["slab_breakdown"] if regime_to_show == "New Regime" else result["old_regime"]["slab_breakdown"]
        
        if slab_data:
            st.markdown('<div class="tax-card">', unsafe_allow_html=True)
            for slab in slab_data:
                pct = min(slab['tax'] / max(result["new_regime"]["total_tax"], result["old_regime"]["total_tax"], 1), 1)
                st.markdown(f"""
                <div style="margin:0.5rem 0">
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px">
                        <span style="color:#9A9A9A">{slab['range']}</span>
                        <span>@ {slab['rate']}% → <b>₹{slab['tax']:,}</b></span>
                    </div>
                    <div style="background:#1A1A2E;border-radius:4px;height:6px">
                        <div style="background:linear-gradient(90deg,#FF9933,#C9A84C);width:{pct*100:.1f}%;height:100%;border-radius:4px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No tax applicable in this regime for given income.")

# ═══════════════════════════════════════════════════════════════════════════════
# AI CHATBOT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💬 AI Tax Chatbot":
    st.markdown('<div class="section-header">💬 AI Tax Assistant Chatbot</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("#### 💡 Quick Questions")
        quick_questions = [
            "Which ITR form should I file?",
            "What is Section 80C?",
            "New vs Old regime?",
            "What is HRA exemption?",
            "What is Section 80D?",
            "NPS tax benefits?",
            "Capital gains tax rules?",
            "What is TDS?",
        ]
        for q in quick_questions:
            if st.button(q, key=f"quick_{q}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.get_response(q)
                st.session_state.chat_history.append({"role": "bot", "content": response})
                st.rerun()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col1:
        # Chat display
        chat_container = st.container()
        
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#9A9A9A">
                <div style="font-size:3rem">🤖</div>
                <div style="font-size:1.1rem;margin-top:1rem">Ask me anything about Indian Income Tax!</div>
                <div style="font-size:0.85rem;margin-top:0.5rem">I'm trained on official Income Tax Department documents, the Income Tax Act, and Budget announcements.</div>
            </div>
            """, unsafe_allow_html=True)
        
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-container">
                        <div class="chat-bubble-user">
                            <span style="font-size:0.7rem;color:#9A9A9A">You</span><br>
                            {msg['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-container">
                        <div class="chat-bubble-bot">
                            <span style="font-size:0.7rem;color:#FF9933">🤖 TaxSaathi AI</span><br>
                            {msg['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "Ask your tax question...",
                    placeholder="e.g. How much can I save under 80C?",
                    label_visibility="collapsed"
                )
            with col_send:
                submitted = st.form_submit_button("Send →", use_container_width=True)
        
        if submitted and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Consulting tax knowledge base..."):
                response = st.session_state.chatbot.get_response(user_input)
            st.session_state.chat_history.append({"role": "bot", "content": response})
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAX GUIDE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📚 Tax Guide":
    st.markdown('<div class="section-header">📚 Complete Indian Income Tax Guide</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🗂️ ITR Forms", "💰 Deductions", "📋 Filing Process", "📅 Important Dates", "❓ FAQs"])
    
    with tabs[0]:
        st.markdown("### Which ITR Form Should You File?")
        itr_data = [
            ("ITR-1 (Sahaj)", "Salary/Pension + 1 House Property + Other sources", "Income ≤ ₹50 Lakh. NOT for business income."),
            ("ITR-2", "Capital Gains + Foreign Income + Multiple properties", "No business/professional income"),
            ("ITR-3", "Business/Professional income (non-presumptive)", "Individuals/HUF with business"),
            ("ITR-4 (Sugam)", "Presumptive business income (44AD, 44ADA, 44AE)", "Turnover ≤ ₹2Cr, Professionals ≤ ₹50L"),
            ("ITR-5", "Partnership Firms, LLPs, AOPs, BOIs", "Not for individuals"),
            ("ITR-6", "Companies (not claiming 11 exemption)", "For companies"),
            ("ITR-7", "Trusts, Political Parties, Universities", "Special entities"),
        ]
        for form, desc, note in itr_data:
            st.markdown(f"""
            <div class="tax-card" style="padding:1rem">
                <b style="color:#FF9933">{form}</b> — {desc}<br>
                <small style="color:#9A9A9A">📌 {note}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown("### Key Deductions Under Old Tax Regime")
        deductions = {
            "Section 80C": ("₹1,50,000", "PPF, ELSS, LIC Premium, NSC, EPF, ELSS, Home Loan Principal, Sukanya Samriddhi, 5-yr FD, Tuition fees"),
            "Section 80CCD(1B)": ("₹50,000", "Additional NPS contribution (over and above 80C limit)"),
            "Section 80D": ("₹25,000–₹1,00,000", "Health insurance premium. +₹25K for parents; +₹50K if parents are senior citizens"),
            "Section 80E": ("No limit", "Interest on education loan (for 8 years)"),
            "Section 80EEA": ("₹1,50,000", "Interest on home loan for affordable housing (stamp duty ≤ ₹45L)"),
            "Section 80G": ("50%–100%", "Donations to approved funds/charities"),
            "Section 80GG": ("₹5,000/month max", "Rent paid when no HRA received"),
            "Section 80TTA": ("₹10,000", "Interest on savings account"),
            "Section 80TTB": ("₹50,000", "Interest income for senior citizens (savings + FD)"),
            "Section 24(b)": ("₹2,00,000", "Home loan interest for self-occupied property"),
            "Standard Deduction": ("₹50,000", "Available to all salaried individuals (both regimes from AY 2024-25 in New)"),
            "HRA Exemption": ("Min of 3 conditions", "Actual HRA | Actual Rent - 10% salary | 50%/40% of salary"),
        }
        for sec, (limit, desc) in deductions.items():
            st.markdown(f"""
            <div class="tax-card" style="padding:0.75rem">
                <div style="display:flex;justify-content:space-between">
                    <b style="color:#C9A84C">{sec}</b>
                    <span style="color:#4CAF50;font-weight:600">Max: {limit}</span>
                </div>
                <small style="color:#9A9A9A">{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[2]:
        st.markdown("### ITR Filing Process")
        steps = [
            ("1", "Gather Documents", "Form 16, Form 26AS, AIS, Bank statements, Investment proofs"),
            ("2", "Choose ITR Form", "Based on your income sources (see ITR Forms tab)"),
            ("3", "Choose Tax Regime", "Compare Old vs New regime using our Tax Calculator"),
            ("4", "Go to e-Filing Portal", "Visit incometax.gov.in and login with PAN/Aadhaar"),
            ("5", "Pre-fill & Verify", "Cross-check pre-filled data with Form 16 and 26AS"),
            ("6", "Fill Deductions", "Enter 80C, 80D and other deductions (if Old Regime)"),
            ("7", "Compute Tax", "Verify tax liability and pay any remaining tax (Self Assessment)"),
            ("8", "e-Verify ITR", "Verify using Aadhaar OTP, Net Banking, DSC, or Bank A/C"),
        ]
        for num, title, detail in steps:
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin:0.5rem 0;align-items:flex-start">
                <div style="background:linear-gradient(135deg,#FF9933,#C9A84C);color:#000;border-radius:50%;width:2rem;height:2rem;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">{num}</div>
                <div class="tax-card" style="flex:1;padding:0.75rem;margin:0">
                    <b>{title}</b><br><small style="color:#9A9A9A">{detail}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[3]:
        st.markdown("### Important Tax Dates — FY 2023-24 / AY 2024-25")
        dates = [
            ("June 15", "Advance Tax — 1st Installment (15% of tax)", "warning"),
            ("July 31", "📌 ITR Filing Deadline (Non-audit cases)", "warning"),
            ("September 15", "Advance Tax — 2nd Installment (45% cumulative)", "info"),
            ("October 31", "ITR Filing — Tax Audit cases", "info"),
            ("December 15", "Advance Tax — 3rd Installment (75% cumulative)", "info"),
            ("December 31", "Belated/Revised ITR filing deadline", "warning"),
            ("March 15", "Advance Tax — Final Installment (100%)", "info"),
        ]
        for date, event, type_ in dates:
            color = "#FF9933" if type_ == "warning" else "#6699FF"
            st.markdown(f"""
            <div class="tax-card" style="display:flex;justify-content:space-between;align-items:center;padding:0.75rem;border-color:{color}30">
                <span style="color:{color};font-weight:600;min-width:120px">{date}</span>
                <span>{event}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[4]:
        st.markdown("### Frequently Asked Questions")
        faqs = [
            ("Is it mandatory to file ITR if income < ₹2.5L?", 
             "Generally no, but filing is recommended for loan applications, visa, and refunds. Mandatory if foreign assets, signing authority in foreign account, or high-value transactions exist."),
            ("What is the penalty for late filing?",
             "Fee u/s 234F: ₹5,000 if income > ₹5L, ₹1,000 if income ≤ ₹5L. Additional interest u/s 234A at 1% per month on unpaid tax."),
            ("Can I switch between Old and New regime?",
             "Salaried: Can switch every year. Business income: Can switch only once from New to Old (vice versa allowed once)."),
            ("What is Form 26AS?",
             "Annual Tax Statement showing all TDS deducted on your PAN, advance tax paid, and high-value transactions. Available on Income Tax portal."),
            ("What is AIS (Annual Information Statement)?",
             "Comprehensive statement showing financial transactions — salary, interest, dividends, securities transactions, mutual funds, and more. Verify before filing ITR."),
            ("What happens if TDS is more than tax liability?",
             "You get a refund. Claim it while filing ITR. Refunds are processed within 3-6 months and credited directly to your bank account."),
        ]
        for q, a in faqs:
            with st.expander(q):
                st.markdown(f'<div class="info-box">{a}</div>', unsafe_allow_html=True)
