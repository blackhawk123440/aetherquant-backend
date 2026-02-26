from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import asyncio
import os
import polygon   # works with old keys even after rebrand
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

app = FastAPI(title="AetherQuant Backend v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load keys from Railway Variables
POLYGON_KEY = os.getenv("POLYGON_KEY")
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

# Connect to brokers
trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=ALPACA_PAPER)
polygon_client = polygon.RESTClient(POLYGON_KEY)

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "time": datetime.utcnow().isoformat(),
        "mode": "PAPER" if ALPACA_PAPER else "LIVE",
        "backend_version": "2.0"
    }

@app.get("/api/market_data")
async def market_data():
    # Real Polygon data for your 4 charts
    aggs = polygon_client.get_aggs("SPY", 1, "minute", limit=120)
    return {
        "spy": [a.close for a in aggs[-20:]],  # last 20 minutes
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/agent_cycle")
async def agent_cycle():
    print("🚀 Starting Agent Cycle v2...")
    
    # 1. Get real market data
    price = polygon_client.get_last_trade("SPY").price
    
    # 2. Simple but real decision logic (this is where RL will grow later)
    signal = "HOLD"
    if price > 0:  # placeholder for real strategy
        signal = "BUY" if price % 2 == 0 else "SELL"  # demo logic - we upgrade next
    
    # 3. Risk check (Monte Carlo style placeholder)
    risk_ok = True
    
    # 4. Execute if needed (paper mode safe)
    decision_log = f"Price: ${price:.2f} → Signal: {signal} → Risk OK: {risk_ok}"
    print(decision_log)
    
    return {
        "success": True,
        "price": price,
        "signal": signal,
        "thought_stream": decision_log,
        "action": "No trade executed (paper mode)"
    }

@app.post("/api/emergency_stop")
async def emergency_stop():
    try:
        trading_client.close_all_positions(cancel_orders=True)
        return {"success": True, "message": "✅ ALL POSITIONS FLATTENED"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/performance")
async def performance():
    # Real equity from Alpaca
    account = trading_client.get_account()
    return {
        "equity": float(account.equity),
        "pnl_today": float(account.equity) - float(account.last_equity),
        "sharpe": 1.85  # placeholder - we add real calc later
    }

# Auto-run every 5 minutes (true 24/7)
async def autonomous_loop():
    while True:
        await agent_cycle()
        await asyncio.sleep(300)  # 5 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_loop())
    print("✅ AetherQuant Backend v2 started - autonomous loop active")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
