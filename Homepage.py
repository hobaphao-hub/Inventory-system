import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import unquote
from utils import load_session, save_session, clear_session, render_main_sidebar

st.set_page_config(
    page_title="Trang Chủ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Khôi phục trạng thái đăng nhập từ file
if "logged_in" not in st.session_state:
    st.session_state.logged_in = load_session()

# Hàm kiểm tra đăng nhập
def check_login(email, password):
    return email == "admin@example.com" and password == "123456"

# ================================
# 1. Giao diện đăng nhập bằng HTML
# ================================
if not st.session_state.logged_in:

    # Ẩn sidebar, menu + kéo full width
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {display: none;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            #MainMenu {visibility: hidden;}

            .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }
            [data-testid="stAppViewContainer"] {
                padding: 0 !important;
            }
            body {
                margin: 0;
                padding: 0;
                background-color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Đọc query params để nhận email+password từ HTML
    email = st.query_params.get("email", "")
    password = st.query_params.get("password", "")

    if email and password:
        email = unquote(email)
        password = unquote(password)

        if check_login(email, password):
            st.session_state.logged_in = True
            save_session(True)  # Lưu trạng thái vào file
            st.rerun()
        else:
            st.error("Sai email hoặc mật khẩu!")

    # Load giao diện HTML
    try:
        with open("login.html", "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=800, scrolling=False)
    except FileNotFoundError:
        st.error("Không tìm thấy file login.html")
        # Fallback form đăng nhập
        st.title("Đăng nhập vào hệ thống")
        with st.form("login_form"):
            email_input = st.text_input("Email")
            password_input = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("Đăng nhập")
            if submitted:
                if check_login(email_input, password_input):
                    st.session_state.logged_in = True
                    save_session(True)  # Lưu trạng thái vào file
                    st.rerun()
                else:
                    st.error("Sai email hoặc mật khẩu!")

# =======================
# 2. Giao diện sau login
# =======================
else:
    # Sidebar chung sau khi đăng nhập
    render_main_sidebar()

    # CSS Styling
    st.markdown(
        """
        <style>
            /* Nền trang màu xám nhạt */
            [data-testid="stAppViewContainer"] {
                background-color: #f5f5f5;
            }

            /* Function Card */
            .function-card {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 24px;
                margin: 12px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                height: 100%;
            }

            .function-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }

            .function-icon {
                font-size: 48px;
                margin-bottom: 12px;
            }

            .function-title {
                font-size: 20px;
                font-weight: 700;
                color: #111827;
                margin-bottom: 8px;
            }

            .function-desc {
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
                line-height: 1.5;
            }

            .function-subtitle {
                font-size: 12px;
                color: #9ca3af;
                margin-bottom: 16px;
            }

            /* Nút trong function card */
            div[data-testid="column"] button {
                background-color: #4c78d3 !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }

            div[data-testid="column"] button:hover {
                background-color: #3b63b5 !important;
            }

            /* Welcome Banner */
            .welcome-banner {
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                border-radius: 12px;
                padding: 32px;
                margin: 24px 0;
                color: #ffffff;
            }

            .welcome-greeting {
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 12px;
            }

            .welcome-text {
                font-size: 16px;
                margin-bottom: 20px;
                opacity: 0.95;
            }

            .welcome-pill-btn {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                margin-right: 8px;
                margin-bottom: 8px;
                display: inline-block;
                cursor: pointer;
                transition: all 0.2s;
            }

            .welcome-pill-btn:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }

            .tips-section {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 16px;
                margin-top: 20px;
            }

            .tips-title {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header
    header_col1, header_col2 = st.columns([3, 2])
    with header_col1:
        st.markdown(
            """
            <div style="margin-bottom: 8px;">
                <span style="font-size: 24px; font-weight: 700; color: #111827;">🏠 Trang chủ</span>
                <span style="background-color: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-left: 12px;">
                    Hệ thống quản lý kho
                </span>
            </div>
            <p style="color: #6b7280; font-size: 14px; margin: 0;">
                Chào mừng đến với hệ thống quản lý kho. Hãy chọn chức năng phù hợp để bắt đầu quản lý sản phẩm, nhập - xuất hàng và theo dõi tồn kho một cách trực quan.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with header_col2:
        btn_header_col1, btn_header_col2 = st.columns(2)
        with btn_header_col1:
            if st.button("➕ Thêm sản phẩm nhanh", type="primary", use_container_width=True):
                st.switch_page("pages/1_Products.py")
        with btn_header_col2:
            st.button("❓ Hướng dẫn sử dụng", use_container_width=True)

    # Welcome Banner
    st.markdown(
        """
        <div class="welcome-banner">
            <div class="welcome-greeting">Xin chào, Hồ Bá Phao 👋</div>
            <div class="welcome-text">
                Vui lòng chọn trang từ menu hoặc các thẻ chức năng bên dưới để bắt đầu thao tác với kho hàng.
            </div>
            <div>
                <span class="welcome-pill-btn">Quản lý tồn kho nhanh</span>
                <span class="welcome-pill-btn">Theo dõi cảnh báo ROP</span>
                <span class="welcome-pill-btn">Báo cáo trực quan</span>
            </div>
            <div class="tips-section">
                <div class="tips-title">
                    ⭐ Gợi ý bắt đầu:
                </div>
                <div style="font-size: 14px; line-height: 1.8;">
                    1. Thêm sản phẩm mới vào danh mục<br>
                    2. Tạo phiếu nhập kho đầu tiên<br>
                    3. Thiết lập ngưỡng cảnh báo tồn kho
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chức năng chính
    st.markdown("### 🕐 Chức năng chính")

    # Row 1
    func_row1_col1, func_row1_col2, func_row1_col3 = st.columns(3)

    with func_row1_col1:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">📦</div>
                <div class="function-title">Sản phẩm</div>
                <div class="function-desc">Quản lý danh sách sản phẩm, mã SKU, tồn kho và các chỉ số ROP, tồn kho an toàn.</div>
                <div class="function-subtitle">Quản lý danh mục hàng hóa</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Mở trang >", key="btn_products", use_container_width=True):
            st.switch_page("pages/1_Products.py")

    with func_row1_col2:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">📥</div>
                <div class="function-title">Nhập hàng</div>
                <div class="function-desc">Tạo và quản lý phiếu nhập kho, cập nhật số lượng tồn kho một cách nhanh chóng.</div>
                <div class="function-subtitle">Ghi nhận hàng vào kho</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Tạo phiếu nhập >", key="btn_import", use_container_width=True):
            st.switch_page("pages/2_Import.py")

    with func_row1_col3:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">📤</div>
                <div class="function-title">Xuất hàng</div>
                <div class="function-desc">Tạo phiếu xuất kho, trừ tồn tự động, hỗ trợ xuất file Excel/CSV.</div>
                <div class="function-subtitle">Xuất hàng cho bán lẻ / đại lý</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Tạo phiếu xuất >", key="btn_export", use_container_width=True):
            st.switch_page("pages/3_Export.py")

    # Row 2
    func_row2_col1, func_row2_col2, func_row2_col3 = st.columns(3)

    with func_row2_col1:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">🚨</div>
                <div class="function-title">Ngưỡng cảnh báo</div>
                <div class="function-desc">Theo dõi các sản phẩm dưới ROP, chỉnh sửa mức ROP và cấu hình nhận email cảnh báo.</div>
                <div class="function-subtitle">Tránh thiếu hàng đột ngột</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Xem cảnh báo >", key="btn_alert", use_container_width=True):
            st.switch_page("pages/4_Alert_Threshold.py")

    with func_row2_col2:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">📊</div>
                <div class="function-title">Dashboard</div>
                <div class="function-desc">Xem báo cáo tổng quan: tổng số sản phẩm, tổng tồn kho, sản phẩm dưới ROP, vòng quay tồn kho,...</div>
                <div class="function-subtitle">Phân tích & ra quyết định</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Mở dashboard >", key="btn_dashboard", use_container_width=True):
            st.switch_page("pages/5_Dashboard.py")

    with func_row2_col3:
        st.markdown(
            """
            <div class="function-card">
                <div class="function-icon">🏢</div>
                <div class="function-title">Quản lý khu vực kho</div>
                <div class="function-desc">Thiết lập sơ đồ kho, phân khu A/B/C/D/E, quản lý kệ & ô chứa. Liên kết sản phẩm với khu vực để hỗ trợ kiểm kê và tìm kiếm nhanh.</div>
                <div class="function-subtitle">Tổ chức không gian kho hàng</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Quản lý khu vực kho >", key="btn_warehouse", use_container_width=True):
            st.switch_page("pages/6_Warehouse_Areas.py")

