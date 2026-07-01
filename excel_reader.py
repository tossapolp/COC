from pathlib import Path
import pandas as pd

EXCEL_FILE = Path("uploads") / "master.xlsx"


def load_data():
    """อ่านไฟล์ Excel"""

    if not EXCEL_FILE.exists():
        return None

    # ใช้แถวที่ 3 เป็น Header
    df = pd.read_excel(EXCEL_FILE, header=2)

    # ลบคอลัมน์ว่าง
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    # ลบช่องว่างหน้าหลังชื่อคอลัมน์
    df.columns = df.columns.str.strip()

    # แทนค่า NaN
    df = df.fillna("")

    return df


def search_data(keyword):

    df = load_data()

    if df is None:
        return pd.DataFrame()

    keyword = str(keyword).strip()

    # แปลงเป็นข้อความทุกคอลัมน์
    search_df = df.astype(str)

    result = search_df[
        search_df["โควตา"].str.contains(keyword, case=False, na=False)
        | search_df["เลขแปลง"].str.contains(keyword, case=False, na=False)
        | search_df["ชื่อเจ้าของโควตา"].str.contains(keyword, case=False, na=False)
        | search_df["ยืนยันรหัสรถตัด"].str.contains(keyword, case=False, na=False)
    ]

    # คืนข้อมูลจาก DataFrame ต้นฉบับ
    return df.loc[result.index]