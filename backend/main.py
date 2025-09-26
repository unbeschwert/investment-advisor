from fastapi import FastAPI
from .models import ChatRequest, ChatResponse


app = FastAPI("Investment Advisor for Stocks")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await run_react_agent(req.message, max_steps=req.max_steps)
    return ChatResponse(answer=result["answer"], trace=result["trace"])

@app.get("/tools")
async def list_tools():
    return {"tools": sorted(list(TOOLS.keys()))}

# health
@app.get("/health")
async def health():
    return {"status": "ok"}