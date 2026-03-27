import type { AppIconName } from '@/lib/icon-registry'

export type AgentStatus = 'active' | 'draft' | 'paused'
export type StanceTone = 'support' | 'caution' | 'question' | 'synthesis'
export type SourceType = 'PDF' | 'Markdown' | 'Аналитика' | 'Протокол'
export type SkillCategory = 'analysis' | 'research' | 'risk' | 'writing'

export interface SourceReference {
  id: string
  title: string
  type: SourceType
  location?: string
  summary: string
}

export interface DebateMessage {
  id: string
  agentId: string
  stage: 'position' | 'debate' | 'synthesis'
  stance: string
  tone: StanceTone
  content: string
  timestamp: string
  replyToLabel?: string
  citations: SourceReference[]
}

export interface ChatMessage {
  id: string
  author: 'user' | 'system'
  label: string
  content: string
  timestamp: string
}

export interface ExportOption {
  id: 'html' | 'pdf' | 'markdown' | 'summary'
  label: string
  description: string
  icon: AppIconName
}

export interface AgentSkill {
  id: string
  name: string
  description: string
  category: SkillCategory
}

export interface AgentDocument {
  id: string
  title: string
  type: string
  status: string
  date: string
  tags: string[]
  summary: string
}

export interface AgentProfile {
  id: string
  name: string
  role: string
  description: string
  systemPrompt: string
  goals: string[]
  constraints: string[]
  status: AgentStatus
  icon: AppIconName
  documentsCount: number
  skillsCount: number
  documents: AgentDocument[]
  skills: AgentSkill[]
  focus: string
}

export interface LandingNode {
  id: string
  label: string
  description: string
  icon: AppIconName
}
