import streamlit as st
import pandas as pd
import os
import io
import sys
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Thêm thư mục gốc vào path để import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_login_required, render_main_sidebar

st.set_page_config(
    page_title="Phiếu Nhập",
    page_icon="🧾",
    layout="wide",
)

# ======================
# CHECK LOGIN + SIDEBAR
# ======================
check_login_required()
render_main_sidebar()

# ======================
# CSS STYLING
# ======================
st.markdown(
    """
    <style>
        /* Nền trang màu trắng */
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff;
        }

        /* Giữ spacing mặc định của Streamlit */

        /* Style cho các nút trắng (không phải primary) */
        div[data-testid="column"] button:not([kind="primary"]) {
            background-color: #ffffff !important;
            color: #374151 !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="column"] button:not([kind="primary"]):hover {
            background-color: #f9fafb !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }

        /* Nút "Thêm phiếu nhập" - primary button xanh */
        button[key="add_receipt_btn"],
        button[kind="primary"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        
        button[key="add_receipt_btn"]:hover,
        button[kind="primary"]:hover {
            background-color: #3b63b5 !important;
            border-color: #3b63b5 !important;
        }

        /* Style cho subheader - đẩy lên cao hơn */
        h3 {
            font-weight: 600 !important;
            color: #1f2937 !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.8rem !important;
        }

        /* Style cho thông báo info */
        div[data-baseweb="notification"] {
            background-color: #e0f2fe !important;
            border-left: 4px solid #0ea5e9 !important;
            border-radius: 8px !important;
        }

        /* Style cho file uploader */
        .uploadedFile {
            border-radius: 8px !important;
        }

        /* Cải thiện file uploader */
        [data-testid="stFileUploader"] {
            border-radius: 8px !important;
        }

        [data-testid="stFileUploader"] > div {
            border: 2px dashed #d1d5db !important;
            border-radius: 8px !important;
            background-color: #f9fafb !important;
            padding: 2rem !important;
        }

        [data-testid="stFileUploader"] > div:hover {
            border-color: #4c78d3 !important;
            background-color: #f0f9ff !important;
        }

        /* Cải thiện dataframe */
        [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* Nút Lưu trong form */
        form[data-testid="stForm"] button[type="submit"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            width: 100% !important;
        }

        form[data-testid="stForm"] button[type="submit"]:hover {
            background-color: #3b63b5 !important;
            border-color: #3b63b5 !important;
        }

        /* Căn giữa header và nội dung trong AgGrid */
        .ag-theme-balham .ag-header-cell-label {
            justify-content: center;
        }
        .ag-theme-balham .ag-cell {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# PATH DATABASE
# ======================
os.makedirs("database", exist_ok=True)

PRODUCT_DB = "database/sanpham.csv"      # từ trang sản phẩm
IMPORT_DB = "database/phieu_nhap.csv"    # lịch sử phiếu nhập
WAREHOUSE_ASSIGN_DB = "database/warehouse_areas.csv"  # Lưu khu vực kho được gán

# Định nghĩa khu vực kho
WAREHOUSE_AREAS = {
    "Khu A": {"capacity": 2034},
    "Khu B": {"capacity": 2116},
    "Khu C": {"capacity": 492},
    "Khu D": {"capacity": 111},
    "Khu E": {"capacity": 450, "is_expiry_area": True},
}

# Mapping mã sản phẩm -> khu vực đề xuất
PRODUCT_WAREHOUSE_SUGGESTION = {
    # Khu A - Bánh & Snack
    "SP001": "Khu A",  # Bánh quy bơ
    "SP002": "Khu A",  # Bánh quy socola
    "SP003": "Khu A",  # Bánh kem xốp
    "SP008": "Khu A",  # Snack khoai tây
    "SP009": "Khu A",  # Snack rong biển
    # Khu B - Kẹo & Socola
    "SP004": "Khu B",  # Kẹo cứng hương cam
    "SP005": "Khu B",  # Kẹo mềm sữa
    "SP006": "Khu B",  # Kẹo dẻo trái cây
    "SP007": "Khu B",  # Socola nhân hạnh nhân
    "SP014": "Khu B",  # Kẹo bạc hà
    "SP015": "Khu B",  # Kẹo me chua cay
    # Khu C - Ăn nhẹ & Bánh mì
    "SP012": "Khu C",  # Thanh ngũ cốc dinh dưỡng
    "SP013": "Khu C",  # Bánh mì mini
    # Khu D - Mùa vụ (Trung thu)
    "SP010": "Khu D",  # Bánh trung thu truyền thống
    "SP011": "Khu D",  # Bánh trung thu nhân đậu xanh
}

# Nếu file phiếu nhập chưa có → tạo mới đúng cấu trúc bạn muốn
if not os.path.exists(IMPORT_DB):
    empty = pd.DataFrame({
        "Mã phiếu": [],
        "Nhân viên nhập": [],
        "Mã sản phẩm": [],
        "Tên sản phẩm": [],
        "Số lượng nhập": [],
        "Hạn sử dụng": [],
        "Ngày nhập": []
    })
    empty.to_csv(IMPORT_DB, index=False, encoding="utf-8-sig")


@st.cache_data
def load_products():
    return pd.read_csv(PRODUCT_DB)


@st.cache_data
def load_receipts():
    df = pd.read_csv(IMPORT_DB)
    # Chuẩn hóa dữ liệu để tránh lỗi so sánh / lọc:
    # - Mã phiếu luôn là string và bỏ khoảng trắng dư
    # - Hạn sử dụng luôn là string (có thể rỗng)
    if "Mã phiếu" in df.columns:
        df["Mã phiếu"] = df["Mã phiếu"].astype(str).str.strip()
    if "Hạn sử dụng" in df.columns:
        df["Hạn sử dụng"] = df["Hạn sử dụng"].astype(str)
    return df


def save_products(df):
    df.to_csv(PRODUCT_DB, index=False, encoding="utf-8-sig")
    load_products.clear()  # Clear cache của trang Import
    st.cache_data.clear()  # Clear tất cả cache để trang Products cũng cập nhật


def save_receipts(df):
    df.to_csv(IMPORT_DB, index=False, encoding="utf-8-sig")
    # Clear cache để mọi chỗ dùng load_receipts() luôn đọc dữ liệu mới nhất,
    # đảm bảo khi sửa HSD trong thông tin phiếu nhập thì bảng hiển thị cập nhật ngay.
    load_receipts.clear()
    st.cache_data.clear()


@st.cache_data
def load_warehouse_assignments():
    """Đọc file gán khu vực kho (nếu có)."""
    if not os.path.exists(WAREHOUSE_ASSIGN_DB):
        return pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
    try:
        df = pd.read_csv(WAREHOUSE_ASSIGN_DB)
        if "Mã sản phẩm" not in df.columns:
            df["Mã sản phẩm"] = ""
        if "Lô" not in df.columns:
            df["Lô"] = 0
        if "Khu" not in df.columns:
            df["Khu"] = ""
        if "Số lượng" not in df.columns:
            df["Số lượng"] = pd.NA
        return df[["Mã sản phẩm", "Lô", "Khu", "Số lượng"]]
    except Exception:
        return pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])


def save_warehouse_assignments(df):
    """Lưu lại cấu hình khu vực kho và clear cache."""
    df.to_csv(WAREHOUSE_ASSIGN_DB, index=False, encoding="utf-8-sig")
    load_warehouse_assignments.clear()
    st.cache_data.clear()


# ======================
# LOAD DATA
# ======================
df_sp = load_products()
df_phieu = load_receipts()

st.title("📦 Phiếu Nhập Kho")

# ======================
# THANH BUTTON
# ======================
b1, b2, b3 = st.columns(3)

with b1:
    if st.button("➕ Thêm phiếu nhập", type="primary", use_container_width=True, key="add_receipt_btn"):
        st.session_state["show_add_receipt"] = True

with b2:
    st.download_button(
        "📤 Xuất Excel phiếu nhập",
        data=df_phieu.to_csv(index=False).encode("utf-8-sig"),
        file_name="phieu_nhap.csv",
        mime="text/csv",
        use_container_width=True
    )

with b3:
    st.button("🔄 Làm mới", on_click=lambda: st.rerun(), use_container_width=True)

# ======================
# DANH SÁCH PHIẾU NHẬP
# ======================
st.subheader("📜 Danh sách phiếu nhập")
if len(df_phieu) == 0:
    st.markdown(
        """
        <div style="
            background-color: #e0f2fe;
            border-left: 4px solid #0ea5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 20px;">ℹ️</span>
                <span style="color: #0c4a6e; font-weight: 500;">
                    Chưa có phiếu nhập nào. Hãy thêm phiếu nhập mới hoặc import từ file Excel/CSV.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Ô tìm kiếm theo ngày nhập
    col_search, _ = st.columns([2, 4])
    with col_search:
        search_date = st.date_input(
            "🔎 Tìm kiếm phiếu nhập theo ngày",
            value=None,
            format="DD/MM/YYYY",
            key="import_search_date",
        )

    df_filtered = df_phieu.copy()
    if search_date:
        date_str = search_date.strftime("%d/%m/%Y")
        df_filtered = df_filtered[
            df_filtered["Ngày nhập"].astype(str).str.contains(date_str)
        ]

    if len(df_filtered) == 0:
        st.info("⚠ Không tìm thấy phiếu nhập nào cho ngày đã chọn.")
    else:
        # Tạo bảng tổng hợp theo Mã phiếu (1 phiếu có thể có nhiều sản phẩm)
        df_summary = (
            df_filtered[["Mã phiếu", "Nhân viên nhập", "Ngày nhập"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Thêm cột STT (số thứ tự)
        df_summary.insert(0, "STT", range(1, len(df_summary) + 1))

        # Cấu hình AgGrid cho danh sách phiếu
        gb = GridOptionsBuilder.from_dataframe(df_summary)
        # Căn giữa toàn bộ nội dung ô
        center_style = {"textAlign": "center"}
        gb.configure_default_column(cellStyle=center_style)

        gb.configure_selection(
            selection_mode="single",
            use_checkbox=False,
            rowMultiSelectWithClick=False,
        )
        gb.configure_grid_options(
            domLayout="normal",
            suppressRowClickSelection=False,
        )
        gb.configure_column("STT", header_name="STT", width=80)
        gb.configure_column("Mã phiếu", header_name="Mã phiếu")
        gb.configure_column("Nhân viên nhập", header_name="Nhân viên nhập")
        gb.configure_column("Ngày nhập", header_name="Ngày nhập")

        grid_options = gb.build()

        grid_response = AgGrid(
            df_summary,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=False,
            theme="balham",
            height=350,
        )

        selected = grid_response.get("selected_rows", [])
        # Chuẩn hóa selected về list dict
        if isinstance(selected, pd.DataFrame):
            selected = selected.to_dict(orient="records")
        elif selected is None:
            selected = []

        # Hiển thị thông tin phiếu + danh sách sản phẩm trong phiếu được chọn
        if len(selected) > 0:
            selected_receipt = selected[0]
            ma_phieu_chon = str(selected_receipt["Mã phiếu"])
            nv_nhap_chon = selected_receipt["Nhân viên nhập"]
            ngay_nhap_chon = selected_receipt["Ngày nhập"]

            # Tiêu đề "Thông tin phiếu nhập" căn giữa
            st.markdown(
                """
                <div style="text-align: center; margin-top: 8px; margin-bottom: 16px;">
                    <h4 style="margin: 0; font-weight: 700;">📥 Thông tin phiếu nhập</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 3 ô thông tin: Mã phiếu nhập, Nhân viên nhập, Ngày nhập
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f9fafb;
                        border-radius: 8px;
                        padding: 10px 12px;
                        border: 1px solid #e5e7eb;
                        text-align: center;
                    ">
                        <div style="font-size: 12px; color: #6b7280;">Mã phiếu nhập</div>
                        <div style="font-weight: 600; color: #111827; margin-top: 2px;">{ma_phieu_chon}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with info_col2:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f9fafb;
                        border-radius: 8px;
                        padding: 10px 12px;
                        border: 1px solid #e5e7eb;
                        text-align: center;
                    ">
                        <div style="font-size: 12px; color: #6b7280;">Nhân viên nhập</div>
                        <div style="font-weight: 600; color: #111827; margin-top: 2px;">{nv_nhap_chon}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with info_col3:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f9fafb;
                        border-radius: 8px;
                        padding: 10px 12px;
                        border: 1px solid #e5e7eb;
                        text-align: center;
                    ">
                        <div style="font-size: 12px; color: #6b7280;">Ngày nhập</div>
                        <div style="font-weight: 600; color: #111827; margin-top: 2px;">{ngay_nhap_chon}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Khoảng cách nhẹ giữa khối thông tin phiếu và bảng chi tiết
            st.markdown(
                "<div style='height: 12px;'></div>",
                unsafe_allow_html=True,
            )

            # Bảng chi tiết sản phẩm trong phiếu
            df_ct = df_phieu[df_phieu["Mã phiếu"] == ma_phieu_chon][
                ["Mã sản phẩm", "Tên sản phẩm", "Số lượng nhập", "Hạn sử dụng"]
            ].reset_index(drop=True)

            if len(df_ct) > 0:
                # Thêm cột STT và chỉ giữ 1 cột đánh số thứ tự
                df_ct.insert(0, "STT", range(1, len(df_ct) + 1))

                # Sử dụng lại AgGrid cho bảng chi tiết và căn giữa toàn bộ
                gb_ct = GridOptionsBuilder.from_dataframe(df_ct)
                center_style_ct = {"textAlign": "center"}
                gb_ct.configure_default_column(cellStyle=center_style_ct)

                # Cho phép chọn 1 dòng để xem chi tiết phân bổ khu vực kho
                gb_ct.configure_selection(
                    selection_mode="single",
                    use_checkbox=False,
                    rowMultiSelectWithClick=False,
                )
                gb_ct.configure_grid_options(domLayout="normal")
                gb_ct.configure_column("STT", header_name="STT", width=80)
                gb_ct.configure_column("Mã sản phẩm", header_name="Mã sản phẩm")
                gb_ct.configure_column("Tên sản phẩm", header_name="Tên sản phẩm")
                gb_ct.configure_column("Số lượng nhập", header_name="Số lượng nhập")
                gb_ct.configure_column("Hạn sử dụng", header_name="Hạn sử dụng")

                # Tính chiều cao động dựa trên số dòng
                row_height = 36
                header_height = 40
                base_padding = 20
                n_rows = len(df_ct)
                dynamic_height = header_height + n_rows * row_height + base_padding
                # Giới hạn chiều cao từ 120 đến 400 để không quá thấp/quá dài
                dynamic_height = max(120, min(dynamic_height, 400))

                grid_options_ct = gb_ct.build()

                grid_response_ct = AgGrid(
                    df_ct,
                    gridOptions=grid_options_ct,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    allow_unsafe_jscode=False,
                    theme="balham",
                    height=dynamic_height,
                )

                # ============================
                # XEM PHÂN BỔ KHU VỰC KHO CHO DÒNG ĐANG CHỌN
                # ============================
                selected_ct = grid_response_ct.get("selected_rows", [])
                if isinstance(selected_ct, pd.DataFrame):
                    selected_ct = selected_ct.to_dict(orient="records")
                elif selected_ct is None:
                    selected_ct = []

                if selected_ct:
                    selected_row_ct = selected_ct[0]
                    ma_sp_chi_tiet = str(selected_row_ct.get("Mã sản phẩm", "")).strip()

                    if ma_sp_chi_tiet:
                        # Tính số lô của dòng này dựa trên thứ tự xuất hiện trong df_phieu
                        df_sp_all = df_phieu[
                            df_phieu["Mã sản phẩm"].astype(str) == ma_sp_chi_tiet
                        ].reset_index()  # giữ index gốc làm cột "index"

                        if not df_sp_all.empty:
                            # Sắp xếp theo index gốc để có đúng thứ tự nhập
                            df_sp_all = df_sp_all.sort_values("index")
                            df_sp_all["__lot_number"] = range(
                                1, len(df_sp_all) + 1
                            )

                            # Tìm đúng dòng thuộc mã phiếu đang xem
                            row_in_receipt = df_sp_all[
                                df_sp_all["Mã phiếu"].astype(str) == ma_phieu_chon
                            ]

                            lot_number = None
                            if not row_in_receipt.empty:
                                lot_number = int(row_in_receipt.iloc[0]["__lot_number"])

                            if lot_number is not None:
                                assign_df = load_warehouse_assignments()
                                if not assign_df.empty:
                                    tmp = assign_df.copy()
                                    tmp["Mã sản phẩm"] = tmp["Mã sản phẩm"].astype(str)
                                    tmp["Lô"] = (
                                        pd.to_numeric(tmp["Lô"], errors="coerce")
                                        .fillna(0)
                                        .astype(int)
                                    )
                                    tmp["Số lượng"] = (
                                        pd.to_numeric(
                                            tmp.get("Số lượng", 0), errors="coerce"
                                        )
                                        .fillna(0)
                                        .astype(int)
                                    )

                                    df_khu = tmp[
                                        (tmp["Mã sản phẩm"] == ma_sp_chi_tiet)
                                        & (tmp["Lô"] == lot_number)
                                        & (tmp["Số lượng"] > 0)
                                    ][["Khu", "Số lượng"]].reset_index(drop=True)

                                    if not df_khu.empty:
                                        st.markdown(
                                            """
                                            <div style="
                                                margin-top: 8px;
                                                margin-bottom: 4px;
                                                font-weight: 600;
                                                color: #111827;
                                            ">
                                                🏢 Phân bổ khu vực kho cho dòng đã chọn
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )

                                        from st_aggrid import GridOptionsBuilder

                                        gb_khu = GridOptionsBuilder.from_dataframe(df_khu)
                                        center_style_khu = {"textAlign": "center"}
                                        gb_khu.configure_default_column(
                                            cellStyle=center_style_khu
                                        )
                                        gb_khu.configure_grid_options(
                                            domLayout="autoHeight",
                                            suppressRowClickSelection=True,
                                        )
                                        gb_khu.configure_column(
                                            "Khu", header_name="Khu", width=120
                                        )
                                        gb_khu.configure_column(
                                            "Số lượng", header_name="Số lượng", width=120
                                        )

                                        grid_options_khu = gb_khu.build()

                                        AgGrid(
                                            df_khu,
                                            gridOptions=grid_options_khu,
                                            update_mode=GridUpdateMode.NO_UPDATE,
                                            allow_unsafe_jscode=False,
                                            theme="balham",
                                            height=120,
                                        )
                                    else:
                                        st.info(
                                            "ℹ Dòng sản phẩm này chưa được chia số lượng cho từng khu khi tạo phiếu nhập."
                                        )

                # ===== Sửa HSD cho từng dòng trong phiếu nhập =====
                st.markdown("#### ✏️ Sửa hạn sử dụng cho các dòng trong phiếu")

                # Lấy lại toàn bộ các dòng của phiếu này cùng index gốc trong df_phieu
                df_receipt_rows = df_phieu[df_phieu["Mã phiếu"] == ma_phieu_chon].reset_index()

                if len(df_receipt_rows) > 0:
                    lot_numbers = list(range(1, len(df_receipt_rows) + 1))

                    selected_lot = st.selectbox(
                        "Chọn dòng cần sửa HSD",
                        lot_numbers,
                        format_func=lambda x: f"Dòng {x} - {df_receipt_rows.iloc[x-1]['Mã sản phẩm']}",
                        key=f"edit_hsd_row_{ma_phieu_chon}",
                    )

                    row_info = df_receipt_rows.iloc[selected_lot - 1]
                    current_hsd_str = str(row_info.get("Hạn sử dụng", "") or "").strip()

                    # Cố gắng parse HSD hiện tại sang date, nếu không được thì để None
                    current_hsd_date = None
                    if current_hsd_str and current_hsd_str.lower() != "nan":
                        try:
                            current_hsd_date = datetime.strptime(current_hsd_str, "%d/%m/%Y").date()
                        except Exception:
                            current_hsd_date = None

                    new_hsd = st.date_input(
                        "Hạn sử dụng mới cho dòng đã chọn",
                        value=current_hsd_date,
                        key=f"edit_hsd_date_{ma_phieu_chon}_{selected_lot}",
                        help="Chọn hạn sử dụng mới rồi bấm Lưu để cập nhật.",
                    )

                    if st.button(
                        "💾 Lưu hạn sử dụng",
                        key=f"btn_save_hsd_{ma_phieu_chon}_{selected_lot}",
                    ):
                        # Nếu chưa chọn ngày mới thì báo lỗi
                        if new_hsd is None:
                            st.error("⚠ Vui lòng chọn ngày hạn sử dụng.")
                            st.stop()

                        # index gốc trong df_phieu
                        orig_idx = int(row_info["index"])
                        df_phieu.at[orig_idx, "Hạn sử dụng"] = new_hsd.strftime("%d/%m/%Y")
                        save_receipts(df_phieu)
                        st.success("✔ Đã cập nhật hạn sử dụng.")
                        st.rerun()

# ======================
# IMPORT PHIẾU TỪ EXCEL / CSV – CÓ CẬP NHẬT TỒN KHO
# ======================
st.subheader("📥 Nhập phiếu từ Excel / CSV")

upload = st.file_uploader(
    "Chọn file Excel / CSV",
    type=["xlsx", "xls", "csv"],
    help="Hỗ trợ định dạng: XLSX, XLS, CSV. Giới hạn 200MB mỗi file."
)

if upload is not None:
    file_bytes = upload.read()
    df_excel = None

    # 1) Thử đọc xlsx bằng openpyxl
    try:
        df_excel = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        df_excel = None

    # 2) Thử đọc xls bằng xlrd
    if df_excel is None:
        try:
            df_excel = pd.read_excel(io.BytesIO(file_bytes), engine="xlrd")
        except Exception:
            df_excel = None

    # 3) Thử đọc csv
    if df_excel is None:
        try:
            df_excel = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            st.error(f"❌ Không thể đọc file. Lỗi: {str(e)}")
            st.stop()

    required_cols = [
        "Mã phiếu",
        "Nhân viên nhập",
        "Mã sản phẩm",
        "Tên sản phẩm",
        "Số lượng nhập",
        "Hạn sử dụng",
        "Ngày nhập"
    ]

    df_excel.columns = [c.strip() for c in df_excel.columns]
    missing = [c for c in required_cols if c not in df_excel.columns]

    if missing:
        st.error(f"⚠ File thiếu cột: {missing}")
    else:
        st.success("✔ File hợp lệ, sẵn sàng import")

        if st.button("🚀 Import phiếu nhập"):
            errors = []
            warnings = []
            
            # Kiểm tra hạn sử dụng không được để trống
            if "Hạn sử dụng" in df_excel.columns:
                missing_hsd_rows = []
                for idx_excel, row in df_excel.iterrows():
                    han_sd = row.get("Hạn sử dụng", "")
                    if pd.isna(han_sd) or str(han_sd).strip() == "":
                        missing_hsd_rows.append(idx_excel + 2)  # +2 vì index bắt đầu từ 0 và có header
                
                if missing_hsd_rows:
                    errors.append(f"Hạn sử dụng là trường bắt buộc. Các dòng thiếu hạn sử dụng: {', '.join(map(str, missing_hsd_rows))}")
            
            # Cập nhật tồn kho + cộng vào lịch sử phiếu
            for idx_excel, row in df_excel.iterrows():
                try:
                    ma_sp = str(row["Mã sản phẩm"]).strip()
                    so_luong_nhap = int(row["Số lượng nhập"])

                    if ma_sp in df_sp["Mã sản phẩm"].astype(str).values:
                        idx = df_sp[df_sp["Mã sản phẩm"] == ma_sp].index[0]
                        ton_cu = int(df_sp.at[idx, "Số lượng tồn kho"])
                        ton_moi = ton_cu + so_luong_nhap
                        df_sp.at[idx, "Số lượng tồn kho"] = ton_moi
                    else:
                        warnings.append(f"Dòng {idx_excel + 2}: Mã sản phẩm {ma_sp} không tồn tại")
                except Exception as e:
                    errors.append(f"Dòng {idx_excel + 2}: {str(e)}")

            if errors:
                st.error("❌ Có lỗi xảy ra:\n" + "\n".join(errors))
            if warnings:
                st.warning("⚠ Cảnh báo:\n" + "\n".join(warnings))

            # Chỉ gộp data nếu không có lỗi
            if not errors:
                # Gộp data
                df_phieu = pd.concat([df_phieu, df_excel[required_cols]], ignore_index=True)

                save_products(df_sp)
                save_receipts(df_phieu)
                
                st.success("✔ Import phiếu nhập thành công!")
                st.rerun()

# ======================
# FORM THÊM PHIẾU NHẬP – CẬP NHẬT TỒN KHO + HIỂN THỊ NGAY
# ======================
if st.session_state.get("show_add_receipt"):
    # Khởi tạo danh sách sản phẩm nếu chưa có
    if "products_list" not in st.session_state:
        st.session_state["products_list"] = []

    # Xử lý xóa sản phẩm (phải làm trước form)
    if "delete_product_idx" in st.session_state:
        idx_to_delete = st.session_state["delete_product_idx"]
        if 0 <= idx_to_delete < len(st.session_state["products_list"]):
            st.session_state["products_list"].pop(idx_to_delete)
        del st.session_state["delete_product_idx"]
        st.rerun()

    st.markdown(
        """
        <div style="
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
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">
            THÊM PHIẾU NHẬP MỚI
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hiển thị danh sách sản phẩm đã thêm (ngoài form)
    if len(st.session_state["products_list"]) > 0:
        st.markdown("#### 📋 Danh sách sản phẩm đã thêm:")
        
        for idx, product in enumerate(st.session_state["products_list"]):
            col_info, col_del = st.columns([5, 1])
            with col_info:
                warehouse_info = ""
                if product.get("warehouse_allocation"):
                    wh_list = ", ".join([f"{a['khu']}: {a['so_luong']}" for a in product["warehouse_allocation"]])
                    warehouse_info = f"<br>🏢 Khu vực: {wh_list}"
                
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0f9ff;
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        border-left: 4px solid #4c78d3;
                    ">
                        <strong>{product['ma_sp']}</strong> - {product['ten_sp']}<br>
                        Số lượng: {product['so_luong']} | 
                        Tồn hiện tại: {product['ton_hien_tai']} | 
                        Hạn SD: {product['han_sd']}{warehouse_info}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_del:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    st.session_state["delete_product_idx"] = idx
                    st.rerun()
        
        st.markdown("---")

    # --- Thông tin phiếu nhập và thêm sản phẩm (không dùng st.form để UI phản hồi ngay) ---
    c1, c2 = st.columns(2)
    with c1:
        ma_phieu = st.text_input("Mã phiếu nhập (ví dụ: PN001)", key="ma_phieu_input").strip()
        nhan_vien = st.text_input("Nhân viên nhập", key="nhan_vien_input")
    with c2:
        ngay_nhap = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.write(f"📅 Ngày nhập: **{ngay_nhap}**")

    st.markdown("### Thêm sản phẩm vào phiếu")

    # Tạo danh sách mã sản phẩm cho selectbox
    if len(df_sp) > 0:
        ma_sp_list = ["-- Chọn mã sản phẩm --"] + df_sp["Mã sản phẩm"].astype(str).tolist()
    else:
        ma_sp_list = ["-- Chưa có sản phẩm --"]

    # Khởi tạo counter để reset widget
    if "form_reset_counter" not in st.session_state:
        st.session_state["form_reset_counter"] = 0
    reset_counter = st.session_state.get("form_reset_counter", 0)
    
    # Khởi tạo session state cho khu vực đã chọn và mã sản phẩm đã chọn
    warehouse_key = f"selected_warehouses_{reset_counter}"
    last_ma_sp_key = f"last_ma_sp_{reset_counter}"
    if warehouse_key not in st.session_state:
        st.session_state[warehouse_key] = []
    if last_ma_sp_key not in st.session_state:
        st.session_state[last_ma_sp_key] = None
    
    c3, c5 = st.columns([3, 1])
    with c3:
        selected_ma_sp = st.selectbox(
            "Mã sản phẩm", 
            ma_sp_list, 
            key=f"select_ma_sp_{reset_counter}",
            index=0,  # Luôn chọn phần tử đầu tiên (-- Chọn mã sản phẩm --)
        )
    
    # Kiểm tra xem mã sản phẩm có thay đổi không
    if selected_ma_sp != st.session_state[last_ma_sp_key]:
        # Mã sản phẩm đã thay đổi, cập nhật khu đề xuất
        st.session_state[last_ma_sp_key] = selected_ma_sp
        suggested_warehouse = PRODUCT_WAREHOUSE_SUGGESTION.get(selected_ma_sp)
        if suggested_warehouse and suggested_warehouse in list(WAREHOUSE_AREAS.keys()):
            # Thêm khu đề xuất vào danh sách nếu chưa có
            if suggested_warehouse not in st.session_state[warehouse_key]:
                st.session_state[warehouse_key].append(suggested_warehouse)
                # Rerun để cập nhật multiselect
                st.rerun()
        elif selected_ma_sp == "-- Chọn mã sản phẩm --" or selected_ma_sp == "-- Chưa có sản phẩm --":
            # Reset về rỗng nếu chưa chọn sản phẩm
            if st.session_state[warehouse_key]:
                st.session_state[warehouse_key] = []
                st.rerun()
    with c5:
        han_sd = st.date_input(
            "Hạn sử dụng *", 
            value=None, 
            key=f"input_han_sd_{reset_counter}", 
            help="Trường bắt buộc",
        )

    # Biến tạm lưu phân bổ khu vực cho sản phẩm đang nhập
    current_allocation = []
    total_allocated = 0

    # Hiển thị thông tin sản phẩm (nếu đã chọn hợp lệ)
    suggested_warehouse = None
    if (
        selected_ma_sp
        and selected_ma_sp != "-- Chọn mã sản phẩm --"
        and selected_ma_sp != "-- Chưa có sản phẩm --"
        and selected_ma_sp in df_sp["Mã sản phẩm"].astype(str).values
    ):
        row_sp = df_sp[df_sp["Mã sản phẩm"] == selected_ma_sp].iloc[0]
        ten_sp = row_sp["Tên sản phẩm"]
        ton_hien_tai = int(row_sp["Số lượng tồn kho"])
        st.info(f"📌 Tên sản phẩm: {ten_sp} | 📦 Tồn kho hiện tại: {ton_hien_tai}")
        
        # Lấy khu vực đề xuất
        suggested_warehouse = PRODUCT_WAREHOUSE_SUGGESTION.get(selected_ma_sp)
        if suggested_warehouse:
            st.markdown(
                f"""
                <div style="
                    background-color: #e0f2fe;
                    border-left: 4px solid #0ea5e9;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 8px 0;
                ">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 18px;">📍</span>
                        <span style="color: #0c4a6e; font-weight: 600;">
                            Khu đề xuất cho sản phẩm này: <strong>{suggested_warehouse}</strong>
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Khu đề xuất đã được thêm vào session state ở trên khi mã sản phẩm thay đổi

    # Khu vực lưu kho luôn hiển thị (ngay từ đầu)
    st.markdown("#### 🏢 Khu vực lưu kho")
    available_warehouses = list(WAREHOUSE_AREAS.keys())

    # Nếu có khu đề xuất, chỉ hiển thị khu đó trong multiselect; nếu không, hiển thị tất cả
    if suggested_warehouse and suggested_warehouse in available_warehouses:
        # Chỉ hiển thị khu đề xuất trong multiselect (người dùng vẫn có thể bỏ chọn nếu muốn)
        selected_warehouses = st.multiselect(
            "Chọn khu vực lưu kho",
            [suggested_warehouse],  # Chỉ hiển thị khu đề xuất
            default=[suggested_warehouse],  # Tự động chọn khu đề xuất
            key=f"multi_warehouse_{reset_counter}",
        )
        
        # Cập nhật session state
        st.session_state[warehouse_key] = selected_warehouses
    else:
        # Không có khu đề xuất, hiển thị tất cả các khu
        selected_warehouses = st.multiselect(
            "Chọn khu vực lưu kho",
            available_warehouses,
            default=st.session_state[warehouse_key],
            key=f"multi_warehouse_{reset_counter}",
        )
        
        # Cập nhật session state khi người dùng thay đổi lựa chọn
        st.session_state[warehouse_key] = selected_warehouses

    # Load warehouse assignments để tính số lượng hiện tại trong mỗi khu
    assign_df_current = load_warehouse_assignments()
    warehouse_current_qty = {}
    if not assign_df_current.empty:
        assign_df_current["Khu"] = assign_df_current["Khu"].astype(str)
        assign_df_current["Số lượng"] = pd.to_numeric(assign_df_current["Số lượng"], errors="coerce").fillna(0).astype(int)
        for wh_name in available_warehouses:
            wh_qty = assign_df_current[assign_df_current["Khu"] == wh_name]["Số lượng"].sum()
            warehouse_current_qty[wh_name] = int(wh_qty)
    else:
        for wh_name in available_warehouses:
            warehouse_current_qty[wh_name] = 0

    has_any_capacity_error = False  # Theo dõi xem có lỗi sức chứa nào không
    
    for wh in selected_warehouses:
        # Tính sức chứa còn lại
        max_capacity = WAREHOUSE_AREAS[wh].get("capacity", 0)
        current_qty_in_wh = warehouse_current_qty.get(wh, 0)
        remaining_capacity = max(0, max_capacity - current_qty_in_wh)
        
        # Hiển thị thông tin sức chứa trước ô nhập số lượng
        st.markdown(
            f"""
            <div style="
                background-color: #f9fafb;
                border-left: 3px solid #4c78d3;
                border-radius: 6px;
                padding: 8px 12px;
                margin-bottom: 4px;
                font-size: 12px;
            ">
                <span style="color: #6b7280;">📊 Sức chứa: </span>
                <span style="color: #111827; font-weight: 600;">Tối đa {max_capacity:,} thùng</span>
                <span style="color: #6b7280;"> | </span>
                <span style="color: #6b7280;">Hiện tại: {current_qty_in_wh:,} thùng</span>
                <span style="color: #6b7280;"> | </span>
                <span style="color: {'#059669' if remaining_capacity > 0 else '#dc2626'}; font-weight: 600;">
                    Còn lại: {remaining_capacity:,} thùng
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        qty = st.number_input(
            f"Số lượng tại {wh}",
            min_value=0,
            max_value=remaining_capacity if remaining_capacity > 0 else None,
            value=0,
            key=f"qty_{wh}_{reset_counter}",
            help=f"Sức chứa tối đa: {max_capacity:,} thùng. Hiện tại: {current_qty_in_wh:,} thùng. Còn lại: {remaining_capacity:,} thùng.",
        )
        
        # Cảnh báo nếu nhập vượt quá sức chứa còn lại
        has_capacity_error = False
        if qty > remaining_capacity:
            st.error(
                f"⚠️ **Cảnh báo:** Số lượng nhập ({qty:,} thùng) vượt quá sức chứa còn lại của {wh} ({remaining_capacity:,} thùng)! "
                f"Vui lòng giảm số lượng hoặc chọn khu vực khác."
            )
            has_capacity_error = True
            has_any_capacity_error = True
        elif remaining_capacity == 0 and qty > 0:
            st.warning(f"⚠️ {wh} đã đầy (hiện tại: {current_qty_in_wh:,}/{max_capacity:,} thùng). Không thể nhập thêm.")
            has_capacity_error = True
            has_any_capacity_error = True
        elif remaining_capacity == 0:
            st.warning(f"⚠️ {wh} đã đầy (hiện tại: {current_qty_in_wh:,}/{max_capacity:,} thùng). Không thể nhập thêm.")
        
        # Chỉ thêm vào allocation nếu không có lỗi sức chứa
        if qty > 0 and not has_capacity_error:
            current_allocation.append({"khu": wh, "so_luong": qty})
            total_allocated += qty

    if total_allocated > 0:
        st.caption(f"📊 Tổng số lượng phân bổ: **{total_allocated}**")

    # Nút thêm sản phẩm vào danh sách
    col_add, _ = st.columns([1, 4])
    with col_add:
        add_product = st.button("➕ Thêm sản phẩm", use_container_width=True, key="btn_add_product")

    if add_product:
        if selected_ma_sp == "-- Chọn mã sản phẩm --" or selected_ma_sp == "-- Chưa có sản phẩm --":
            st.error("⚠ Vui lòng chọn mã sản phẩm!")
        elif selected_ma_sp not in df_sp["Mã sản phẩm"].astype(str).values:
            st.error("❌ Mã sản phẩm không tồn tại!")
        elif han_sd is None:
            st.error("⚠ Vui lòng nhập hạn sử dụng! Đây là trường bắt buộc.")
        elif has_any_capacity_error:
            # Nếu có lỗi về sức chứa, không hiển thị cảnh báo "chọn khu vực"
            st.error("⚠️ Vui lòng sửa lỗi về sức chứa trước khi thêm sản phẩm!")
        elif not current_allocation:
            # Chỉ hiển thị cảnh báo này nếu không có lỗi về sức chứa và không có allocation
            st.error("⚠ Vui lòng nhập số lượng > 0 và không vượt quá giới hạn sức chứa của kho")
        else:
            # Tính tổng số lượng từ các khu vực đã chọn
            total_allocated = sum(a["so_luong"] for a in current_allocation)
            if total_allocated <= 0:
                st.error("⚠ Tổng số lượng phải lớn hơn 0!")
            else:
                # Kiểm tra xem sản phẩm đã có trong danh sách chưa
                existing = [p for p in st.session_state["products_list"] if p["ma_sp"] == selected_ma_sp]
                if existing:
                    st.warning(f"⚠ Sản phẩm {selected_ma_sp} đã có trong danh sách!")
                else:
                    row_sp = df_sp[df_sp["Mã sản phẩm"] == selected_ma_sp].iloc[0]
                    st.session_state["products_list"].append({
                        "ma_sp": selected_ma_sp,
                        "ten_sp": row_sp["Tên sản phẩm"],
                        "so_luong": total_allocated,  # Số lượng = tổng các khu vực
                        "han_sd": han_sd.strftime("%d/%m/%Y") if han_sd else "",
                        "ton_hien_tai": int(row_sp["Số lượng tồn kho"]),
                        "warehouse_allocation": current_allocation.copy()
                    })
                    # Tăng counter để reset form cho lần nhập tiếp theo
                    st.session_state["form_reset_counter"] += 1
                    st.rerun()

    st.markdown("---")
    submit = st.button("💾 Lưu phiếu nhập", use_container_width=True, key="btn_save_receipt")

    if st.session_state.get("show_add_receipt"):
        if submit:
            if not ma_phieu or not nhan_vien:
                st.error("⚠ Vui lòng nhập đầy đủ Mã phiếu và Nhân viên nhập.")
            elif len(st.session_state["products_list"]) == 0:
                st.error("⚠ Vui lòng thêm ít nhất một sản phẩm vào phiếu!")
            else:
                # Kiểm tra tất cả sản phẩm đều có hạn sử dụng
                products_missing_hsd = [
                    p["ma_sp"]
                    for p in st.session_state["products_list"]
                    if not p.get("han_sd") or p["han_sd"].strip() == ""
                ]
                if products_missing_hsd:
                    st.error(
                        "⚠ Các sản phẩm sau chưa có hạn sử dụng: "
                        + ", ".join(products_missing_hsd)
                        + ". Vui lòng xóa và thêm lại với hạn sử dụng!"
                    )
                else:
                    # VALIDATION: Kiểm tra sức chứa của các khu vực trước khi lưu
                    assign_df = load_warehouse_assignments()
                    capacity_errors = []
                    
                    # Tính tổng số lượng hiện tại trong mỗi khu vực
                    warehouse_current_totals = {}
                    if not assign_df.empty:
                        assign_df["Khu"] = assign_df["Khu"].astype(str)
                        assign_df["Số lượng"] = pd.to_numeric(assign_df["Số lượng"], errors="coerce").fillna(0).astype(int)
                        for wh_name in WAREHOUSE_AREAS.keys():
                            wh_qty = assign_df[assign_df["Khu"] == wh_name]["Số lượng"].sum()
                            warehouse_current_totals[wh_name] = int(wh_qty)
                    else:
                        for wh_name in WAREHOUSE_AREAS.keys():
                            warehouse_current_totals[wh_name] = 0
                    
                    # Tính tổng số lượng sẽ được thêm vào mỗi khu vực từ danh sách sản phẩm
                    warehouse_new_totals = {}
                    for wh_name in WAREHOUSE_AREAS.keys():
                        warehouse_new_totals[wh_name] = 0
                    
                    for product in st.session_state["products_list"]:
                        warehouse_allocation = product.get("warehouse_allocation", [])
                        for alloc in warehouse_allocation:
                            khu = alloc["khu"]
                            qty = alloc["so_luong"]
                            if khu in warehouse_new_totals:
                                warehouse_new_totals[khu] += qty
                    
                    # Kiểm tra từng khu vực xem có vượt quá sức chứa không
                    for wh_name in WAREHOUSE_AREAS.keys():
                        max_capacity = WAREHOUSE_AREAS[wh_name].get("capacity", 0)
                        current_qty = warehouse_current_totals.get(wh_name, 0)
                        new_qty = warehouse_new_totals.get(wh_name, 0)
                        total_after = current_qty + new_qty
                        
                        if total_after > max_capacity:
                            capacity_errors.append(
                                f"⚠️ **{wh_name}:** Số lượng sau khi nhập ({total_after:,} thùng) "
                                f"vượt quá sức chứa tối đa ({max_capacity:,} thùng). "
                                f"Hiện tại: {current_qty:,} thùng, sẽ thêm: {new_qty:,} thùng. "
                                f"Còn lại: {max(0, max_capacity - current_qty):,} thùng."
                            )
                    
                    # Nếu có lỗi về sức chứa, hiển thị và không cho lưu
                    if capacity_errors:
                        st.error("❌ **Không thể lưu phiếu nhập do vượt quá sức chứa:**")
                        for err in capacity_errors:
                            st.error(err)
                        st.error("⚠️ Vui lòng giảm số lượng hoặc chọn khu vực khác trước khi lưu!")
                    else:
                        # Không có lỗi về sức chứa, tiếp tục lưu
                        errors = []

                        # Lưu từng sản phẩm vào phiếu và cập nhật tồn kho
                        for product in st.session_state["products_list"]:
                            ma_sp = product["ma_sp"]
                            so_luong_nhap = product["so_luong"]
                            ten_sp = product["ten_sp"]
                            han_sd_str = product["han_sd"]
                            warehouse_allocation = product.get("warehouse_allocation", [])

                            try:
                                # 1) Cập nhật tồn kho sản phẩm
                                idx = df_sp[df_sp["Mã sản phẩm"] == ma_sp].index[0]
                                ton_cu = int(df_sp.at[idx, "Số lượng tồn kho"])
                                ton_moi = ton_cu + so_luong_nhap
                                df_sp.at[idx, "Số lượng tồn kho"] = ton_moi

                                # 2) Tính số lô dựa trên số lần nhập của sản phẩm này (trước khi lưu)
                                previous_imports = df_phieu[
                                    df_phieu["Mã sản phẩm"].astype(str) == str(ma_sp)
                                ]
                                lot_number = len(previous_imports) + 1  # Lô số bắt đầu từ 1

                                # 3) Lưu phiếu nhập vào bảng phiếu
                                new_row = {
                                    "Mã phiếu": ma_phieu,
                                    "Nhân viên nhập": nhan_vien,
                                    "Mã sản phẩm": ma_sp,
                                    "Tên sản phẩm": ten_sp,
                                    "Số lượng nhập": so_luong_nhap,
                                    "Hạn sử dụng": han_sd_str,
                                    "Ngày nhập": ngay_nhap,
                                }
                                df_phieu = pd.concat([df_phieu, pd.DataFrame([new_row])], ignore_index=True)

                                # 4) Lưu phân bổ khu vực vào warehouse_areas.csv
                                if warehouse_allocation:
                                    for alloc in warehouse_allocation:
                                        khu = alloc["khu"]
                                        qty = alloc["so_luong"]

                                        # Kiểm tra xem đã có gán cho lô này chưa
                                        mask = (
                                            (assign_df["Mã sản phẩm"].astype(str) == str(ma_sp))
                                            & (assign_df["Lô"].astype(int) == lot_number)
                                            & (assign_df["Khu"].astype(str) == str(khu))
                                        )

                                        if mask.any():
                                            # Cập nhật số lượng
                                            assign_df.loc[mask, "Số lượng"] = (
                                                pd.to_numeric(assign_df.loc[mask, "Số lượng"], errors="coerce")
                                                .fillna(0)
                                                + qty
                                            ).astype(int)
                                        else:
                                            # Thêm mới
                                            new_row = {
                                                "Mã sản phẩm": ma_sp,
                                                "Lô": lot_number,
                                                "Khu": khu,
                                                "Số lượng": qty,
                                            }
                                            assign_df = pd.concat(
                                                [assign_df, pd.DataFrame([new_row])], ignore_index=True
                                            )
                            except Exception as e:
                                errors.append(f"Lỗi khi xử lý sản phẩm {ma_sp}: {str(e)}")

                        if errors:
                            st.error("❌ Có lỗi xảy ra:\n" + "\n".join(errors))
                        else:
                            # 5) Lưu CSV & refresh
                            save_products(df_sp)
                            save_receipts(df_phieu)
                            if not assign_df.empty:
                                # Chuẩn hóa dữ liệu trước khi lưu
                                assign_df["Mã sản phẩm"] = assign_df["Mã sản phẩm"].astype(str)
                                assign_df["Lô"] = (
                                    pd.to_numeric(assign_df["Lô"], errors="coerce").fillna(0).astype(int)
                                )
                                assign_df["Số lượng"] = (
                                    pd.to_numeric(assign_df["Số lượng"], errors="coerce").fillna(0).astype(int)
                                )
                                assign_df = assign_df[assign_df["Số lượng"] > 0]  # Chỉ giữ các dòng có số lượng > 0
                                save_warehouse_assignments(assign_df)

                            st.success(
                                f"✔ Đã lưu phiếu nhập {ma_phieu} với {len(st.session_state['products_list'])} sản phẩm!"
                            )
                            # Xóa danh sách sản phẩm và đóng form
                            st.session_state["products_list"] = []
                            st.session_state["warehouse_allocation"] = []
                            st.session_state["show_add_receipt"] = False
                            st.rerun()

