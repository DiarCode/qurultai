export type AgentStatus = 'active' | 'draft' | 'paused'
export type RunStatus = 'queued' | 'processing' | 'completed' | 'failed'

export interface ToolRecord {
  id: string
  name: string
  description: string | null
  input_schema_json: Record<string, unknown>
  endpoint_url: string | null
}

export interface SkillRecord {
  id: string
  key: string
  name: string
  description: string | null
  content_md: string
  file_path: string | null
}

export interface DocumentRecord {
  id: string
  title: string
  source_filename: string
  mime_type: string | null
  size_bytes: number
  s3_bucket: string
  s3_key: string
  text_preview: string | null
  metadata_json: Record<string, unknown>
  upload_status: string
  index_status: string
  chunk_count: number
  parser_kind: string | null
  agent_ids: string[]
  download_url: string | null
  created_at: string
  updated_at: string
}

export interface AgentRecord {
  id: string
  key: string
  name: string
  role: string
  description: string | null
  system_prompt: string
  goals: string[]
  constraints: string[]
  status: AgentStatus
  tool_ids: string[]
  skill_ids: string[]
  tools: ToolRecord[]
  skills: SkillRecord[]
  documents: DocumentRecord[]
  created_at: string
  updated_at: string
}

export interface FileReference {
  id: string
  name: string
  mime_type: string | null
  size_bytes: number
  linked_entity_type: string
  linked_entity_id: string
  created_at: string
  download_url: string | null
  text_preview: string | null
  upload_status: string
  index_status: string
  chunk_count: number
  parser_kind: string | null
}

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

export interface RunParticipant {
  id: string
  key: string
  name: string
  role: string
  status: string
}

export interface RunMessage {
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

export interface ReportVariant {
  format: 'markdown' | 'html' | 'pdf'
  download_url: string
  available: boolean
}

export interface RunReport {
  title: string
  summary: string
  body_markdown: string
  body_html: string
  source_agent_name: string | null
  generated_at: string | null
  variants: ReportVariant[]
}

export interface RunEvent {
  id: string
  run_id: string
  sequence: number
  event_type: string
  created_at: string
  payload: Record<string, unknown>
}

export interface RunRecord {
  id: string
  prompt: string
  status: RunStatus
  created_at: string
  updated_at: string
  participants: RunParticipant[]
  attachments: FileReference[]
  messages: RunMessage[]
  final_report: RunReport | null
  events: RunEvent[]
}

export interface RunCreateResponse {
  run_id: string
  status: RunStatus
  websocket_url: string
}

export interface LandingNode {
  id: string
  label: string
  description: string
  icon: AppIconName
}
import type { AppIconName } from '@/lib/icon-registry'
