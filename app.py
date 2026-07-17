"""
Jar - Growth Intern Assignment Dashboard
Author: Hasini

Run with:  streamlit run app.py
Requires List_of_Orders.xlsx, Order_Details.xlsx, Sales_target.xlsx
in the same folder as this file.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# Page config & theme
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Jar | Growth Intern Assignment", page_icon="📊", layout="wide")

NAVY = "#1f3a5f"
GOLD = "#b8860b"
RED = "#b03a2e"
GREEN = "#1e7d32"
GREY = "#5a5a5a"

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    h1, h2, h3 { color: #16283f; }
    .metric-card {
        background: #f4f6f9; border-radius: 10px; padding: 18px 20px;
        border-left: 5px solid #1f3a5f;
    }
    .insight-box {
        background: #fff8e6; border-left: 5px solid #b8860b;
        padding: 14px 18px; border-radius: 8px; margin: 10px 0;
    }
    .loss-box {
        background: #fdecea; border-left: 5px solid #b03a2e;
        padding: 14px 18px; border-radius: 8px; margin: 10px 0;
    }
    .good-box {
        background: #e8f5e9; border-left: 5px solid #1e7d32;
        padding: 14px 18px; border-radius: 8px; margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    orders = pd.read_excel("List_of_Orders.xlsx")
    details = pd.read_excel("Order_Details.xlsx")
    target = pd.read_excel("Sales_target.xlsx")
    orders["Order Date"] = pd.to_datetime(orders["Order Date"])
    merged = pd.merge(orders, details, on="Order ID", how="inner")
    return orders, details, target, merged


try:
    orders, details, target, merged = load_data()
except FileNotFoundError as e:
    st.error(
        "Couldn't find one of the Excel files. Make sure List_of_Orders.xlsx, "
        "Order_Details.xlsx and Sales_target.xlsx are in the same folder as app.py.\n\n"
        f"Details: {e}"
    )
    st.stop()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📊 Jar — Growth Intern Assignment")
st.caption("Sales Analysis · App Exploration · Product Strategy  |  Submitted by Hasini")

tabs = st.tabs([
    "🏠 Overview",
    "🛋️ Part 1 — Category Profitability",
    "🎯 Part 2 — Furniture Targets",
    "🗺️ Part 3 — Regional Insights",
    "📱 Q2 — App Exploration",
    "💡 Q3 — Product Strategy",
])

# ===========================================================================
# TAB 0 — OVERVIEW
# ===========================================================================
with tabs[0]:
    st.subheader("Executive Summary")

    total_sales = merged["Amount"].sum()
    total_profit = merged["Profit"].sum()
    margin = total_profit / total_sales * 100
    n_orders = merged["Order ID"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", f"{n_orders:,}")
    c2.metric("Total Sales", f"₹{total_sales:,.0f}")
    c3.metric("Total Profit", f"₹{total_profit:,.0f}")
    c4.metric("Overall Margin", f"{margin:.2f}%")

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Key findings at a glance")
        st.markdown(
            """
            - **Clothing** has the healthiest profit margin (8.03%) despite the lowest profit-per-order.
            - **Electronics** generates the highest total profit, driven by high per-order value.
            - **Furniture** is the clear underperformer (1.81% margin) — almost entirely because of the
              **Tables** sub-category, which runs at **−17.74% margin**.
            - Furniture's monthly target rises smoothly (~1%/month) with quarterly step-ups in **Jul, Nov, Mar**.
            - **Madhya Pradesh** and **Maharashtra** drive order volume, but **Punjab** — also a top-5 state —
              is actually **loss-making**. Several lower-volume states (West Bengal, UP, Haryana) are far
              more profitable per order.
            """
        )
    with colB:
        cat_summary = (
            merged.groupby("Category")
            .agg(Total_Sales=("Amount", "sum"), Total_Profit=("Profit", "sum"))
            .reset_index()
        )
        cat_summary["Margin %"] = (cat_summary["Total_Profit"] / cat_summary["Total_Sales"] * 100).round(2)
        fig = px.pie(
            cat_summary, names="Category", values="Total_Sales", hole=0.5,
            color="Category",
            color_discrete_map={"Electronics": NAVY, "Clothing": GOLD, "Furniture": RED},
            title="Share of Total Sales by Category",
        )
        fig.update_traces(textinfo="label+percent")
        st.plotly_chart(fig, width='stretch', config={'scrollZoom': False})

# ===========================================================================
# TAB 1 — PART 1: CATEGORY PROFITABILITY
# ===========================================================================
with tabs[1]:
    st.subheader("Part 1: Sales & Profitability Analysis by Category")
    st.write(
        "List of Orders and Order Details were merged on **Order ID** "
        f"({merged['Order ID'].nunique()} orders → {len(merged)} line items, zero unmatched records)."
    )

    cat = (
        merged.groupby("Category")
        .agg(Total_Sales=("Amount", "sum"), Total_Profit=("Profit", "sum"), Line_Items=("Amount", "count"))
        .reset_index()
    )
    cat["Avg_Profit_per_Order"] = (cat["Total_Profit"] / cat["Line_Items"]).round(2)
    cat["Profit_Margin_%"] = (cat["Total_Profit"] / cat["Total_Sales"] * 100).round(2)
    cat = cat.sort_values("Total_Sales", ascending=False)

    st.dataframe(
        cat.rename(columns={
            "Total_Sales": "Total Sales (₹)", "Total_Profit": "Total Profit (₹)",
            "Line_Items": "Line Items", "Avg_Profit_per_Order": "Avg Profit/Order (₹)",
            "Profit_Margin_%": "Profit Margin (%)"
        }),
        width='stretch', hide_index=True,
    )

    fig1 = go.Figure()
    fig1.add_bar(x=cat["Category"], y=cat["Total_Sales"], name="Total Sales (₹)", marker_color=NAVY, yaxis="y1")
    fig1.add_trace(go.Scatter(
        x=cat["Category"], y=cat["Profit_Margin_%"], name="Profit Margin (%)",
        mode="lines+markers+text", line=dict(color=RED, width=3), marker=dict(size=10),
        text=[f"{v}%" for v in cat["Profit_Margin_%"]], textposition="top center", yaxis="y2",
    ))
    fig1.update_layout(
        title="Category-wise Total Sales vs Profit Margin",
        yaxis=dict(title="Total Sales (₹)"),
        yaxis2=dict(title="Profit Margin (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.15), height=460,
    )
    st.plotly_chart(fig1, width='stretch', config={'scrollZoom': False})

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="good-box"><b>Top performers</b><br>'
                    '<b>Clothing</b> — best margin (8.03%), high volume, low risk.<br>'
                    '<b>Electronics</b> — best absolute profit (₹10,494) and profit/order (₹34.07).</div>',
                    unsafe_allow_html=True)
    with right:
        st.markdown('<div class="loss-box"><b>Underperformer</b><br>'
                    '<b>Furniture</b> — weakest on every metric: just 1.81% margin, '
                    '4–5× thinner than the other two categories.</div>', unsafe_allow_html=True)

    st.markdown("#### Sub-category drill-down: where the losses actually come from")
    sub = (
        merged.groupby(["Category", "Sub-Category"])
        .agg(Total_Sales=("Amount", "sum"), Total_Profit=("Profit", "sum"), Line_Items=("Amount", "count"))
        .reset_index()
    )
    sub["Profit_Margin_%"] = (sub["Total_Profit"] / sub["Total_Sales"] * 100).round(2)

    cat_filter = st.selectbox("Filter sub-categories by category", ["All"] + list(cat["Category"]))
    sub_view = sub if cat_filter == "All" else sub[sub["Category"] == cat_filter]

    fig2 = px.bar(
        sub_view.sort_values("Profit_Margin_%"), x="Sub-Category", y="Profit_Margin_%",
        color="Profit_Margin_%", color_continuous_scale=[RED, "#f4d35e", GREEN],
        title="Profit Margin by Sub-Category", text="Profit_Margin_%",
    )
    fig2.update_traces(texttemplate="%{text}%", textposition="outside")
    fig2.add_hline(y=0, line_color="black", line_width=1)
    fig2.update_layout(height=440, coloraxis_showscale=False)
    st.plotly_chart(fig2, width='stretch', config={'scrollZoom': False})

    loss_makers = sub[sub["Total_Profit"] < 0].sort_values("Total_Profit")
    st.markdown(
        f'<div class="loss-box"><b>Net-loss sub-categories:</b><br>'
        + "<br>".join(
            f"• <b>{r['Sub-Category']}</b> ({r['Category']}) — ₹{r['Total_Sales']:,.0f} sales, "
            f"₹{r['Total_Profit']:,.0f} profit, {r['Profit_Margin_%']}% margin"
            for _, r in loss_makers.iterrows()
        )
        + "</div>", unsafe_allow_html=True,
    )

    with st.expander("Likely reasons & recommendations"):
        st.markdown(
            """
            **Likely reasons for the gap**
            - Discounting pressure on big-ticket, low-frequency items (Tables) erodes margin more than on small accessories.
            - Bulky/fragile Furniture items carry a higher logistics-cost-to-value ratio (shipping, damage, returns).
            - Electronic Games likely behaves as a promotional/loss-leader line rather than a standalone profit driver.
            - Clothing's portfolio mix skews toward small, high-margin accessories that offset weaker lines like Saree.

            **Recommendations**
            - Re-price or add a paid delivery/assembly add-on for Tables instead of absorbing the cost in the product price.
            - Check whether Electronic Games genuinely lifts attach-rate sales elsewhere; if not, reprice it.
            - Prioritise marketing spend on high-margin lines: T-Shirt, Stole, Hankerchief, Electronics Accessories, Printers.
            """
        )

# ===========================================================================
# TAB 2 — PART 2: FURNITURE TARGETS
# ===========================================================================
with tabs[2]:
    st.subheader("Part 2: Target Achievement Analysis — Furniture")

    furn = target[target["Category"] == "Furniture"].copy()
    furn["Month"] = furn["Month of Order Date"].dt.strftime("%b")
    fiscal_order = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    furn["Month"] = pd.Categorical(furn["Month"], categories=fiscal_order, ordered=True)
    furn = furn.sort_values("Month").reset_index(drop=True)
    furn["Pct_Change_MoM"] = furn["Target"].pct_change().mul(100).round(2)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=furn["Month"], y=furn["Target"], mode="lines+markers+text",
        line=dict(color=NAVY, width=3), marker=dict(size=9),
        text=furn["Target"], textposition="top center", fill="tozeroy",
        fillcolor="rgba(31,58,95,0.08)",
    ))
    # highlight quarterly step-ups
    for m in ["Jul", "Nov", "Mar"]:
        row = furn[furn["Month"] == m]
        fig3.add_annotation(
            x=m, y=row["Target"].values[0], text=f"+{row['Pct_Change_MoM'].values[0]}%",
            showarrow=True, arrowhead=2, ay=-35, font=dict(color=RED, size=13, family="Arial Black"),
        )
    fig3.update_layout(
        title="Furniture Monthly Target Trend (Apr → Mar)",
        yaxis_title="Target (₹)",
        yaxis=dict(range=[furn["Target"].min() * 0.9, furn["Target"].max() * 1.1]),
        height=460,
    )
    st.plotly_chart(fig3, width='stretch', config={'scrollZoom': False})

    st.dataframe(
        furn[["Month", "Target", "Pct_Change_MoM"]].rename(
            columns={"Target": "Furniture Target (₹)", "Pct_Change_MoM": "MoM % Change"}
        ),
        width='stretch', hide_index=True,
    )

    st.markdown(
        '<div class="insight-box">'
        "<b>Trend analysis</b><br>"
        "• Overall pattern is smooth, not volatile — targets rise ~0.9–1%/month, "
        "growing +13.5% cumulatively from April to March.<br>"
        "• The three largest increases — <b>Jul (+1.89%), Nov (+1.80%), Mar (+1.72%)</b> — each fall at a "
        "quarter-end, suggesting a quarterly re-baseline rather than pure linear growth (likely tied to "
        "festive/wedding-season demand and financial-year-end pushes).<br>"
        "• No genuine 'fluctuation' risk — the real risk is whether steadily rising targets are matched by "
        "steadily rising <i>actual</i> sales, especially since Furniture already has the thinnest margin (1.81%)."
        "</div>", unsafe_allow_html=True,
    )

    with st.expander("Strategies to align targets with actual performance"):
        st.markdown(
            """
            - Tie the Jul/Nov/Mar step-ups explicitly to seasonal campaigns so the sales team has a matching lever.
            - Set targets with a margin-adjusted view, not just revenue — Tables already runs at a loss.
            - Use a rolling 3-month actual-vs-target variance review instead of a single annual check.
            - Set sub-category-level sub-targets (protect Bookcases, restructure Tables) within the category target.
            """
        )

# ===========================================================================
# TAB 3 — PART 3: REGIONAL INSIGHTS
# ===========================================================================
with tabs[3]:
    st.subheader("Part 3: Regional Performance Insights")

    state_perf = (
        merged.groupby("State")
        .agg(Order_Count=("Order ID", "nunique"), Total_Sales=("Amount", "sum"), Total_Profit=("Profit", "sum"))
        .reset_index()
    )
    state_perf["Avg_Profit_per_Order"] = (state_perf["Total_Profit"] / state_perf["Order_Count"]).round(2)
    state_perf["Profit_Margin_%"] = (state_perf["Total_Profit"] / state_perf["Total_Sales"] * 100).round(2)

    top5 = state_perf.sort_values("Order_Count", ascending=False).head(5)

    c1, c2 = st.columns(2)
    with c1:
        fig4 = px.bar(
            top5.sort_values("Order_Count"), x="Order_Count", y="State", orientation="h",
            color="Order_Count", color_continuous_scale=[[0, "#a9c1dd"], [1, NAVY]],
            title="Top 5 States by Order Count", text="Order_Count",
        )
        fig4.update_layout(height=420, coloraxis_showscale=False)
        st.plotly_chart(fig4, width='stretch', config={'scrollZoom': False})
    with c2:
        colors = [GREEN if m > 0 else RED for m in top5["Profit_Margin_%"]]
        fig5 = go.Figure(go.Bar(
            x=top5["State"], y=top5["Profit_Margin_%"], marker_color=colors,
            text=[f"{v}%" for v in top5["Profit_Margin_%"]], textposition="outside",
        ))
        fig5.add_hline(y=0, line_color="black", line_width=1)
        fig5.update_layout(title="Profit Margin — Top 5 States by Volume", height=420)
        st.plotly_chart(fig5, width='stretch', config={'scrollZoom': False})

    st.dataframe(
        top5.rename(columns={
            "Order_Count": "Order Count", "Total_Sales": "Total Sales (₹)", "Total_Profit": "Total Profit (₹)",
            "Avg_Profit_per_Order": "Avg Profit/Order (₹)", "Profit_Margin_%": "Profit Margin (%)"
        }),
        width='stretch', hide_index=True,
    )

    st.markdown("#### Full state ranking (all 19 states) — volume vs. profitability")
    sort_choice = st.radio("Sort by:", ["Profit Margin (%)", "Order Count", "Total Sales (₹)"], horizontal=True)
    sort_map = {"Profit Margin (%)": "Profit_Margin_%", "Order Count": "Order_Count", "Total Sales (₹)": "Total_Sales"}
    st.dataframe(
        state_perf.sort_values(sort_map[sort_choice], ascending=False).rename(columns={
            "Order_Count": "Order Count", "Total_Sales": "Total Sales (₹)", "Total_Profit": "Total Profit (₹)",
            "Avg_Profit_per_Order": "Avg Profit/Order (₹)", "Profit_Margin_%": "Profit Margin (%)"
        }),
        width='stretch', hide_index=True, height=350,
    )

    st.markdown(
        '<div class="loss-box"><b>Regional disparities</b><br>'
        "• <b>Punjab</b> is a top-5 state by volume but the only one of the five running at a "
        "<b>net loss (−3.63% margin)</b>.<br>"
        "• <b>Tamil Nadu</b> has the worst margin in the entire dataset (−36.41%), though low volume today.<br>"
        "• Order volume does not predict profitability — <b>West Bengal (17.75%), Uttar Pradesh (14.48%), "
        "Haryana (14.95%)</b> are far more profitable per rupee than any top-5 state by volume."
        "</div>", unsafe_allow_html=True,
    )

    with st.expander("Regions to prioritise"):
        st.markdown(
            """
            - **Punjab** — diagnose the loss (likely discounting or product mix) before scaling volume further.
            - **Tamil Nadu** — contain and fix before any expansion investment; currently the worst-margin state.
            - **West Bengal, UP, Haryana, Kerala** — already highly profitable at moderate volume; strong
              candidates for increased marketing/distribution investment to scale volume, the way Maharashtra has.
            """
        )

# ===========================================================================
# TAB 4 — Q2: APP EXPLORATION
# ===========================================================================
with tabs[4]:
    st.subheader("Question 2 — App Exploration")
    st.caption("Based on hands-on use of the Jar app plus a review of Play Store / App Store / independent reviews.")

    good, improve = st.columns(2)
    with good:
        st.markdown("### ✅ Five things Jar gets right")
        items = [
            ("Radically low entry point (₹10 auto-save)",
             "Removes the biggest psychological barrier to investing for first-time savers."),
            ("Round-off / spare-change automation",
             "Rounding UPI spends and auto-investing the difference makes saving a zero-decision habit."),
            ("Flexible auto-pay cadence (daily/weekly/monthly)",
             "Fits irregular income patterns — gig workers, students, small-business owners."),
            ("Bundled financial services on the same rails",
             "Loans, health insurance, jewellery cross-sold inside an app users already trust."),
            ("Gamified engagement layer (Spin & Win, Jar Coins, referrals)",
             "Keeps a low-involvement product feeling active and rewarding day to day."),
        ]
        for i, (t, d) in enumerate(items, 1):
            st.markdown(f"**{i}. {t}**")
            st.write(d)

    with improve:
        st.markdown("### 🔧 Five areas where Jar could improve")
        items2 = [
            ("Pricing transparency at the point of purchase",
             "Users report confusion about how much of the paid amount converts to gold after spread/GST/charges."),
            ("Withdrawal speed and clarity",
             "Delays and unclear status updates during redemption undercut the 'available when you need it' promise."),
            ("Customer support responsiveness",
             "Slow or templated responses on account/withdrawal issues are trust-critical, not just service quality."),
            ("Referral and rewards reliability",
             "Reports of rewards not crediting correctly quietly undermine a core organic growth channel."),
            ("Clarity on regulatory status & jewellery terms",
             "Being proactive about protections and no-cancellation terms (before checkout) builds more trust than reactive replies."),
        ]
        for i, (t, d) in enumerate(items2, 1):
            st.markdown(f"**{i}. {t}**")
            st.write(d)

# ===========================================================================
# TAB 5 — Q3: PRODUCT STRATEGY
# ===========================================================================
with tabs[5]:
    st.subheader("Question 3 — New Business Opportunities for Jar")
    st.write(
        "Jar's real asset isn't gold — it's the automated, trusted, daily-touch savings habit built with "
        "4 crore+ users. Every opportunity below extends that same automation-and-trust engine into an "
        "adjacent need, rather than asking users to adopt a new behaviour from scratch."
    )

    ideas = [
        ("🎯 Goal-based micro-investing beyond gold",
         "Extend the round-off/auto-pay engine to goals (a phone, a wedding, an emergency fund), split "
         "across gold, liquid funds, or RDs based on time horizon — same mechanism, more destinations."),
        ("📈 'Jar Score' — a credit-readiness layer",
         "Consistent automated saving is a strong signal of repayment discipline. Build a savings-based "
         "credit score to underwrite cheaper Jar loans, and eventually share it (with consent) with partner lenders."),
        ("👨‍👩‍👧 Family & group savings pots",
         "A shared pot for multiple contributors auto-paying into one goal matches how Indian households "
         "already pool money informally — a natural entry into group/community savings."),
        ("🛡️ Bite-sized insurance & protection products",
         "Extend the existing health insurance model to accident cover, gold-theft cover, or gold-linked "
         "life cover — sold in the same ₹10–50/day increments users already trust."),
        ("🏪 Merchant & gig-worker savings-as-a-service",
         "A merchant-facing version of the auto-save engine that diverts a % of each UPI payment received "
         "into savings — extending the same tech to the supply side of UPI, not just consumers."),
    ]
    for title, desc in ideas:
        st.markdown(f"#### {title}")
        st.write(desc)

    st.markdown("---")
    st.markdown("#### How Jar can execute without diluting its core value proposition")
    st.markdown(
        """
        - **Automation-first, not app-redesign-first** — every idea reuses the existing auto-pay engine, so it
          feels like "more of what Jar already does for me," not a new product to learn.
        - **Trust before monetisation** — close the pricing-transparency and support gaps from Q2 before
          layering new financial products on top; new offerings inherit the reputation of the old ones.
        - **Segment by income regularity, not just demographics** — salaried users, gig workers, and merchants
          have different cash-flow shapes and need different default cadences.
        - **Milestone-based trust building** — auto gold saving → goal-based diversification → credit-readiness →
          protection products, each unlocked by demonstrated saving behaviour.
        """
    )

st.markdown("---")
st.caption("Built with Python (pandas) + Streamlit + Plotly · Data: List of Orders, Order Details, Sales Target")