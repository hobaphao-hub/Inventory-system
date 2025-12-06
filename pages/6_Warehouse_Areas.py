import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, date, timedelta

# Thêm thư mục gốc vào path để import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_login_required, render_main_sidebar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ======================
# CẤU HÌNH TRANG
# ======================
st.set_page_config(
    page_title="Khu Vực Kho",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto",
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
        /* Nền trang */
        [data-testid="stAppViewContainer"] {
            background-color: #eff3f9;
        }

        /* Ẩn header mặc định */
        header[data-testid="stHeader"] {
            height: 0px !important;
            padding: 0px !important;
            background: transparent !important;
        }

        header [data-testid="stToolbar"] {
            display: none !important;
        }

        main .block-container {
            padding-top: 0.2rem !important;
            padding-bottom: 2.5rem !important;
            margin-top: -30px !important;
        }

        main .block-container h1 {
            margin-top: 0.4rem !important;
            margin-bottom: 1.2rem !important;
        }

        /* Button cho khu vực kho */
        button[kind="secondary"] {
            background-color: white !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 10px !important;
            padding: 30px !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #2f5597 !important;
            min-height: 120px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }

        button[kind="secondary"]:hover {
            border-color: #4c78d3 !important;
            box-shadow: 0 4px 8px rgba(76, 120, 211, 0.2) !important;
            transform: translateY(-2px) !important;
        }

        button[kind="primary"] {
            background-color: #f0f4ff !important;
            border: 2px solid #4c78d3 !important;
            border-radius: 10px !important;
            padding: 30px !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #2f5597 !important;
            min-height: 120px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }

        button[kind="primary"]:hover {
            border-color: #4c78d3 !important;
            box-shadow: 0 4px 8px rgba(76, 120, 211, 0.2) !important;
            transform: translateY(-2px) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# ĐỊNH NGHĨA KHU VỰC KHO
# ======================
WAREHOUSE_AREAS = {
    "Khu A": {
        "capacity": 2034,  # Sức chứa tính bằng thùng
    },
    "Khu B": {
        "capacity": 2116,
    },
    "Khu C": {
        "capacity": 492,
    },
    "Khu D": {
        "capacity": 111,
    },
    "Khu E": {
        "capacity": 450,  # Sức chứa tối đa 250-450 thùng
        "is_expiry_area": True,  # Đánh dấu là khu chứa lô cận hạn
    },
}

# ======================
# DATABASE PATHS
# ======================
DB_PATH = "database/sanpham.csv"
IMPORT_DB_PATH = "database/phieu_nhap.csv"
EXPORT_DB_PATH = "database/phieu_xuat.csv"
WAREHOUSE_ASSIGN_DB = "database/warehouse_areas.csv"  # Lưu khu vực kho được gán thủ công

os.makedirs("database", exist_ok=True)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_products():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    return pd.read_csv(DB_PATH)

@st.cache_data
def load_imports():
    if not os.path.exists(IMPORT_DB_PATH):
        return pd.DataFrame()
    return pd.read_csv(IMPORT_DB_PATH)

@st.cache_data
def load_exports():
    if not os.path.exists(EXPORT_DB_PATH):
        return pd.DataFrame()
    return pd.read_csv(EXPORT_DB_PATH)

@st.cache_data
def load_warehouse_assignments():
    """Đọc file gán khu vực kho thủ công (nếu có)."""
    if not os.path.exists(WAREHOUSE_ASSIGN_DB):
        return pd.DataFrame(columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"])
    try:
        df = pd.read_csv(WAREHOUSE_ASSIGN_DB)
        # Đảm bảo luôn có đủ các cột cần thiết
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
    """Lưu lại cấu hình khu vực kho thủ công và clear cache."""
    df.to_csv(WAREHOUSE_ASSIGN_DB, index=False, encoding="utf-8-sig")
    load_warehouse_assignments.clear()
    st.cache_data.clear()

# ======================
# HÀM KIỂM TRA CÓ LÔ ẢO INIT KHÔNG
# ======================
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

# ======================
# HÀM TÍNH LÔ HÀNG CHO SẢN PHẨM
# ======================
def calculate_product_lots(ma_sp, df_products, df_imports, df_exports):
    """
    Tính toán danh sách lô hàng cho một sản phẩm, tương tự logic trong Products.py
    Trả về DataFrame với các cột: Mã sản phẩm, Tên sản phẩm, Lô, Số lượng, Ngày nhập hàng, Hạn sử dụng
    """
    # Lấy thông tin sản phẩm
    product_row = df_products[df_products["Mã sản phẩm"].astype(str) == str(ma_sp)]
    if product_row.empty:
        return pd.DataFrame()

    ten_sp = product_row.iloc[0].get("Tên sản phẩm", "")
    try:
        current_stock = int(product_row.iloc[0].get("Số lượng tồn kho", 0))
    except Exception:
        current_stock = 0

    # Lịch sử nhập hàng (các phiếu nhập thật)
    if "Mã sản phẩm" in df_imports.columns:
        df_product_imports = df_imports[
            df_imports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_product_imports = pd.DataFrame()

    # Lịch sử xuất hàng
    if "Mã sản phẩm" in df_exports.columns:
        df_export_product = df_exports[
            df_exports["Mã sản phẩm"].astype(str) == str(ma_sp)
        ].copy()
    else:
        df_export_product = pd.DataFrame()

    # Tính tổng nhập
    total_imported = 0
    if not df_product_imports.empty and "Số lượng nhập" in df_product_imports.columns:
        total_imported = (
            pd.to_numeric(df_product_imports["Số lượng nhập"], errors="coerce")
            .fillna(0)
            .astype(int)
            .sum()
        )

    # Tính tổng xuất
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

    # Tạo lô 1 ảo từ số lượng ban đầu (nếu có), giống trang Chi tiết sản phẩm
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

    # Ghép lô 1 ảo + các lô nhập thật
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

    # Sắp xếp theo thời gian nhập
    if "Ngày nhập" in df_product_imports.columns:
        df_product_imports["_dt"] = pd.to_datetime(
            df_product_imports["Ngày nhập"], errors="coerce", dayfirst=True
        )
        df_product_imports = df_product_imports.sort_values(by="_dt").drop(
            columns=["_dt"]
        )

    # Tính số lượng còn lại cho từng lô (FEFO)
    lots = df_product_imports.reset_index(drop=True).copy()

    # Parse HSD để ưu tiên lô có HSD gần nhất
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

    # Khởi tạo số lượng theo từng lô
    remaining_by_lot = {}
    exported_by_lot = {}
    for i in range(len(lots)):
        imported_qty = int(lots.get("Số lượng nhập", pd.Series([0] * len(lots)))[i])
        remaining_by_lot[i] = max(imported_qty, 0)
        exported_by_lot[i] = 0

    # Phân bổ các phiếu xuất vào các lô (FEFO)
    if not df_export_product.empty:
        if "Ngày xuất" in df_export_product.columns:
            df_export_product["_dt_xuat"] = pd.to_datetime(
                df_export_product["Ngày xuất"], errors="coerce", dayfirst=True
            )
            df_export_product = df_export_product.sort_values(by="_dt_xuat").drop(
                columns=["_dt_xuat"]
            )

        for _, exp_row in df_export_product.iterrows():
            try:
                qty_to_allocate = int(exp_row.get("Số lượng xuất", 0))
            except Exception:
                qty_to_allocate = 0

            if qty_to_allocate <= 0:
                continue

            for _, lot_row in lots_for_sort.iterrows():
                if qty_to_allocate <= 0:
                    break

                lot_idx = int(lot_row["lot_idx"])
                remain = remaining_by_lot.get(lot_idx, 0)
                if remain <= 0:
                    continue

                take = min(remain, qty_to_allocate)
                remaining_by_lot[lot_idx] = remain - take
                exported_by_lot[lot_idx] = exported_by_lot.get(lot_idx, 0) + take
                qty_to_allocate -= take

    # Tạo danh sách lô với số lượng còn lại
    lot_list = []
    for i in range(len(lots)):
        imported_qty = int(lots.get("Số lượng nhập", pd.Series([0] * len(lots)))[i])
        remaining_qty = remaining_by_lot.get(i, 0)

        if remaining_qty > 0:  # Chỉ lấy lô còn hàng
            # Lô hiển thị: 1, 2, 3, ... theo đúng thứ tự lô ảo + các lần nhập,
            # giống trang Chi tiết sản phẩm (Products).
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

# ======================
# HÀM PHÂN CHIA LÔ HÀNG VÀO CÁC KHU VỰC
# ======================
def distribute_lots_to_warehouses(df_products, df_imports, df_exports, days_threshold=60, manual_assignments=None):
    """
    Phân chia tất cả lô hàng vào các khu vực kho.
    - Đọc trực tiếp từ warehouse_areas.csv để đảm bảo số lô khớp với cách tính trong trang Import
    - Kết hợp với thông tin từ phiếu nhập để lấy HSD và ngày nhập
    - Khu E: chứa các lô cận hạn (HSD < 60 ngày)
    - Khu A, B, C, D: phân chia các lô còn lại
    Trả về dict: {warehouse_name: DataFrame với các lô hàng}
    """
    today = date.today()
    
    # Bước 1: Đọc trực tiếp từ warehouse_areas.csv (nếu có)
    # QUAN TRỌNG: Chỉ hiển thị sản phẩm còn tồn kho > 0
    if manual_assignments is None or manual_assignments.empty:
        # Nếu không có warehouse_areas.csv, tính toán từ đầu (fallback)
        all_lots = []
        for _, prod in df_products.iterrows():
            ma_sp = str(prod.get("Mã sản phẩm", "")).strip()
            if not ma_sp:
                continue
            
            # Kiểm tra tồn kho: chỉ tính lô nếu tồn kho > 0
            try:
                current_stock = int(prod.get("Số lượng tồn kho", 0))
            except Exception:
                current_stock = 0
            
            if current_stock <= 0:
                continue  # Bỏ qua sản phẩm đã hết tồn kho
            
            lots_df = calculate_product_lots(ma_sp, df_products, df_imports, df_exports)
            if not lots_df.empty:
                all_lots.append(lots_df)
        
        if not all_lots:
            return {warehouse: pd.DataFrame() for warehouse in WAREHOUSE_AREAS.keys()}
        
        all_lots_df = pd.concat(all_lots, ignore_index=True)
    else:
        # Đọc từ warehouse_areas.csv và kết hợp với thông tin từ phiếu nhập
        assign_df = manual_assignments.copy()
        assign_df["Mã sản phẩm"] = assign_df["Mã sản phẩm"].astype(str)
        assign_df["Lô"] = pd.to_numeric(assign_df["Lô"], errors="coerce").fillna(0).astype(int)
        assign_df["Số lượng"] = pd.to_numeric(assign_df["Số lượng"], errors="coerce").fillna(0).astype(int)
        assign_df = assign_df[assign_df["Số lượng"] > 0]
        
        # QUAN TRỌNG: Lọc các sản phẩm còn tồn kho > 0
        # Tạo mapping tồn kho từ df_products
        stock_map = {}
        for _, prod in df_products.iterrows():
            ma_sp = str(prod.get("Mã sản phẩm", "")).strip()
            try:
                current_stock = int(prod.get("Số lượng tồn kho", 0))
            except Exception:
                current_stock = 0
            stock_map[ma_sp] = current_stock
        
        # Chỉ giữ các dòng có sản phẩm còn tồn kho > 0
        assign_df = assign_df[
            assign_df["Mã sản phẩm"].map(lambda x: stock_map.get(x, 0) > 0)
        ].reset_index(drop=True)
        
        # Tạo mapping từ (Mã sản phẩm, Lô) -> thông tin từ phiếu nhập
        import_info_map = {}
        if not df_imports.empty and "Mã sản phẩm" in df_imports.columns:
            # Sắp xếp theo ngày nhập và đánh số lô theo thứ tự nhập (không có lô ảo)
            for ma_sp in assign_df["Mã sản phẩm"].unique():
                df_sp_imports = df_imports[
                    df_imports["Mã sản phẩm"].astype(str) == str(ma_sp)
                ].copy()
                
                if not df_sp_imports.empty:
                    # Sắp xếp theo ngày nhập
                    if "Ngày nhập" in df_sp_imports.columns:
                        df_sp_imports["_dt"] = pd.to_datetime(
                            df_sp_imports["Ngày nhập"], errors="coerce", dayfirst=True
                        )
                        df_sp_imports = df_sp_imports.sort_values(by="_dt").reset_index(drop=True)
                    
                    # Đánh số lô theo thứ tự nhập (1, 2, 3, ...) - không có lô ảo
                    for idx, row in df_sp_imports.iterrows():
                        lot_num = idx + 1  # Lô bắt đầu từ 1
                        import_info_map[(str(ma_sp), lot_num)] = {
                            "Tên sản phẩm": str(row.get("Tên sản phẩm", "")),
                            "Hạn sử dụng": str(row.get("Hạn sử dụng", "")),
                            "Ngày nhập hàng": str(row.get("Ngày nhập", "")),
                        }
        
        # Tạo all_lots_df từ warehouse_areas.csv
        # QUAN TRỌNG: Điều chỉnh số lô để khớp với trang chi tiết sản phẩm
        # Nếu có lô ảo INIT, số lô trong warehouse_areas.csv cần +1
        lot_rows = []
        for _, row in assign_df.iterrows():
            ma_sp = str(row["Mã sản phẩm"])
            lo_warehouse = int(row["Lô"])  # Lô trong warehouse_areas.csv (1, 2, 3...)
            khu = str(row["Khu"])
            so_luong = int(row["Số lượng"])
            
            # Kiểm tra xem sản phẩm có lô ảo INIT không
            has_init = has_initial_lot(ma_sp, df_products, df_imports, df_exports)
            
            # Điều chỉnh số lô để khớp với trang chi tiết sản phẩm
            if has_init:
                # Có lô ảo INIT: lô trong warehouse_areas.csv + 1 = lô trong trang Products
                # Ví dụ: warehouse_areas.csv lô 1 -> trang Products lô 2
                lo_display = lo_warehouse + 1
            else:
                # Không có lô ảo INIT: giữ nguyên
                lo_display = lo_warehouse
            
            # Lấy thông tin từ phiếu nhập (dùng lo_warehouse để map đúng)
            info = import_info_map.get((ma_sp, lo_warehouse), {})
            
            # QUAN TRỌNG: Chỉ hiển thị lô nếu có thông tin từ phiếu nhập (có Ngày nhập hàng và Hạn sử dụng)
            # Nếu không có thông tin, có nghĩa là lô này không hợp lệ (đã bị xóa hoặc không tồn tại)
            if not info.get("Ngày nhập hàng", "") and not info.get("Hạn sử dụng", ""):
                # Bỏ qua lô này - không thêm vào lot_rows
                continue
            
            ten_sp = info.get("Tên sản phẩm", "")
            if not ten_sp:
                # Nếu không tìm thấy, lấy từ df_products
                prod_row = df_products[df_products["Mã sản phẩm"].astype(str) == ma_sp]
                if not prod_row.empty:
                    ten_sp = str(prod_row.iloc[0].get("Tên sản phẩm", ""))
            
            lot_rows.append({
                "Mã sản phẩm": ma_sp,
                "Tên sản phẩm": ten_sp,
                "Lô": lo_display,  # Số lô đã điều chỉnh để khớp với trang Products
                "Số lượng": so_luong,
                "Ngày nhập hàng": info.get("Ngày nhập hàng", ""),
                "Hạn sử dụng": info.get("Hạn sử dụng", ""),
                "Khu": khu,  # Lưu tạm khu để phân bổ sau
            })
        
        all_lots_df = pd.DataFrame(lot_rows)
    
    # Bước 2: Xác định lô cận hạn và phân bổ vào các khu vực
    expiring_flags = []
    for _, lot_row in all_lots_df.iterrows():
        hsd_str = str(lot_row.get("Hạn sử dụng", "")).strip()
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
    all_lots_df = all_lots_df.copy()
    all_lots_df["__is_expiring"] = expiring_flags
    
    # Bước 3: Phân bổ vào các khu vực kho
    result = {warehouse: pd.DataFrame() for warehouse in WAREHOUSE_AREAS.keys()}
    
    # Nếu có thông tin từ warehouse_areas.csv (có cột "Khu")
    if "Khu" in all_lots_df.columns:
        # Phân bổ trực tiếp theo khu đã lưu trong warehouse_areas.csv
        for _, row in all_lots_df.iterrows():
            khu = str(row.get("Khu", "")).strip()
            if khu and khu in WAREHOUSE_AREAS:
                row_dict = row.to_dict()
                row_dict.pop("__is_expiring", None)
                row_dict.pop("Khu", None)  # Xóa cột Khu vì đã phân bổ
                result[khu] = pd.concat(
                    [result[khu], pd.DataFrame([row_dict])], ignore_index=True
                )
    else:
        # Nếu không có thông tin khu (fallback), phân bổ theo quy tắc mặc định
        for _, row in all_lots_df.iterrows():
            qty = int(row.get("Số lượng", 0))
            if qty <= 0:
                continue

            is_expiring = bool(row.get("__is_expiring", False))
            target_wh = "Khu E" if is_expiring else "Khu A"
            if target_wh not in WAREHOUSE_AREAS:
                target_wh = list(WAREHOUSE_AREAS.keys())[0]

            row_dict = row.to_dict()
            row_dict.pop("__is_expiring", None)
            result[target_wh] = pd.concat(
                [result[target_wh], pd.DataFrame([row_dict])], ignore_index=True
            )
    
    return result

# ======================
# GIAO DIỆN CHÍNH
# ======================
st.title("🏢 Quản Lý Khu Vực Kho")

# Load dữ liệu
df_products = load_products()
df_imports = load_imports()
df_exports = load_exports()

if df_products.empty:
    st.warning("⚠ Chưa có dữ liệu sản phẩm. Vui lòng thêm sản phẩm trước.")
    st.stop()

# Phân chia lô hàng vào các khu vực (có tính đến cấu hình chuyển khu thủ công)
manual_assign_df = load_warehouse_assignments()

# Tự động dọn dẹp warehouse_areas.csv: xóa các sản phẩm đã hết tồn kho và các lô không hợp lệ
if not manual_assign_df.empty:
    # Tạo mapping tồn kho từ df_products
    stock_map = {}
    for _, prod in df_products.iterrows():
        ma_sp = str(prod.get("Mã sản phẩm", "")).strip()
        try:
            current_stock = int(prod.get("Số lượng tồn kho", 0))
        except Exception:
            current_stock = 0
        stock_map[ma_sp] = current_stock
    
    # Tạo mapping từ (Mã sản phẩm, Lô) -> có tồn tại trong phiếu nhập
    valid_lots = set()
    if df_imports is not None and not df_imports.empty and "Mã sản phẩm" in df_imports.columns:
        for ma_sp in manual_assign_df["Mã sản phẩm"].unique():
            df_sp_imports = df_imports[
                df_imports["Mã sản phẩm"].astype(str) == str(ma_sp)
            ].copy()
            
            if not df_sp_imports.empty:
                # Sắp xếp theo ngày nhập
                if "Ngày nhập" in df_sp_imports.columns:
                    df_sp_imports["_dt"] = pd.to_datetime(
                        df_sp_imports["Ngày nhập"], errors="coerce", dayfirst=True
                    )
                    df_sp_imports = df_sp_imports.sort_values(by="_dt").reset_index(drop=True)
                
                # Đánh số lô theo thứ tự nhập (1, 2, 3, ...)
                for idx, row in df_sp_imports.iterrows():
                    lot_num = idx + 1  # Lô bắt đầu từ 1
                    valid_lots.add((str(ma_sp), lot_num))
    
    # Lọc: chỉ giữ các dòng có sản phẩm còn tồn kho > 0 VÀ lô hợp lệ (có trong phiếu nhập)
    manual_assign_df["Mã sản phẩm"] = manual_assign_df["Mã sản phẩm"].astype(str)
    manual_assign_df["Lô"] = pd.to_numeric(manual_assign_df["Lô"], errors="coerce").fillna(0).astype(int)
    
    def is_valid_row(row):
        ma_sp = str(row["Mã sản phẩm"])
        lo = int(row["Lô"])
        # Kiểm tra tồn kho > 0
        if stock_map.get(ma_sp, 0) <= 0:
            return False
        # Kiểm tra lô có trong phiếu nhập không
        if (ma_sp, lo) not in valid_lots:
            return False
        return True
    
    manual_assign_df_cleaned = manual_assign_df[
        manual_assign_df.apply(is_valid_row, axis=1)
    ].reset_index(drop=True)
    
    # Nếu có thay đổi (đã xóa một số dòng), lưu lại
    if len(manual_assign_df_cleaned) < len(manual_assign_df):
        save_warehouse_assignments(manual_assign_df_cleaned)
        manual_assign_df = manual_assign_df_cleaned
warehouse_lots = distribute_lots_to_warehouses(
    df_products,
    df_imports,
    df_exports,
    days_threshold=60,
    manual_assignments=manual_assign_df,
)

# Khởi tạo session state cho khu vực được chọn
if "selected_warehouse" not in st.session_state:
    st.session_state["selected_warehouse"] = None

# Hiển thị các khu vực kho
st.subheader("📍 Danh sách khu vực kho")

# Tạo 2 cột để hiển thị các khu vực
col1, col2 = st.columns(2)

warehouse_keys = list(WAREHOUSE_AREAS.keys())
for idx, warehouse_name in enumerate(warehouse_keys):
    # Chọn cột để hiển thị
    col = col1 if idx % 2 == 0 else col2
    
    with col:
        # Tạo button với style như card
        is_selected = st.session_state.get("selected_warehouse") == warehouse_name
        
        # Sử dụng button với label là tên khu, style sẽ được CSS xử lý
        if st.button(
            warehouse_name,
            key=f"warehouse_btn_{idx}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            if st.session_state.get("selected_warehouse") == warehouse_name:
                st.session_state["selected_warehouse"] = None
            else:
                st.session_state["selected_warehouse"] = warehouse_name
            st.rerun()

# ======================
# HIỂN THỊ CHI TIẾT KHU VỰC ĐƯỢC CHỌN
# ======================
selected_warehouse = st.session_state.get("selected_warehouse")
if selected_warehouse:
    st.markdown("---")
    st.subheader(f"📋 Chi tiết {selected_warehouse}")

    detail_df = warehouse_lots.get(selected_warehouse, pd.DataFrame())

    if not detail_df.empty:
        # Sắp xếp theo Mã sản phẩm và Lô
        if "Mã sản phẩm" in detail_df.columns and "Lô" in detail_df.columns:
            detail_df = detail_df.sort_values(by=["Mã sản phẩm", "Lô"]).reset_index(drop=True)
        
        # Xóa cột _hsd_dt nếu có (chỉ dùng để sắp xếp nội bộ)
        if "_hsd_dt" in detail_df.columns:
            detail_df = detail_df.drop(columns=["_hsd_dt"])

        # Cấu hình AgGrid
        gb = GridOptionsBuilder.from_dataframe(detail_df)
        gb.configure_default_column(cellStyle={"textAlign": "center"})
        gb.configure_grid_options(domLayout="normal")
        
        gb.configure_column("Mã sản phẩm", header_name="Mã sản phẩm")
        gb.configure_column("Tên sản phẩm", header_name="Tên sản phẩm")
        gb.configure_column("Lô", header_name="Lô")
        gb.configure_column("Số lượng", header_name="Số lượng")
        gb.configure_column("Ngày nhập hàng", header_name="Ngày nhập hàng")
        gb.configure_column("Hạn sử dụng", header_name="Hạn sử dụng")

        grid_options = gb.build()

        # Tính chiều cao động
        row_h = 36
        header_h = 40
        pad_h = 20
        n_rows = len(detail_df)
        dynamic_height = header_h + n_rows * row_h + pad_h
        dynamic_height = max(140, min(dynamic_height, 600))

        AgGrid(
            detail_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=False,
            theme="balham",
            height=dynamic_height,
        )
        
        # Hiển thị thông tin sức chứa
        total_qty = detail_df["Số lượng"].sum() if "Số lượng" in detail_df.columns else 0
        max_capacity = WAREHOUSE_AREAS[selected_warehouse].get("capacity", 0)
        remaining_capacity = max(0, max_capacity - int(total_qty))
        usage_percent = (int(total_qty) / max_capacity * 100) if max_capacity > 0 else 0
        
        # Hiển thị thông tin sức chứa dạng card (4 ô)
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
        with col_info1:
            st.markdown(
                f"""
                <div style="
                    background-color: #f0f9ff;
                    border-left: 4px solid #0ea5e9;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Hiện tại</div>
                    <div style="font-size: 20px; font-weight: 700; color: #0c4a6e;">{int(total_qty):,}</div>
                    <div style="font-size: 11px; color: #6b7280;">thùng</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_info2:
            st.markdown(
                f"""
                <div style="
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Tối đa</div>
                    <div style="font-size: 20px; font-weight: 700; color: #92400e;">{max_capacity:,}</div>
                    <div style="font-size: 11px; color: #6b7280;">thùng</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_info3:
            st.markdown(
                f"""
                <div style="
                    background-color: {'#d1fae5' if remaining_capacity > 0 else '#fee2e2'};
                    border-left: 4px solid {'#059669' if remaining_capacity > 0 else '#dc2626'};
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Còn lại</div>
                    <div style="font-size: 20px; font-weight: 700; color: {'#065f46' if remaining_capacity > 0 else '#991b1b'};">{remaining_capacity:,}</div>
                    <div style="font-size: 11px; color: #6b7280;">thùng</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_info4:
            # Xác định màu sắc dựa trên % sử dụng
            if usage_percent >= 90:
                bg_color = "#fee2e2"
                border_color = "#dc2626"
                text_color = "#991b1b"
            elif usage_percent >= 70:
                bg_color = "#fef3c7"
                border_color = "#f59e0b"
                text_color = "#92400e"
            else:
                bg_color = "#dbeafe"
                border_color = "#3b82f6"
                text_color = "#1e40af"
            
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    border-left: 4px solid {border_color};
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Đã chứa</div>
                    <div style="font-size: 20px; font-weight: 700; color: {text_color};">{usage_percent:.1f}%</div>
                    <div style="font-size: 11px; color: #6b7280;">dung lượng</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ======================
        # CHUYỂN HÀNG SANG KHU KHÁC
        # ======================
        st.markdown("#### 🔁 Chuyển hàng sang khu vực khác")

        if (
            "Mã sản phẩm" in detail_df.columns
            and "Lô" in detail_df.columns
            and "Số lượng" in detail_df.columns
        ):
            # 1) Chọn mã sản phẩm
            ma_sp_options = sorted(detail_df["Mã sản phẩm"].astype(str).unique().tolist())
            col_ma, col_ten = st.columns([2, 3])
            with col_ma:
                selected_ma_sp = st.selectbox(
                    "Chọn mã sản phẩm",
                    options=["-- Chọn mã sản phẩm --"] + ma_sp_options,
                    key=f"move_ma_sp_{selected_warehouse}",
                )

            ten_sp_selected = ""
            if selected_ma_sp and selected_ma_sp != "-- Chọn mã sản phẩm --":
                rows_sp = detail_df[detail_df["Mã sản phẩm"].astype(str) == selected_ma_sp]
                if not rows_sp.empty:
                    ten_sp_selected = str(rows_sp.iloc[0].get("Tên sản phẩm", ""))

            with col_ten:
                st.markdown(
                    f"**Tên sản phẩm:** {ten_sp_selected if ten_sp_selected else '—'}"
                )

            selected_lot = None
            available_qty = 0

            # 2) Chọn lô theo mã sản phẩm
            if selected_ma_sp and selected_ma_sp != "-- Chọn mã sản phẩm --":
                lots_for_sp = detail_df[detail_df["Mã sản phẩm"].astype(str) == selected_ma_sp]
                lot_options = sorted(
                    pd.to_numeric(lots_for_sp["Lô"], errors="coerce").dropna().astype(int).unique().tolist()
                )

                col_lo, col_info = st.columns([2, 3])
                with col_lo:
                    selected_lot = st.selectbox(
                        "Chọn lô",
                        options=lot_options if lot_options else [],
                        key=f"move_lot_{selected_warehouse}",
                    )

                if selected_lot is not None and lot_options:
                    lot_rows = lots_for_sp[
                        pd.to_numeric(lots_for_sp["Lô"], errors="coerce").fillna(0).astype(int)
                        == int(selected_lot)
                    ]
                    if not lot_rows.empty:
                        available_qty = int(
                            pd.to_numeric(lot_rows["Số lượng"], errors="coerce").fillna(0).sum()
                        )

                with col_info:
                    st.info(
                        f"Số lượng hiện tại ở {selected_warehouse}: "
                        f"**{available_qty}**"
                    )

            qty_to_move = 0
            target_warehouse = None

            # 3) Nhập số lượng cần chuyển và khu đích
            if selected_lot is not None and available_qty > 0:
                col_qty, col_target = st.columns(2)
                with col_qty:
                    qty_to_move = st.number_input(
                        "Số lượng cần chuyển",
                        min_value=1,
                        max_value=available_qty,
                        value=1,
                        step=1,
                        key=f"move_qty_{selected_warehouse}",
                    )
                with col_target:
                    other_warehouses = [
                        w for w in WAREHOUSE_AREAS.keys() if w != selected_warehouse
                    ]
                    target_warehouse = st.selectbox(
                        "Chuyển sang khu",
                        options=other_warehouses,
                        key=f"move_target_{selected_warehouse}",
                    )
                    
                    # Hiển thị thông tin sức chứa của khu đích
                    if target_warehouse:
                        assign_df_info = load_warehouse_assignments()
                        target_current_qty_info = 0
                        if not assign_df_info.empty:
                            assign_df_info["Khu"] = assign_df_info["Khu"].astype(str)
                            assign_df_info["Số lượng"] = pd.to_numeric(assign_df_info["Số lượng"], errors="coerce").fillna(0).astype(int)
                            target_current_qty_info = int(assign_df_info[assign_df_info["Khu"] == target_warehouse]["Số lượng"].sum())
                        
                        target_max_capacity_info = WAREHOUSE_AREAS[target_warehouse].get("capacity", 0)
                        target_remaining_info = max(0, target_max_capacity_info - target_current_qty_info)
                        
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #f0f9ff;
                                border-left: 3px solid #0ea5e9;
                                border-radius: 6px;
                                padding: 8px 12px;
                                margin-top: 8px;
                                font-size: 12px;
                            ">
                                <div style="color: #6b7280; margin-bottom: 4px;">
                                    📊 <strong>{target_warehouse}:</strong>
                                </div>
                                <div style="color: #111827;">
                                    Tối đa: <strong>{target_max_capacity_info:,}</strong> thùng | 
                                    Hiện tại: <strong>{target_current_qty_info:,}</strong> thùng | 
                                    Còn lại: <strong style="color: {'#059669' if target_remaining_info > 0 else '#dc2626'};">{target_remaining_info:,}</strong> thùng
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # 4) Bước 1: Xác nhận thông tin (chưa chuyển ngay)
            move_state_key = f"pending_move_{selected_warehouse}"
            if (
                selected_ma_sp
                and selected_ma_sp != "-- Chọn mã sản phẩm --"
                and selected_lot is not None
                and available_qty > 0
                and target_warehouse
                and st.button("✅ Xác nhận", key=f"confirm_move_{selected_warehouse}")
            ):
                # Lưu trạng thái chuyển để hỏi lại lần nữa
                st.session_state[move_state_key] = {
                    "ma_sp": selected_ma_sp,
                    "lot": int(selected_lot),
                    "qty": int(qty_to_move),
                    "source": selected_warehouse,
                    "target": target_warehouse,
                }

            # 5) Bước 2: Hỏi lại người dùng trước khi chuyển
            if move_state_key in st.session_state:
                pending = st.session_state[move_state_key]
                st.warning(
                    f"Bạn có chắc chắn muốn chuyển **{pending['qty']}** thùng của "
                    f"**mã sản phẩm {pending['ma_sp']}**, lô **{pending['lot']}** "
                    f"từ **{pending['source']}** sang **{pending['target']}** không?"
                )
                col_cf1, col_cf2 = st.columns(2)
                with col_cf1:
                    agree = st.button(
                        "👍 Đồng ý chuyển khu vực kho",
                        key=f"do_move_{selected_warehouse}",
                    )
                with col_cf2:
                    cancel = st.button(
                        "✖ Hủy thao tác",
                        key=f"cancel_move_{selected_warehouse}",
                    )

                if cancel and not agree:
                    del st.session_state[move_state_key]
                    st.info("Đã hủy thao tác chuyển khu vực kho.")

                if agree:
                    ma_sp_move = str(pending["ma_sp"]).strip()
                    lo_move = int(pending["lot"])
                    qty_move = int(pending["qty"])
                    target_warehouse = pending["target"]
                    
                    # Cần điều chỉnh số lô từ display (có thể có lô ảo INIT) sang lô thật trong warehouse_areas.csv
                    has_init = has_initial_lot(ma_sp_move, df_products, df_imports, df_exports)
                    if has_init:
                        # Có lô ảo INIT: lô hiển thị - 1 = lô trong warehouse_areas.csv
                        # Ví dụ: hiển thị lô 2 -> warehouse_areas.csv lô 1
                        lo_warehouse = lo_move - 1
                    else:
                        # Không có lô ảo INIT: giữ nguyên
                        lo_warehouse = lo_move
                    
                    if lo_warehouse <= 0:
                        st.error("⚠ Không thể chuyển lô ảo INIT.")
                        st.stop()

                    assign_df = load_warehouse_assignments()
                    if assign_df.empty:
                        assign_df = pd.DataFrame(
                            columns=["Mã sản phẩm", "Lô", "Khu", "Số lượng"]
                        )

                    # Chuẩn hóa dữ liệu
                    assign_df["Mã sản phẩm"] = assign_df["Mã sản phẩm"].astype(str)
                    assign_df["Lô"] = pd.to_numeric(
                        assign_df["Lô"], errors="coerce"
                    ).fillna(0).astype(int)
                    assign_df["Số lượng"] = pd.to_numeric(
                        assign_df["Số lượng"], errors="coerce"
                    ).fillna(0).astype(int)

                    # Tìm dòng ở khu nguồn (cần chuyển từ đây)
                    mask_source = (
                        (assign_df["Mã sản phẩm"] == ma_sp_move)
                        & (assign_df["Lô"] == lo_warehouse)
                        & (assign_df["Khu"].astype(str) == selected_warehouse)
                    )
                    
                    # Tìm dòng ở khu đích (sẽ chuyển đến đây)
                    mask_target = (
                        (assign_df["Mã sản phẩm"] == ma_sp_move)
                        & (assign_df["Lô"] == lo_warehouse)
                        & (assign_df["Khu"].astype(str) == target_warehouse)
                    )

                    source_rows = assign_df[mask_source]
                    
                    if source_rows.empty:
                        st.error(
                            f"⚠ Không tìm thấy lô {lo_move} của sản phẩm {ma_sp_move} ở {selected_warehouse}."
                        )
                        st.stop()
                    
                    # Lấy số lượng hiện có ở khu nguồn
                    source_qty = int(source_rows["Số lượng"].sum())
                    
                    if source_qty < qty_move:
                        st.error(
                            f"⚠ Số lượng ở {selected_warehouse} ({source_qty}) không đủ để chuyển {qty_move}."
                        )
                        st.stop()
                    
                    # Kiểm tra sức chứa tối đa của khu đích
                    # Tính số lượng hiện tại ở khu đích (tổng tất cả các sản phẩm)
                    target_current_qty = assign_df[assign_df["Khu"].astype(str) == target_warehouse]["Số lượng"].sum()
                    target_current_qty = int(target_current_qty) if not pd.isna(target_current_qty) else 0
                    
                    # Tính số lượng sẽ có sau khi chuyển
                    target_qty_after_move = target_current_qty + qty_move
                    
                    # Lấy sức chứa tối đa của khu đích
                    target_max_capacity = WAREHOUSE_AREAS[target_warehouse].get("capacity", 0)
                    
                    # Kiểm tra nếu vượt quá sức chứa tối đa
                    if target_qty_after_move > target_max_capacity:
                        remaining_capacity_target = max(0, target_max_capacity - target_current_qty)
                        st.error(
                            f"⚠️ **Không thể chuyển!** Số lượng sau khi chuyển ({target_qty_after_move:,} thùng) "
                            f"vượt quá sức chứa tối đa của {target_warehouse} ({target_max_capacity:,} thùng).\n\n"
                            f"Hiện tại {target_warehouse} đang chứa: **{target_current_qty:,}** thùng\n"
                            f"Sức chứa còn lại: **{remaining_capacity_target:,}** thùng\n"
                            f"Bạn chỉ có thể chuyển tối đa **{remaining_capacity_target:,}** thùng."
                        )
                        # Xóa trạng thái pending để người dùng có thể nhập lại
                        if move_state_key in st.session_state:
                            del st.session_state[move_state_key]
                        st.stop()
                    
                    # Cập nhật số lượng ở khu nguồn (giảm đi)
                    new_source_qty = source_qty - qty_move
                    
                    # Xóa tất cả các dòng ở khu nguồn (có thể có nhiều dòng trùng lặp)
                    assign_df = assign_df[~mask_source].reset_index(drop=True)
                    
                    # Thêm lại dòng ở khu nguồn nếu còn số lượng > 0
                    if new_source_qty > 0:
                        assign_df = pd.concat(
                            [
                                assign_df,
                                pd.DataFrame([{
                                    "Mã sản phẩm": ma_sp_move,
                                    "Lô": lo_warehouse,
                                    "Khu": selected_warehouse,
                                    "Số lượng": new_source_qty,
                                }])
                            ],
                            ignore_index=True
                        )
                    
                    # Cập nhật số lượng ở khu đích (tăng lên)
                    target_rows = assign_df[mask_target]
                    if not target_rows.empty:
                        # Đã có dòng ở khu đích: cộng thêm số lượng
                        target_qty = int(target_rows["Số lượng"].sum())
                        new_target_qty = target_qty + qty_move
                        
                        # Xóa dòng cũ ở khu đích
                        assign_df = assign_df[~mask_target].reset_index(drop=True)
                        
                        # Thêm lại với số lượng mới
                        assign_df = pd.concat(
                            [
                                assign_df,
                                pd.DataFrame([{
                                    "Mã sản phẩm": ma_sp_move,
                                    "Lô": lo_warehouse,
                                    "Khu": target_warehouse,
                                    "Số lượng": new_target_qty,
                                }])
                            ],
                            ignore_index=True
                        )
                    else:
                        # Chưa có dòng ở khu đích: tạo mới
                        assign_df = pd.concat(
                            [
                                assign_df,
                                pd.DataFrame([{
                                    "Mã sản phẩm": ma_sp_move,
                                    "Lô": lo_warehouse,
                                    "Khu": target_warehouse,
                                    "Số lượng": qty_move,
                                }])
                            ],
                            ignore_index=True
                        )
                    
                    # Đảm bảo chỉ giữ các dòng có số lượng > 0
                    assign_df["Số lượng"] = pd.to_numeric(
                        assign_df["Số lượng"], errors="coerce"
                    ).fillna(0).astype(int)
                    assign_df = assign_df[assign_df["Số lượng"] > 0].reset_index(drop=True)
                    
                    # Gom nhóm để tránh trùng lặp (cùng Mã sản phẩm, Lô, Khu)
                    assign_df = assign_df.groupby(["Mã sản phẩm", "Lô", "Khu"], as_index=False)["Số lượng"].sum()
                    
                    save_warehouse_assignments(assign_df)
                    
                    # Xóa trạng thái pending sau khi chuyển xong
                    if move_state_key in st.session_state:
                        del st.session_state[move_state_key]

                    st.success(
                        f"✔ Đã chuyển {qty_move} thùng của lô {lo_move} "
                        f"sản phẩm {ma_sp_move} từ {selected_warehouse} sang {target_warehouse}."
                    )
                    st.rerun()
    else:
        st.info(f"📭 {selected_warehouse} hiện chưa có lô hàng nào.")
