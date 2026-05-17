import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Olist Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #1a1d27; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3450;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #7c83fd;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b92a5;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 0.8rem;
        color: #43d9a0;
        margin-top: 4px;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e0e4f5;
        padding: 8px 0;
        border-bottom: 2px solid #7c83fd;
        margin-bottom: 16px;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3450;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #8b92a5 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #7c83fd !important;
        font-size: 1.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Database connection ────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine("mysql+pymysql://root:Password@localhost/olist")

engine = get_engine()

# ── Data loaders ───────────────────────────────────────────
@st.cache_data
def load_revenue():
    return pd.read_sql("""
        SELECT
            DATE_FORMAT(o.purchase_timestamp, '%%Y-%%m') AS month,
            COUNT(DISTINCT o.order_id)                   AS total_orders,
            ROUND(SUM(p.payment_value), 2)               AS gross_revenue,
            ROUND(AVG(p.payment_value), 2)               AS avg_order_value
        FROM orders o
        JOIN payments p USING (order_id)
        WHERE o.order_status = 'delivered'
        GROUP BY DATE_FORMAT(o.purchase_timestamp, '%%Y-%%m')
        ORDER BY month
    """, engine)

@st.cache_data
def load_delivery():
    return pd.read_sql("""
        SELECT
            c.state,
            COUNT(*) AS total_orders,
            ROUND(AVG(DATEDIFF(o.delivered_customer_at,
                o.purchase_timestamp)), 1) AS actual_days,
            ROUND(AVG(DATEDIFF(o.estimated_delivery,
                o.purchase_timestamp)), 1) AS promised_days,
            ROUND(AVG(DATEDIFF(o.estimated_delivery,
                o.delivered_customer_at)), 1) AS days_early_late
        FROM orders o
        JOIN customers c USING (customer_id)
        WHERE o.order_status = 'delivered'
        AND o.delivered_customer_at IS NOT NULL
        GROUP BY c.state
        ORDER BY actual_days DESC
    """, engine)

@st.cache_data
def load_categories():
    return pd.read_sql("""
        SELECT
            COALESCE(t.category_name_english, p.category_name) AS category_name,
            COUNT(DISTINCT i.order_id) AS total_orders,
            ROUND(SUM(i.price), 2)     AS revenue,
            ROUND(AVG(r.score), 2)     AS avg_score
        FROM order_items i
        JOIN products p USING (product_id)
        JOIN orders o USING (order_id)
        LEFT JOIN reviews r USING (order_id)
        LEFT JOIN category_translation t
            ON p.category_name = t.category_name_portuguese
        WHERE o.order_status = 'delivered'
        GROUP BY COALESCE(t.category_name_english, p.category_name)
        ORDER BY revenue DESC
        LIMIT 20
    """, engine)

@st.cache_data
def load_late():
    return pd.read_sql("""
        SELECT
            DATE_FORMAT(purchase_timestamp, '%%Y-%%u') AS week,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN delivered_customer_at > estimated_delivery
                THEN 1 ELSE 0 END) AS late_orders,
            ROUND(100.0 * SUM(CASE WHEN delivered_customer_at > estimated_delivery
                THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_pct
        FROM orders
        WHERE order_status = 'delivered'
        AND delivered_customer_at IS NOT NULL
        GROUP BY DATE_FORMAT(purchase_timestamp, '%%Y-%%u')
        HAVING COUNT(*) >= 10
        ORDER BY week
    """, engine)

@st.cache_data
def load_sellers():
    return pd.read_sql("""
        SELECT
            i.seller_id,
            COUNT(DISTINCT i.order_id)                        AS total_orders,
            ROUND(SUM(i.price), 2)                            AS total_revenue,
            ROUND(AVG(r.score), 2)                            AS avg_review_score,
            SUM(CASE WHEN r.score <= 2 THEN 1 ELSE 0 END)   AS poor_reviews
        FROM order_items i
        JOIN orders o USING (order_id)
        LEFT JOIN reviews r USING (order_id)
        WHERE o.order_status = 'delivered'
        GROUP BY i.seller_id
        HAVING COUNT(DISTINCT i.order_id) >= 10
        ORDER BY avg_review_score ASC
        LIMIT 20
    """, engine)

# ── Load data ──────────────────────────────────────────────
revenue_df  = load_revenue()
delivery_df = load_delivery()
category_df = load_categories()
late_df     = load_late()
seller_df   = load_sellers()
seller_df.index = [f"Seller {i+1}" for i in range(len(seller_df))]
seller_df = seller_df.drop(columns=["seller_id"])

# ── Plotly theme ───────────────────────────────────────────
PLOT_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor" : "rgba(0,0,0,0)",
    "font"         : {"color": "#c0c6d9", "family": "Inter, sans-serif"},
    "xaxis"        : {"gridcolor": "#1e2130", "showgrid": True},
    "yaxis"        : {"gridcolor": "#1e2130", "showgrid": True},
}

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=60)
    st.markdown("## Olist Analytics")
    st.markdown("---")
    page = st.radio("Navigate", [
        "📈 Revenue Overview",
        "🚚 Delivery Performance",
        "🏷️ Category Insights",
        "⭐ Seller Scorecard",
        "⚠️ Late Delivery Alerts"
    ])
    st.markdown("---")
    st.markdown("**Dataset**")
    st.caption("Brazilian E-Commerce")
    st.caption("99,441 orders · 2017–2018")

# ── KPI Cards (always visible) ─────────────────────────────
st.markdown("### Key Performance Indicators")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Total Revenue",   f"R$ {revenue_df['gross_revenue'].sum():,.0f}")
c2.metric("📦 Total Orders",    f"{revenue_df['total_orders'].sum():,}")
c3.metric("🛒 Avg Order Value", f"R$ {revenue_df['avg_order_value'].mean():.2f}")
c4.metric("⏱️ Avg Delivery",   f"{delivery_df['actual_days'].mean():.1f} days")
c5.metric("⚠️ Avg Late Rate",  f"{late_df['late_pct'].mean():.1f}%")

st.markdown("---")

# ══════════════════════════════════════════════════════════
# PAGE 1 — Revenue Overview
# ══════════════════════════════════════════════════════════
if page == "📈 Revenue Overview":
    st.markdown('<div class="section-header">Monthly Revenue Trend</div>',
                unsafe_allow_html=True)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=revenue_df["month"],
        y=revenue_df["gross_revenue"],
        mode="lines+markers",
        name="Revenue",
        line=dict(color="#7c83fd", width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(124,131,253,0.1)"
    ))
    fig1.update_layout(**PLOT_THEME, height=350,
                       xaxis_title="Month", yaxis_title="Revenue (BRL)")
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Orders per Month</div>',
                    unsafe_allow_html=True)
        fig2 = px.bar(revenue_df, x="month", y="total_orders",
                      color="total_orders",
                      color_continuous_scale=["#1e2130", "#7c83fd"])
        fig2.update_layout(**PLOT_THEME, height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Avg Order Value Trend</div>',
                    unsafe_allow_html=True)
        fig3 = px.line(revenue_df, x="month", y="avg_order_value",
                       markers=True,
                       color_discrete_sequence=["#43d9a0"])
        fig3.update_layout(**PLOT_THEME, height=300)
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — Delivery Performance
# ══════════════════════════════════════════════════════════
elif page == "🚚 Delivery Performance":
    st.markdown('<div class="section-header">Actual vs Promised Delivery Days by State</div>',
                unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=delivery_df["state"], y=delivery_df["actual_days"],
        name="Actual Days", marker_color="#7c83fd"
    ))
    fig.add_trace(go.Bar(
        x=delivery_df["state"], y=delivery_df["promised_days"],
        name="Promised Days", marker_color="#43d9a0"
    ))
    fig.update_layout(**PLOT_THEME, barmode="group", height=400,
                      xaxis_title="State", yaxis_title="Days")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Top 10 Slowest States</div>',
                    unsafe_allow_html=True)
        fig2 = px.bar(delivery_df.head(10), x="actual_days", y="state",
                      orientation="h", color="actual_days",
                      color_continuous_scale=["#252a3d", "#ff6b6b"])
        fig2.update_layout(**PLOT_THEME, height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Days Early vs Late by State</div>',
                    unsafe_allow_html=True)
        fig3 = px.bar(delivery_df, x="state", y="days_early_late",
                      color="days_early_late",
                      color_continuous_scale=["#ff6b6b", "#43d9a0"])
        fig3.update_layout(**PLOT_THEME, height=350)
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 3 — Category Insights
# ══════════════════════════════════════════════════════════
elif page == "🏷️ Category Insights":
    st.markdown('<div class="section-header">Revenue vs Satisfaction by Category</div>',
                unsafe_allow_html=True)

    fig = px.scatter(
        category_df, x="revenue", y="avg_score",
        size="total_orders", hover_name="category_name",
        color="avg_score", color_continuous_scale=["#ff6b6b", "#43d9a0"],
        labels={"revenue": "Revenue (BRL)", "avg_score": "Avg Review Score"}
    )
    fig.update_layout(**PLOT_THEME, height=420)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Top 10 by Revenue</div>',
                    unsafe_allow_html=True)
        fig2 = px.bar(category_df.head(10), x="revenue", y="category_name",
                      orientation="h", color="revenue",
                      color_continuous_scale=["#1e2130", "#7c83fd"])
        fig2.update_layout(**PLOT_THEME, height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Top 10 by Satisfaction</div>',
                    unsafe_allow_html=True)
        top_sat = category_df.sort_values("avg_score", ascending=False).head(10)
        fig3 = px.bar(top_sat, x="avg_score", y="category_name",
                      orientation="h", color="avg_score",
                      color_continuous_scale=["#1e2130", "#43d9a0"])
        fig3.update_layout(**PLOT_THEME, height=350)
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════
# PAGE 4 — Seller Scorecard
# ══════════════════════════════════════════════════════════
elif page == "⭐ Seller Scorecard":
    st.markdown('<div class="section-header">Bottom 20 Sellers by Review Score</div>',
                unsafe_allow_html=True)

    fig = px.scatter(
        seller_df, x="total_orders", y="avg_review_score",
        size="poor_reviews", color="avg_review_score",
        hover_data=["total_revenue", "poor_reviews"],
        color_continuous_scale=["#ff6b6b", "#43d9a0"],
        labels={"total_orders": "Total Orders",
                "avg_review_score": "Avg Review Score"}
    )
    fig.update_layout(**PLOT_THEME, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Seller Data Table</div>',
                unsafe_allow_html=True)
    st.dataframe(
        seller_df.style.background_gradient(
            subset=["avg_review_score"], cmap="RdYlGn"
        ),
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════
# PAGE 5 — Late Delivery Alerts
# ══════════════════════════════════════════════════════════
elif page == "⚠️ Late Delivery Alerts":
    st.markdown('<div class="section-header">Weekly Late Delivery Rate</div>',
                unsafe_allow_html=True)

    breaches = late_df[late_df["late_pct"] > 10]
    st.error(f"⚠️ {len(breaches)} weeks exceeded the 10% late delivery threshold")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=late_df["week"], y=late_df["late_pct"],
        mode="lines", name="Late %",
        line=dict(color="#7c83fd", width=2),
        fill="tozeroy", fillcolor="rgba(124,131,253,0.1)"
    ))
    fig.add_hline(y=10, line_dash="dash", line_color="#ff6b6b",
                  annotation_text="10% Alert Threshold",
                  annotation_font_color="#ff6b6b")
    fig.update_layout(**PLOT_THEME, height=380,
                      xaxis_title="Week", yaxis_title="Late Delivery %")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Weeks Breaching Threshold</div>',
                unsafe_allow_html=True)
    st.dataframe(breaches.sort_values("late_pct", ascending=False),
                 use_container_width=True)

st.markdown("---")
st.caption("Olist Brazilian E-Commerce Analytics · Built with Streamlit + MySQL + Python")
