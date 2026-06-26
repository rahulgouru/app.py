import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# 1. Page Configuration setup (Very first command asalu break avvakudadhu)
st.set_page_config(
    page_title="Neon Portfolio Ledger", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Neon and Glassmorphic Custom UI style scripts (Unsafe HTML values corrected!)
st.markdown("""
<style>
    /* Space dark theme background details and fonts setup */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #060814 0%, #0b0f24 50%, #150b2b 100%) !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Glowing visual metrics panels */
    .metric-card {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(139, 92, 246, 0.05) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 16px;
    }
    .metric-card:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
        box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.15) !important;
    }
    
    /* Elegant dynamic glass panels crypto cards */
    .crypto-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .crypto-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
    }
    
    /* Chain based border color accents */
    .solana-card { border-left-color: #14f195 !important; }
    .base-card { border-left-color: #0052ff !important; }
    .ethereum-card { border-left-color: #627eea !important; }
    .other-card { border-left-color: #ec4899 !important; }
    
    /* Network style badges configuration */
    .chain-badge {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 30px;
        display: inline-block;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-solana { background: rgba(20, 241, 149, 0.15); color: #14f195; border: 1px solid rgba(20, 241, 149, 0.3); }
    .badge-base { background: rgba(0, 82, 255, 0.15); color: #3b82f6; border: 1px solid rgba(0, 82, 255, 0.3); }
    .badge-eth { background: rgba(98, 126, 234, 0.15); color: #a5b4fc; border: 1px solid rgba(98, 126, 234, 0.3); }
    .badge-other { background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }

    /* Green and Red neon glowing pills for P&L indicators */
    .glow-profit {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        color: #10b981 !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    .glow-loss {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 8px;
        color: #ef4444 !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 2. Local File Based database configuration
DATA_FILE = "portfolio_data.json"

# Local JSON storage database load cheyaniki helper function
def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = [
            {
                "Chain": "Solana", 
                "Token": "WIF", 
                "Balance": 450.0, 
                "Current Price": 2.85,
                "Buy Price": 1.50,
                "Buy Date": "2026-03-10",
                "Status": "Active",
                "Sell Price": 0.0,
                "Sell Date": None
            }
        ]
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
            
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for item in data:
            if item.get("Buy Date") and isinstance(item["Buy Date"], str):
                item["Buy Date"] = datetime.strptime(item["Buy Date"], "%Y-%m-%d").date()
            if item.get("Sell Date") and isinstance(item["Sell Date"], str):
                item["Sell Date"] = datetime.strptime(item["Sell Date"], "%Y-%m-%d").date()
        return data
    except Exception as e:
        st.error(f"Error loading JSON DB: {e}")
        return []

# Local JSON storage database save cheyaniki helper function
def save_data(data):
    serializable_data = []
    for item in data:
        new_item = item.copy()
        if isinstance(new_item.get("Buy Date"), (date, datetime)):
            new_item["Buy Date"] = new_item["Buy Date"].strftime("%Y-%m-%d")
        if isinstance(new_item.get("Sell Date"), (date, datetime)):
            new_item["Sell Date"] = new_item["Sell Date"].strftime("%Y-%m-%d")
        serializable_data.append(new_item)
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(serializable_data, f, indent=4)
    except Exception as e:
        st.error(f"Error writing to file DB: {e}")

# Session state initialization check
if "custom_tokens" not in st.session_state:
    st.session_state.custom_tokens = load_data()

# Decimals precision layouts formats
def format_price(val):
    if val == 0:
        return "$0.00"
    elif abs(val) < 0.01:
        return f"${val:.8f}"
    elif abs(val) < 1.0:
        return f"${val:.4f}"
    else:
        return f"${val:,.2f}"

# 3. Sidebar Panel controls and form setup
st.sidebar.markdown("<h2 style='font-family:\"Space Grotesk\", sans-serif; color: #8b5cf6;'>💜 Controls Panel</h2>", unsafe_allow_html=True)

with st.sidebar.expander("🔗 Wallet Tracking Addresses", expanded=False):
    sol_address = st.text_input("Solana Address:", value="7xKX...v9Wq")
    evm_address = st.text_input("EVM Address:", value="0x71C...3a90")

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Transaction Record")

with st.sidebar.form("token_form", clear_on_submit=True):
    chain_choice = st.selectbox("Select Blockchain:", ["Solana", "Base", "Ethereum", "Arbitrum", "Polygon"])
    token_name = st.text_input("Token Name / Symbol:", placeholder="e.g., PEPE")
    
    new_balance = st.number_input("Token Quantity / Balance:", min_value=0.0, value=0.0, step=0.01, format="%.2f")
    
    new_buy_price = st.number_input(
        "Your Purchase Price (USD):", 
        min_value=0.0, 
        value=0.0, 
        step=0.00000001,
        format="%.8f"
    )
    
    new_price = st.number_input(
        "Current Market Price (USD):", 
        min_value=0.0, 
        value=0.0, 
        step=0.00000001,
        format="%.8f"
    )
    
    buy_date = st.date_input("Purchase Date:", date.today())
    status = st.selectbox("Status:", ["Active", "Sold (Position Closed)"])
    
    sell_price = 0.0
    sell_date = None
    if status == "Sold (Position Closed)":
        sell_price = st.number_input("Sell Price (USD):", min_value=0.0, value=0.0, step=0.00000001, format="%.8f")
        sell_date = st.date_input("Sell Date:", date.today())

    submit_btn = st.form_submit_button("Submit Entry 🚀")

if submit_btn and token_name:
    new_record = {
        "Chain": chain_choice,
        "Token": token_name,
        "Balance": new_balance,
        "Current Price": new_price,
        "Buy Price": new_buy_price,
        "Buy Date": buy_date,
        "Status": status,
        "Sell Price": sell_price,
        "Sell Date": sell_date if status == "Sold (Position Closed)" else None
    }
    st.session_state.custom_tokens.append(new_record)
    save_data(st.session_state.custom_tokens)
    st.toast(f"Added {token_name} successfully!")
    st.rerun()

# Dynamic item delete module
st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete / Manage Record")
if len(st.session_state.custom_tokens) > 0:
    token_list = [f"{t['Token']} ({t['Chain']})" for t in st.session_state.custom_tokens]
    selected_to_delete = st.sidebar.selectbox("Select Token to Delete:", token_list)
    if st.sidebar.button("Delete Selected Token ❌", use_container_width=True):
        idx = token_list.index(selected_to_delete)
        deleted_name = st.session_state.custom_tokens[idx]["Token"]
        st.session_state.custom_tokens.pop(idx)
        save_data(st.session_state.custom_tokens)
        st.toast(f"Deleted {deleted_name} successfully!")
        st.rerun()

# 4. Main Header layout configurations and calculations
st.markdown("<h1 style='font-family:\"Space Grotesk\", sans-serif; text-align: center; color: #a78bfa;'>🌌 Premium Multi-Chain Web3 Ledger</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Monitor entries, dynamic exits, holding periods, and real-time glowing metrics.</p>", unsafe_allow_html=True)
st.markdown("---")

records = st.session_state.custom_tokens
total_portfolio_value = 0.0
total_investment = 0.0
solana_value = 0.0
evm_value = 0.0

# Calculations logic loop
for r in records:
    qty = r["Balance"]
    buy_p = r["Buy Price"]
    curr_p = r["Current Price"]
    cost_basis = qty * buy_p
    
    if r["Status"] == "Active":
        current_value = qty * curr_p
        net_pl = current_value - cost_basis
    else:
        sell_p = r["Sell Price"]
        current_value = qty * sell_p
        net_pl = current_value - cost_basis

    total_investment += cost_basis
    total_portfolio_value += current_value
    if r["Status"] == "Active":
        if r["Chain"] == "Solana":
            solana_value += current_value
        else:
            evm_value += current_value

total_net_profit = total_portfolio_value - total_investment
total_pl_pct = (total_net_profit / total_investment * 100) if total_investment > 0 else 0.0

# Top metrics header glow cards (Exact arguments used!)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Net Worth Value</div>
        <div style="color: #f8fafc; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">${total_portfolio_value:,.2f}</div>
        <div style="color: #64748b; font-size: 0.85rem;">Total Cost: ${total_investment:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    profit_sign = "+" if total_net_profit >= 0 else ""
    glow_style = "color: #10b981;" if total_net_profit >= 0 else "color: #ef4444;"
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Net Profit / Loss</div>
        <div style="{glow_style} font-size: 1.8rem; font-weight: 800; margin: 8px 0;">{profit_sign}${total_net_profit:,.2f}</div>
        <div style="{glow_style} font-size: 0.85rem; font-weight: 700;">{profit_sign}{total_pl_pct:.2f}% (ROI)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #14f195; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Active Solana Bags</div>
        <div style="color: #f8fafc; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">${solana_value:,.2f}</div>
        <div style="color: #64748b; font-size: 0.85rem;">Solana Chain Assets</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #3b82f6; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Active EVM Bags</div>
        <div style="color: #f8fafc; font-size: 1.8rem; font-weight: 800; margin: 8px 0;">${evm_value:,.2f}</div>
        <div style="color: #64748b; font-size: 0.85rem;">Base / ETH Chains</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# THE DEFINITIVE FIX: Streamlit st.columns explicitly passing specifications ratio list!
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<h3 style='font-family:\"Space Grotesk\", sans-serif; color: #c084fc;'>🔥 Your Active & Realized Positions</h3>", unsafe_allow_html=True)
    
    if len(records) > 0:
        for r in records:
            qty = r["Balance"]
            buy_p = r["Buy Price"]
            curr_p = r["Current Price"]
            cost_basis = qty * buy_p
            
            # Purchase date active vs sold checking structures
            if r["Status"] == "Active":
                current_value = qty * curr_p
                hold_days = (date.today() - r["Buy Date"]).days
                net_pl = current_value - cost_basis
                current_price_str = format_price(curr_p)
            else:
                sell_p = r["Sell Price"]
                current_value = qty * sell_p
                hold_days = (r["Sell Date"] - r["Buy Date"]).days if r["Sell Date"] else 0
                net_pl = current_value - cost_basis
                current_price_str = f"Sold @ {format_price(sell_p)}"
                
            pl_pct = (net_pl / cost_basis * 100) if cost_basis > 0 else 0.0
            
            # Dynamic borders logic mapper checking
            chain_class = "other-card"
            badge_class = "badge-other"
            if r["Chain"] == "Solana":
                chain_class = "solana-card"
                badge_class = "badge-solana"
            elif r["Chain"] == "Base":
                chain_class = "base-card"
                badge_class = "badge-base"
            elif r["Chain"] in ["Ethereum", "Arbitrum"]:
                chain_class = "ethereum-card"
                badge_class = "badge-eth"
                
            pl_class = "glow-profit" if net_pl >= 0 else "glow-loss"
            pl_sign = "+" if net_pl >= 0 else ""
            
            # HTML stylized dynamic crypto card
            st.markdown(f"""
            <div class="crypto-card {chain_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span class="chain-badge {badge_class}">{r["Chain"]}</span>
                        <h4 style="margin: 4px 0; color: #f8fafc; font-size: 1.4rem; font-family: 'Space Grotesk', sans-serif;">{r["Token"]}</h4>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin: 4px 0;">Qty: <b>{qty:,.4f}</b> | Buy Date: {r["Buy Date"].strftime("%b %d, %Y")}</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="{pl_class}" style="display: inline-block; font-size: 1rem; margin-bottom: 8px;">
                            {pl_sign}${net_pl:,.2f} ({pl_sign}{pl_pct:.2f}%)
                        </div>
                        <div style="color: #64748b; font-size: 0.85rem;">Holding period: <b>{hold_days} Days</b></div>
                    </div>
                </div>
                <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8;">
                    <div>Buy Price: <span style="color: #e2e8f0; font-weight: 600;">{format_price(buy_p)}</span></div>
                    <div>Current Price: <span style="color: #e2e8f0; font-weight: 600;">{current_price_str}</span></div>
                    <div>Invested: <span style="color: #e2e8f0; font-weight: 600;">{format_price(cost_basis)}</span></div>
                    <div>Net Value: <span style="color: #a78bfa; font-weight: 700;">{format_price(current_value)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No tokens found. Use the sidebar to add custom entries!")

with col_right:
    st.markdown("<h3 style='font-family:\"Space Grotesk\", sans-serif; color: #c084fc;'>📊 Portfolio Split</h3>", unsafe_allow_html=True)
    
    active_tokens = [r for r in records if r["Status"] == "Active"]
    if len(active_tokens) > 0:
        chart_data = pd.DataFrame([
            {"Token": t["Token"], "Value": t["Balance"] * t["Current Price"]}
            for t in active_tokens
        ])
        
        # Plotly charts checks
        try:
            import plotly.express as px
            fig = px.pie(
                chart_data, 
                values='Value', 
                names='Token', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Agsunset
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#e2e8f0",
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart(chart_data.set_index("Token"))
    else:
        st.caption("No active asset positions to chart right now.")