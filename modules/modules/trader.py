import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import time
from dataclasses import dataclass
import json

@dataclass
class TradeSignal:
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    stop_loss: float
    take_profit: float
    timestamp: str
    reason: str

@dataclass
class Position:
    symbol: str
    side: str
    amount: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    pnl: float
    timestamp: str

class AutoTrader:
    def __init__(self, api_key: str = "", secret: str = ""):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'sandbox': True,  # حالت تست
            'enableRateLimit': True
        })
        
        self.positions = []
        self.trading_enabled = False
        self.max_position_size = 1000  # حداکثر سایز پوزیشن (USDT)
        self.risk_per_trade = 0.02  # 2% ریسک در هر معامله
        
    async def analyze_market(self, symbol: str) -> TradeSignal:
        """آنالیز بازار و تولید سیگنال معاملاتی"""
        try:
            # دریافت داده‌های قیمت
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            current_price = df['close'].iloc[-1]
            
            # محاسبه اندیکاتورها
            df['SMA_20'] = df['close'].rolling(20).mean()
            df['SMA_50'] = df['close'].rolling(50).mean()
            df['RSI'] = self.calculate_rsi(df['close'])
            
            # استراتژی Moving Average Crossover
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            # تولید سیگنال
            if sma_20 > sma_50 and rsi < 70:
                action = "BUY"
                confidence = min(0.8, (sma_20 - sma_50) / sma_50 * 100)
                stop_loss = current_price * 0.95
                take_profit = current_price * 1.08
                reason = "روند صعودی - کراس اوور میانگین متحرک"
                
            elif sma_20 < sma_50 and rsi > 30:
                action = "SELL"
                confidence = min(0.8, (sma_50 - sma_20) / sma_20 * 100)
                stop_loss = current_price * 1.05
                take_profit = current_price * 0.92
                reason = "روند نزولی - کراس اوور میانگین متحرک"
                
            else:
                action = "HOLD"
                confidence = 0.5
                stop_loss = 0
                take_profit = 0
                reason = "روند خنثی - عدم سیگنال واضح"
            
            return TradeSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now().isoformat(),
                reason=reason
            )
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return TradeSignal(symbol, "HOLD", 0.1, 0, 0, 0, datetime.now().isoformat(), f"Error: {str(e)}")
    
    def calculate_rsi(self, prices, period=14):
        """محاسبه RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_position_size(self, signal: TradeSignal, balance: float) -> float:
        """محاسبه سایز پوزیشن بر اساس مدیریت ریسک"""
        risk_amount = balance * self.risk_per_trade
        price_diff = abs(signal.price - signal.stop_loss)
        
        if price_diff > 0:
            position_size = risk_amount / price_diff
            return min(position_size, self.max_position_size)
        return 0
    
    async def execute_trade(self, signal: TradeSignal):
        """اجرای معامله بر اساس سیگنال"""
        if not self.trading_enabled or signal.action == "HOLD":
            return {"status": "skipped", "reason": "Trading disabled or HOLD signal"}
        
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            
            if usdt_balance < 10:  # حداقل موجودی
                return {"status": "failed", "reason": "Insufficient balance"}
            
            position_size = self.calculate_position_size(signal, usdt_balance)
            
            if position_size <= 0:
                return {"status": "failed", "reason": "Invalid position size"}
            
            # اجرای سفارش
            if signal.action == "BUY":
                order = self.exchange.create_market_buy_order(
                    symbol=signal.symbol,
                    amount=position_size
                )
            else:  # SELL
                order = self.exchange.create_market_sell_order(
                    symbol=signal.symbol,
                    amount=position_size
                )
            
            # ثبت پوزیشن
            position = Position(
                symbol=signal.symbol,
                side=signal.action,
                amount=position_size,
                entry_price=signal.price,
                current_price=signal.price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                pnl=0,
                timestamp=datetime.now().isoformat()
            )
            self.positions.append(position)
            
            return {
                "status": "success",
                "order_id": order['id'],
                "symbol": signal.symbol,
                "action": signal.action,
                "amount": position_size,
                "price": signal.price,
                "position": position
            }
            
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    async def monitor_positions(self):
        """مانیتورینگ پوزیشن‌های باز"""
        if not self.positions:
            return []
        
        updates = []
        for position in self.positions[:]:  # کپی از لیست
            try:
                # دریافت قیمت فعلی
                ticker = self.exchange.fetch_ticker(position.symbol)
                current_price = ticker['last']
                
                # محاسبه PnL
                if position.side == "BUY":
                    pnl = (current_price - position.entry_price) * position.amount
                else:
                    pnl = (position.entry_price - current_price) * position.amount
                
                position.current_price = current_price
                position.pnl = pnl
                
                # بررسی حد سود/ضرر
                if (position.side == "BUY" and current_price <= position.stop_loss) or \
                   (position.side == "SELL" and current_price >= position.stop_loss):
                    # بستن پوزیشن با ضرر
                    close_order = await self.close_position(position, "STOP_LOSS")
                    updates.append(close_order)
                    self.positions.remove(position)
                    
                elif (position.side == "BUY" and current_price >= position.take_profit) or \
                     (position.side == "SELL" and current_price <= position.take_profit):
                    # بستن پوزیشن با سود
                    close_order = await self.close_position(position, "TAKE_PROFIT")
                    updates.append(close_order)
                    self.positions.remove(position)
                    
            except Exception as e:
                print(f"Error monitoring position {position.symbol}: {e}")
        
        return updates
    
    async def close_position(self, position: Position, reason: str):
        """بستن پوزیشن"""
        try:
            if position.side == "BUY":
                order = self.exchange.create_market_sell_order(
                    symbol=position.symbol,
                    amount=position.amount
                )
            else:
                order = self.exchange.create_market_buy_order(
                    symbol=position.symbol,
                    amount=position.amount
                )
            
            return {
                "status": "closed",
                "symbol": position.symbol,
                "side": position.side,
                "reason": reason,
                "pnl": position.pnl,
                "order_id": order['id'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "close_failed",
                "symbol": position.symbol,
                "reason": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_trading_stats(self) -> Dict:
        """دریافت آمار معاملاتی"""
        total_trades = len(self.positions)
        total_pnl = sum(pos.pnl for pos in self.positions)
        winning_trades = len([pos for pos in self.positions if pos.pnl > 0])
        
        return {
            "total_trades": total_trades,
            "active_positions": len(self.positions),
            "total_pnl": total_pnl,
            "win_rate": winning_trades / max(total_trades, 1),
            "trading_enabled": self.trading_enabled,
            "last_update": datetime.now().isoformat()
        }

# نمونه استفاده
auto_trader = AutoTrader()
