import streamlit as st
import pandas as pd
import os
import sys

# Thêm thư mục gốc vào path để import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_login_required, render_main_sidebar

# ======================
# CẤU HÌNH TRANG
# ======================
st.set_page_config(
    page_title="Sản Phẩm",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="auto",
)

# ======================
# KIỂM TRA ĐĂNG NHẬP + SIDEBAR
# ======================
check_login_required()
render_main_sidebar()

# ======================
# DATABASE
# ======================
DB_PATH = "database/sanpham.csv"
os.makedirs("database", exist_ok=True)

# Nếu database chưa có thì tạo mới với các cột đúng yêu cầu
if not os.path.exists(DB_PATH):
    df_init = pd.DataFrame({
        "Mã sản phẩm": [],
        "Tên sản phẩm": [],
        "Số lượng tồn kho": [],
        "Điểm đặt hàng lại (ROP)": [],
        "Tồn kho an toàn": [],
        "Hệ số luân chuyển số lượng": []
    })
    df_init.to_csv(DB_PATH, index=False)

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame({
            "Mã sản phẩm": [],
            "Tên sản phẩm": [],
            "Số lượng tồn kho": [],
            "Điểm đặt hàng lại (ROP)": [],
            "Tồn kho an toàn": [],
            "Hệ số luân chuyển số lượng": []
        })
    return pd.read_csv(DB_PATH)

def save_data(data):
    data.to_csv(DB_PATH, index=False, encoding="utf-8-sig")
    load_data.clear()  # Clear cache để cập nhật dữ liệu

# ======================
# GIAO DIỆN CHÍNH
# ======================

# Nền trang màu #eff3f9 giống thiết kế + đẩy nội dung lên trên một chút
st.markdown(
    """
    <style>
        /* Nền trang */
        [data-testid="stAppViewContainer"] {
            background-color: #eff3f9;
        }

        /* Ẩn header mặc định và thu nhỏ khoảng trống phía trên cùng */
        header[data-testid="stHeader"] {
            height: 0px !important;
            padding: 0px !important;
            background: transparent !important;
        }

        header [data-testid="stToolbar"] {
            display: none !important;
        }

        /* Giảm khoảng trống trên cùng của nội dung chính
           và kéo toàn bộ nội dung lên cao hơn một chút */
        main .block-container {
            padding-top: 0.2rem !important;
            padding-bottom: 2.5rem !important;
            margin-top: -30px !important;
        }

        /* Giảm margin trên của tiêu đề chính để kéo lên cao hơn */
        main .block-container h1 {
            margin-top: 0.4rem !important;
            margin-bottom: 1.2rem !important;
        }


        /* Nút "Thêm sản phẩm" màu xanh #4c78d3 */
        button[kind="primary"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
        }

        button[kind="primary"]:hover {
            background-color: #3b63b5 !important;
            border-color: #3b63b5 !important;
        }

        /* Thanh tìm kiếm kết hợp - search và filter trong cùng một container */
        .search-bar-wrapper {
            display: flex;
            align-items: center;
            background-color: #ffffff;
            border-radius: 999px;
            border: 1px solid #d0d7e6;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
            padding: 0;
            height: 44px;
            margin-bottom: 16px;
            overflow: hidden;
        }

        .search-bar-wrapper:focus-within {
            border-color: #4c78d3;
            box-shadow: 0 0 0 2px rgba(76, 120, 211, 0.15);
        }

        /* Icon kính lúp bên trái */
        .search-icon-wrapper {
            padding: 0 12px 0 16px;
            display: flex;
            align-items: center;
            color: #6b7280;
            font-size: 16px;
        }

        /* Input search - không có border riêng */
        .search-bar-wrapper div[data-testid="stTextInput"] {
            flex: 1;
            margin: 0;
        }

        .search-bar-wrapper div[data-testid="stTextInput"] input {
            background-color: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 10px 12px 10px 0 !important;
            height: 44px !important;
            font-size: 14px !important;
            box-shadow: none !important;
        }

        .search-bar-wrapper div[data-testid="stTextInput"] input:focus {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        .search-bar-wrapper div[data-testid="stTextInput"] input::placeholder {
            color: #9ca3af !important;
        }

        /* Divider giữa search và filter */
        .search-divider {
            width: 1px;
            height: 24px;
            background-color: #d0d7e6;
            margin: 0 4px;
        }

        /* Selectbox filter bên phải */
        .search-bar-wrapper div[data-testid="stSelectbox"] {
            margin: 0;
            padding: 0;
        }

        .search-bar-wrapper div[data-testid="stSelectbox"] > div {
            background-color: #f9fafb !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            height: 44px !important;
            padding: 0 16px 0 8px !important;
        }

        .search-bar-wrapper div[data-testid="stSelectbox"] > div > div {
            background-color: transparent !important;
            padding: 0 !important;
            font-size: 14px !important;
            color: #374151 !important;
        }

        .search-bar-wrapper div[data-testid="stSelectbox"] label {
            display: none !important;
        }

        /* Banner "THÊM SẢN PHẨM MỚI" */
        .add-product-banner {
            background-color: #4c78d3;
            color: #ffffff;
            padding: 12px 20px;
            margin: 16px 0;
            border-radius: 4px;
            text-align: center;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Nút "Lưu" trong form thêm sản phẩm */
        .add-product-form button[type="submit"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
            color: #ffffff !important;
        }

        .add-product-form button[type="submit"]:hover {
            background-color: #3b63b5 !important;
            border-color: #3b63b5 !important;
        }

        /* Ẩn columns gốc của search bar */
        div[data-testid="column"]:has(input[placeholder="Tìm theo mã hoặc tên sản phẩm..."]) {
            display: none !important;
        }

        div[data-testid="column"]:has(div[data-testid="stSelectbox"]:not(.search-bar-wrapper div[data-testid="stSelectbox"])) {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📦 Quản lý sản phẩm")
df = load_data()

# Làm sạch các cột không cần thiết
columns_to_drop = ["Cảnh báo", "Sửa ROP", "::auto_unique_id::", "auto_unique_id", "autoGeneratedId"]
for col in columns_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])

# ======================
# THẺ TỔNG QUAN (KPI)
# ======================
try:
    total_products = len(df)
    total_stock = int(df["Số lượng tồn kho"].sum()) if "Số lượng tồn kho" in df.columns else 0
    below_rop = 0
    if "Số lượng tồn kho" in df.columns and "Điểm đặt hàng lại (ROP)" in df.columns:
        below_rop = int((df["Số lượng tồn kho"] <= df["Điểm đặt hàng lại (ROP)"]).sum())

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

    def _kpi_card(container, title, value):
        container.markdown(
            f"""
            <div style="
                background-color: #ffffff;
                padding: 12px 20px;
                border-radius: 14px;
                box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08);
                text-align: center;
            ">
                <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 4px;">
                    {title}
                </div>
                <div style="font-size: 30px; font-weight: 700; color: #111827;">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _kpi_card(kpi_col1, "Tổng Sản Phẩm", f"{total_products}")
    _kpi_card(kpi_col2, "Tổng lượng tồn", f"{total_stock:,}")
    _kpi_card(kpi_col3, "Sản phẩm dưới ROP", f"{below_rop}")
except Exception:
    # Nếu có lỗi dữ liệu, không làm vỡ giao diện chính
    pass

# ======================
# THANH CHỨC NĂNG
# ======================

# Tạo khoảng cách rõ ràng giữa 3 ô KPI và dãy nút chức năng
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("➕ Thêm sản phẩm", type="primary", use_container_width=True):
        st.session_state["add_form"] = True

with col2:
    if st.button("✏️ Sửa", width='stretch'):
        st.session_state["edit_form"] = True

with col3:
    if st.button("🗑 Xóa", width='stretch'):
        st.session_state["delete_form"] = True

with col4:
    if st.button("📄 Chi tiết", width='stretch'):
        st.session_state["detail_form"] = True

with col5:
    st.download_button(
        "📥 Xuất Excel",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="danhsach_sanpham.csv",
        mime="text/csv",
        width='stretch'
    )

with col6:
    st.button("🔄 Làm mới", on_click=lambda: st.rerun(), width='stretch')

# ======================
# THANH TÌM KIẾM
# ======================

# Tạo thanh tìm kiếm đơn giản với columns
search_col1, search_col2 = st.columns([8, 2])

with search_col1:
    keyword = st.text_input(
        "",
        placeholder="Tìm theo mã hoặc tên sản phẩm...",
        label_visibility="collapsed",
        key="product_search",
    )

with search_col2:
    status_filter = st.selectbox(
        "",
        ["Tất cả", "Dưới ROP", "Trên ROP"],
        index=0,
        label_visibility="collapsed",
    )

# JavaScript để wrap search và filter vào container chung và ẩn columns gốc
st.markdown(
    """
    <script>
    (function() {
        function wrapSearchBar() {
            const searchInput = document.querySelector('input[placeholder="Tìm theo mã hoặc tên sản phẩm..."]');
            const selectbox = document.querySelector('div[data-testid="stSelectbox"]');
            
            if (searchInput && selectbox) {
                const searchCol = searchInput.closest('[data-testid="column"]');
                const filterCol = selectbox.closest('[data-testid="column"]');
                
                // Ẩn columns gốc ngay lập tức
                if (searchCol) searchCol.style.display = 'none';
                if (filterCol) filterCol.style.display = 'none';
                
                // Tìm container cha chung
                if (searchCol && filterCol && searchCol.parentElement === filterCol.parentElement) {
                    const parentContainer = searchCol.parentElement;
                    
                    // Kiểm tra xem đã có wrapper chưa
                    if (!parentContainer.querySelector('.search-bar-wrapper')) {
                        // Tạo wrapper mới
                        const wrapper = document.createElement('div');
                        wrapper.className = 'search-bar-wrapper';
                        
                        // Thêm icon
                        const icon = document.createElement('div');
                        icon.className = 'search-icon-wrapper';
                        icon.innerHTML = '🔍';
                        wrapper.appendChild(icon);
                        
                        // Di chuyển search input vào wrapper
                        const searchInputParent = searchInput.closest('div[data-testid="stTextInput"]');
                        if (searchInputParent) {
                            wrapper.appendChild(searchInputParent);
                        }
                        
                        // Thêm divider
                        const divider = document.createElement('div');
                        divider.className = 'search-divider';
                        wrapper.appendChild(divider);
                        
                        // Di chuyển filter vào wrapper
                        wrapper.appendChild(selectbox);
                        
                        // Thay thế columns bằng wrapper
                        parentContainer.insertBefore(wrapper, searchCol);
                    }
                }
            }
        }
        
        // Chạy ngay và sau mỗi 100ms để đảm bảo ẩn columns sớm
        wrapSearchBar();
        setTimeout(wrapSearchBar, 100);
        setTimeout(wrapSearchBar, 300);
        setInterval(wrapSearchBar, 500);
        
        // Chạy khi DOM thay đổi
        const observer = new MutationObserver(wrapSearchBar);
        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
        }
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

# Lọc dữ liệu
df_filtered = df.copy()

# Lọc theo keyword
if keyword:
    keyword = keyword.lower()
    df_filtered = df_filtered[
        df_filtered.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    ]

# Lọc theo trạng thái tồn kho
if (
    status_filter != "Tất cả"
    and "Số lượng tồn kho" in df_filtered.columns
    and "Điểm đặt hàng lại (ROP)" in df_filtered.columns
):
    if status_filter == "Dưới ROP":
        df_filtered = df_filtered[
            df_filtered["Số lượng tồn kho"] <= df_filtered["Điểm đặt hàng lại (ROP)"]
        ]
    elif status_filter == "Trên ROP":
        df_filtered = df_filtered[
            df_filtered["Số lượng tồn kho"] > df_filtered["Điểm đặt hàng lại (ROP)"]
    ]

# ======================
# HIỂN THỊ BẢNG
# ======================
st.dataframe(df_filtered, width='stretch')

# ======================
# FORM THÊM
# ======================
if st.session_state.get("add_form"):
    st.markdown(
        '<div class="add-product-banner">THÊM SẢN PHẨM MỚI</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="add-product-form">', unsafe_allow_html=True)
    with st.form("add_form_form"):
        ma_sp = st.text_input("Mã sản phẩm")
        ten_sp = st.text_input("Tên sản phẩm")
        ton = st.number_input("Số lượng", min_value=0)
        khu_vuc_kho = st.selectbox(
            "Khu vực kho",
            options=["Khu A", "Khu B", "Khu C", "Khu D", "Khu E"],
            index=0
        )
        rop = st.number_input("Điểm đặt hàng lại (ROP)", min_value=0)
        safe = st.number_input("Tồn kho an toàn", min_value=0)
        heso = st.number_input("Hệ số luân chuyển số lượng", min_value=0.0)

        submitted = st.form_submit_button("Lưu")
        if submitted:
            if not ma_sp or not ten_sp:
                st.error("⚠ Vui lòng nhập đầy đủ Mã sản phẩm và Tên sản phẩm!")
            else:
                # Kiểm tra mã sản phẩm trùng lặp
                if ma_sp in df["Mã sản phẩm"].astype(str).values:
                    st.error("⚠ Mã sản phẩm đã tồn tại!")
                else:
                    df.loc[len(df)] = [ma_sp, ten_sp, ton, rop, safe, heso]
                    save_data(df)
                    st.success("✔ Đã thêm!")
                    st.session_state["add_form"] = False
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# FORM SỬA
# ======================
if st.session_state.get("edit_form"):
    st.subheader("✏️ Sửa sản phẩm")
    list_names = df["Tên sản phẩm"].tolist()
    selected = st.selectbox("Chọn sản phẩm để sửa", list_names)
    row = df[df["Tên sản phẩm"] == selected].iloc[0]

    with st.form("edit_form_form"):
        ma_sp = st.text_input("Mã sản phẩm", row["Mã sản phẩm"])
        ten_sp = st.text_input("Tên sản phẩm", row["Tên sản phẩm"])
        ton = st.number_input("Số lượng", min_value=0, value=int(row["Số lượng tồn kho"]))
        rop = st.number_input("Điểm đặt hàng lại (ROP)", min_value=0, value=int(row["Điểm đặt hàng lại (ROP)"]))
        safe = st.number_input("Tồn kho an toàn", min_value=0, value=int(row["Tồn kho an toàn"]))
        heso = st.number_input(
            "Hệ số luân chuyển số lượng",
            min_value=0.0,
            value=float(row["Hệ số luân chuyển số lượng"])
        )

        submitted = st.form_submit_button("Lưu thay đổi")
        if submitted:
            if not ma_sp or not ten_sp:
                st.error("⚠ Vui lòng nhập đầy đủ thông tin!")
            else:
                # Kiểm tra mã sản phẩm trùng (nếu đổi mã)
                if ma_sp != row["Mã sản phẩm"] and ma_sp in df["Mã sản phẩm"].astype(str).values:
                    st.error("⚠ Mã sản phẩm mới đã tồn tại!")
                else:
                    df.loc[df["Mã sản phẩm"] == row["Mã sản phẩm"], :] = [
                        ma_sp, ten_sp, ton, rop, safe, heso
                    ]
                    save_data(df)
                    st.success("✔ Đã cập nhật!")
                    st.session_state["edit_form"] = False
                    st.rerun()

# ======================
# FORM XÓA
# ======================
if st.session_state.get("delete_form"):
    st.subheader("🗑 Xóa sản phẩm")
    if len(df) == 0:
        st.warning("⚠ Không có sản phẩm nào để xóa!")
    else:
        selected = st.selectbox("Chọn sản phẩm", df["Tên sản phẩm"])
        if st.button("Xóa", type="primary"):
            df = df[df["Tên sản phẩm"] != selected]
            save_data(df)
            st.success("✔ Đã xóa!")
            st.session_state["delete_form"] = False
            st.rerun()

# ======================
# FORM CHI TIẾT
# ======================
if st.session_state.get("detail_form"):
    st.subheader("📄 Chi tiết sản phẩm")
    if len(df) == 0:
        st.warning("⚠ Không có sản phẩm nào!")
    else:
        selected = st.selectbox("Chọn sản phẩm", df["Tên sản phẩm"])
        row = df[df["Tên sản phẩm"] == selected].iloc[0]

        ma_sp = str(row.get("Mã sản phẩm", "")).strip()
        current_stock = int(row.get("Số lượng tồn kho", 0))

        if not ma_sp:
            st.info("ℹ Không tìm được mã sản phẩm, không thể tra lịch sử nhập/xuất.")
        else:
            # ===== Đọc lịch sử nhập hàng (có thể trống) =====
            import_db_path = "database/phieu_nhap.csv"
            if os.path.exists(import_db_path):
                df_import = pd.read_csv(import_db_path)
            else:
                df_import = pd.DataFrame()

            if "Mã sản phẩm" in df_import.columns:
                df_product_imports = df_import[
                    df_import["Mã sản phẩm"].astype(str) == ma_sp
                ].copy()
            else:
                df_product_imports = pd.DataFrame()

            # ===== Đọc lịch sử xuất hàng (có thể trống) =====
            export_db_path = "database/phieu_xuat.csv"
            if os.path.exists(export_db_path):
                df_export = pd.read_csv(export_db_path)
            else:
                df_export = pd.DataFrame()

            if (
                "Mã sản phẩm" in df_export.columns
                and "Số lượng xuất" in df_export.columns
            ):
                df_export_product = df_export[
                    df_export["Mã sản phẩm"].astype(str) == ma_sp
                ].copy()
            else:
                df_export_product = pd.DataFrame()

            # ===== Tính lại "số lượng ban đầu" để tạo lô 1 ảo =====
            total_imported = 0
            if not df_product_imports.empty and "Số lượng nhập" in df_product_imports.columns:
                total_imported = (
                    pd.to_numeric(
                        df_product_imports["Số lượng nhập"], errors="coerce"
                    )
                    .fillna(0)
                    .astype(int)
                    .sum()
                )

            total_exported = 0
            if not df_export_product.empty:
                total_exported = (
                    pd.to_numeric(
                        df_export_product["Số lượng xuất"], errors="coerce"
                    )
                    .fillna(0)
                    .astype(int)
                    .sum()
                )

            # Công thức: tồn hiện tại = tồn ban đầu + tổng nhập - tổng xuất
            # => tồn ban đầu = tồn hiện tại - tổng nhập + tổng xuất
            initial_qty = current_stock - total_imported + total_exported
            if initial_qty < 0:
                initial_qty = 0

            # Lô 1 ảo cho số lượng ban đầu (nếu > 0)
            synthetic_lots = []
            if initial_qty > 0:
                # HSD mặc định: 30/11 của năm hiện tại
                from datetime import datetime as _dt

                year_now = _dt.now().year
                synthetic_lots.append(
                    {
                        "Mã phiếu": "INIT",
                        "Nhân viên nhập": "Khởi tạo",
                        "Mã sản phẩm": ma_sp,
                        "Tên sản phẩm": row.get("Tên sản phẩm", ""),
                        "Số lượng nhập": initial_qty,
                        "Hạn sử dụng": f"30/11/{year_now}",
                        # Ngày nhập rất cũ để luôn là lô 1 khi sắp xếp theo thời gian
                        "Ngày nhập": "01/01/2000 00:00",
                    }
                )

            # Ghép lô 1 ảo (nếu có) + các lô nhập thật
            if synthetic_lots:
                df_synthetic = pd.DataFrame(synthetic_lots)
                if not df_product_imports.empty:
                    df_product_imports = pd.concat(
                        [df_synthetic, df_product_imports], ignore_index=True
                    )
                else:
                    df_product_imports = df_synthetic

            if df_product_imports.empty:
                st.info("📭 Sản phẩm này chưa có lịch sử nhập hàng hoặc tồn kho ban đầu.")
            else:
                # Sắp xếp theo thời gian nhập (nếu parse được), nếu không thì giữ nguyên thứ tự
                if "Ngày nhập" in df_product_imports.columns:
                    df_product_imports["_dt"] = pd.to_datetime(
                        df_product_imports["Ngày nhập"],
                        errors="coerce",
                        dayfirst=True,
                    )
                    df_product_imports = df_product_imports.sort_values(
                        by="_dt"
                    ).drop(columns=["_dt"])

                # ============================
                # TÍNH TÌNH TRẠNG TỪNG LÔ HÀNG
                # ============================
                # QUAN TRỌNG: Đọc trực tiếp số lượng còn lại từ warehouse_areas.csv
                # KHÔNG dùng logic FEFO để tính lại - chỉ dùng để sắp xếp đề xuất ở trang xuất hàng
                
                # Đọc warehouse_areas.csv để lấy số lượng còn lại thực tế
                warehouse_areas_path = "database/warehouse_areas.csv"
                remaining_by_lot = {}  # Map: lot_idx -> số lượng còn lại (tổng từ tất cả các khu)
                
                # Kiểm tra xem có lô ảo INIT không
                has_init = False
                for lot_idx in range(len(df_product_imports)):
                    ma_phieu_val = str(df_product_imports.iloc[lot_idx].get("Mã phiếu", "")).strip()
                    if ma_phieu_val == "INIT":
                        has_init = True
                        break
                
                if os.path.exists(warehouse_areas_path):
                    try:
                        df_warehouse = pd.read_csv(warehouse_areas_path)
                        if not df_warehouse.empty and "Mã sản phẩm" in df_warehouse.columns:
                            df_warehouse["Mã sản phẩm"] = df_warehouse["Mã sản phẩm"].astype(str)
                            df_warehouse["Lô"] = pd.to_numeric(df_warehouse["Lô"], errors="coerce").fillna(0).astype(int)
                            df_warehouse["Số lượng"] = pd.to_numeric(df_warehouse.get("Số lượng", 0), errors="coerce").fillna(0).astype(int)
                            df_warehouse = df_warehouse[df_warehouse["Số lượng"] > 0]  # Chỉ lấy các dòng còn số lượng
                            
                            # Lọc các dòng của sản phẩm này
                            df_warehouse_sp = df_warehouse[df_warehouse["Mã sản phẩm"] == ma_sp].copy()

                            # Tổng hợp số lượng còn lại theo từng lô (tổng từ tất cả các khu)
                            for _, wh_row in df_warehouse_sp.iterrows():
                                lo_warehouse = int(wh_row["Lô"])  # Lô trong warehouse_areas.csv
                                so_luong = int(wh_row["Số lượng"])
                                
                                if so_luong <= 0:
                                    continue
                                
                                # Map lô từ warehouse_areas.csv sang lot_idx trong Products.py
                                if has_init:
                                    # Có lô ảo INIT: lô trong warehouse_areas.csv -> lot_idx trong Products.py
                                    # warehouse_areas.csv lô 1 -> Products.py lot_idx 1 (lô thật đầu tiên, hiển thị là lô 2)
                                    lot_idx = lo_warehouse  # lot_idx 1-based (lot_idx 0 là INIT)
                                else:
                                    # Không có lô ảo INIT: lô trong warehouse_areas.csv -> lot_idx trong Products.py
                                    # warehouse_areas.csv lô 1 -> Products.py lot_idx 0 (hiển thị là lô 1)
                                    lot_idx = lo_warehouse - 1  # lot_idx 0-based
                                
                                if 0 <= lot_idx < len(df_product_imports):
                                    remaining_by_lot[lot_idx] = remaining_by_lot.get(lot_idx, 0) + so_luong
                    except Exception:
                        pass  # Nếu có lỗi, sẽ dùng số lượng nhập ban đầu
                
                # Tính tổng số lượng các lô thật còn lại (từ warehouse_areas.csv)
                total_real_lots_remaining = sum(remaining_by_lot.values())
                
                # Tính số lượng lô ảo INIT còn lại
                # Công thức: Tồn kho hiện tại = Lô ảo INIT còn lại + Tổng số lượng các lô thật còn lại
                # => Lô ảo INIT còn lại = Tồn kho hiện tại - Tổng số lượng các lô thật còn lại
                init_lot_idx = None
                if has_init:
                    for i in range(len(df_product_imports)):
                        ma_phieu_val = str(df_product_imports.iloc[i].get("Mã phiếu", "")).strip()
                        if ma_phieu_val == "INIT":
                            init_lot_idx = i
                            break

                if init_lot_idx is not None:
                    # Tính số lượng lô ảo INIT còn lại
                    init_remaining = max(0, current_stock - total_real_lots_remaining)
                    remaining_by_lot[init_lot_idx] = init_remaining
                
                # Khởi tạo remaining_by_lot cho các lô thật không có trong warehouse_areas.csv
                # (các lô này đã xuất hết)
                for i in range(len(df_product_imports)):
                    if i not in remaining_by_lot:
                        ma_phieu_val = str(df_product_imports.iloc[i].get("Mã phiếu", "")).strip()
                        if ma_phieu_val != "INIT":
                            # Lô thật nhưng không có trong warehouse_areas.csv -> đã xuất hết
                            remaining_by_lot[i] = 0

                # Tạo danh sách trạng thái cho từng lô
                lot_status = []
                for i in range(len(df_product_imports)):
                    # Số lượng nhập của lô
                    try:
                        imported_qty = int(
                            df_product_imports.get(
                                "Số lượng nhập",
                                pd.Series([0] * len(df_product_imports)),
                            )[i]
                        )
                    except Exception:
                        imported_qty = 0

                    # Số lượng còn lại từ warehouse_areas.csv
                    remaining_qty = remaining_by_lot.get(i, 0)

                    # Tính trạng thái
                    if remaining_qty <= 0:
                        status = "đã xuất hàng"
                    elif remaining_qty >= imported_qty:
                        status = "chưa xuất hàng"
                    else:
                        status = f"còn dư {remaining_qty}"

                    lot_status.append(status)

                # ===== Lấy thông tin khu vực cho từng lô (chỉ lô còn tồn) =====
                warehouse_areas_path = "database/warehouse_areas.csv"
                vi_tri_list = []
                
                if os.path.exists(warehouse_areas_path):
                    try:
                        df_warehouse = pd.read_csv(warehouse_areas_path)
                        if not df_warehouse.empty and "Mã sản phẩm" in df_warehouse.columns:
                            df_warehouse["Mã sản phẩm"] = df_warehouse["Mã sản phẩm"].astype(str)
                            df_warehouse["Lô"] = pd.to_numeric(df_warehouse["Lô"], errors="coerce").fillna(0).astype(int)
                            df_warehouse["Số lượng"] = pd.to_numeric(df_warehouse.get("Số lượng", 0), errors="coerce").fillna(0).astype(int)
                            df_warehouse = df_warehouse[df_warehouse["Số lượng"] > 0]  # Chỉ lấy các dòng còn số lượng

                            # Với mỗi dòng nhập: nếu là INIT (tồn ban đầu) thì không map vào warehouse_areas;
                            # các lần nhập thật được đánh lô 1,2,3,... theo đúng thứ tự để khớp với warehouse_areas.csv.
                            real_lot_no = 0
                            for lot_idx in range(len(df_product_imports)):
                                ma_phieu_val = str(
                                    df_product_imports.iloc[lot_idx].get("Mã phiếu", "")
                                ).strip()

                                # Dòng khởi tạo tồn ban đầu (INIT) -> không có trong warehouse_areas
                                if ma_phieu_val == "INIT":
                                    vi_tri_list.append("—")
                                    continue

                                real_lot_no += 1  # Lô thật 1, 2, 3,... giống khi tạo phiếu nhập
                                status = (
                                    lot_status[lot_idx]
                                    if lot_idx < len(lot_status)
                                    else "chưa xuất hàng"
                                )

                                # Chỉ lấy vị trí khu nếu lô còn tồn (chưa xuất hoặc còn dư)
                                if status == "đã xuất hàng":
                                    vi_tri_list.append("—")
                                else:
                                    # Tìm tất cả các khu có lô này (có thể một lô ở nhiều khu)
                                    mask = (
                                        (df_warehouse["Mã sản phẩm"] == ma_sp)
                                        & (df_warehouse["Lô"] == real_lot_no)
                                    )
                                    khu_list = (
                                        df_warehouse[mask]["Khu"]
                                        .astype(str)
                                        .unique()
                                        .tolist()
                                    )

                                    if khu_list:
                                        # Sắp xếp khu theo thứ tự A, B, C, D, E
                                        khu_sorted = sorted(
                                            khu_list, key=lambda x: x.replace("Khu ", "")
                                        )
                                        vi_tri_list.append(", ".join(khu_sorted))
                                    else:
                                        # Lô còn tồn nhưng chưa có trong warehouse_areas.csv
                                        # -> mặc định là Khu A (theo logic mặc định khi chưa phân bổ)
                                        vi_tri_list.append("Khu A")
                        else:
                            # Không có dữ liệu warehouse -> tất cả đều '—' hoặc 'Khu A' nếu còn tồn
                            for lot_idx in range(len(df_product_imports)):
                                ma_phieu_val = str(
                                    df_product_imports.iloc[lot_idx].get("Mã phiếu", "")
                                ).strip()
                                if ma_phieu_val == "INIT":
                                    vi_tri_list.append("—")
                                else:
                                    status = (
                                        lot_status[lot_idx]
                                        if lot_idx < len(lot_status)
                                        else "chưa xuất hàng"
                                    )
                                    if status == "đã xuất hàng":
                                        vi_tri_list.append("—")
                                    else:
                                        vi_tri_list.append("Khu A")
                    except Exception:
                        # Lỗi khi đọc file -> mặc định
                        for lot_idx in range(len(df_product_imports)):
                            ma_phieu_val = str(
                                df_product_imports.iloc[lot_idx].get("Mã phiếu", "")
                            ).strip()
                            if ma_phieu_val == "INIT":
                                vi_tri_list.append("—")
                            else:
                                status = (
                                    lot_status[lot_idx]
                                    if lot_idx < len(lot_status)
                                    else "chưa xuất hàng"
                                )
                                if status == "đã xuất hàng":
                                    vi_tri_list.append("—")
                                else:
                                    vi_tri_list.append("Khu A")
                else:
                    # Không có file warehouse -> mặc định 'Khu A' cho lô còn tồn (không phải INIT)
                    for lot_idx in range(len(df_product_imports)):
                        ma_phieu_val = str(
                            df_product_imports.iloc[lot_idx].get("Mã phiếu", "")
                        ).strip()
                        if ma_phieu_val == "INIT":
                            vi_tri_list.append("—")
                        else:
                            status = (
                                lot_status[lot_idx]
                                if lot_idx < len(lot_status)
                                else "chưa xuất hàng"
                            )
                            if status == "đã xuất hàng":
                                vi_tri_list.append("—")
                            else:
                                vi_tri_list.append("Khu A")

                # Đảm bảo độ dài vi_tri_list = len(df_product_imports)
                if len(vi_tri_list) < len(df_product_imports):
                    vi_tri_list.extend(["—"] * (len(df_product_imports) - len(vi_tri_list)))

                # Tính số lượng còn lại cho từng lô để hiển thị (dùng remaining_by_lot đã tính)
                so_luong_con_lai_list = []
                for i in range(len(df_product_imports)):
                    remaining_qty = remaining_by_lot.get(i, 0)
                    so_luong_con_lai_list.append(remaining_qty)
                
                # Đảm bảo tổng số lượng các lô = Tồn kho hiện tại
                total_lots_qty = sum(so_luong_con_lai_list)
                if abs(total_lots_qty - current_stock) > 0.01:  # Cho phép sai số nhỏ do làm tròn
                    # Điều chỉnh lô ảo INIT nếu có để đảm bảo tổng đúng
                    if init_lot_idx is not None and init_lot_idx < len(so_luong_con_lai_list):
                        diff = current_stock - total_lots_qty
                        so_luong_con_lai_list[init_lot_idx] = max(0, so_luong_con_lai_list[init_lot_idx] + diff)
                        remaining_by_lot[init_lot_idx] = so_luong_con_lai_list[init_lot_idx]
                        # Cập nhật lại trạng thái cho lô ảo INIT
                        if init_lot_idx < len(lot_status):
                            imported_qty_init = int(
                                df_product_imports.get("Số lượng nhập", pd.Series([0] * len(df_product_imports)))[init_lot_idx]
                            )
                            remaining_qty_init = so_luong_con_lai_list[init_lot_idx]
                            if remaining_qty_init <= 0:
                                lot_status[init_lot_idx] = "đã xuất hàng"
                            elif remaining_qty_init >= imported_qty_init:
                                lot_status[init_lot_idx] = "chưa xuất hàng"
                            else:
                                lot_status[init_lot_idx] = f"còn dư {remaining_qty_init}"

                # Lấy số lượng nhập ban đầu cho từng lô (không thay đổi)
                so_luong_nhap_ban_dau_list = []
                for i in range(len(df_product_imports)):
                    try:
                        imported_qty = int(
                            df_product_imports.get(
                                "Số lượng nhập",
                                pd.Series([0] * len(df_product_imports)),
                            )[i]
                        )
                    except Exception:
                        imported_qty = 0
                    so_luong_nhap_ban_dau_list.append(imported_qty)

                # Tạo bảng chi tiết: STT, Lô, Số lượng (ban đầu khi nhập), Thời gian nhập hàng, Hạn sử dụng, Tình trạng, Vị trí
                detail_df = pd.DataFrame(
                    {
                        "STT": range(1, len(df_product_imports) + 1),
                        "Lô": range(1, len(df_product_imports) + 1),
                        "Số lượng": so_luong_nhap_ban_dau_list,  # Hiển thị số lượng ban đầu khi nhập
                        "Thời gian nhập hàng": df_product_imports.get(
                            "Ngày nhập", ""
                        ),
                        "Hạn sử dụng": df_product_imports.get(
                            "Hạn sử dụng", ""
                        ).fillna(""),
                        "Tình trạng": lot_status,
                        "Vị trí": vi_tri_list,
                    }
                )

                st.markdown(
                    f"**Lịch sử nhập hàng cho sản phẩm:** `{ma_sp}` - **{row['Tên sản phẩm']}**"
                )
                st.dataframe(detail_df, use_container_width=True, hide_index=True)

    if st.button("Đóng"):
        st.session_state["detail_form"] = False
        st.rerun()

