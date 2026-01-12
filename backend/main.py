from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import market
import agent

app = FastAPI(title="Arbitra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())

async def simulation_loop():
    while True:
        market.market_sim.update_prices()
        agent.trading_agent.make_decisions()
        await asyncio.sleep(10) # Update every 10 seconds to avoid rate limits

@app.get("/status")
async def get_status():
    status = agent.trading_agent.get_status()
    status["market_prices"] = market.market_sim.get_prices()
    return status

@app.get("/history")
async def get_history():
    return {
        "capital": agent.trading_agent.capital_history,
        "trades": agent.trading_agent.trade_history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
