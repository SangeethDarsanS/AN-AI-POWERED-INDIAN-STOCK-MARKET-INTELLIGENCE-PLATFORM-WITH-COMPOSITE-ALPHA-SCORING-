import uuid
from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from agents.chatbot_agent import ChatbotAgent

router = APIRouter()
chatbot = ChatbotAgent()

# In-memory session store
sessions: dict[str, list[dict]] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    try:
        result = chatbot.chat(req.message, history)
        # Update history
        sessions[session_id].append({"role": "user", "content": req.message})
        sessions[session_id].append({"role": "assistant", "content": result["response"]})

        # Keep last 20 messages to avoid token overflow
        if len(sessions[session_id]) > 20:
            sessions[session_id] = sessions[session_id][-20:]

        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            tool_calls_made=result.get("tool_calls_made", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    history = sessions.get(session_id, [])
    return {"session_id": session_id, "messages": history}


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "History cleared", "session_id": session_id}
