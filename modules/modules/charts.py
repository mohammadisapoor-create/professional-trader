import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt

class AdvancedCharts:
    def __init__(self):
        self.exchange = ccxt.binance()
    
    def create_candlestick_chart(self, symbol: str, timeframe: str = '1h', periods: int = 100):
        """ایجاد نمودار کندل استیک پیشرفته"""
        try:
            # دریافت داده‌های تاریخی
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=periods)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # ایجاد نمودار کندل استیک
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=(f'نمودار قیمت {symbol}', 'حجم معاملات'),
                row_width=[0.7, 0.3]
            )
            
            # کندل استیک
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # حجم معاملات
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(0, 128, 255, 0.7)'
                ),
                row=2, col=1
            )
            
            # اضافه کردن میانگین متحرک
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['MA20'],
                    line=dict(color='orange', width=2),
                    name='MA20'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['MA50'],
                    line=dict(color='red', width=2),
                    name='MA50'
                ),
                row=1, col=1
            )
            
            # تنظیمات layout
            fig.update_layout(
                title=f'نمودار پیشرفته {symbol} - {timeframe}',
                xaxis_title='زمان',
                yaxis_title='قیمت (USDT)',
                template='plotly_dark',
                height=600,
                showlegend=True
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
    
    def create_technical_analysis_chart(self, symbol: str):
        """نمودار تحلیل تکنیکال با اندیکاتورهای مختلف"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1d', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # محاسبه اندیکاتورها
            df['RSI'] = self.calculate_rsi(df['close'])
            df['MACD'], df['MACD_signal'] = self.calculate_macd(df['close'])
            
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('قیمت و حجم', 'RSI', 'MACD'),
                row_width=[0.4, 0.3, 0.3]
            )
            
            # نمودار قیمت
            fig.add_trace(
                go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # حجم
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(0, 128, 255, 0.7)'
                ),
                row=1, col=1
            )
            
            # RSI
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['RSI'],
                    line=dict(color='purple', width=2),
                    name='RSI'
                ),
                row=2, col=1
            )
            
            # خطوط RSI
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # MACD
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['MACD'],
                    line=dict(color='blue', width=2),
                    name='MACD'
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['MACD_signal'],
                    line=dict(color='red', width=2),
                    name='Signal'
                ),
                row=3, col=1
            )
            
            fig.update_layout(
                title=f'تحلیل تکنیکال {symbol}',
                height=800,
                template='plotly_dark',
                showlegend=True
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """محاسبه RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """محاسبه MACD"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal

# نمونه استفاده
chart_manager = AdvancedCharts()
