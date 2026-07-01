from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from excel_reader import search_data, get_dashboard

app = FastAPI(
    title="Cane Operation Center",
    version="0.2.1"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# ==========================
# หน้าแรก
# ==========================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    dashboard = get_dashboard()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Cane Operation Center",
            "dashboard": dashboard
        }
    )


# ==========================
# ค้นหาข้อมูล
# ==========================
@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, keyword: str = Form(...)):

    result, search_type = search_data(keyword)

    summary = {}

    if result is not None and not result.empty:

        try:
            area = (
                result["พื้นที่ (ไร่)"]
                .astype(str)
                .str.replace(",", "")
                .astype(float)
                .sum()
            )
        except Exception:
            area = 0

        # ============================
        # สรุปข้อมูลตามประเภทการค้นหา
        # ============================

        if search_type == "machine":

            summary = {
                "machine": result.iloc[0]["ยืนยันรหัสรถตัด"],
                "plots": len(result),
                "area": round(area, 2),
                "quota_count": result["โควตา"].nunique()
            }

        elif search_type == "plot":

            summary = {
                "plot": result.iloc[0]["เลขแปลง"],
                "quota": result.iloc[0]["โควตา"],
                "owner": result.iloc[0]["ชื่อเจ้าของโควตา"],
                "machine": result.iloc[0]["ยืนยันรหัสรถตัด"],
                "area": round(area, 2)
            }

        else:

            summary = {
                "quota": result.iloc[0]["โควตา"],
                "owner": result.iloc[0]["ชื่อเจ้าของโควตา"],
                "zone": result.iloc[0]["เขต"],
                "subzone": result.iloc[0]["เขตย่อย"],
                "machine": result.iloc[0]["ยืนยันรหัสรถตัด"],
                "plots": len(result),
                "area": round(area, 2)
            }

    rows = []

    if result is not None:
        rows = result.to_dict(orient="records")

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "keyword": keyword,
            "summary": summary,
            "rows": rows,
            "search_type": search_type
        }
    )