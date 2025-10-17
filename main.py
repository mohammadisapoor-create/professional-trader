from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import json
from datetime import datetime

app = FastAPI(
    title="🚀 تریدر حرفه‌ای ارزدیجیتال",
    description="سیستم کامل ترید خودکار با قابلیت‌های پیشرفته",
    version="1.0.0"
)

# مسیر اصلی - رابط کاربری
@app.get("/")
async def read_root():
    return {"message": "خوش آمدید به تریدر حرفه‌ای", "status": "active"}

# وضعیت سیستم
@app.get("/status")
async def get_status():
    return {
        "status": "فعال",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": [
            "اسکنر ۲۰۰ کوین برتر",
            "شناسایی شت‌کوین‌های انفجاری", 
            "نمودارهای پیشرفته",
            "تحلیل نهنگ‌ها و اخبار",
            "تریدر تمام اتوماتیک"
        ]
    }

# WebSocket برای داده‌های زنده
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # ارسال داده‌های زنده بازار
            market_data = {
                "type": "market_update",
                "timestamp": datetime.now().isoformat(),
                "message": "سیستم در حال راه‌اندازی...",
                "progress": "75%"
            }
            await websocket.send_json(market_data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
