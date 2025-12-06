import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Thêm thư mục gốc vào path để import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_login_required, render_main_sidebar

# ======================
# CẤU HÌNH TRANG
# ======================
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)

# ======================
# KIỂM TRA ĐĂNG NHẬP + SIDEBAR
# ======================
check_login_required()
render_main_sidebar()

# ======================
# CSS STYLING
# ======================
st.markdown(
    """
    <style>
        /* Nền trang màu xám nhạt */
        [data-testid="stAppViewContainer"] {
            background-color: #f5f5f5;
        }

        /* KPI Cards */
        .kpi-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        .kpi-icon {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin: 0 auto 12px;
        }

        .kpi-icon.pink {
            background-color: #fce7f3;
            color: #ec4899;
        }

        .kpi-icon.orange {
            background-color: #fed7aa;
            color: #f97316;
        }

        .kpi-icon.yellow {
            background-color: #fef3c7;
            color: #f59e0b;
        }

        .kpi-value {
            font-size: 32px;
            font-weight: 700;
            color: #111827;
            margin: 8px 0;
        }

        .kpi-label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }

        .kpi-badge {
            display: inline-block;
            background-color: #dc2626;
            color: #ffffff;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 8px;
        }

        /* Nút header */
        button[key="refresh_btn"] {
            background-color: #f3f4f6 !important;
            border-color: #e5e7eb !important;
            color: #374151 !important;
        }

        button[key="refresh_btn"]:hover {
            background-color: #e5e7eb !important;
        }

        button[key="customize_btn"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
            color: #ffffff !important;
        }

        button[key="customize_btn"]:hover {
            background-color: #3b63b5 !important;
            border-color: #3b63b5 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# LOAD DỮ LIỆU
# ======================
DB_PATH = "database/sanpham.csv"
import os

if not os.path.exists(DB_PATH):
    st.error("❌ Chưa có dữ liệu sản phẩm. Vui lòng thêm sản phẩm trước.")
    st.info("💡 Vui lòng vào trang **Sản Phẩm** để thêm sản phẩm.")
    st.stop()

try:
    df = pd.read_csv(DB_PATH)
    if len(df) == 0:
        st.warning("⚠ Chưa có dữ liệu sản phẩm nào. Vui lòng thêm sản phẩm.")
        st.stop()
except Exception as e:
    st.error(f"❌ Lỗi đọc dữ liệu: {str(e)}")
    st.stop()

# ======================
# HEADER VỚI TITLE VÀ NÚT
# ======================
col_header1, col_header2 = st.columns([3, 2])
with col_header1:
    st.markdown("### 📊 Dashboard tổng quan sản phẩm")
    st.markdown("**Nhìn nhanh tình hình tồn kho, sản phẩm dưới ROP và hiệu quả luân chuyển hàng.**")

with col_header2:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("🔄 Làm mới dữ liệu", use_container_width=True, key="refresh_btn")
    with btn_col2:
        st.button("⚙️ Tuỳ chỉnh dashboard", type="primary", use_container_width=True, key="customize_btn")

# ======================
# KPI TỔNG QUAN
# ======================
total_products = len(df)
total_stock = int(df["Số lượng tồn kho"].sum())
total_rop_low = (df["Số lượng tồn kho"] < df["Điểm đặt hàng lại (ROP)"]).sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon pink">🏷️</div>
            <div class="kpi-value">{total_products}</div>
            <div class="kpi-label">Tổng số sản phẩm</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon orange">📦</div>
            <div class="kpi-value">{total_stock:,}</div>
            <div class="kpi-label">Tổng tồn kho</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    badge_html = f'<span class="kpi-badge">Cần chú ý</span>' if total_rop_low > 0 else ''
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon yellow">⚠️</div>
            <div class="kpi-value">{total_rop_low} {badge_html}</div>
            <div class="kpi-label">Số SP dưới ROP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ======================
# BIỂU ĐỒ - HÀNG 1
# ======================
chart_row1_col1, chart_row1_col2 = st.columns(2)

with chart_row1_col1:
    fig1 = px.bar(
        df,
        x="Tên sản phẩm",
        y="Số lượng tồn kho",
        title="Số lượng tồn kho theo sản phẩm",
        text_auto=True,
        color_discrete_sequence=['#3b82f6']
    )
    fig1.update_layout(
        title_font_size=16,
        title_font_weight='bold',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("**Biểu đồ cột thể hiện tổng tồn kho của từng SKU.**")

with chart_row1_col2:
    fig3 = px.line(
        df,
        x="Tên sản phẩm",
        y="Tồn kho an toàn",
        title="Mức tồn kho an toàn",
        markers=True,
        color_discrete_sequence=['#3b82f6']
    )
    fig3.update_layout(
        title_font_size=16,
        title_font_weight='bold',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("**Đường xu hướng mức tồn kho an toàn theo từng sản phẩm.**")

# ======================
# BIỂU ĐỒ - HÀNG 2
# ======================
chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row2_col1:
    df_chart2 = df.melt(
        id_vars=["Tên sản phẩm"],
        value_vars=["Số lượng tồn kho", "Điểm đặt hàng lại (ROP)"],
        var_name="Loại",
        value_name="Giá trị"
    )
    fig2 = px.bar(
        df_chart2,
        x="Tên sản phẩm",
        y="Giá trị",
        color="Loại",
        barmode="group",
        title="So sánh tồn kho & ROP",
        color_discrete_map={
            "Số lượng tồn kho": "#1e40af",
            "Điểm đặt hàng lại (ROP)": "#60a5fa"
        }
    )
    fig2.update_layout(
        title_font_size=16,
        title_font_weight='bold',
        height=400,
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("**So sánh tồn kho thực tế với điểm đặt hàng lại.**")

with chart_row2_col2:
    fig4 = px.bar(
    df,
    x="Tên sản phẩm",
    y="Hệ số luân chuyển số lượng",
        title="Hệ số luân chuyển sản phẩm",
        text_auto=True,
        color_discrete_sequence=['#3b82f6']
    )
    fig4.update_layout(
        title_font_size=16,
        title_font_weight='bold',
        showlegend=False,
        height=400
)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("**Đánh giá tốc độ luân chuyển của từng SKU trong kỳ.**")

# ======================
# BẢNG TỔNG HỢP
# ======================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📋 Bảng tổng hợp dữ liệu sản phẩm")

# Tạo bảng với style đẹp hơn
st.markdown(
    """
    <style>
        /* Style cho bảng dataframe */
        [data-testid="stDataFrame"] {
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Style cho header của bảng */
        [data-testid="stDataFrame"] table thead {
            background-color: #f9fafb;
        }

        [data-testid="stDataFrame"] table thead th {
            font-weight: 600;
            color: #111827;
            padding: 12px;
        }

        /* Style cho các dòng trong bảng */
        [data-testid="stDataFrame"] table tbody tr {
            border-bottom: 1px solid #e5e7eb;
        }

        [data-testid="stDataFrame"] table tbody tr:hover {
            background-color: #f9fafb;
        }

        [data-testid="stDataFrame"] table tbody td {
            padding: 12px;
            color: #374151;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hiển thị bảng với các cột quan trọng
display_columns = ["Tên sản phẩm", "Mã sản phẩm", "Số lượng tồn kho", 
                   "Điểm đặt hàng lại (ROP)", "Tồn kho an toàn", 
                   "Hệ số luân chuyển số lượng"]

# Thêm cột cảnh báo nếu cần
df_display = df[display_columns].copy()
df_display["Trạng thái"] = df.apply(
    lambda r: "🔴 Dưới ROP" if r["Số lượng tồn kho"] < r["Điểm đặt hàng lại (ROP)"] else "🟢 Bình thường",
    axis=1
)

st.dataframe(df_display, use_container_width=True, height=400)

