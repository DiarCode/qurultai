from __future__ import annotations

import asyncio

from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from sqlmodel import select

from app.api.deps import SessionDep
from app.db.session import SessionLocal
from app.models.room import Room
from app.schemas.runs import FileReferenceRead, RunCreateResponse, RunListResponse, RunRead
from app.services import council_service

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunCreateResponse, status_code=201)
async def create_run(
    session: SessionDep,
    prompt: str = Form(...),
    files: list[UploadFile] | None = File(default=None),
) -> RunCreateResponse:
    attachments: list[tuple[bytes, str, str]] = []
    for upload in files or []:
        attachments.append(
            (
                await upload.read(),
                upload.filename or "upload.bin",
                upload.content_type or "application/octet-stream",
            )
        )

    room = council_service.create_run(session, prompt=prompt, attachments=attachments)
    return RunCreateResponse(
        run_id=room.id,
        status=room.status,  # type: ignore[arg-type]
        websocket_url=f"/api/v1/runs/{room.id}/events/ws",
    )


@router.get("", response_model=RunListResponse)
def list_runs(session: SessionDep) -> RunListResponse:
    items = [
        council_service.build_run_read(session, room.id, include_events=False)
        for room in session.exec(select(Room).order_by(Room.created_at.desc()))
    ]
    return RunListResponse(items=items)


@router.get("/{run_id}", response_model=RunRead)
def get_run(run_id: str, session: SessionDep) -> RunRead:
    return council_service.build_run_read(session, run_id)


@router.get("/{run_id}/attachments", response_model=list[FileReferenceRead])
def get_run_attachments(run_id: str, session: SessionDep) -> list[FileReferenceRead]:
    attachments = council_service.list_run_attachments(session, run_id)
    return [
        council_service._build_file_reference(
            document, linked_entity_type="run", linked_entity_id=run_id
        )
        for document in attachments
    ]


@router.get("/{run_id}/report/download")
def download_report(run_id: str, format: str, session: SessionDep) -> Response:
    payload, media_type, filename = council_service.load_report_bytes(session, run_id, format)
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.websocket("/{run_id}/events/ws")
async def stream_run_events(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    await websocket.send_json({"event_type": "connection_ready", "payload": {"run_id": run_id}})

    if council_service.claim_run_for_processing(run_id):
        asyncio.create_task(asyncio.to_thread(council_service.process_run, run_id))

    last_sequence = 0

    try:
        while True:
            with SessionLocal() as session:
                events = council_service.list_events(session, run_id, after_sequence=last_sequence)
                run = council_service.build_run_read(session, run_id, include_events=False)

            for event in events:
                last_sequence = event.sequence
                await websocket.send_json(
                    {
                        "id": event.id,
                        "run_id": event.room_id,
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
