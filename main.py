from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import asyncio
import json
from modules.scanner import MarketScanner
from modules.charts import AdvancedCharts
from modules.whales import WhaleTracker
from modules.trader import AutoTrader

app = FastAPI(
    title="🚀 تریدر حرفه‌ای ارزدیجیتال - نسخه کامل",
    description="سیستم کامل ترید خودکار با تمام ماژول‌های پیشرفته",
    version="3.0.0"
)

# سرویس فایل‌های استاتیک
app.mount("/static", StaticFiles(directory="static"), name="static")

# نمونه‌های ماژول‌ها
scanner = MarketScanner()
charts = AdvancedCharts()
whale_tracker = WhaleTracker()
auto_trader = AutoTrader()

# مسیر اصلی - نمایش دشبورد
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>خطا در بارگذاری دشبورد: {str(e)}</h1>")

@app.get("/status")
async def status():
    return {
        "status": "فعال",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "modules": {
            "scanner": "فعال",
            "charts": "فعال", 
            "whale_tracker": "فعال",
            "auto_trader": "آماده"
        }
    }

# APIهای اسکنر بازار
@app.get("/api/market/top-coins")
async def get_top_coins():
    """دریافت 200 ارز برتر بازار"""
    coins = await scanner.get_top_200_coins()
    return {
        "count": len(coins),
        "timestamp": datetime.now().isoformat(),
        "coins": coins[:50]
    }

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

# APIهای نمودارها
@app.get("/api/charts/candlestick/{symbol}")
async def get_candlestick_chart(symbol: str, timeframe: str = "1h"):
    """دریافت نمودار کندل استیک"""
    chart_data = charts.create_candlestick_chart(symbol, timeframe)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "chart_data": chart_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/charts/technical/{symbol}")
async def get_technical_chart(symbol: str):
    """دریافت نمودار تحلیل تکنیکال"""
    chart_data = charts.create_technical_analysis_chart(symbol)
    return {
        "symbol": symbol,
        "chart_data": chart_data,
        "timestamp": datetime.now().isoformat()
    }

# APIهای تحلیل نهنگ‌ها
@app.get("/api/whales/transactions")
async def get_whale_transactions():
    """دریافت تراکنش‌های نهنگ‌ها"""
    transactions = whale_tracker.get_whale_transactions()
    analysis = whale_tracker.analyze_whale_behavior(transactions)
    return {
        "transactions": transactions,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/whales/sentiment")
async def get_whale_sentiment():
    """دریافت احساسات بازار از نهنگ‌ها"""
    sentiment = whale_tracker.get_whale_sentiment()
    return {
        "sentiment": sentiment,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/whales/alerts")
async def get_whale_alerts():
    """دریافت هشدارهای نهنگ‌ها"""
    alerts = whale_tracker.get_whale_alerts()
    return {
        "alerts": alerts,
        "timestamp": datetime.now().isoformat()
    }

# APIهای تریدر اتوماتیک
@app.get("/api/trading/signal/{symbol}")
async def get_trading_signal(symbol: str):
    """دریافت سیگنال معاملاتی"""
    signal = await auto_trader.analyze_market(symbol)
    return {
        "signal": signal,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/trading/stats")
async def get_trading_stats():
    """دریافت آمار معاملاتی"""
    stats = auto_trader.get_trading_stats()
    return stats

@app.post("/api/trading/toggle")
async def toggle_trading():
    """فعال/غیرفعال کردن ترید خودکار"""
    auto_trader.trading_enabled = not auto_trader.trading_enabled
    return {
        "trading_enabled": auto_trader.trading_enabled,
        "timestamp": datetime.now().isoformat()
    }

# WebSocket برای داده‌های زنده
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # ارسال داده‌های زنده از تمام ماژول‌ها
            market_data = {
                "type": "full_market_update",
                "timestamp": datetime.now().isoformat(),
                "whale_alerts": whale_tracker.get_whale_alerts(),
                "trading_stats": auto_trader.get_trading_stats(),
                "market_status": "active"
            }
            await websocket.send_json(market_data)
            await asyncio.sleep(10)
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
