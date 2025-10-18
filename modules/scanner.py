import ccxt
import pandas as pd
from datetime import datetime
from typing import List, Dict
import asyncio

class MarketScanner:
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'kucoin': ccxt.kucoin(),
        }
        
    async def get_top_200_coins(self) -> List[Dict]:
        """دریافت 200 ارز برتر بازار"""
        try:
            # استفاده از Binance برای داده‌های واقعی
            exchange = self.exchanges['binance']
            markets = exchange.fetch_markets()
            
            # فیلتر ارزهای USDT
            usdt_pairs = [m for m in markets if m['quote'] == 'USDT' and m['active']]
            
            # دریافت قیمت‌های لحظه‌ای
            tickers = exchange.fetch_tickers([m['symbol'] for m in usdt_pairs[:200]])
            
            coins_data = []
            for symbol, ticker in list(tickers.items())[:200]:
                coin_data = {
                    'symbol': symbol,
                    'price': ticker['last'],
                    'change_24h': ticker['percentage'],
                    'volume': ticker['baseVolume'],
                    'high_24h': ticker['high'],
                    'low_24h': ticker['low'],
                    'timestamp': datetime.now().isoformat()
                }
                coins_data.append(coin_data)
            
            # مرتب‌سازی بر اساس حجم معاملات
            coins_data.sort(key=lambda x: x['volume'], reverse=True)
            return coins_data[:200]
            
        except Exception as e:
            print(f"Error in market scan: {e}")
            return []

    def detect_explosive_coins(self, coins_data: List[Dict]) -> List[Dict]:
        """شناسایی شت‌کوین‌های انفجاری"""
        explosive_coins = []
        
        for coin in coins_data:
            # معیارهای شناسایی شت‌کوین انفجاری
            if (coin['change_24h'] > 20 and  # رشد بیش از 20%
                coin['price'] < 1.0 and      # قیمت زیر 1 دلار
                coin['volume'] > 100000):    # حجم معاملات بالا
                
                explosive_coins.append({
                    **coin,
                    'potential': self.calculate_potential(coin),
                    'risk_level': self.assess_risk(coin)
                })
        
        return sorted(explosive_coins, key=lambda x: x['change_24h'], reverse=True)

    def calculate_potential(self, coin: Dict) -> str:
        """محاسبه پتانسیل سود"""
        change = coin['change_24h']
        if change > 100:
            return "10x+"
        elif change > 50:
            return "5x-10x" 
        elif change > 20:
            return "2x-5x"
        else:
            return "1x-2x"

    def assess_risk(self, coin: Dict) -> str:
        """ارزیابی ریسک"""
        volume = coin['volume']
        if volume > 1000000:
            return "کم"
        elif volume > 100000:
            return "متوسط"
        else:
            return "بالا"

# نمونه استفاده
scanner = MarketScanner()
