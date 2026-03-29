<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import { buildApiUrl } from "@/lib/api";
import { renderMarkdownHtml } from "@/lib/richText";
import type {
  ChatModePreference,
  ChatMessageRecord,
  ChatRunRecord,
  ChatSessionRecord,
  ChatSessionSummaryRecord,
  MessageActionRecord,
} from "@/types/chat";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

import AppIcon from "./AppIcon.vue";

const props = defineProps<{
  sessions: ChatSessionSummaryRecord[];
  currentSession: ChatSessionRecord | null;
  currentRun: ChatRunRecord | null;
  sending: boolean;
  socketState: "idle" | "connecting" | "open" | "closed";
  error: string | null;
}>();

const emit = defineEmits<{
  createSession: [];
  selectSession: [sessionId: string];
  submit: [payload: { content: string; files: File[]; modePreference: ChatModePreference }];
}>();

const composer = ref("");
const pendingFiles = ref<File[]>([]);
const fileInputRef = ref<HTMLInputElement | null>(null);
const messagesScrollerRef = ref<HTMLElement | null>(null);
const openSourcesFor = ref<string | null>(null);
const openAnalysisFor = ref<string | null>(null);
const stickToBottom = ref(true);
const modePreference = ref<ChatModePreference>("auto");

const modeOptions: Array<{ value: ChatModePreference; label: string; hint: string }> = [
  { value: "auto", label: "Auto", hint: "LLM decides the best path" },
  { value: "direct_answer", label: "Direct answer", hint: "Fast single-assistant reply" },
  { value: "rag_answer", label: "RAG answer", hint: "Prefer document-grounded retrieval" },
  { value: "specialist_assist", label: "Specialist assist", hint: "Bring in 1-2 institutions" },
  { value: "council", label: "Council", hint: "Force a broader institutional review" },
];

const statusLabel = computed(() => {
  if (!props.currentRun) {
    return "Idle";
  }
  return (
    {
      queued: "Queued",
      processing: "Working",
      completed: "Completed",
      failed: "Failed",
    }[props.currentRun.status] || props.currentRun.status
  );
});

function openFilePicker() {
  fileInputRef.value?.click();
}

function handleFiles(event: Event) {
  const input = event.target as HTMLInputElement;
  pendingFiles.value = [...(input.files ?? [])];
}

function removeFile(index: number) {
  pendingFiles.value.splice(index, 1);
}

function updateStickiness() {
  const scroller = messagesScrollerRef.value;
  if (!scroller) {
    return;
  }
  const remaining = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
  stickToBottom.value = remaining < 160;
}

function scrollToBottom() {
  const scroller = messagesScrollerRef.value;
  if (!scroller) {
    return;
  }
  scroller.scrollTo({ top: scroller.scrollHeight, behavior: "smooth" });
}

function submit() {
  const content = composer.value.trim();
  if (!content) {
    return;
  }
  emit("submit", {
    content,
    files: [...pendingFiles.value],
    modePreference: modePreference.value,
  });
  composer.value = "";
  pendingFiles.value = [];
}

const selectedModeOption = computed(
  () => modeOptions.find((item) => item.value === modePreference.value) ?? modeOptions[0]!,
);

async function copyText(text: string) {
  await navigator.clipboard.writeText(text);
}

function exportText(filename: string, text: string) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function handleAction(message: ChatMessageRecord, action: MessageActionRecord) {
  switch (action.kind) {
    case "download_report": {
      const url = action.payload.url;
      if (typeof url === "string") {
        window.open(buildApiUrl(url), "_blank", "noopener,noreferrer");
      }
      break;
    }
    case "download_pdf": {
      const url = action.payload.url;
      if (typeof url === "string") {
        window.open(buildApiUrl(url), "_blank", "noopener,noreferrer");
      }
      break;
    }
    case "copy_summary": {
      const text = action.payload.text;
      if (typeof text === "string") {
        await copyText(text);
      }
      break;
    }
    case "export_summary": {
      const text = action.payload.text;
      const filename = action.payload.filename;
      if (typeof text === "string" && typeof filename === "string") {
        exportText(filename, text);
      }
      break;
    }
    case "open_sources": {
      openSourcesFor.value = openSourcesFor.value === message.id ? null : message.id;
      break;
    }
    case "expand_analysis": {
      openAnalysisFor.value = openAnalysisFor.value === message.id ? null : message.id;
      break;
    }
    default:
      break;
  }
}

function timestamp(value: string) {
  return new Date(value).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function analysisHtml(message: ChatMessageRecord) {
  const candidate = message.metadata.analysis_html;
  return typeof candidate === "string" ? candidate : null;
}

function assistantHtml(message: ChatMessageRecord) {
  if (message.html_content) {
    return message.html_content;
  }
  return renderMarkdownHtml(message.content);
}

const liveMessageSignal = computed(() => {
  const message = props.currentSession?.messages.at(-1);
  if (!message) {
    return "";
  }
  return `${props.currentSession?.id}:${message.id}:${message.status}:${message.content.length}:${Boolean(message.html_content)}`;
});

watch(
  liveMessageSignal,
  async () => {
    await nextTick();
    if (stickToBottom.value || props.currentRun?.status === "processing") {
      scrollToBottom();
    }
  },
  { flush: "post" },
);
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-[18rem_minmax(0,1fr)]">
    <aside class="surface-panel flex min-h-[42rem] flex-col overflow-hidden">
      <div class="border-b border-slate-100 px-5 py-5">
        <div class="flex items-center justify-between gap-4">
          <div>
            <p class="section-kicker">History</p>
            <h2 class="mt-3 font-display text-3xl tracking-tight text-slate-900">
              Persistent chats
            </h2>
          </div>
          <Button
            data-testid="new-chat-button"
            class="rounded-full"
            size="sm"
            @click="$emit('createSession')"
          >
            <AppIcon name="addCircle" :size="16" />
            New
          </Button>
        </div>
      </div>

      <div class="flex-1 space-y-2 overflow-y-auto px-3 py-3">
        <button
          v-for="session in sessions"
          :key="session.id"
          :data-testid="`session-item-${session.id}`"
          type="button"
          class="w-full rounded-3xl border px-4 py-4 text-left transition"
          :class="
            currentSession?.id === session.id
              ? 'border-slate-900 bg-slate-900 text-white'
              : 'border-slate-100 bg-white/70 text-slate-900 hover:border-slate-200 hover:bg-white'
          "
          @click="$emit('selectSession', session.id)"
        >
          <div class="flex items-start justify-between gap-3">
            <p class="text-sm font-medium tracking-tight">{{ session.title }}</p>
            <span
              class="text-[11px]"
              :class="currentSession?.id === session.id ? 'text-slate-300' : 'text-slate-400'"
            >
              {{ timestamp(session.updated_at) }}
            </span>
          </div>
          <p
            class="mt-2 line-clamp-3 text-sm leading-6"
            :class="currentSession?.id === session.id ? 'text-slate-200' : 'text-slate-500'"
          >
            {{ session.last_message_preview || "No messages yet." }}
          </p>
        </button>

        <div
          v-if="!sessions.length"
          class="rounded-3xl border border-dashed border-slate-200 bg-white/60 px-4 py-6 text-sm leading-6 text-slate-500"
        >
          Start a chat to keep messages, documents, and reports together in one thread.
        </div>
      </div>
    </aside>

    <div class="surface-panel flex min-h-[42rem] flex-col overflow-hidden">
      <input ref="fileInputRef" type="file" class="hidden" multiple @change="handleFiles" />

      <div class="border-b border-slate-100 px-6 py-5">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="space-y-3">
            <p class="section-kicker">Workspace</p>
            <h1
              class="font-display text-[clamp(2rem,4vw,3.35rem)] leading-[0.96] tracking-tight text-slate-900"
            >
              {{ currentSession?.title || "Continuous assistant chat" }}
            </h1>
            <p class="max-w-3xl text-sm leading-7 text-slate-500">
              Simple questions stay direct. Retrieval and specialist escalation only show up when
              they actually help.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="outline" data-testid="current-run-mode">
              {{ currentRun ? currentRun.mode.replace("_", " ") : "awaiting message" }}
            </Badge>
            <Badge variant="secondary">{{ statusLabel }}</Badge>
            <Badge variant="outline">Socket {{ socketState }}</Badge>
            <Badge
              v-if="currentRun?.status === 'processing'"
              class="bg-emerald-600 text-white hover:bg-emerald-600"
            >
              Live answer
            </Badge>
          </div>
        </div>

        <div v-if="currentSession?.documents.length" class="mt-5 flex flex-wrap gap-2">
          <Badge
            v-for="document in currentSession.documents"
            :key="document.id"
            variant="outline"
            class="bg-white/70"
          >
            {{ document.name }}
          </Badge>
        </div>
      </div>

      <div
        ref="messagesScrollerRef"
        class="flex-1 overflow-y-auto px-5 py-5 sm:px-6"
        @scroll="updateStickiness"
      >
        <div v-if="!currentSession" class="flex h-full items-center justify-center">
          <div class="max-w-lg space-y-5 text-center">
            <div
              class="mx-auto flex size-16 items-center justify-center rounded-full border border-slate-200 bg-white/70"
            >
              <AppIcon name="aiChat" :size="24" />
            </div>
            <h2 class="font-display text-4xl tracking-tight text-slate-900">
              Start a new conversation
            </h2>
            <p class="text-sm leading-7 text-slate-500">
              Create a chat when you want a fresh thread. Once a session is open, follow-up messages
              stay in the same conversation until you intentionally start another one.
            </p>
            <Button
              data-testid="empty-new-chat-button"
              class="rounded-full"
              @click="$emit('createSession')"
            >
              <AppIcon name="addCircle" :size="16" />
              Start new chat
            </Button>
          </div>
        </div>

        <div v-else class="space-y-5">
          <article
            v-for="message in currentSession.messages"
            :key="message.id"
            data-testid="chat-message"
            class="flex"
            :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-3xl rounded-[2rem] border px-5 py-4 shadow-[0_8px_30px_-20px_rgba(15,23,42,0.25)]"
              :class="
                message.role === 'user'
                  ? 'border-slate-900 bg-slate-900 text-white'
                  : 'border-slate-100 bg-white/88 text-slate-900'
              "
            >
              <div class="mb-3 flex items-center gap-3">
                <Badge :variant="message.role === 'user' ? 'secondary' : 'outline'">
                  {{ message.role === "user" ? "You" : message.source_agent_name || "Qurultai" }}
                </Badge>
                <span
                  class="text-xs"
                  :class="message.role === 'user' ? 'text-slate-300' : 'text-slate-400'"
                >
                  {{ timestamp(message.created_at) }}
                </span>
              </div>

              <div v-if="message.role === 'assistant'" class="space-y-4">
                <div
                  class="qurultai-richtext"
                  :class="{ 'is-streaming': message.status === 'processing' }"
                  v-html="assistantHtml(message)"
                />

                <div v-if="message.actions.length" class="flex flex-wrap gap-2">
                  <Button
                    v-for="action in message.actions"
                    :key="action.id"
                    variant="outline"
                    size="sm"
                    class="rounded-full bg-white/80"
                    @click="handleAction(message, action)"
                  >
                    {{ action.label }}
                  </Button>
                </div>

                <div
                  v-if="openSourcesFor === message.id && message.citations.length"
                  data-testid="sources-panel"
                  class="rounded-3xl border border-slate-100 bg-slate-50/80 p-4"
                >
                  <p class="mb-3 text-sm font-medium text-slate-900">Grounding</p>
                  <div class="space-y-3">
                    <a
                      v-for="citation in message.citations"
                      :key="citation.id"
                      class="block rounded-2xl border border-slate-100 bg-white px-4 py-3 text-sm leading-6 text-slate-600 transition hover:border-slate-200"
                      :href="citation.download_url ? buildApiUrl(citation.download_url) : undefined"
                      target="_blank"
                      rel="noreferrer"
                    >
                      <p class="font-medium text-slate-900">{{ citation.title }}</p>
                      <p v-if="citation.location" class="text-xs text-slate-400">
                        {{ citation.location }}
                      </p>
                      <p v-if="citation.snippet" class="mt-2">{{ citation.snippet }}</p>
                    </a>
                  </div>
                </div>

                <div
                  v-if="openAnalysisFor === message.id && analysisHtml(message)"
                  class="qurultai-richtext rounded-3xl border border-slate-100 bg-slate-50/80 p-4"
                  v-html="analysisHtml(message) || ''"
                />
              </div>

              <div v-else>
                <p class="text-sm leading-7 whitespace-pre-wrap">{{ message.content || "..." }}</p>
              </div>

              <div v-if="message.attachments.length" class="mt-4 flex flex-wrap gap-2">
                <a
                  v-for="attachment in message.attachments"
                  :key="attachment.id"
                  :href="attachment.download_url ? buildApiUrl(attachment.download_url) : undefined"
                  target="_blank"
                  rel="noreferrer"
                  class="inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs"
                  :class="
                    message.role === 'user'
                      ? 'border-white/15 bg-white/10 text-white'
                      : 'border-slate-200 bg-slate-50 text-slate-700'
                  "
                >
                  <AppIcon name="attachment" :size="12" />
                  {{ attachment.name }}
                </a>
              </div>
            </div>
          </article>
        </div>
      </div>

      <div class="border-t border-slate-100 px-5 py-5 sm:px-6">
        <div class="space-y-4">
          <Textarea
            v-model="composer"
            class="min-h-32 bg-white/92"
            :disabled="!currentSession || sending"
            placeholder="Ask directly, upload supporting documents when useful, and continue the same thread with follow-up questions."
          />

          <div class="flex flex-wrap items-start gap-3">
            <div class="min-w-[15rem] flex-1 sm:max-w-[20rem]">
              <Select v-model="modePreference">
                <SelectTrigger class="w-full rounded-2xl bg-white/90" size="sm">
                  <SelectValue placeholder="Select mode" />
                </SelectTrigger>
                <SelectContent class="rounded-2xl border-slate-100 bg-white/95 backdrop-blur-xl">
                  <SelectItem
                    v-for="option in modeOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    <div class="flex flex-col">
                      <span>{{ option.label }}</span>
                      <span class="text-xs text-slate-400">{{ option.hint }}</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              class="rounded-full"
              :disabled="!currentSession"
              @click="openFilePicker"
            >
              <AppIcon name="attachment" :size="16" />
              Add documents
            </Button>
            <Button
              class="rounded-full"
              :disabled="!currentSession || sending || !composer.trim()"
              @click="submit"
            >
              <AppIcon name="arrowRight" :size="16" />
              {{ sending ? "Sending…" : "Send message" }}
            </Button>
          </div>

          <div v-if="pendingFiles.length" class="flex flex-wrap gap-2">
            <Badge
              v-for="(file, index) in pendingFiles"
              :key="`${file.name}-${index}`"
              variant="outline"
              class="inline-flex items-center gap-2"
            >
              {{ file.name }}
              <button
                type="button"
                class="text-slate-400 hover:text-slate-700"
                @click="removeFile(index)"
              >
                ×
              </button>
            </Badge>
          </div>

          <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
