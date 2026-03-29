export type ChatRunMode = 'direct_answer' | 'rag_answer' | 'specialist_assist' | 'council'
export type ChatRunStatus = 'queued' | 'processing' | 'completed' | 'failed'
export type ChatModePreference = 'auto' | ChatRunMode

export interface CitationRecord {
  id: string
  document_id: string | null
  title: string
  snippet: string | null
  score: number | null
  location: string | null
  download_url: string | null
}

export interface ToolCallRecord {
  name: string
  status: string
  input: Record<string, unknown>
  output_summary: string | null
}

export interface MessageAttachmentRecord {
  id: string
  name: string
  mime_type: string | null
  size_bytes: number
  download_url: string | null
  created_at: string | null
}

export interface MessageActionRecord {
  id: string
  kind: string
  label: string
  icon: string | null
  payload: Record<string, unknown>
}

export interface ChatMessageRecord {
  id: string
  session_id: string
  run_id: string | null
  role: string
  type: string
  source_agent_id: string | null
  source_agent_name: string | null
  content: string
  html_content: string | null
  citations: CitationRecord[]
  attachments: MessageAttachmentRecord[]
  actions: MessageActionRecord[]
  metadata: Record<string, unknown>
  status: string
  created_at: string
}

export interface ChatParticipantRecord {
  id: string
  key: string
  name: string
  role: string
  status: string
  reason: string | null
}

export interface ChatRunEventRecord {
  id: string
  run_id: string
  sequence: number
  event_type: string
  created_at: string
  payload: Record<string, unknown>
}

export interface DebateMessageRecord {
  id: string
  run_id: string
  role: string
  source_agent_id: string | null
  source_agent_name: string | null
  stage: string | null
  status: string
  content: string
  citations: CitationRecord[]
  tool_calls: ToolCallRecord[]
  is_partial: boolean
  created_at: string
}

export interface ChatRunRecord {
  id: string
  session_id: string
  input_message_id: string
  output_message_id: string | null
  mode: ChatRunMode
  selected_agents: ChatParticipantRecord[]
  status: ChatRunStatus
  started_at: string | null
  finished_at: string | null
  events: ChatRunEventRecord[]
}

export interface UploadedDocumentRecord {
  id: string
  session_id: string
  name: string
  mime_type: string | null
  size_bytes: number
  storage_path: string | null
  download_url: string | null
  linked_run_id: string | null
  created_at: string
}

export interface ChatSessionSummaryRecord {
  id: string
  title: string
  created_at: string
  updated_at: string
  status: string
  last_message_preview: string | null
}

export interface ChatSessionRecord extends ChatSessionSummaryRecord {
  messages: ChatMessageRecord[]
  documents: UploadedDocumentRecord[]
  runs: ChatRunRecord[]
}

export interface ChatSessionListResponse {
  items: ChatSessionSummaryRecord[]
}

export interface ChatSessionCreateResponse {
  session: ChatSessionSummaryRecord
}

export interface ChatSendMessageResponse {
  session: ChatSessionRecord
  run: ChatRunRecord
}
