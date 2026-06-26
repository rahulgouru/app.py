import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime, date

# 1. Page Configuration setup
st.set_page_config(
    page_title="Neon Portfolio Ledger", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Neon Custom UI style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #060814 0%, #0b0f24 50%, #150b2b 100%) !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .metric-card {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(139, 92, 246, 0.05) !important;
        margin-bottom: 16px;
    }
    .crypto-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .solana-card { border-left-color: #14f195 !important; }
    .base-card { border-left-color: #0052ff !important; }
    .ethereum-card { border-left-color: #627eea !important; }
    .other-card { border-left-color: #ec4899 !important; }
    
    .chain-badge {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 30px;
        display: inline-block;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .badge-solana { background: rgba(20, 241, 149, 0.15); color: #14f195; border: 1px solid rgba(20, 241, 149, 0.3); }
    .badge-base { background: rgba(0, 82, 255, 0.15); color: #3b82f6; border: 1px solid rgba(0, 82, 255, 0.3); }
    .badge-eth { background: rgba(98, 126, 234, 0.15); color: #a5b4fc; border: 1px solid rgba(98, 126, 234, 0.3); }
    .badge-other { background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }

    .glow-profit {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        color: #10b981 !important;
        font-weight: 700;
    }
    .glow-loss {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        color: #ef4444 !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# File DB Path setup
DB_FILE = "portfolio_db.json"

# Load data helper
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# Save data helper
def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Load current records to session state
if "portfolio_records" not in st.session_state:
    st.session_state.portfolio_records = load_data()

records = st.session_state.portfolio_records

def format_price(val):
    if val == 0: return "$0.00"
    elif abs(val) < 0.01: return f"${val:.8f}"
    elif abs(val) < 1.0: return f"${val:.4f}"
    else: return f"${val:,.2f}"

# Sidebar layout
st.sidebar.markdown("<h2 style='font-family:\"Space Grotesk\", sans-serif; color: #8b5cf6;'>💜 Controls Panel</h2>", unsafe_allow_html=True)

st.sidebar.subheader("➕ Add Transaction Record")
with st.sidebar.form("token_form", clear_on_submit=True):
    chain_choice = st.selectbox("Select Blockchain:", ["Solana", "Base", "Ethereum", "Arbitrum", "Polygon"])
    token_name = st.text_input("Token Name / Symbol:", placeholder="e.g., PEPE")
    new_balance = st.number_input("Token Quantity / Balance:", min_value=0.0, value=0.0, step=0.01)
    new_buy_price = st.number_input("Your Purchase Price (USD):", min_value=0.0, value=0.0, format="%.8f")
    new_price = st.number_input("Current Market Price (USD):", min_value=0.0, value=0.0, format="%.8f")
    buy_date = st.date_input("Purchase Date:", date.today())
    status = st.selectbox("Status:", ["Active", "Sold (Position Closed)"])
    
    sell_price = 0.0
    sell_date = ""
    if status == "Sold (Position Closed)":
        sell_price = st.number_input("Sell Price (USD):", min_value=0.0, value=0.0, format="%.8f")
        sell_date = st.date_input("Sell Date:", date.today()).strftime("%Y-%m-%d")

    submit_btn = st.form_submit_button("Submit Entry 🚀")

if submit_btn and token_name:
    new_record = {
        "Chain": chain_choice,
        "Token": token_name,
        "Balance": float(new_balance),
        "Current Price": float(new_price),
        "Buy Price": float(new_buy_price),
        "Buy Date": buy_date.strftime("%Y-%m-%d"),
        "Status": status,
        "Sell Price": float(sell_price),
        "Sell Date": str(sell_date)
    }
    st.session_state.portfolio_records.append(new_record)
    save_data(st.session_state.portfolio_records)
    st.toast(f"Added {token_name} permanently!")
    st.rerun()

# --- FIXED DELETE RECORD MODULE ---
st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete Record")
if len(records) > 0:
    # Creating dictionary with readable tokens mapping to their actual index
    token_options = {f"{t['Token']} ({t['Chain']}) - Ref #{i}": i for i, t in enumerate(records)}
    selected_option = st.sidebar.selectbox("Select Token to Delete:", list(token_options.keys()))
    
    if st.sidebar.button("Delete Selected ❌", use_container_width=True):
        idx_to_drop = token_options[selected_option] # Get safe accurate integer index
        st.session_state.portfolio_records.pop(idx_to_drop)
        save_data(st.session_state.portfolio_records)
        st.toast("Record deleted successfully!")
        st.rerun()

# Calculations layout main screen
st.markdown("<h1 style='font-family:\"Space Grotesk\", sans-serif; text-align: center; color: #a78bfa;'>🌌 Premium Multi-Chain Web3 Ledger</h1>", unsafe_allow_html=True)
st.markdown("---")

total_portfolio_value = 0.0
total_investment = 0.0
solana_value = 0.0
evm_value = 0.0

for r in records:
    qty = float(r["Balance"])
    buy_p = float(r["Buy Price"])
    curr_p = float(r["Current Price"])
    cost_basis = qty * buy_p
    
    if r["Status"] == "Active":
        current_value = qty * curr_p
        if r["Chain"] == "Solana": solana_value += current_value
        else: evm_value += current_value
    else:
        sell_p = float(r["Sell Price"])
        current_value = qty * sell_p

    total_investment += cost_basis
    total_portfolio_value += current_value

total_net_profit = total_portfolio_value - total_investment
total_pl_pct = (total_net_profit / total_investment * 100) if total_investment > 0 else 0.0

# Metrics Header Panels
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem;font-weight:700;">NET WORTH VALUE</div><div style="color:#f8fafc;font-size:1.8rem;font-weight:800;margin:8px 0;">${total_portfolio_value:,.2f}</div><div style="color:#64748b;font-size:0.85rem;">Cost: ${total_investment:,.2f}</div></div>', unsafe_allow_html=True)
with col2:
    p_sign = "+" if total_net_profit >= 0 else ""
    g_style = "color: #10b981;" if total_net_profit >= 0 else "color: #ef4444;"
    st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem;font-weight:700;">NET PROFIT / LOSS</div><div style="{g_style}font-size:1.8rem;font-weight:800;margin:8px 0;">{p_sign}${total_net_profit:,.2f}</div><div style="{g_style}font-size:0.85rem;font-weight:700;">{p_sign}{total_pl_pct:.2f}% ROI</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div style="color:#14f195;font-size:0.8rem;font-weight:700;">SOLANA BAGS</div><div style="color:#f8fafc;font-size:1.8rem;font-weight:800;margin:8px 0;">${solana_value:,.2f}</div><div style="color:#64748b;font-size:0.85rem;">Active Bags</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div style="color:#3b82f6;font-size:0.8rem;font-weight:700;">EVM BAGS</div><div style="color:#f8fafc;font-size:1.8rem;font-weight:800;margin:8px 0;">${evm_value:,.2f}</div><div style="color:#64748b;font-size:0.85rem;">Base / ETH</div></div>', unsafe_allow_html=True)

# Cards split
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<h3 style='font-family:\"Space Grotesk\", sans-serif; color: #c084fc;'>🔥 Your Positions</h3>", unsafe_allow_html=True)
    if len(records) > 0:
        for r in records:
            qty = float(r["Balance"])
            buy_p = float(r["Buy Price"])
            curr_p = float(r["Current Price"])
            cost_basis = qty * buy_p
            
            try:
                b_date = datetime.strptime(str(r["Buy Date"]), "%Y-%m-%d").date() if isinstance(r["Buy Date"], str) else r["Buy Date"]
            except:
                b_date = date.today()
            
            if r["Status"] == "Active":
                current_value = qty * curr_p
                hold_days = (date.today() - b_date).days
                net_pl = current_value - cost_basis
                curr_price_str = format_price(curr_p)
            else:
                sell_p = float(r["Sell Price"])
                current_value = qty * sell_p
                try:
                    s_date = datetime.strptime(str(r["Sell Date"]), "%Y-%m-%d").date() if r["Sell Date"] else date.today()
                except:
                    s_date = date.today()
                hold_days = (s_date - b_date).days
                net_pl = current_value - cost_basis
                curr_price_str = f"Sold @ {format_price(sell_p)}"
                
            pl_pct = (net_pl / cost_basis * 100) if cost_basis > 0 else 0.0
            chain_class = "solana-card" if r["Chain"] == "Solana" else ("base-card" if r["Chain"] == "Base" else ("ethereum-card" if r["Chain"] in ["Ethereum", "Arbitrum"] else "other-card"))
            badge_class = "badge-solana" if r["Chain"] == "Solana" else ("badge-base" if r["Chain"] == "Base" else ("badge-eth" if r["Chain"] in ["Ethereum", "Arbitrum"] else "badge-other"))
            pl_class = "glow-profit" if net_pl >= 0 else "glow-loss"
            pl_sign = "+" if net_pl >= 0 else ""
            
            st.markdown(f"""
            <div class="crypto-card {chain_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span class="chain-badge {badge_class}">{r["Chain"]}</span>
                        <h4 style="margin: 4px 0; color: #f8fafc; font-size: 1.4rem;">{r["Token"]}</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0;">Qty: <b>{qty:,.4f}</b> | Buy Date: {b_date}</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="{pl_class}" style="display: inline-block; font-size: 1rem; margin-bottom: 8px;">
                            {pl_sign}${net_pl:,.2f} ({pl_sign}{pl_pct:.2f}%)
                        </div>
                        <div style="color: #64748b; font-size: 0.85rem;">Holding: <b>{hold_days} Days</b></div>
                    </div>
                </div>
                <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8;">
                    <div>Buy: <span style="color: #e2e8f0; font-weight: 600;">{format_price(buy_p)}</span></div>
                    <div>Current: <span style="color: #e2e8f0; font-weight: 600;">{curr_price_str}</span></div>
                    <div>Invested: <span style="color: #e2e8f0; font-weight: 600;">{format_price(cost_basis)}</span></div>
                    <div>Value: <span style="color: #a78bfa; font-weight: 700;">{format_price(current_value)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tokens found. Use Sidebar to add fields!")

with col_right:
    st.markdown("<h3 style='font-family:\"Space Grotesk\", sans-serif; color: #c084fc;'>📊 Portfolio Split</h3>", unsafe_allow_html=True)
    active_tokens = [r for r in records if r["Status"] == "Active"]
    if len(active_tokens) > 0:
        chart_data = pd.DataFrame([
            {"Token": row["Token"], "Value": float(row["Balance"]) * float(row["Current Price"])}
            for row in active_tokens
        ])
        fig = px.pie(chart_data, values='Value', names='Token', hole=0.4, color_discrete_sequence=px.colors.sequential.Agsunset)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e2e8f0", margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No active asset positions to chart right now.")
