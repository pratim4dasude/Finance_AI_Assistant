import asyncio
import json
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

from src.schemas import ChatRequest,UserContext
from src.safety_guard import safety_check
from src.classifier import IntentClassifier
from src.router import AgentRouter
from src.memory import memory_store
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Finance AI Microservice")

classifier = IntentClassifier()
router = AgentRouter()


@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        try:
            yield {
                "event": "status",
                "data": json.dumps({"stage": "safety_check"}),
            }

            safety = safety_check(request.query)

            if not safety.allowed:
                yield {
                    "event": "blocked",
                    "data": json.dumps(
                        {
                            "allowed": False,
                            "category": safety.category,
                            "message": safety.response,
                        }
                    ),
                }
                return

            yield {
                "event": "status",
                "data": json.dumps({"stage": "classification"}),
            }

            history = memory_store.get_history(request.session_id)

            incoming_context = request.user_context.model_dump()

            if incoming_context.get("portfolio"):
                memory_store.save_user_context(request.session_id, incoming_context)
            else:
                saved_context = memory_store.get_saved_user_context(request.session_id)
                if saved_context:
                    request.user_context = UserContext(**saved_context)

            # classification = await asyncio.to_thread(
            #     classifier.classify,
            #     request.query,
            #     history,
            # )
            resolved_query = memory_store.resolve_follow_up(
                request.session_id,
                request.query,
            )

            classification = await asyncio.to_thread(
                classifier.classify,
                resolved_query,
                history,
            )

            yield {
                "event": "classification",
                "data": classification.model_dump_json(),
            }

            yield {
                "event": "status",
                "data": json.dumps({"stage": "agent_execution"}),
            }

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    router.route,
                    resolved_query,
                    request.user_context,
                    classification,
                ),
                timeout=60,
            )

            memory_store.add_turn(request.session_id, "user", request.query)
            memory_store.add_turn(
                request.session_id,
                "assistant",
                json.dumps(result),
            )

            yield {
                "event": "response",
                "data": json.dumps(result),
            }

            yield {
                "event": "done",
                "data": json.dumps({"ok": True}),
            }

        except asyncio.TimeoutError:
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "type": "timeout",
                        "message": "The request timed out. Please try a smaller query.",
                    }
                ),
            }

        except Exception:
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "type": "internal_error",
                        "message": "Something went wrong while processing the request.",
                    }
                ),
            }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )