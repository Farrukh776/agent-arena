from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from debate_manager import run_debate_websocket
from memory.debate_memory import init_db, get_all_stats
import json
import asyncio

app = FastAPI(title="AgentArena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"status": "AgentArena API is running"}

@app.get("/stats")
async def get_stats():
    return {"stats": get_all_stats()}

@app.websocket("/debate")
async def debate_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        data   = await websocket.receive_text()
        config = json.loads(data)

        topic  = config.get("topic", "").strip()
        rounds = int(config.get("rounds", 2))

        if not topic:
            await websocket.send_text(json.dumps({
                "type": "error", "message": "Topic cannot be empty"
            }))
            await websocket.close()
            return

        if rounds < 1 or rounds > 4:
            rounds = 2

        # Shared cancellation flag between debate task and disconnect watcher
        cancelled = asyncio.Event()

        async def watch_disconnect():
            """Sets cancelled flag the moment client disconnects."""
            try:
                while True:
                    try:
                        await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                    except asyncio.TimeoutError:
                        continue  # no message yet, keep watching
            except Exception:
                cancelled.set()  # any error = client gone

        debate_task     = asyncio.create_task(
            run_debate_websocket(topic, rounds, websocket, cancelled)
        )
        disconnect_task = asyncio.create_task(watch_disconnect())

        done, pending = await asyncio.wait(
            [debate_task, disconnect_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error", "message": str(e)
            }))
        except Exception:
            pass