"""
Utility functions for session management
"""
import streamlit as st
import json
import os
from datetime import datetime

SESSION_FILE = "session.json"
EMAIL_HISTORY_FILE = "email_sent_history.json"  # Lịch sử trạng thái gửi theo SẢN PHẨM (chống spam)
EMAIL_EVENT_FILE = "email_events_history.json"  # Lịch sử từng LẦN GỬI email (phục vụ xem lịch sử)

def load_session():
    """Đọc trạng thái đăng nhập từ file"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("logged_in", False)
        except:
            return False
    return False

def save_session(logged_in):
    """Lưu trạng thái đăng nhập vào file"""
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"logged_in": logged_in}, f)
    except:
        pass

def clear_session():
    """Xóa file session"""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except:
            pass

def check_login_required():
    """Kiểm tra và khôi phục trạng thái đăng nhập từ file nếu chưa có trong session"""
    # Khôi phục từ file nếu chưa có trong session
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = load_session()
    
    # Kiểm tra đăng nhập
    if not st.session_state.logged_in:
        st.error("❌ Bạn chưa đăng nhập! Vui lòng quay lại trang chủ để đăng nhập.")
        st.stop()
    
    return True


def render_main_sidebar():
    """
    Sidebar chung cho tất cả các trang, giao diện giống ảnh mẫu:
    - Nền xanh nhạt
    - Trên cùng là thông tin quản lý
    - Menu có icon cho từng trang, item đang chọn nền xanh đậm.
    """
    # CSS: nền xanh nhạt + style lại navigation mặc định của Streamlit
    st.markdown(
        """
        <style>
            /* Nền sidebar xanh nhạt */
            [data-testid="stSidebar"] {
                background-color: #c7e3ff;
            }

            [data-testid="stSidebar"] > div:first-child {
                padding-top: 0.3rem;
            }

            /* Ẩn label "Pages" mặc định nếu có */
            [data-testid="stSidebarNav"] h2,
            [data-testid="stSidebarNav"] h3 {
                display: none;
            }

            /* Bọc cả sidebar trong wrapper để dễ style + sắp xếp lại thứ tự */
            .custom-sb-wrapper {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                display: flex;
                flex-direction: column;
                height: 100%;
            }

            /* Khối thông tin quản lý – nằm trên menu nhưng nhỏ gọn như ban đầu */
            .custom-sb-profile {
                background: #ffffff;
                border-radius: 8px;
                margin: 0.3rem 0.5rem 0.4rem 0.5rem;
                padding: 0.5rem 0.6rem;
                display: flex;
                align-items: center;
                gap: 0.6rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                order: 0;  /* đứng trước menu */
            }

            .custom-sb-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #3b82f6;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
                flex-shrink: 0;
            }

            .custom-sb-name {
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 1px;
                color: #1f2937;
                line-height: 1.2;
            }

            .custom-sb-role {
                font-size: 10px;
                color: #4b5563;
                line-height: 1.2;
            }

            /* Khu vực menu (navigation mặc định của Streamlit) */
            [data-testid="stSidebarNav"] {
                margin-top: 0.2rem;
                padding: 0.3rem 0.25rem 0.25rem 0.25rem;
                order: 1;
            }

            [data-testid="stSidebarNav"] ul {
                list-style: none;
                margin: 0;
                padding: 0;
            }

            [data-testid="stSidebarNav"] li {
                margin: 1px 0;
            }

            /* Link menu: chỉ còn chữ, bo tròn bên phải */
            [data-testid="stSidebarNav"] a {
                display: block;
                padding: 6px 12px;
                border-radius: 18px 0 0 18px;
                color: #111827;
                text-decoration: none;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.15s ease, color 0.15s ease, padding-left 0.15s ease;
                white-space: normal;
                overflow: visible;
            }

            /* Hover: hơi đậm hơn */
            [data-testid="stSidebarNav"] a:hover {
                background-color: #a9c8f8;
                padding-left: 14px;
            }

            /* Item đang active: nền xanh đậm, chữ trắng */
            [data-testid="stSidebarNav"] a[aria-current="page"] {
                background-color: #2f5597;
                color: #ffffff;
                font-weight: 600;
            }

            [data-testid="stSidebarNav"] a[aria-current="page"] span:first-child {
                color: #ffffff;
            }

            /* Khu vực nút Đăng xuất – luôn ở gần đáy sidebar */
            .custom-sb-logout-wrap {
                margin: 0.6rem 0.5rem 0.8rem 0.5rem;
                order: 2;
                margin-top: auto;  /* đẩy xuống dưới */
            }

            .custom-sb-logout-btn {
                width: 100%;
                border-radius: 20px;
                border: none;
                padding: 6px 10px;
                background: #ffffff;
                color: #dc2626;
                font-weight: 600;
                font-size: 13px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.18);
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .custom-sb-logout-btn:hover {
                background: #fee2e2;
                color: #b91c1c;
                transform: translateY(-1px);
                box-shadow: 0 3px 6px rgba(220, 38, 38, 0.2);
            }
        </style>

        """,
        unsafe_allow_html=True,
    )

    # Bọc nội dung sidebar trong wrapper
    st.sidebar.markdown('<div class="custom-sb-wrapper">', unsafe_allow_html=True)

    # Menu navigation sẽ hiển thị tự động bởi Streamlit

    # Divider và phần quản lý + đăng xuất ở dưới cùng
    st.sidebar.markdown('<hr style="margin: 20px 0; border: none; border-top: 1px solid #d1d5db;">', unsafe_allow_html=True)
    
    # Khối thông tin người quản lý - ĐẶT Ở DƯỚI CÙNG
    st.sidebar.markdown(
        """
        <div class="custom-sb-profile">
            <div class="custom-sb-avatar">S</div>
            <div>
                <div class="custom-sb-name">Hồ Bá Phao</div>
                <div class="custom-sb-role">Quản lý kho</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Nút đăng xuất phía dưới
    st.sidebar.markdown('<div class="custom-sb-logout-wrap">', unsafe_allow_html=True)
    
    # Hàm xử lý đăng xuất
    def handle_logout():
        st.session_state.logged_in = False
        clear_session()
        # Chuyển về trang Homepage (trang login/chủ)
        st.switch_page("Homepage.py")
    
    # Tạo nút đăng xuất với style tùy chỉnh
    if st.sidebar.button("Đăng xuất", key="logout_btn", use_container_width=True):
        handle_logout()
    
    # CSS cho nút đăng xuất Streamlit
    st.sidebar.markdown(
        """
        <style>
            button[key="logout_btn"] {
                border-radius: 8px !important;
                border: none !important;
                padding: 10px 16px !important;
                background: #fce7f3 !important;
                color: #991b1b !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
                transition: all 0.2s ease !important;
            }
            button[key="logout_btn"]:hover {
                background: #fbcfe8 !important;
                color: #7f1d1d !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ======================
# Email History Management
# ======================

def load_email_history():
    """Đọc lịch sử đã gửi email từ file"""
    if os.path.exists(EMAIL_HISTORY_FILE):
        try:
            with open(EMAIL_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_email_history(history):
    """Lưu lịch sử đã gửi email vào file"""
    try:
        with open(EMAIL_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except:
        pass

def should_send_email(ma_sp, ton_kho, rop):
    """
    Kiểm tra xem có nên gửi email cho sản phẩm này không
    Trả về True nếu:
    - Chưa từng gửi email cho sản phẩm này
    - Hoặc số lượng tồn kho/ROP đã thay đổi so với lần gửi trước
    """
    history = load_email_history()
    
    if ma_sp not in history:
        return True  # Chưa từng gửi
    
    last_sent = history[ma_sp]
    # Kiểm tra xem tồn kho hoặc ROP có thay đổi không
    if (last_sent.get("ton_kho") != ton_kho or 
        last_sent.get("rop") != rop):
        return True  # Có thay đổi, nên gửi lại
    
    return False  # Đã gửi và không có thay đổi

def mark_email_sent(ma_sp, ten_sp, ton_kho, rop):
    """Đánh dấu đã gửi email cho sản phẩm"""
    history = load_email_history()
    history[ma_sp] = {
        "ten_sp": ten_sp,
        "ton_kho": ton_kho,
        "rop": rop,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_email_history(history)

def clear_email_history():
    """Xóa toàn bộ lịch sử đã gửi email (cả theo sản phẩm và theo lần gửi)"""
    if os.path.exists(EMAIL_HISTORY_FILE):
        try:
            os.remove(EMAIL_HISTORY_FILE)
        except:
            pass
    if os.path.exists(EMAIL_EVENT_FILE):
        try:
            os.remove(EMAIL_EVENT_FILE)
        except:
            pass


def load_email_events():
    """Đọc lịch sử các LẦN gửi email (để hiển thị 'Lịch sử email')"""
    if os.path.exists(EMAIL_EVENT_FILE):
        try:
            with open(EMAIL_EVENT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except:
            return []
    return []


def save_email_events(events):
    """Lưu lại toàn bộ lịch sử các lần gửi email"""
    try:
        with open(EMAIL_EVENT_FILE, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
    except:
        pass


def log_email_event(products):
    """
    Ghi lại một LẦN gửi email cảnh báo ROP.

    products: danh sách dict {ma_sp, ten_sp, ton_kho, rop}
    """
    events = load_email_events()
    events.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "ROP",  # Đánh dấu là email cảnh báo ROP
            "count": len(products),
            "products": products,
        }
    )
    save_email_events(events)


def prune_email_history_for_safe_products(safe_product_ids):
    """
    Xóa lịch sử email cho các sản phẩm hiện đang AN TOÀN (tồn kho >= ROP).
    Mục tiêu: mỗi lần sản phẩm rơi xuống dưới ROP sau khi đã an toàn lại,
    hệ thống sẽ xem như một lần cảnh báo mới và gửi email lại.
    """
    if not safe_product_ids:
        return

    history = load_email_history()
    if not history:
        return

    # Đảm bảo so sánh dưới dạng chuỗi để khớp với key trong history
    safe_ids_str = {str(x) for x in safe_product_ids}

    changed = False
    any_safe_cleared = False

    # 1) Xóa lịch sử cho các sản phẩm hiện đang AN TOÀN
    for ma_sp in list(history.keys()):
        if str(ma_sp) in safe_ids_str:
            del history[ma_sp]
            changed = True
            any_safe_cleared = True

    # 2) Nếu có ít nhất một sản phẩm đã từ dưới ROP trở về AN TOÀN,
    #    thì coi như một "chu kỳ cảnh báo" mới và reset lịch sử
    #    cho các sản phẩm vẫn đang dưới ROP, để chúng được gửi email lại.
    if any_safe_cleared:
        for ma_sp in list(history.keys()):
            if str(ma_sp) not in safe_ids_str:
                del history[ma_sp]
                changed = True

    if changed:
        save_email_history(history)

