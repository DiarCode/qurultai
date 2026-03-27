import { computed, onBeforeUnmount, ref, toValue, watch } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import { useMediaQuery } from '@vueuse/core'

import type { DebateMessage } from '@/types/council'

export interface AnimatedDebateMessage extends DebateMessage {
  displayContent: string
  isTyping: boolean
  isDelivered: boolean
  sequence: number
}

function getTypingStep(message: DebateMessage) {
  return Math.max(2, Math.ceil(message.content.length / 44))
}

function getTypingInterval(message: DebateMessage) {
  return message.stage === 'synthesis' ? 34 : 28
}

function getPauseAfterMessage(message: DebateMessage) {
  switch (message.stage) {
    case 'position':
      return 520
    case 'debate':
      return 720
    case 'synthesis':
      return 0
    default:
      return 480
  }
}

export function useDebatePlayback(messagesSource: MaybeRefOrGetter<DebateMessage[]>) {
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')
  const visibleCount = ref(0)
  const activeIndex = ref(-1)
  const typedLength = ref(0)
  const isFinished = ref(false)

  let typingTimer: ReturnType<typeof window.setInterval> | null = null
  let nextMessageTimer: ReturnType<typeof window.setTimeout> | null = null

  const sourceMessages = computed(() => toValue(messagesSource))

  const activeMessage = computed(() => {
    return activeIndex.value >= 0 ? (sourceMessages.value[activeIndex.value] ?? null) : null
  })

  const visibleMessages = computed<AnimatedDebateMessage[]>(() => {
    return sourceMessages.value.slice(0, visibleCount.value).map((message, index) => {
      const isTyping = index === activeIndex.value && typedLength.value < message.content.length
      const displayContent = isTyping
        ? message.content.slice(0, typedLength.value)
        : message.content

      return {
        ...message,
        displayContent,
        isTyping,
        isDelivered: index < visibleCount.value,
        sequence: index + 1,
      }
    })
  })

  function clearPlaybackTimers() {
    if (typingTimer) {
      window.clearInterval(typingTimer)
      typingTimer = null
    }

    if (nextMessageTimer) {
      window.clearTimeout(nextMessageTimer)
      nextMessageTimer = null
    }
  }

  function revealAllMessages() {
    clearPlaybackTimers()
    visibleCount.value = sourceMessages.value.length
    activeIndex.value = -1
    typedLength.value = 0
    isFinished.value = true
  }

  function queueNextMessage() {
    if (activeIndex.value >= sourceMessages.value.length - 1) {
      activeIndex.value = -1
      typedLength.value = 0
      isFinished.value = true
      return
    }

    const current = sourceMessages.value[activeIndex.value]
    if (!current) {
      isFinished.value = true
      activeIndex.value = -1
      return
    }

    nextMessageTimer = window.setTimeout(() => {
      visibleCount.value += 1
      activeIndex.value += 1
      typedLength.value = 0
      startTyping()
    }, getPauseAfterMessage(current))
  }

  function startTyping() {
    clearPlaybackTimers()

    const message = activeMessage.value
    if (!message) {
      isFinished.value = true
      return
    }

    const step = getTypingStep(message)
    const interval = getTypingInterval(message)

    typingTimer = window.setInterval(() => {
      typedLength.value = Math.min(typedLength.value + step, message.content.length)

      if (typedLength.value >= message.content.length) {
        clearPlaybackTimers()
        queueNextMessage()
      }
    }, interval)
  }

  function restartPlayback() {
    if (!sourceMessages.value.length) {
      clearPlaybackTimers()
      visibleCount.value = 0
      activeIndex.value = -1
      typedLength.value = 0
      isFinished.value = true
      return
    }

    if (prefersReducedMotion.value) {
      revealAllMessages()
      return
    }

    clearPlaybackTimers()
    visibleCount.value = 1
    activeIndex.value = 0
    typedLength.value = 0
    isFinished.value = false
    startTyping()
  }

  watch([sourceMessages, prefersReducedMotion], restartPlayback, {
    immediate: true,
    deep: true,
  })

  onBeforeUnmount(() => {
    clearPlaybackTimers()
  })

  return {
    activeMessage,
    isFinished,
    restartPlayback,
    visibleMessages,
  }
}
