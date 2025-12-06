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
    page_title="Phiếu Xuất",
    page_icon="📤",
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

        /* Nút "Thêm phiếu xuất" - primary button xanh */
        button[key="add_export_btn"],
        button[kind="primary"] {
            background-color: #4c78d3 !important;
            border-color: #4c78d3 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        
        button[key="add_export_btn"]:hover,
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
# ĐƯỜNG DẪN DATABASE
# ======================
os.makedirs("database", exist_ok=True)

PRODUCT_DB = "database/sanpham.csv"
EXPORT_DB = "database/phieu_xuat.csv"
# Bổ sung file phiếu nhập & phân bổ khu vực kho để tính tồn theo từng khu
IMPORT_DB = "database/phieu_nhap.csv"
WAREHOUSE_ASSIGN_DB = "database/warehouse_areas.csv"

# Định nghĩa khu vực kho (đồng bộ với các trang khác)
WAREHOUSE_AREAS = {
    "Khu A": {"capacity": 2034},
    "Khu B": {"capacity": 2116},
    "Khu C": {"capacity": 492},
    "Khu D": {"capacity": 111},
    "Khu E": {"capacity": 450, "is_expiry_area": True},
}

# Tạo file nếu chưa có
if not os.path.exists(EXPORT_DB):
    df_init = pd.DataFrame({
        "Mã phiếu": [],
        "Nhân viên xuất": [],
        "Mã sản phẩm": [],
        "Tên sản phẩm": [],
        "Số lượng xuất": [],
        "Tồn trước xuất": [],
        "Tồn sau xuất": [],
        "Ngày xuất": [],
        "Ghi chú": []
    })
    df_init.to_csv(EXPORT_DB, index=False, encoding="utf-8-sig")


# ======================
# HÀM LOAD + SAVE (CÓ CLEAR CACHE)
# ======================
@st.cache_data
def load_products():
    return pd.read_csv(PRODUCT_DB)

@st.cache_data
def load_exports():
    return pd.read_csv(EXPORT_DB)

@st.cache_data
def load_imports():
    if not os.path.exists(IMPORT_DB):
        return pd.DataFrame()
    return pd.read_csv(IMPORT_DB)

@st.cache_data
def load_warehouse_assignments():
    """Đọc file phân bổ khu vực kho (nếu có)."""
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

def save_products(df):
    df.to_csv(PRODUCT_DB, index=False, encoding="utf-8-sig")
    load_products.clear()   # Clear cache của trang Export
    st.cache_data.clear()   # Clear tất cả cache để trang Products cũng cập nhật

def save_exports(df):
    df.to_csv(EXPORT_DB, index=False, encoding="utf-8-sig")
    load_exports.clear()    # CLEAR CACHE

def save_warehouse_assignments(df):
    """Lưu lại cấu hình khu vực kho và clear cache."""
    df.to_csv(WAREHOUSE_ASSIGN_DB, index=False, encoding="utf-8-sig")
    load_warehouse_assignments.clear()
    st.cache_data.clear()


# ======================
# HÀM TÍNH LÔ + TỒN THEO KHU CHO 1 SẢN PHẨM
# ======================
from datetime import date


def calculate_product_lots_for_export(ma_sp, df_products, df_imports, df_exports):
    """
    Tính toán danh sách lô hàng còn lại cho một sản phẩm,
    đồng bộ với cách hiển thị ở trang Chi tiết sản phẩm.
    Trả về DataFrame: Mã sản phẩm, Tên sản phẩm, Lô, Số lượng, Ngày nhập hàng, Hạn sử dụng.
    """
    product_row = df_products[df_products["Mã sản phẩm"].astype(str) == str(ma_sp)]
    if product_row.empty:
        return pd.DataFrame()

    ten_sp = product_row.iloc[0].get("Tên sản phẩm", "")
    try:
        current_stock = int(product_row.iloc[0].get("Số lượng tồn kho", 0))
    except Exception:
        current_stock = 0

    # Lịch sử nhập
    if "Mã sản phẩm" in df_imports.columns:
        df_product_imports = df_imports[
            df_imports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_product_imports = pd.DataFrame()

    # Lịch sử xuất
    if "Mã sản phẩm" in df_exports.columns:
        df_export_product = df_exports[
            df_exports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_export_product = pd.DataFrame()

    # Tổng nhập
    total_imported = 0
    if not df_product_imports.empty and "Số lượng nhập" in df_product_imports.columns:
        total_imported = (
            pd.to_numeric(df_product_imports["Số lượng nhập"], errors="coerce")
            .fillna(0)
            .astype(int)
            .sum()
        )

    # Tổng xuất
    total_exported = 0
    if not df_export_product.empty:
        total_exported = (
            pd.to_numeric(df_export_product["Số lượng xuất"], errors="coerce")
            .fillna(0)
            .astype(int)
            .sum()
        )

    # Tồn ban đầu = tồn hiện tại - tổng nhập + tổng xuất
    initial_qty = current_stock - total_imported + total_exported
    if initial_qty < 0:
        initial_qty = 0

    # Lô 1 ảo từ tồn ban đầu (nếu có)
    synthetic_lots = []
    if initial_qty > 0:
        year_now = datetime.now().year
        synthetic_lots.append(
            {
                "Mã phiếu": "INIT",
                "Nhân viên nhập": "Khởi tạo",
                "Mã sản phẩm": ma_sp,
                "Tên sản phẩm": ten_sp,
                "Số lượng nhập": initial_qty,
                "Hạn sử dụng": f"30/11/{year_now}",
                "Ngày nhập": "01/01/2000 00:00",
            }
        )

    if synthetic_lots:
        df_synthetic = pd.DataFrame(synthetic_lots)
        if not df_product_imports.empty:
            df_product_imports = pd.concat(
                [df_synthetic, df_product_imports], ignore_index=True
            )
        else:
            df_product_imports = df_synthetic

    if df_product_imports.empty:
        return pd.DataFrame()

    # Sắp xếp theo thời gian nhập (nếu có)
    if "Ngày nhập" in df_product_imports.columns:
        df_product_imports["_dt"] = pd.to_datetime(
            df_product_imports["Ngày nhập"], errors="coerce", dayfirst=True
        )
        df_product_imports = df_product_imports.sort_values(by="_dt").drop(
            columns=["_dt"]
        )

    lots = df_product_imports.reset_index(drop=True).copy()

    # HSD để ưu tiên lô cận hạn
    if "Hạn sử dụng" in lots.columns:
        lots["_hsd_dt"] = pd.to_datetime(
            lots["Hạn sử dụng"], errors="coerce", dayfirst=True
        )
    else:
        lots["_hsd_dt"] = pd.NaT

    if "Ngày nhập" in lots.columns:
        lots["_import_dt"] = pd.to_datetime(
            lots["Ngày nhập"], errors="coerce", dayfirst=True
        )
    else:
        lots["_import_dt"] = pd.NaT

    lots_for_sort = lots.reset_index().rename(columns={"index": "lot_idx"})
    lots_for_sort["_hsd_rank"] = lots_for_sort["_hsd_dt"]
    lots_for_sort.loc[
        lots_for_sort["_hsd_rank"].isna(), "_hsd_rank"
    ] = pd.Timestamp.max
    lots_for_sort = lots_for_sort.sort_values(
        by=["_hsd_rank", "_import_dt", "lot_idx"], ascending=[True, True, True]
    )

    # QUAN TRỌNG: Đọc trực tiếp số lượng còn lại từ warehouse_areas.csv
    # KHÔNG dùng logic FEFO để tính lại - chỉ dùng để sắp xếp đề xuất
    warehouse_areas_path = "database/warehouse_areas.csv"
    remaining_by_lot = {}  # Map: lot_idx -> số lượng còn lại (tổng từ tất cả các khu)
    
    # Kiểm tra xem có lô ảo INIT không
    has_init = initial_qty > 0
    
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

                    # Map lô từ warehouse_areas.csv sang lot_idx trong lots (0-based)
                    if has_init:
                        # Có lô ảo INIT: warehouse_areas.csv lô 1 -> lots lot_idx 1 (lô thật đầu tiên)
                        lot_idx = lo_warehouse  # lot_idx 1-based (lot_idx 0 là INIT)
                    else:
                        # Không có lô ảo INIT: warehouse_areas.csv lô 1 -> lots lot_idx 0
                        lot_idx = lo_warehouse - 1  # lot_idx 0-based
                    
                    if 0 <= lot_idx < len(lots):
                        remaining_by_lot[lot_idx] = remaining_by_lot.get(lot_idx, 0) + so_luong
        except Exception:
            pass  # Nếu có lỗi, sẽ dùng số lượng nhập ban đầu
    
    # Tính số lượng lô ảo INIT còn lại (nếu có)
    # Công thức: Tồn kho hiện tại = Lô ảo INIT còn lại + Tổng số lượng các lô thật còn lại
    total_real_lots_remaining = sum(remaining_by_lot.values())
    if has_init:
        init_lot_idx = 0  # Lô ảo INIT luôn là lot_idx 0
        init_remaining = max(0, current_stock - total_real_lots_remaining)
        if init_remaining > 0:
            remaining_by_lot[init_lot_idx] = init_remaining
    
    # Khởi tạo remaining_by_lot cho các lô thật không có trong warehouse_areas.csv
    # (các lô này đã xuất hết)
    for i in range(len(lots)):
        if i not in remaining_by_lot:
            ma_phieu_val = str(lots.iloc[i].get("Mã phiếu", "")).strip()
            if ma_phieu_val != "INIT":
                # Lô thật nhưng không có trong warehouse_areas.csv -> đã xuất hết
                remaining_by_lot[i] = 0

    # Kết quả: danh sách lô còn hàng (chỉ lấy các lô có số lượng > 0)
    lot_list = []
    for i in range(len(lots)):
        remaining_qty = remaining_by_lot.get(i, 0)
        if remaining_qty > 0:
            lot_list.append(
                {
                    "Mã sản phẩm": ma_sp,
                    "Tên sản phẩm": ten_sp,
                    "Lô": i + 1,
                    "Số lượng": remaining_qty,
                    "Ngày nhập hàng": lots.get("Ngày nhập", "")[i]
                    if "Ngày nhập" in lots.columns
                    else "",
                    "Hạn sử dụng": lots.get("Hạn sử dụng", "")[i]
                    if "Hạn sử dụng" in lots.columns
                    else "",
                }
            )

    return pd.DataFrame(lot_list)


def has_initial_lot(ma_sp, df_products, df_imports, df_exports) -> bool:
    """Kiểm tra sản phẩm có tồn ban đầu (=> có lô 1 ảo) hay không."""
    product_row = df_products[df_products["Mã sản phẩm"].astype(str) == str(ma_sp)]
    if product_row.empty:
        return False
    try:
        current_stock = int(product_row.iloc[0].get("Số lượng tồn kho", 0))
    except Exception:
        current_stock = 0

    if "Mã sản phẩm" in df_imports.columns:
        df_imp = df_imports[
            df_imports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_imp = pd.DataFrame()

    if "Mã sản phẩm" in df_exports.columns:
        df_exp = df_exports[
            df_exports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_exp = pd.DataFrame()

    total_imported = 0
    if not df_imp.empty and "Số lượng nhập" in df_imp.columns:
        total_imported = (
            pd.to_numeric(df_imp["Số lượng nhập"], errors="coerce")
            .fillna(0)
            .astype(int)
            .sum()
        )

    total_exported = 0
    if not df_exp.empty:
        total_exported = (
            pd.to_numeric(df_exp["Số lượng xuất"], errors="coerce")
            .fillna(0)
            .astype(int)
            .sum()
        )

    initial_qty = current_stock - total_imported + total_exported
    return initial_qty > 0


def get_product_warehouse_view(ma_sp, df_products, df_imports, df_exports, manual_assignments, days_threshold=60):
    """
    Trả về DataFrame các dòng theo từng Khu / Lô còn hàng cho sản phẩm:
    Khu, Lô, Số lượng, Ngày nhập hàng, Hạn sử dụng.
    Các dòng được sắp xếp theo HSD gần nhất trước.
    """
    lots_df = calculate_product_lots_for_export(ma_sp, df_products, df_imports, df_exports)
    if lots_df.empty:
        return pd.DataFrame(columns=["Khu", "Lô", "Số lượng", "Ngày nhập hàng", "Hạn sử dụng"])

    today = date.today()

    # Cờ lô cận hạn
    expiring_flags = []
    for _, row in lots_df.iterrows():
        hsd_str = str(row.get("Hạn sử dụng", "")).strip()
        is_expiring = False
        if hsd_str and hsd_str.lower() != "nan":
            try:
                hsd_date = datetime.strptime(hsd_str, "%d/%m/%Y").date()
                days_until_expiry = (hsd_date - today).days
                if days_until_expiry < days_threshold:
                    is_expiring = True
            except Exception:
                pass
        expiring_flags.append(is_expiring)
    lots_df = lots_df.copy()
    lots_df["__is_expiring"] = expiring_flags

    manual_df = None
    if manual_assignments is not None and not manual_assignments.empty:
        manual_df = manual_assignments.copy()
        manual_df["Mã sản phẩm"] = manual_df["Mã sản phẩm"].astype(str)
        manual_df["Lô"] = pd.to_numeric(manual_df["Lô"], errors="coerce").fillna(0).astype(int)
        if "Số lượng" not in manual_df.columns:
            manual_df["Số lượng"] = pd.NA
        manual_df["Số lượng"] = (
            pd.to_numeric(manual_df["Số lượng"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        manual_df = manual_df[manual_df["Số lượng"] > 0]

        # Lưu ý: warehouse_areas.csv lưu lô thật (1, 2, 3...) không có lô ảo INIT
        # lots_df từ calculate_product_lots_for_export có thể có lô ảo INIT (lô 1)
        # Vậy khi so sánh: nếu có lô ảo INIT, lô thật trong lots_df là 2, 3, 4...
        # nhưng trong warehouse_areas.csv là 1, 2, 3...
        # Cần map: lô trong lots_df (có lô ảo) -> lô trong warehouse_areas.csv = lô - 1 (nếu lô > 1)

    # Kiểm tra xem có lô ảo INIT không
    has_init = has_initial_lot(ma_sp, df_products, df_imports, df_exports)

    rows = []
    for _, base_row in lots_df.iterrows():
        lo = int(base_row.get("Lô", 0))
        base_qty = int(base_row.get("Số lượng", 0))  # Số lượng từ calculate_product_lots_for_export (đã đọc từ warehouse_areas.csv)
        if lo <= 0 or base_qty <= 0:
            continue

        is_exp = bool(base_row.get("__is_expiring", False))
        hsd_val = base_row.get("Hạn sử dụng", "")
        ngay_nhap_val = base_row.get("Ngày nhập hàng", "")

        # Map lô từ lots_df (có thể có lô ảo) sang lô trong warehouse_areas.csv (chỉ có lô thật)
        # Nếu có lô ảo INIT: lô 1 trong lots_df = lô ảo -> không có trong warehouse_areas.csv
        #                     lô 2 trong lots_df = lô thật đầu tiên -> map với lô 1 trong warehouse_areas.csv
        #                     lô 3 trong lots_df = lô thật thứ hai -> map với lô 2 trong warehouse_areas.csv
        # Nếu không có lô ảo: lô trong lots_df = lô trong warehouse_areas.csv
        warehouse_lot = lo
        if has_init:
            if lo == 1:
                # Lô 1 là lô ảo INIT -> không có trong warehouse_areas.csv
                warehouse_lot = None
            else:
                # Lô thật: lô trong lots_df - 1 = lô trong warehouse_areas.csv
                warehouse_lot = lo - 1

        overrides = None
        if manual_df is not None and warehouse_lot is not None:
            overrides = manual_df[
                (manual_df["Mã sản phẩm"].astype(str) == str(ma_sp))
                & (manual_df["Lô"] == warehouse_lot)
            ]

        if overrides is None or overrides.empty:
            # Chưa có phân bổ tay -> toàn bộ lô nằm ở Khu A hoặc Khu E
            # Dùng base_qty (đã đọc từ warehouse_areas.csv hoặc tính từ tồn kho)
            default_wh = "Khu E" if is_exp else "Khu A"
            if default_wh not in WAREHOUSE_AREAS:
                default_wh = list(WAREHOUSE_AREAS.keys())[0]
            rows.append(
                {
                    "Khu": default_wh,
                    "Lô": lo,
                    "Số lượng": base_qty,  # Dùng số lượng từ calculate_product_lots_for_export
                    "Ngày nhập hàng": ngay_nhap_val,
                    "Hạn sử dụng": hsd_val,
                }
            )
        else:
            # Có phân bổ trong warehouse_areas.csv -> dùng trực tiếp số lượng từ đó
            # Không cần so sánh với base_qty vì base_qty đã được tính từ warehouse_areas.csv
            for _, ov in overrides.iterrows():
                wh = str(ov.get("Khu", "")).strip()
                if wh not in WAREHOUSE_AREAS:
                    continue
                qty_cfg = int(ov.get("Số lượng", 0))
                if qty_cfg <= 0:
                    continue
                # Dùng trực tiếp số lượng từ warehouse_areas.csv
                rows.append(
                    {
                        "Khu": wh,
                        "Lô": lo,
                        "Số lượng": qty_cfg,  # Dùng trực tiếp từ warehouse_areas.csv
                        "Ngày nhập hàng": ngay_nhap_val,
                        "Hạn sử dụng": hsd_val,
                    }
                )

    df_result = pd.DataFrame(rows)
    if df_result.empty:
        return df_result

    # Sắp xếp theo HSD gần nhất, sau đó theo ngày nhập
    df_result["_hsd_dt"] = pd.to_datetime(
        df_result["Hạn sử dụng"], errors="coerce", dayfirst=True
    )
    df_result["_import_dt"] = pd.to_datetime(
        df_result["Ngày nhập hàng"], errors="coerce", dayfirst=True
    )
    df_result = df_result.sort_values(
        by=["_hsd_dt", "_import_dt", "Khu"], ascending=[True, True, True]
    )
    df_result = df_result.drop(columns=["_hsd_dt", "_import_dt"])
    return df_result


# ======================
# LOAD DỮ LIỆU
# ======================
df_sp = load_products()
df_px = load_exports()

st.title("📤 Phiếu Xuất Kho")

# ======================
# THANH NÚT CHỨC NĂNG
# ======================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Thêm phiếu xuất", type="primary", use_container_width=True, key="add_export_btn"):
        st.session_state["show_form_px"] = True

with col2:
    st.download_button(
        "📥 Xuất Excel phiếu xuất",
        df_px.to_csv(index=False).encode("utf-8-sig"),
        file_name="phieu_xuat.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    st.button("🔄 Làm mới", on_click=lambda: st.rerun(), use_container_width=True)


# ======================
# BẢNG DANH SÁCH PHIẾU XUẤT
# ======================
st.subheader("📋 Danh sách phiếu xuất")
if len(df_px) == 0:
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
                    Chưa có phiếu xuất nào. Hãy thêm phiếu xuất mới hoặc import từ file Excel/CSV.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Ô tìm kiếm theo ngày xuất
    col_search, _ = st.columns([2, 4])
    with col_search:
        search_date = st.date_input(
            "🔎 Tìm kiếm phiếu xuất theo ngày",
            value=None,
            format="DD/MM/YYYY",
            key="export_search_date",
        )

    df_filtered = df_px.copy()
    if search_date:
        date_str = search_date.strftime("%d/%m/%Y")
        df_filtered = df_filtered[
            df_filtered["Ngày xuất"].astype(str).str.contains(date_str)
        ]

    if len(df_filtered) == 0:
        st.info("⚠ Không tìm thấy phiếu xuất nào cho ngày đã chọn.")
    else:
        # Tạo bảng tổng hợp theo Mã phiếu (1 phiếu có thể có nhiều sản phẩm)
        df_summary = (
            df_filtered[["Mã phiếu", "Nhân viên xuất", "Ngày xuất"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Thêm cột STT
        df_summary.insert(0, "STT", range(1, len(df_summary) + 1))

        # Cấu hình AgGrid cho danh sách phiếu
        gb = GridOptionsBuilder.from_dataframe(df_summary)
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
        gb.configure_column("Nhân viên xuất", header_name="Nhân viên xuất")
        gb.configure_column("Ngày xuất", header_name="Ngày xuất")

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
        if isinstance(selected, pd.DataFrame):
            selected = selected.to_dict(orient="records")
        elif selected is None:
            selected = []

        # Hiển thị chi tiết phiếu + danh sách sản phẩm trong phiếu được chọn
        if len(selected) > 0:
            selected_receipt = selected[0]
            ma_phieu_chon = str(selected_receipt["Mã phiếu"])
            nv_xuat_chon = selected_receipt["Nhân viên xuất"]
            ngay_xuat_chon = selected_receipt["Ngày xuất"]

            # Tiêu đề "Thông tin phiếu xuất" căn giữa
            st.markdown(
                """
                <div style="text-align: center; margin-top: 8px; margin-bottom: 16px;">
                    <h4 style="margin: 0; font-weight: 700;">📦 Thông tin phiếu xuất</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 3 ô thông tin: Mã phiếu xuất, Nhân viên xuất, Ngày xuất
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
                        <div style="font-size: 12px; color: #6b7280;">Mã phiếu xuất</div>
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
                        <div style="font-size: 12px; color: #6b7280;">Nhân viên xuất</div>
                        <div style="font-weight: 600; color: #111827; margin-top: 2px;">{nv_xuat_chon}</div>
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
                        <div style="font-size: 12px; color: #6b7280;">Ngày xuất</div>
                        <div style="font-weight: 600; color: #111827; margin-top: 2px;">{ngay_xuat_chon}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Tạo khoảng cách nhẹ giữa khối thông tin phiếu và bảng chi tiết phía dưới
            st.markdown(
                "<div style='height: 12px;'></div>",
                unsafe_allow_html=True,
            )

            # Lấy chi tiết sản phẩm theo mã phiếu.
            # Lưu ý: bảng phiếu xuất KHÔNG có cột "Hạn sử dụng", nên chỉ hiển thị
            #       các thông tin hiện có: Mã SP, Tên SP, Số lượng xuất, Tồn sau xuất, Ghi chú.
            df_ct = df_px[df_px["Mã phiếu"] == ma_phieu_chon][
                ["Mã sản phẩm", "Tên sản phẩm", "Số lượng xuất", "Tồn sau xuất", "Ghi chú"]
            ].reset_index(drop=True)

            if len(df_ct) > 0:
                df_ct.insert(0, "STT", range(1, len(df_ct) + 1))

                gb_ct = GridOptionsBuilder.from_dataframe(df_ct)
                center_style_ct = {"textAlign": "center"}
                gb_ct.configure_default_column(cellStyle=center_style_ct)
                gb_ct.configure_selection(
                    selection_mode="single",
                    use_checkbox=False,
                    rowMultiSelectWithClick=False,
                )
                gb_ct.configure_grid_options(domLayout="normal")
                gb_ct.configure_column("STT", header_name="STT", width=80)
                gb_ct.configure_column("Mã sản phẩm", header_name="Mã sản phẩm")
                gb_ct.configure_column("Tên sản phẩm", header_name="Tên sản phẩm")
                gb_ct.configure_column("Số lượng xuất", header_name="Số lượng xuất")
                gb_ct.configure_column("Tồn sau xuất", header_name="Tồn sau xuất")
                gb_ct.configure_column("Ghi chú", header_name="Ghi chú")

                # Chiều cao động theo số dòng
                row_height = 36
                header_height = 40
                base_padding = 20
                n_rows = len(df_ct)
                dynamic_height = header_height + n_rows * row_height + base_padding
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



# ======================
# IMPORT PHIẾU XUẤT TỪ EXCEL – TỰ TRỪ TỒN KHO
# ======================
st.subheader("📥 Nhập phiếu xuất từ Excel / CSV")

uploaded_file = st.file_uploader(
    "Chọn file Excel / CSV",
    type=["xlsx", "xls", "csv"],
    help="Hỗ trợ định dạng: XLSX, XLS, CSV. Giới hạn 200MB mỗi file."
)

if uploaded_file:
    file_bytes = uploaded_file.read()
    df_excel = None

    # 1. thử đọc bằng openpyxl
    try:
        df_excel = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception:
        df_excel = None

    # 2. thử đọc bằng xlrd
    if df_excel is None:
        try:
            df_excel = pd.read_excel(io.BytesIO(file_bytes), engine="xlrd")
        except Exception:
            df_excel = None

    # 3. thử đọc bằng CSV
    if df_excel is None:
        try:
            df_excel = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            st.error(f"❌ Không thể đọc file! Lỗi: {str(e)}")
            st.stop()

    required_cols = [
        "Mã phiếu", "Nhân viên xuất", "Mã sản phẩm",
        "Tên sản phẩm", "Số lượng xuất", "Ngày xuất", "Ghi chú"
    ]

    df_excel.columns = [col.strip() for col in df_excel.columns]

    missing = [c for c in required_cols if c not in df_excel.columns]
    if missing:
        st.error(f"⚠ Thiếu cột: {missing}")
    else:
        st.success("✔ File hợp lệ")

        if st.button("🚀 Import phiếu xuất"):
            errors = []
            warnings = []
            
            # Load warehouse assignments để cập nhật
            assign_df = load_warehouse_assignments()
            if assign_df.empty:
                assign_df = pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
            
            # Chuẩn hóa dữ liệu warehouse assignments
            assign_df["Mã sản phẩm"] = assign_df["Mã sản phẩm"].astype(str)
            assign_df["Lô"] = pd.to_numeric(assign_df["Lô"], errors="coerce").fillna(0).astype(int)
            assign_df["Số lượng"] = pd.to_numeric(assign_df["Số lượng"], errors="coerce").fillna(0).astype(int)
            
            # Load imports để tính FEFO (dùng df_px hiện tại, chưa có dữ liệu mới)
            df_imports_all = load_imports()
            manual_assign_df = assign_df.copy()  # Dùng bản sao để tính toán
            
            for idx_excel, row in df_excel.iterrows():
                try:
                    ma_sp = str(row["Mã sản phẩm"]).strip()
                    sl_xuat = int(row["Số lượng xuất"])

                    if ma_sp in df_sp["Mã sản phẩm"].astype(str).values:
                        idx = df_sp[df_sp["Mã sản phẩm"] == ma_sp].index[0]
                        ton_cu = int(df_sp.at[idx, "Số lượng tồn kho"])
                        
                        if sl_xuat > ton_cu:
                            warnings.append(f"Dòng {idx_excel + 2}: Số lượng xuất ({sl_xuat}) > tồn kho ({ton_cu}) cho mã {ma_sp}")
                            ton_moi = 0
                            sl_xuat_actual = ton_cu  # Chỉ xuất số lượng có sẵn
                        else:
                            ton_moi = ton_cu - sl_xuat
                            sl_xuat_actual = sl_xuat
                        
                        df_sp.at[idx, "Số lượng tồn kho"] = ton_moi
                        
                        # Cập nhật warehouse_areas.csv theo FEFO
                        # Lấy thông tin lô/khu hiện tại của sản phẩm
                        warehouse_view = get_product_warehouse_view(
                            ma_sp, df_sp, df_imports_all, df_px, manual_assign_df
                        )
                        
                        # Kiểm tra xem có lô ảo INIT không
                        has_init = has_initial_lot(ma_sp, df_sp, df_imports_all, df_px)
                        
                        if not warehouse_view.empty and sl_xuat_actual > 0:
                            qty_remaining = sl_xuat_actual
                            # Xuất theo FEFO (đã được sắp xếp trong warehouse_view)
                            for _, wh_row in warehouse_view.iterrows():
                                if qty_remaining <= 0:
                                    break
                                
                                khu_xuat = str(wh_row["Khu"])
                                lo_xuat_lots_df = int(wh_row["Lô"])  # Lô từ lots_df (có thể có lô ảo)
                                available_qty = int(wh_row["Số lượng"])
                                
                                if available_qty <= 0:
                                    continue
                                
                                qty_to_export = min(qty_remaining, available_qty)
                                
                                # Map lô từ lots_df sang warehouse_areas.csv
                                if has_init:
                                    if lo_xuat_lots_df == 1:
                                        # Lô 1 là lô ảo INIT -> không có trong warehouse_areas.csv, bỏ qua
                                        qty_remaining -= qty_to_export
                                        continue
                                    else:
                                        # Lô thật: lô trong lots_df - 1 = lô trong warehouse_areas.csv
                                        lo_xuat_warehouse = lo_xuat_lots_df - 1
                                else:
                                    # Không có lô ảo: lô trong lots_df = lô trong warehouse_areas.csv
                                    lo_xuat_warehouse = lo_xuat_lots_df
                                
                                # Tìm dòng tương ứng trong warehouse_areas.csv
                                mask = (
                                    (assign_df["Mã sản phẩm"] == str(ma_sp))
                                    & (assign_df["Lô"] == lo_xuat_warehouse)
                                    & (assign_df["Khu"].astype(str) == khu_xuat)
                                )
                                
                                if mask.any():
                                    # Trừ số lượng đã xuất
                                    current_qty = int(assign_df.loc[mask, "Số lượng"].iloc[0])
                                    new_qty = max(0, current_qty - qty_to_export)
                                    
                                    if new_qty > 0:
                                        # Cập nhật số lượng còn lại
                                        assign_df.loc[mask, "Số lượng"] = new_qty
                                    else:
                                        # Xóa dòng nếu số lượng = 0 (lô đã xuất hết)
                                        assign_df = assign_df[~mask].reset_index(drop=True)
                                    
                                    # Cập nhật manual_assign_df để tính toán đúng cho các dòng tiếp theo
                                    mask_manual = (
                                        (manual_assign_df["Mã sản phẩm"] == str(ma_sp))
                                        & (manual_assign_df["Lô"] == lo_xuat_warehouse)
                                        & (manual_assign_df["Khu"].astype(str) == khu_xuat)
                                    )
                                    if mask_manual.any():
                                        if new_qty > 0:
                                            manual_assign_df.loc[mask_manual, "Số lượng"] = new_qty
                                        else:
                                            manual_assign_df = manual_assign_df[~mask_manual].reset_index(drop=True)
                                
                                qty_remaining -= qty_to_export
                    else:
                        warnings.append(f"Dòng {idx_excel + 2}: Mã sản phẩm {ma_sp} không tồn tại")
                except Exception as e:
                    errors.append(f"Dòng {idx_excel + 2}: {str(e)}")

            if errors:
                st.error("❌ Có lỗi xảy ra:\n" + "\n".join(errors))
            if warnings:
                st.warning("⚠ Cảnh báo:\n" + "\n".join(warnings))

            # thêm phiếu vào bảng
            df_px = pd.concat([df_px, df_excel], ignore_index=True)

            save_products(df_sp)
            save_exports(df_px)
            
            # Lưu warehouse assignments (đã cập nhật/xóa các lô xuất hết)
            # Chỉ giữ các dòng có số lượng > 0
            assign_df = assign_df[assign_df["Số lượng"] > 0].reset_index(drop=True)
            if not assign_df.empty:
                save_warehouse_assignments(assign_df)
            else:
                # Nếu không còn dòng nào, tạo file rỗng
                empty_df = pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
                save_warehouse_assignments(empty_df)

            if not errors:
                st.success("✔ Import phiếu xuất thành công!")
                st.rerun()


# ======================
# FORM TẠO PHIẾU XUẤT – TRỪ TỒN KHO + UPDATE UI NGAY
# ======================
if st.session_state.get("show_form_px"):
    # Khởi tạo danh sách sản phẩm nếu chưa có
    if "export_products_list" not in st.session_state:
        st.session_state["export_products_list"] = []

    # Xử lý xóa sản phẩm (phải làm trước form)
    if "delete_export_product_idx" in st.session_state:
        idx_to_delete = st.session_state["delete_export_product_idx"]
        if 0 <= idx_to_delete < len(st.session_state["export_products_list"]):
            st.session_state["export_products_list"].pop(idx_to_delete)
        del st.session_state["delete_export_product_idx"]
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
            THÊM PHIẾU XUẤT MỚI
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hiển thị danh sách sản phẩm đã thêm (ngoài form)
    if len(st.session_state["export_products_list"]) > 0:
        st.markdown("#### 📋 Danh sách sản phẩm đã thêm:")
        
        for idx, product in enumerate(st.session_state["export_products_list"]):
            col_info, col_del = st.columns([5, 1])
            with col_info:
                ton_sau = product["ton_cu"] - product["so_luong"]
                st.markdown(
                    f"""
                    <div style="
                        background-color: #fef2f2;
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 8px;
                        border-left: 4px solid #dc2626;
                    ">
                        <strong>{product['ma_sp']}</strong> - {product['ten_sp']}<br>
                        Số lượng xuất: {product['so_luong']} | 
                        Tồn trước: {product['ton_cu']} → Tồn sau: {ton_sau} | 
                        Ghi chú: {product['ghi_chu'] if product['ghi_chu'] else 'Không có'}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_del:
                if st.button("🗑️", key=f"export_del_{idx}", use_container_width=True):
                    st.session_state["delete_export_product_idx"] = idx
                    st.rerun()
        
        st.markdown("---")

    # Thông tin phiếu xuất (ngoài form để UI phản hồi ngay)
    colA, colB = st.columns(2)
    with colA:
        ma_phieu = st.text_input(
            "Mã phiếu xuất (VD: PX001)", key="export_ma_phieu"
        ).strip()
        nv_xuat = st.text_input("Nhân viên xuất", key="export_nv_xuat")

    with colB:
        ngay_xuat = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.write(f"📅 Ngày xuất: **{ngay_xuat}**")

    st.markdown("### Thêm sản phẩm vào phiếu")

    # Tạo danh sách mã sản phẩm cho selectbox
    if len(df_sp) > 0:
        ma_sp_list = ["-- Chọn mã sản phẩm --"] + df_sp["Mã sản phẩm"].astype(str).tolist()
    else:
        ma_sp_list = ["-- Chưa có sản phẩm --"]

    # Nếu vừa thêm xong một sản phẩm, reset lựa chọn & các ô nhập
    reset_info = st.session_state.pop("export_reset_form", None)
    if reset_info is not None:
        # Đưa selectbox về trạng thái mặc định trước khi hiển thị widget
        if ma_sp_list:
            st.session_state["export_select_ma_sp"] = ma_sp_list[0]
        # Xoá ghi chú
        st.session_state["export_input_ghi_chu"] = ""
        # Xoá các ô nhập số lượng theo khu/lô của sản phẩm trước đó
        for key in reset_info.get("warehouse_keys", []):
            if key in st.session_state:
                del st.session_state[key]

    col1, col2 = st.columns([3, 3])
    with col1:
        selected_ma_sp = st.selectbox("Mã sản phẩm", ma_sp_list, key="export_select_ma_sp")
    with col2:
        ghi_chu = st.text_input("Ghi chú (tuỳ chọn)", "", key="export_input_ghi_chu")

    warehouse_view = pd.DataFrame()
    ten_sp = ""
    ton_cu = 0

    # Hiển thị thông tin sản phẩm được chọn + tồn theo từng khu
    if (
        selected_ma_sp
        and selected_ma_sp != "-- Chọn mã sản phẩm --"
        and selected_ma_sp != "-- Chưa có sản phẩm --"
    ):
        if selected_ma_sp in df_sp["Mã sản phẩm"].astype(str).values:
            sp_row = df_sp[df_sp["Mã sản phẩm"] == selected_ma_sp].iloc[0]
            ten_sp = sp_row["Tên sản phẩm"]
            ton_cu = int(sp_row["Số lượng tồn kho"])

            # Số lượng đã được chọn trong danh sách phiếu xuất (chưa lưu)
            reserved = 0
            reserved_per_lot = {}
            for p in st.session_state.get("export_products_list", []):
                if str(p.get("ma_sp", "")) != str(selected_ma_sp):
                    continue
                reserved += int(p.get("so_luong", 0) or 0)
                for alloc in p.get("per_lot", []):
                    khu_key = str(alloc.get("khu", ""))
                    lo_key = int(alloc.get("lo", 0) or 0)
                    if not khu_key or lo_key <= 0:
                        continue
                    k = (khu_key, lo_key)
                    reserved_per_lot[k] = reserved_per_lot.get(k, 0) + int(
                        alloc.get("so_luong", 0) or 0
                    )
            con_lai = max(ton_cu - reserved, 0)

            if reserved > 0:
                msg = (
                    f"📌 Tên sản phẩm: {ten_sp} | 📦 Tồn kho hiện tại: {ton_cu} "
                    f"(còn {con_lai} chưa chọn trong phiếu này)"
                )
            else:
                msg = f"📌 Tên sản phẩm: {ten_sp} | 📦 Tồn kho hiện tại: {ton_cu}"
            st.info(msg)
            if con_lai <= 0 and ton_cu > 0:
                st.warning("Sản phẩm này đã được chọn hết số lượng trong phiếu xuất hiện tại.")

            df_imports = load_imports()
            manual_assign = load_warehouse_assignments()
            warehouse_view = get_product_warehouse_view(
                selected_ma_sp, df_sp, df_imports, df_px, manual_assign
            )

            if warehouse_view.empty:
                st.warning("⚠ Sản phẩm này hiện không còn tồn trong bất kỳ khu vực kho nào.")
            else:
                st.markdown("#### 🏢 Khu vực kho đang chứa sản phẩm này")
                total_available = int(
                    pd.to_numeric(warehouse_view["Số lượng"], errors="coerce")
                    .fillna(0)
                    .sum()
                )

                for _, row in warehouse_view.iterrows():
                    khu = str(row["Khu"])
                    lo = int(row["Lô"])
                    base_available = int(row["Số lượng"])
                    used_here = reserved_per_lot.get((khu, lo), 0)
                    available = max(base_available - used_here, 0)
                    hsd = str(row.get("Hạn sử dụng", ""))
                    ngay_nhap_hang = str(row.get("Ngày nhập hàng", ""))

                    st.number_input(
                        f"Số lượng xuất từ {khu} - Lô {lo} (HSD {hsd}, còn {available}, nhập {ngay_nhap_hang})",
                        min_value=0,
                        max_value=available,
                        value=0,
                        step=1,
                        key=f"export_qty_{selected_ma_sp}_{khu}_{lo}",
                    )

                st.caption(
                    "Các khu vực ở trên hiển thị số lượng còn lại theo từng lô, "
                    "được sắp xếp theo **hạn sử dụng tăng dần** (lô cận hạn ở trên cùng). "
                    "Bạn chỉ cần điền số lượng xuất cho từng dòng, hệ thống sẽ tự cộng tổng."
                )

    # Nút thêm sản phẩm vào danh sách
    col_add, _ = st.columns([1, 4])
    with col_add:
        add_product = st.button("➕ Thêm sản phẩm", use_container_width=True, key="btn_export_add_product")

    if add_product:
        if selected_ma_sp == "-- Chọn mã sản phẩm --" or selected_ma_sp == "-- Chưa có sản phẩm --":
            st.error("⚠ Vui lòng chọn mã sản phẩm!")
        elif selected_ma_sp not in df_sp["Mã sản phẩm"].astype(str).values:
            st.error("❌ Mã sản phẩm không tồn tại!")
        else:
            sp_row = df_sp[df_sp["Mã sản phẩm"] == selected_ma_sp].iloc[0]
            ton_cu = int(sp_row["Số lượng tồn kho"])

            # Tính tổng số lượng xuất từ các khu vừa nhập
            df_imports = load_imports()
            manual_assign = load_warehouse_assignments()
            warehouse_view = get_product_warehouse_view(
                selected_ma_sp, df_sp, df_imports, df_px, manual_assign
            )

            if warehouse_view.empty:
                st.error("⚠ Sản phẩm này hiện không còn tồn trong bất kỳ khu vực kho nào!")
            else:
                total_export = 0
                per_lot_exports = []
                for _, row in warehouse_view.iterrows():
                    khu = str(row["Khu"])
                    lo = int(row["Lô"])
                    key = f"export_qty_{selected_ma_sp}_{khu}_{lo}"
                    qty_val = int(st.session_state.get(key, 0) or 0)
                    if qty_val > 0:
                        per_lot_exports.append(
                            {"khu": khu, "lo": lo, "so_luong": qty_val}
                        )
                    total_export += qty_val

                if total_export <= 0:
                    st.error("⚠ Vui lòng nhập số lượng xuất (lớn hơn 0) cho ít nhất một khu vực ở trên!")
                elif total_export > ton_cu:
                    st.error(
                        f"❌ Tổng số lượng xuất ({total_export}) vượt quá tồn kho hiện tại ({ton_cu})!"
                    )
                else:
                    # Nếu sản phẩm đã có trong danh sách thì cộng dồn vào cùng một ô
                    merged = False
                    for item in st.session_state["export_products_list"]:
                        if str(item.get("ma_sp", "")) == str(selected_ma_sp) and str(
                            item.get("ghi_chu", "")
                        ) == str(ghi_chu):
                            item["so_luong"] = int(item.get("so_luong", 0)) + total_export
                            # Cộng dồn chi tiết theo lô
                            existing_per_lot = item.get("per_lot", [])
                            existing_per_lot.extend(per_lot_exports)
                            item["per_lot"] = existing_per_lot
                            merged = True
                            break

                    if not merged:
                        # Ghi nhận một dòng sản phẩm mới
                        st.session_state["export_products_list"].append(
                            {
                                "ma_sp": selected_ma_sp,
                                "ten_sp": sp_row["Tên sản phẩm"],
                                "so_luong": total_export,
                                "ghi_chu": ghi_chu,
                                "ton_cu": ton_cu,
                                "per_lot": per_lot_exports,
                            }
                        )
                    # Đánh dấu cần reset form cho lần nhập tiếp theo
                    st.session_state["export_reset_form"] = {
                        "selected_ma_sp": selected_ma_sp,
                        "warehouse_keys": [
                            f"export_qty_{selected_ma_sp}_{row['Khu']}_{int(row['Lô'])}"
                            for _, row in warehouse_view.iterrows()
                        ],
                    }
                    st.rerun()

    st.markdown("---")
    submitted = st.button("💾 Lưu phiếu xuất", use_container_width=True, key="btn_save_export")

    if submitted:
        if not ma_phieu or not nv_xuat:
            st.error("⚠ Vui lòng nhập đầy đủ Mã phiếu và Nhân viên xuất.")
        elif len(st.session_state["export_products_list"]) == 0:
            st.error("⚠ Vui lòng thêm ít nhất một sản phẩm vào phiếu!")
        else:
            errors = []
            warnings = []
            # Load warehouse assignments để cập nhật
            assign_df = load_warehouse_assignments()
            if assign_df.empty:
                assign_df = pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
            
            # Chuẩn hóa dữ liệu warehouse assignments
            assign_df["Mã sản phẩm"] = assign_df["Mã sản phẩm"].astype(str)
            assign_df["Lô"] = pd.to_numeric(assign_df["Lô"], errors="coerce").fillna(0).astype(int)
            assign_df["Số lượng"] = pd.to_numeric(assign_df["Số lượng"], errors="coerce").fillna(0).astype(int)
            
            # Load imports để sử dụng trong vòng lặp
            df_imports = load_imports()
            
            # Lưu từng sản phẩm vào phiếu và cập nhật tồn kho
            for product in st.session_state["export_products_list"]:
                ma_sp = product["ma_sp"]
                so_luong_xuat = product["so_luong"]
                ten_sp = product["ten_sp"]
                ghi_chu_sp = product["ghi_chu"]
                ton_cu_sp = product["ton_cu"]
                per_lot_exports = product.get("per_lot", [])  # Chi tiết xuất theo từng lô/khu

                try:
                    # Kiểm tra lại tồn kho (có thể đã thay đổi)
                    idx = df_sp[df_sp["Mã sản phẩm"] == ma_sp].index[0]
                    ton_cu_actual = int(df_sp.at[idx, "Số lượng tồn kho"])
                    
                    if so_luong_xuat > ton_cu_actual:
                        warnings.append(
                            f"Sản phẩm {ma_sp}: Số lượng xuất ({so_luong_xuat}) > tồn kho ({ton_cu_actual})"
                        )
                        ton_sau = 0
                    else:
                        ton_sau = ton_cu_actual - so_luong_xuat

                    # Cập nhật tồn kho
                    df_sp.at[idx, "Số lượng tồn kho"] = ton_sau

                    # Thêm phiếu vào bảng
                    new_row = {
                        "Mã phiếu": ma_phieu,
                        "Nhân viên xuất": nv_xuat,
                        "Mã sản phẩm": ma_sp,
                        "Tên sản phẩm": ten_sp,
                        "Số lượng xuất": so_luong_xuat,
                        "Tồn trước xuất": ton_cu_actual,
                        "Tồn sau xuất": ton_sau,
                        "Ngày xuất": ngay_xuat,
                        "Ghi chú": ghi_chu_sp,
                    }
                    df_px = pd.concat([df_px, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Cập nhật warehouse_areas.csv theo từng lô/khu đã xuất
                    # Lưu ý: per_lot_exports chứa lô từ lots_df (có thể có lô ảo INIT)
                    # warehouse_areas.csv chỉ có lô thật (1, 2, 3...)
                    # Cần map: nếu có lô ảo INIT, lô trong per_lot_exports - 1 = lô trong warehouse_areas.csv
                    has_init = has_initial_lot(ma_sp, df_sp, df_imports, df_px)
                    
                    if per_lot_exports:
                        for lot_export in per_lot_exports:
                            khu_xuat = str(lot_export.get("khu", "")).strip()
                            lo_xuat_lots_df = int(lot_export.get("lo", 0) or 0)  # Lô từ lots_df (có thể có lô ảo)
                            qty_xuat = int(lot_export.get("so_luong", 0) or 0)
                            
                            if not khu_xuat or lo_xuat_lots_df <= 0 or qty_xuat <= 0:
                                continue
                            
                            # Map lô từ lots_df sang warehouse_areas.csv
                            if has_init:
                                if lo_xuat_lots_df == 1:
                                    # Lô 1 là lô ảo INIT -> không có trong warehouse_areas.csv, bỏ qua
                                    continue
                                else:
                                    # Lô thật: lô trong lots_df - 1 = lô trong warehouse_areas.csv
                                    lo_xuat_warehouse = lo_xuat_lots_df - 1
                            else:
                                # Không có lô ảo: lô trong lots_df = lô trong warehouse_areas.csv
                                lo_xuat_warehouse = lo_xuat_lots_df
                            
                            # Tìm dòng tương ứng trong warehouse_areas.csv
                            mask = (
                                (assign_df["Mã sản phẩm"] == str(ma_sp))
                                & (assign_df["Lô"] == lo_xuat_warehouse)
                                & (assign_df["Khu"].astype(str) == khu_xuat)
                            )
                            
                            if mask.any():
                                # Trừ số lượng đã xuất
                                current_qty = int(assign_df.loc[mask, "Số lượng"].iloc[0])
                                new_qty = max(0, current_qty - qty_xuat)
                                
                                if new_qty > 0:
                                    # Cập nhật số lượng còn lại
                                    assign_df.loc[mask, "Số lượng"] = new_qty
                                else:
                                    # Xóa dòng nếu số lượng = 0 (lô đã xuất hết)
                                    assign_df = assign_df[~mask].reset_index(drop=True)
                            else:
                                # Nếu không tìm thấy trong warehouse_areas.csv, có thể là lô chưa được gán thủ công
                                # Trong trường hợp này, hệ thống sẽ tự động tính lại khi hiển thị
                                pass
                    
                except Exception as e:
                    errors.append(f"Lỗi khi xử lý sản phẩm {ma_sp}: {str(e)}")

            if errors:
                st.error("❌ Có lỗi xảy ra:\n" + "\n".join(errors))
            else:
                if warnings:
                    st.warning("⚠ Cảnh báo:\n" + "\n".join(warnings))

                # Lưu CSV + clear cache
                save_products(df_sp)
                save_exports(df_px)
                
                # Lưu warehouse assignments (đã cập nhật/xóa các lô xuất hết)
                # Chỉ giữ các dòng có số lượng > 0
                assign_df = assign_df[assign_df["Số lượng"] > 0].reset_index(drop=True)
                if not assign_df.empty:
                    save_warehouse_assignments(assign_df)
                else:
                    # Nếu không còn dòng nào, tạo file rỗng
                    empty_df = pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
                    save_warehouse_assignments(empty_df)

                st.success(
                    f"✔ Đã lưu phiếu xuất {ma_phieu} với {len(st.session_state['export_products_list'])} sản phẩm!"
                )
                # Xóa danh sách sản phẩm và đóng form
                st.session_state["export_products_list"] = []
                st.session_state["show_form_px"] = False
                st.rerun()

