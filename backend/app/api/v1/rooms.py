from fastapi import APIRouter, BackgroundTasks

from app.api.deps import SessionDep
from app.schemas.rooms import (
    RoomChatRequest,
    RoomChatResponse,
    RoomCreateRequest,
    RoomCreateResponse,
    RoomReportResponse,
    RoomResultDocumentsResponse,
    RoomStatusResponse,
    RoomTraceResponse,
)
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/create", response_model=RoomCreateResponse)
def create_room(
    payload: RoomCreateRequest,
    background_tasks: BackgroundTasks,
    session: SessionDep,
) -> RoomCreateResponse:
    room = room_service.create_room(session, payload.query)

    if payload.async_mode:
        room_service.mark_room_processing(session, room.id)
        background_tasks.add_task(
            room_service.process_room_workflow,
            room.id,
            payload.document_path,
            payload.context_text,
        )
        room = room_service.get_room_status(session, room.id)
    else:
        room = room_service.run_room_workflow(
            session,
            room.id,
            payload.document_path,
            payload.context_text,
        )

    return RoomCreateResponse(room_id=room.id, status=room.status, thread_id=room_service.room_thread_id(room.id))


@router.get("/{room_id}/status", response_model=RoomStatusResponse)
def room_status(room_id: str, session: SessionDep) -> RoomStatusResponse:
    room = room_service.get_room_status(session, room_id)
    return RoomStatusResponse(room_id=room.id, status=room.status, mission_goals=room.mission_goals_json)


@router.get("/{room_id}/report", response_model=RoomReportResponse)
def room_report(room_id: str, session: SessionDep) -> RoomReportResponse:
    room = room_service.get_room_status(session, room_id)
    html_path, pdf_path = room_service.get_room_artifacts(room_id)
    return RoomReportResponse(
        room_id=room.id,
        report_md=room.final_report_md,
        report_html_path=html_path,
        report_pdf_path=pdf_path,
        thread_id=room_service.room_thread_id(room.id),
    )


@router.get("/{room_id}/trace", response_model=RoomTraceResponse)
def room_trace(room_id: str, session: SessionDep) -> RoomTraceResponse:
    return RoomTraceResponse(**room_service.get_room_trace(session, room_id))


@router.post("/chat", response_model=RoomChatResponse)
def room_chat(payload: RoomChatRequest, session: SessionDep) -> RoomChatResponse:
    answer = room_service.chat_with_room(session, payload.room_id, payload.query)
    return RoomChatResponse(answer=answer)


@router.get("/{room_id}/result-documents", response_model=RoomResultDocumentsResponse)
def room_result_documents(room_id: str, session: SessionDep) -> RoomResultDocumentsResponse:
    room_service.get_room_status(session, room_id)
    payload = room_service.get_room_result_documents(room_id)
    return RoomResultDocumentsResponse(room_id=room_id, **payload)
