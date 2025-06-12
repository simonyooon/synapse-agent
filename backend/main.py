from fastapi import FastAPI, Request
from agent.base import SynapseAgent

app = FastAPI()
agent = SynapseAgent()

@app.post("/agent")
async def run_agent(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    response = await agent.handle(user_input)
    return {"response": response}
