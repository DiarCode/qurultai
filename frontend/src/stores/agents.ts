import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiRequest } from '@/lib/api'
import type { AgentRecord, DocumentRecord, SkillRecord } from '@/types/council'

interface UploadResponse {
  document: DocumentRecord
  chunks_ingested: number
}

export const useAgentsStore = defineStore('agents', () => {
  const agents = ref<AgentRecord[]>([])
  const skills = ref<SkillRecord[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)

  const hasLoaded = computed(() => agents.value.length > 0)

  function upsertAgent(agent: AgentRecord) {
    const index = agents.value.findIndex((item) => item.id === agent.id)
    if (index >= 0) {
      agents.value[index] = agent
      return
    }
    agents.value.unshift(agent)
  }

  async function fetchAgents() {
    loading.value = true
    error.value = null
    try {
      agents.value = await apiRequest<AgentRecord[]>('/agents')
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить агентов.'
      throw cause
    } finally {
      loading.value = false
    }
  }

  async function fetchSkills() {
    skills.value = await apiRequest<SkillRecord[]>('/skills')
  }

  async function ensureBootstrap() {
    if (!skills.value.length) {
      await fetchSkills()
    }
    if (!agents.value.length) {
      await fetchAgents()
    }
  }

  async function fetchAgent(agentId: string) {
    const agent = await apiRequest<AgentRecord>(`/agents/${agentId}`)
    upsertAgent(agent)
    return agent
  }

  async function createAgent(payload: Record<string, unknown>) {
    saving.value = true
    try {
      const agent = await apiRequest<AgentRecord>('/agents', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      upsertAgent(agent)
      return agent
    } finally {
      saving.value = false
    }
  }

  async function updateAgent(agentId: string, payload: Record<string, unknown>) {
    saving.value = true
    try {
      const agent = await apiRequest<AgentRecord>(`/agents/${agentId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      upsertAgent(agent)
      return agent
    } finally {
      saving.value = false
    }
  }

  async function deleteAgent(agentId: string) {
    saving.value = true
    try {
      await apiRequest<void>(`/agents/${agentId}`, { method: 'DELETE' })
      agents.value = agents.value.filter((agent) => agent.id !== agentId)
    } finally {
      saving.value = false
    }
  }

  async function uploadAgentDocument(agentId: string, file: File, title?: string) {
    const formData = new FormData()
    formData.set('file', file)
    if (title) {
      formData.set('title', title)
    }

    const response = await apiRequest<UploadResponse>(`/agents/${agentId}/documents/upload-file`, {
      method: 'POST',
      body: formData,
    })
    const agent = await fetchAgent(agentId)
    return { agent, document: response.document }
  }

  async function removeAgentDocument(agentId: string, documentId: string) {
    await apiRequest(`/agents/${agentId}/documents/${documentId}`, { method: 'DELETE' })
    return fetchAgent(agentId)
  }

  async function addAgentSkill(agentId: string, skillId: string) {
    const agent = await apiRequest<AgentRecord>(`/agents/${agentId}/skills/${skillId}`, {
      method: 'POST',
    })
    upsertAgent(agent)
    return agent
  }

  async function removeAgentSkill(agentId: string, skillId: string) {
    const agent = await apiRequest<AgentRecord>(`/agents/${agentId}/skills/${skillId}`, {
      method: 'DELETE',
    })
    upsertAgent(agent)
    return agent
  }

  return {
    agents,
    skills,
    loading,
    saving,
    error,
    hasLoaded,
    ensureBootstrap,
    fetchAgents,
    fetchSkills,
    fetchAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    uploadAgentDocument,
    removeAgentDocument,
    addAgentSkill,
    removeAgentSkill,
  }
})
