from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from datetime import datetime
import asyncio
import json
from modules.scanner import MarketScanner

app = FastAPI(
    title="🚀 تریدر حرفه‌ای ارزدیجیتال",
    description="سیستم کامل ترید خودکار با قابلیت‌های پیشرفته",
    version="2.0.0"
)

# نمونه اسکنر
scanner = MarketScanner()

@app.get("/")
async def root():
    return {"message": "خوش آمدید به تریدر حرفه‌ای", "status": "active"}

@app.get("/status")
async def status():
    return {
        "status": "فعال",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "اسکنر ۲۰۰ کوین برتر",
            "شناسایی شت‌کوین‌های انفجاری", 
            "نمودارهای پیشرفته",
            "تحلیل نهنگ‌ها و اخبار",
            "تریدر تمام اتوماتیک"
        ]
    }

# API جدید: اسکنر بازار
@app.get("/api/market/top-coins")
async def get_top_coins():
    """دریافت 200 ارز برتر بازار"""
    coins = await scanner.get_top_200_coins()
    return {
        "count": len(coins),
        "timestamp": datetime.now().isoformat(),
        "coins": coins[:50]  # نمایش 50 ارز اول برای تست
    }

# API جدید: شت‌کوین‌های انفجاری
@app.get("/api/market/explosive-coins")
async def get_explosive_coins():
    """دریافت شت‌کوین‌های انفجاری"""
    coins = await scanner.get_top_200_coins()
    explosive = scanner.detect_explosive_coins(coins)
    return {
        "count": len(explosive),
        "timestamp": datetime.now().isoformat(),
        "explosive_coins": explosive
    }

# WebSocket برای داده‌های زنده
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # ارسال داده‌های زنده بازار
            coins = await scanner.get_top_200_coins()
            explosive = scanner.detect_explosive_coins(coins)
            
            market_data = {
                "type": "market_update",
                "timestamp": datetime.now().isoformat(),
                "total_coins": len(coins),
                "explosive_coins_count": len(explosive),
                "top_gainer": max(coins, key=lambda x: x['change_24h']) if coins else None
            }
            await websocket.send_json(market_data)
            await asyncio.sleep(10)  # هر 10 ثانیه آپدیت
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
