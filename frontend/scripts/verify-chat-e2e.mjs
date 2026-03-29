import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { chromium } from 'playwright'

const FRONTEND_URL = 'http://127.0.0.1:5173'
const API_URL = 'http://127.0.0.1:8000/api/v1'

function assert(condition, message) {
  if (!condition) {
    throw new Error(message)
  }
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function waitForAssistantCompletion(page) {
  await page.waitForFunction(
    () => {
      const pills = Array.from(document.querySelectorAll('.qurultai-richtext .q-pill'))
      return pills.some((node) => node.textContent?.toLowerCase().includes('confidence'))
    },
    null,
    { timeout: 30000 },
  )
}

async function waitForActionButtons(page) {
  await page.waitForFunction(
    () => Array.from(document.querySelectorAll('button')).some((node) => node.textContent?.includes('Download report')),
    null,
    { timeout: 30000 },
  )
}

async function submitMessage(page, text, files = []) {
  await page.locator('textarea').fill(text)
  if (files.length) {
    await page.locator('input[type="file"]').setInputFiles(files)
  }
  await page.getByRole('button', { name: 'Send message' }).click()
  await waitForAssistantCompletion(page)
}

async function latestModeText(page) {
  return (await page.getByTestId('current-run-mode').textContent()) || ''
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const docPath = path.join(os.tmpdir(), 'qurultai-e2e-doc.txt')
  fs.writeFileSync(
    docPath,
    'Memo: budget clearance, legal review, and environmental permit sequencing are all required before procurement begins.',
    'utf8',
  )

  const results = {
    flowA_simpleQuestion: false,
    flowB_complexQuestion: false,
    flowC_documentQuestion: false,
    flowD_sessionContinuity: false,
    flowE_historyRestore: false,
    flowF_outputUx: false,
    flowG_longerSession: false,
  }

  try {
    await page.goto(`${FRONTEND_URL}/chat`, { waitUntil: 'networkidle' })

    if (await page.getByTestId('empty-new-chat-button').count()) {
      await page.getByTestId('empty-new-chat-button').click()
    } else {
      await page.getByTestId('new-chat-button').click()
    }

    await submitMessage(page, 'What is the practical difference between a budget note and a risk note?')
    assert((await latestModeText(page)).toLowerCase().includes('direct answer'), 'Simple flow did not stay direct')
    assert((await page.locator('.qurultai-richtext .q-answer-card').count()) >= 1, 'Inline answer card missing')
    results.flowA_simpleQuestion = true
    results.flowF_outputUx = true

    const sessionItems = page.locator('[data-testid^="session-item-"]')
    const firstSessionUrl = page.url()
    const firstSessionId = new URL(firstSessionUrl).searchParams.get('session')
    assert(firstSessionId, 'Session id missing from URL after first chat')

    await submitMessage(page, 'Continue this same chat and rewrite the answer as three bullet points.')
    const firstSessionUrlAfterFollowUp = page.url()
    assert(firstSessionUrl === firstSessionUrlAfterFollowUp, 'Follow-up created a different session')
    const sessionStateResponse = await page.request.get(`${API_URL}/chat/sessions/${firstSessionId}`)
    const sessionState = await sessionStateResponse.json()
    assert(sessionState.messages.length >= 4, 'Message history was not preserved in the session')
    results.flowD_sessionContinuity = true
    results.flowG_longerSession = true

    await page.getByTestId('new-chat-button').click()
    await wait(300)
    await submitMessage(
      page,
      'Assess the legal, budget, and environmental risks in the attached memo and give a phased recommendation.',
      [docPath],
    )
    await waitForActionButtons(page)
    const modeText = (await latestModeText(page)).toLowerCase()
    assert(modeText.includes('council') || modeText.includes('specialist assist'), 'Complex flow did not escalate')
    results.flowB_complexQuestion = true

    assert((await page.getByRole('button', { name: 'Download report' }).count()) >= 1, 'Download report action missing')
    assert((await page.getByRole('button', { name: 'Copy summary' }).count()) >= 1, 'Copy summary action missing')
    assert((await page.getByRole('button', { name: 'Open sources' }).count()) >= 1, 'Open sources action missing')
    assert((await page.getByRole('button', { name: 'Expand analysis' }).count()) >= 1, 'Expand analysis action missing')
    await page.getByRole('button', { name: 'Open sources' }).last().click()
    assert((await page.getByText('Grounding').count()) >= 1, 'Sources panel did not open')
    results.flowC_documentQuestion = true

    assert((await sessionItems.count()) >= 2, 'History list did not accumulate multiple chats')

    await page.getByTestId(`session-item-${firstSessionId}`).click()
    await page.waitForFunction(
      (expectedSessionId) => new URL(window.location.href).searchParams.get('session') === expectedSessionId,
      firstSessionId,
      { timeout: 10000 },
    )
    assert(
      new URL(page.url()).searchParams.get('session') === firstSessionId,
      'Reopening history did not restore the original session',
    )
    const restoredResponse = await page.request.get(`${API_URL}/chat/sessions/${firstSessionId}`)
    const restoredSession = await restoredResponse.json()
    assert(restoredSession.messages.length >= 4, 'Original chat contents were not restored')
    results.flowE_historyRestore = true
  } finally {
    await browser.close()
  }

  console.log(JSON.stringify(results, null, 2))
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
