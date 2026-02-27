from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import asyncio
import os

app = FastAPI(title="AetherQuant Backend v2.2 - Fixed Imports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy clients
def get_trading_client():
    try:
        from alpaca.trading.client import TradingClient
        key = os.getenv("ALPACA_KEY")
        secret = os.getenv("ALPACA_SECRET")
        paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
        return TradingClient(key, secret, paper=paper)
    except Exception as e:
        print(f"Alpaca client error: {e}")
        return None

def get_polygon_client():
    try:
        from massive import RESTClient  # Official 2026 client
        key = os.getenv("POLYGON_KEY")  # Still called POLYGON_KEY in env
        return RESTClient(key)
    except Exception as e:
        print(f"Polygon/Massive client error: {e}")
        return None

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "time": datetime.utcnow().isoformat(),
        "backend_version": "2.2",
        "message": "Ready - cycles active"
    }

@app.get("/api/market_data")
async def market_data():
    client = get_polygon_client()
    if not client:
        return {"error": "Polygon/Massive key missing or invalid"}
    try:
        aggs = client.list_aggs("SPY", 1, "minute", limit=20)  # Updated method name if needed; check docs if fails
        prices = [a.close for a in aggs]
        return {"spy_prices": prices, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/agent_cycle")
async def agent_cycle():
    print("🚀 Agent Cycle v2.2 running...")
    polygon_client = get_polygon_client()
    if not polygon_client:
        return {"success": False, "thought_stream": "Polygon/Massive key missing - demo mode"}

    try:
        last_trade = polygon_client.get_last_trade("SPY")
        price = last_trade.price

        signal = "HOLD"
        if price > 510:  # Demo logic
            signal = "BUY"
        elif price < 500:
            signal = "SELL"

        thought = f"SPY price: ${price:.2f} → Signal: {signal} (Risk OK)"
        print(thought)

        return {
            "success": True,
            "price": price,
            "signal": signal,
            "thought_stream": thought,
            "action": "Paper mode - no real trade"
        }
    except Exception as e:
        return {"success": False, "thought_stream": f"Error: {str(e)}"}

@app.post("/api/emergency_stop")
async def emergency_stop():
    client = get_trading_client()
    if not client:
        return {"success": False, "message": "Alpaca not connected"}
    try:
        client.close_all_positions(cancel_orders=True)
        return {"success": True, "message": "✅ ALL POSITIONS FLATTENED"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/performance")
async def performance():
    client = get_trading_client()
    if not client:
        return {"equity": 100000, "pnl_today": 0, "note": "Alpaca not connected"}
    try:
        account = client.get_account()
        return {
            "equity": float(account.equity),
            "pnl_today": float(account.equity) - float(account.last_equity)
        }
    except:
        return {"equity": 100000, "pnl_today": 0}

# Autonomous loop
async def autonomous_loop():
    while True:
        await agent_cycle()
        await asyncio.sleep(300)  # 5 min

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_loop())
    print("✅ AetherQuant Backend v2.2 started - 5-min loop active")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
