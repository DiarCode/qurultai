from __future__ import annotations

import asyncio

from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from app.api.deps import SessionDep
from app.db.session import SessionLocal
from app.schemas.chat import (
    ChatModePreference,
    ChatRunRead,
    ChatSendMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionCreateResponse,
    ChatSessionListResponse,
    ChatSessionRead,
)
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=ChatSessionListResponse)
def list_sessions(session: SessionDep) -> ChatSessionListResponse:
    items = [chat_service._summary_read(room) for room in chat_service.list_sessions(session)]
    return ChatSessionListResponse(items=items)


@router.post("/sessions", response_model=ChatSessionCreateResponse, status_code=201)
def create_session(
    payload: ChatSessionCreateRequest,
    session: SessionDep,
) -> ChatSessionCreateResponse:
    room = chat_service.create_session(session, title=payload.title)
    return ChatSessionCreateResponse(session=chat_service._summary_read(room))


@router.get("/sessions/{session_id}", response_model=ChatSessionRead)
def get_session(session_id: str, session: SessionDep) -> ChatSessionRead:
    return chat_service.get_session_read(session, session_id)


@router.post("/sessions/{session_id}/messages", response_model=ChatSendMessageResponse, status_code=201)
async def send_message(
    session_id: str,
    session: SessionDep,
    content: str = Form(...),
    mode_preference: ChatModePreference = Form("auto"),
    files: list[UploadFile] | None = File(default=None),
) -> ChatSendMessageResponse:
    attachments: list[tuple[bytes, str, str]] = []
    for upload in files or []:
        attachments.append(
            (
                await upload.read(),
                upload.filename or "upload.bin",
                upload.content_type or "application/octet-stream",
            )
        )

    room, run = chat_service.send_message(
        session,
        session_id=session_id,
        content=content,
        mode_preference=mode_preference,
        attachments=attachments,
    )
    return ChatSendMessageResponse(
        session=chat_service.build_session_read(session, room.id),
        run=chat_service.get_run_read(session, run.id),
    )


@router.get("/runs/{run_id}", response_model=ChatRunRead)
def get_run(run_id: str, session: SessionDep) -> ChatRunRead:
    return chat_service.get_run_read(session, run_id)


@router.get("/runs/{run_id}/report/download")
def download_report(run_id: str, format: str, session: SessionDep) -> Response:
    payload, media_type, filename = chat_service.load_report_bytes(session, run_id, format)
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.websocket("/runs/{run_id}/events/ws")
async def stream_run_events(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    await websocket.send_json({"event_type": "connection_ready", "payload": {"run_id": run_id}})

    if chat_service.claim_run_for_processing(run_id):
        asyncio.create_task(asyncio.to_thread(chat_service.process_run, run_id))

    last_sequence = 0

    try:
        while True:
            with SessionLocal() as session:
                events = chat_service.list_run_events(session, run_id, after_sequence=last_sequence)
                run = chat_service.get_run_read(session, run_id)

            for event in events:
                last_sequence = event.sequence
                await websocket.send_json(
                    {
                        "id": event.id,
                        "run_id": event.run_id,
                        "sequence": event.sequence,
                        "event_type": event.event_type,
                        "created_at": event.created_at.isoformat(),
                        "payload": event.payload_json,
                    }
                )

            if run.status in {"completed", "failed"} and not events:
                break

            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        return
