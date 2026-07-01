from pathlib import Path
import pandas as pd

EXCEL_FILE = Path("uploads") / "master.xlsx"


def load_data():
    """อ่านไฟล์ Excel"""

    if not EXCEL_FILE.exists():
        return None

    # ใช้แถวที่ 3 เป็น Header
    df = pd.read_excel(EXCEL_FILE, header=2)

    # ลบคอลัมน์ Unnamed
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    # ลบช่องว่างหัวคอลัมน์
    df.columns = df.columns.str.strip()

    # แทนค่า NaN
    df = df.fillna("")

    return df


def search_data(keyword):

    df = load_data()

    if df is None:
        return pd.DataFrame(), "unknown"

    keyword = str(keyword).strip()

    # แปลงทุกคอลัมน์เป็นข้อความ
    search_df = df.astype(str)

    # -----------------------------
    # ตรวจสอบประเภทการค้นหา
    # -----------------------------

    if search_df["โควตา"].str.fullmatch(keyword, case=False).any():
        search_type = "quota"

    elif search_df["เลขแปลง"].str.fullmatch(keyword, case=False).any():
        search_type = "plot"

    elif search_df["ยืนยันรหัสรถตัด"].str.fullmatch(keyword, case=False).any():
        search_type = "machine"

    else:
        search_type = "owner"

    # -----------------------------
    # ค้นหาข้อมูล
    # -----------------------------

    result = search_df[
        search_df["โควตา"].str.contains(keyword, case=False, na=False)
        | search_df["เลขแปลง"].str.contains(keyword, case=False, na=False)
        | search_df["ชื่อเจ้าของโควตา"].str.contains(keyword, case=False, na=False)
        | search_df["ยืนยันรหัสรถตัด"].str.contains(keyword, case=False, na=False)
    ]

    return df.loc[result.index], search_type


def get_dashboard():

    df = load_data()

    if df is None or df.empty:
        return {
            "machine_count": 0,
            "quota_count": 0,
            "plot_count": 0,
            "total_area": 0
        }

    # จำนวนรถตัด (ไม่นับซ้ำ)
    machine_count = (
        df["ยืนยันรหัสรถตัด"]
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    # จำนวนโควตา (ไม่นับซ้ำ)
    quota_count = (
        df["โควตา"]
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    # จำนวนแปลง
    plot_count = len(df)

    # พื้นที่รวม
    try:
        total_area = (
            df["พื้นที่ (ไร่)"]
            .astype(str)
            .str.replace(",", "")
            .astype(float)
            .sum()
        )
    except Exception:
        total_area = 0

    return {
        "machine_count": machine_count,
        "quota_count": quota_count,
        "plot_count": plot_count,
        "total_area": round(total_area, 2)
    }