from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from debate_manager import run_debate_websocket
from memory.debate_memory import init_db, get_all_stats
import json

app = FastAPI(title="AgentArena API")

# CORS — allows the React frontend (on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tightened to specific domain on deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize database when server starts."""
    init_db()


@app.get("/")
async def root():
    return {"status": "AgentArena API is running"}


@app.get("/stats")
async def get_stats():
    """Return all-time agent statistics."""
    return {"stats": get_all_stats()}


@app.websocket("/debate")
async def debate_websocket(websocket: WebSocket):
    """
    Main WebSocket endpoint.
    
    Flow:
    1. Frontend connects to ws://localhost:8000/debate
    2. Frontend sends JSON: {"topic": "...", "rounds": 2}
    3. Server streams back debate events as JSON messages
    4. Connection closes when debate is done
    """
    await websocket.accept()

    try:
        # Wait for the frontend to send debate config
        data = await websocket.receive_text()
        config = json.loads(data)

        topic = config.get("topic", "").strip()
        rounds = int(config.get("rounds", 2))

        if not topic:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Topic cannot be empty"
            }))
            await websocket.close()
            return

        if rounds < 1 or rounds > 4:
            rounds = 2

        # Run the full debate, streaming events back
        await run_debate_websocket(topic, rounds, websocket)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass