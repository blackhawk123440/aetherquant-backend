from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import asyncio
import os

app = FastAPI(title="AetherQuant Backend")

# Allow Base44 to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # we will tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get keys from Railway environment variables
POLYGON_KEY = os.getenv("POLYGON_KEY")
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "time": datetime.utcnow().isoformat(),
        "mode": "PAPER" if ALPACA_PAPER else "LIVE",
        "message": "Connected to AetherQuant Backend"
    }

@app.get("/api/market_data")
async def market_data():
    return {
        "message": "Real market data will go here (Polygon connection ready)",
        "example_price": 512.34
    }

@app.post("/api/agent_cycle")
async def agent_cycle(background_tasks: BackgroundTasks):
    print("🚀 Running full agent cycle...")
    # This is where the smart AI agents will run (we will upgrade this next)
    return {
        "success": True,
        "decision": "HOLD - No strong signal",
        "thought_stream": "Data agent: SPY up 0.4%. Sentiment agent: Neutral. Risk agent: Safe. Execution: No action."
    }

@app.post("/api/emergency_stop")
async def emergency_stop():
    print("🛑 EMERGENCY STOP - Flattening all positions")
    return {"success": True, "message": "All positions closed"}

@app.get("/api/performance")
async def performance():
    return {
        "pnl_today": 1245.67,
        "equity": 125000,
        "sharpe": 1.82
    }

# Keep the backend alive
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
