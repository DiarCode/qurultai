import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { chromium } from 'playwright'

const FRONTEND_URL = 'http://127.0.0.1:5173'
const API_URL = 'http://127.0.0.1:8000/api/v1'
const uniqueSuffix = Date.now().toString(36)
const agentName = `Browser Council Agent ${uniqueSuffix}`

const agentDocumentPath = path.join(os.tmpdir(), 'qurultai-agent-doc.txt')
const runDocumentPath = path.join(os.tmpdir(), 'qurultai-run-doc.txt')

fs.writeFileSync(
  agentDocumentPath,
  'Agent knowledge document: legal review, transparent citations, staged rollout.',
  'utf8',
)
fs.writeFileSync(
  runDocumentPath,
  'Run attachment: procurement review, phased launch, public evidence trail.',
  'utf8',
)

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

async function ensureSkill(page) {
  const payload = {
    key: 'browser-evidence-audit-verify',
    name: 'Browser Evidence Audit Verify',
    description: 'Checks evidence links in browser verification',
    content_md: '# Browser Evidence Audit Verify',
  }

  const response = await page.request.post(`${API_URL}/skills`, {
    data: payload,
  })

  if (response.ok()) {
    return
  }

  const text = await response.text()
  if (!text.includes('already exists')) {
    throw new Error(`Skill bootstrap failed: ${response.status()} ${text}`)
  }
}

async function createAgent(page) {
  await page.goto(`${FRONTEND_URL}/agents`, { waitUntil: 'networkidle' })
  await page.getByRole('button', { name: 'Добавить агента' }).click()
  await page.getByPlaceholder('Например, Синтез').fill(agentName)
  await page.getByPlaceholder('Например, аналитик доверия').fill('Transparency reviewer')

  const dialog = page.locator('[role="dialog"]').last()
  const textareas = dialog.locator('textarea')
  await textareas.nth(0).fill('Created through browser verification flow.')
  await textareas.nth(1).fill('Always cite evidence and keep council reasoning visible.')
  await textareas.nth(2).fill('Protect transparency\nDemand explicit citations')
  await textareas.nth(3).fill('No unsupported claims')
  await dialog.getByRole('button', { name: 'Сохранить агента' }).click()
  await page.waitForTimeout(600)

  const agentsResponse = await page.request.get(`${API_URL}/agents`)
  const agents = await agentsResponse.json()
  const createdAgent = agents.find((agent) => agent.name === agentName)
  assert(createdAgent, 'Created agent not returned by API')
  return createdAgent.id
}

async function updateAgent(page) {
  const textareas = page.locator('textarea')
  await textareas.nth(0).fill('Updated by browser verification.')
  await page.getByRole('button', { name: 'Сохранить изменения' }).click()
  await page.waitForTimeout(400)
  await page.reload({ waitUntil: 'networkidle' })
  assert(await page.getByText('Updated by browser verification.').count() > 0, 'Agent update did not persist')
}

async function manageAgentDocument(page) {
  await page.getByRole('tab', { name: 'Документы и RAG' }).click()
  await page.locator('input[type="file"]').setInputFiles(agentDocumentPath)
  await page.getByRole('heading', { name: 'qurultai-agent-doc.txt' }).waitFor({ timeout: 10000 })
  await page.reload({ waitUntil: 'networkidle' })
  await page.getByRole('tab', { name: 'Документы и RAG' }).click()
  await page.getByRole('heading', { name: 'qurultai-agent-doc.txt' }).waitFor({ timeout: 10000 })
  await page.getByRole('button', { name: 'Удалить' }).first().click()
  await page.waitForTimeout(500)
  assert(await page.getByRole('heading', { name: 'qurultai-agent-doc.txt' }).count() === 0, 'Document was not removed')
}

async function deleteAgent(page, agentId) {
  await page.getByRole('tab', { name: 'Детали агента' }).click()
  await page.getByRole('button', { name: 'Удалить агента' }).click()
  await page.waitForURL('**/agents')
  await page.waitForLoadState('networkidle')
  const response = await page.request.get(`${API_URL}/agents/${agentId}`)
  assert(response.status() === 404, 'Agent was not deleted')
}

async function verifyCouncilRun(page) {
  await page.goto(`${FRONTEND_URL}/chat`, { waitUntil: 'networkidle' })
  await page
    .locator('textarea')
    .first()
    .fill('Prepare a council recommendation for a phased public pilot and cite the attached document.')
  await page.locator('input[type="file"]').setInputFiles(runDocumentPath)
  await page.getByRole('button', { name: 'Отправить в совет' }).click()

  await page.waitForURL(/.*run=.*/)
  await page.waitForFunction(
    () => document.body.innerText.includes('Скачать Markdown'),
    null,
    { timeout: 20000 },
  )
  await page.waitForFunction(
    () => document.body.innerText.includes('Final Report Agent'),
    null,
    { timeout: 20000 },
  )

  const pageText = await page.textContent('body')
  assert(pageText?.includes('Final Report Agent'), 'Final report agent output not visible')
  assert(pageText?.includes('qurultai-run-doc.txt'), 'Run attachment citation not visible')

  const runId = new URL(page.url()).searchParams.get('run')
  assert(runId, 'Run id missing from chat URL')

  const reportResponse = await page.request.get(`${API_URL}/runs/${runId}/report/download?format=markdown`)
  const reportText = await reportResponse.text()
  assert(reportResponse.ok(), 'Report download endpoint failed')
  assert(reportText.includes('# Council Report'), 'Downloaded report is invalid')
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const results = {
    agentCrud: false,
    documentManagement: false,
    liveCouncilRun: false,
    reportDownload: false,
  }

  try {
    await ensureSkill(page)
    console.log('step:create-agent')
    const createdAgentId = await createAgent(page)
    console.log('step:open-agent')
    await page.goto(`${FRONTEND_URL}/agents/${createdAgentId}`, { waitUntil: 'networkidle' })
    console.log('step:update-agent')
    await updateAgent(page)
    results.agentCrud = true

    console.log('step:document-management')
    await manageAgentDocument(page)
    results.documentManagement = true

    console.log('step:delete-agent')
    await deleteAgent(page, createdAgentId)

    console.log('step:live-run')
    await verifyCouncilRun(page)
    results.liveCouncilRun = true
    results.reportDownload = true
  } finally {
    await browser.close()
  }

  console.log(JSON.stringify(results, null, 2))
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
