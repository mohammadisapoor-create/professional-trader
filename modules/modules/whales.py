import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import json
import time
import random

class WhaleTracker:
    def __init__(self):
        self.whale_watchlist = [
            'BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'DOGE', 'AVAX', 'MATIC'
        ]
        
    def get_whale_transactions(self, min_value: int = 100000) -> List[Dict]:
        """دریافت تراکنش‌های بزرگ (نهنگ‌ها)"""
        try:
            # شبیه‌سازی داده‌های نهنگ‌ها
            whale_transactions = []
            
            # تولید تراکنش‌های نمونه
            for i in range(15):
                symbol = random.choice(self.whale_watchlist)
                amount = random.uniform(100, 5000)
                usd_value = amount * random.uniform(100, 50000)
                
                if usd_value >= min_value:
                    transaction = {
                        'symbol': symbol,
                        'amount': round(amount, 2),
                        'usd_value': round(usd_value, 2),
                        'from_address': f'{"1" if symbol == "BTC" else "0x"}{"".join(random.choices("abcdef0123456789", k=32))}',
                        'to_address': f'{"3" if symbol == "BTC" else "0x"}{"".join(random.choices("abcdef0123456789", k=32))}',
                        'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                        'type': random.choice(['EXCHANGE_INFLOW', 'EXCHANGE_OUTFLOW', 'WHALE_TRANSFER']),
                        'exchange': random.choice(['Binance', 'Coinbase', 'Kraken', 'FTX', 'KuCoin'])
                    }
                    whale_transactions.append(transaction)
            
            # مرتب‌سازی بر اساس ارزش
            whale_transactions.sort(key=lambda x: x['usd_value'], reverse=True)
            return whale_transactions[:10]  # بازگشت 10 تراکنش برتر
            
        except Exception as e:
            print(f"Error fetching whale transactions: {e}")
            return []

    def analyze_whale_behavior(self, transactions: List[Dict]) -> Dict:
        """تحلیل رفتار نهنگ‌ها"""
        if not transactions:
            return {}
            
        df = pd.DataFrame(transactions)
        
        analysis = {
            'total_whale_activity': len(transactions),
            'total_value_moved': df['usd_value'].sum(),
            'most_active_coin': df['symbol'].mode().iloc[0] if not df.empty else 'N/A',
            'inflow_vs_outflow': {
                'inflow': len(df[df['type'].str.contains('INFLOW')]),
                'outflow': len(df[df['type'].str.contains('OUTFLOW')]),
                'transfers': len(df[df['type'] == 'WHALE_TRANSFER'])
            },
            'top_exchanges': df['exchange'].value_counts().to_dict(),
            'risk_level': self.calculate_risk_level(transactions)
        }
        
        return analysis

    def calculate_risk_level(self, transactions: List[Dict]) -> str:
        """محاسبه سطح ریسک بر اساس فعالیت نهنگ‌ها"""
        if not transactions:
            return "پایین"
            
        total_value = sum(t['usd_value'] for t in transactions)
        outflow_count = len([t for t in transactions if 'OUTFLOW' in t['type']])
        
        if total_value > 50000000 or outflow_count > 5:
            return "بسیار بالا"
        elif total_value > 10000000 or outflow_count > 3:
            return "بالا"
        elif total_value > 1000000:
            return "متوسط"
        else:
            return "پایین"

    def get_whale_sentiment(self) -> Dict:
        """دریافت احساسات بازار از فعالیت نهنگ‌ها"""
        transactions = self.get_whale_transactions()
        analysis = self.analyze_whale_behavior(transactions)
        
        sentiment = {
            'bullish_signals': 0,
            'bearish_signals': 0,
            'neutral_signals': 0,
            'overall_sentiment': 'خنثی'
        }
        
        if analysis:
            inflow_ratio = analysis['inflow_vs_outflow']['inflow'] / max(analysis['total_whale_activity'], 1)
            
            if inflow_ratio > 0.6:
                sentiment.update({
                    'bullish_signals': 3,
                    'overall_sentiment': 'صعودی'
                })
            elif inflow_ratio < 0.4:
                sentiment.update({
                    'bearish_signals': 3,
                    'overall_sentiment': 'نزولی'
                })
            else:
                sentiment.update({
                    'neutral_signals': 3,
                    'overall_sentiment': 'خنثی'
                })
        
        return sentiment

    def get_whale_alerts(self) -> List[Dict]:
        """دریافت هشدارهای فوری فعالیت نهنگ‌ها"""
        transactions = self.get_whale_transactions(min_value=1000000)  # فقط تراکنش‌های بالای 1M
        
        alerts = []
        for transaction in transactions:
            if transaction['usd_value'] > 5000000:  # هشدار برای تراکنش‌های بالای 5M
                alert = {
                    'type': 'WHALE_ALERT',
                    'symbol': transaction['symbol'],
                    'value': transaction['usd_value'],
                    'message': f'🚨 فعالیت نهنگ: {transaction["amount"]} {transaction["symbol"]} (${transaction["usd_value"]:,.0f})',
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'HIGH' if transaction['usd_value'] > 10000000 else 'MEDIUM'
                }
                alerts.append(alert)
        
        return alerts

# نمونه استفاده
whale_tracker = WhaleTracker()
