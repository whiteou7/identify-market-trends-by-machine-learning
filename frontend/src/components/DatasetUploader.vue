<template>
  <div class="card dataset-card">
    <div class="card-title-row">
      <h2 class="card-title">Dataset</h2>
      <span class="active-badge" :class="activeSource">
        {{ activeSource === 'custom' ? 'Custom' : 'Default' }}
      </span>
    </div>

    <div class="panels">

      <!-- Default dataset panel -->
      <div class="panel" :class="{ active: activeSource === 'default' }">
        <div class="panel-header">
          <span class="panel-label">Default</span>
        </div>
        <div class="panel-body">
          <p class="file-name">coin_Bitcoin.csv</p>
          <p class="meta-row">2,991 daily rows</p>
          <p class="meta-row">Apr 2013 → Jul 2021</p>
          <p class="meta-row dim">BTC/USD · Kaggle</p>
        </div>
        <div class="panel-footer">
          <button
            v-if="activeSource === 'custom'"
            class="btn-ghost"
            @click="$emit('use-default')"
          >Use Default</button>
          <span v-else class="active-indicator">● Active</span>
        </div>
      </div>

      <!-- Custom upload panel -->
      <div
        class="panel upload-panel"
        :class="{ active: activeSource === 'custom', dragging: isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        @click="openFilePicker"
      >
        <!-- Empty / drag state -->
        <template v-if="!meta && !uploading && !uploadError">
          <div class="drop-hint">
            <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M16 10l-4-4m0 0L8 10m4-4v12"/>
            </svg>
            <p class="drop-label">Drop CSV or click to browse</p>
            <p class="drop-sub">Supports Yahoo Finance, Binance, CoinGecko, Kaggle…</p>
          </div>
        </template>

        <!-- Uploading state -->
        <template v-else-if="uploading">
          <div class="drop-hint">
            <div class="mini-spinner" />
            <p class="drop-label">Detecting columns…</p>
          </div>
        </template>

        <!-- Error state -->
        <template v-else-if="uploadError">
          <div class="drop-hint error-state" @click.stop>
            <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p class="error-msg">{{ uploadError }}</p>
            <button class="btn-ghost small" @click.stop="resetUpload">Try again</button>
          </div>
        </template>

        <!-- Success state -->
        <template v-else-if="meta">
          <div class="panel-header" @click.stop>
            <span class="panel-label">Custom</span>
          </div>
          <div class="panel-body" @click.stop>
            <p class="file-name">{{ meta.filename }}</p>
            <p class="meta-row">{{ meta.daily_rows.toLocaleString() }} daily rows</p>
            <p class="meta-row">{{ meta.date_range.start }} → {{ meta.date_range.end }}</p>
            <p class="meta-row dim">
              Date: <code>{{ meta.detected.date_col }}</code>
              · Close: <code>{{ meta.detected.close_col }}</code>
              <span v-if="meta.detected.is_unix_timestamp"> · Unix ts</span>
            </p>
          </div>
          <div class="panel-footer" @click.stop>
            <button class="btn-ghost small" @click="resetUpload">Re-upload</button>
            <span v-if="activeSource === 'custom'" class="active-indicator">● Active</span>
          </div>
        </template>

      </div>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      accept=".csv"
      style="display:none"
      @change="onFileChange"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadDataset } from '../api/index.js'

const props = defineProps({
  activeSource: { type: String, default: 'default' },  // 'default' | 'custom'
})
const emit = defineEmits(['upload-success', 'use-default'])

const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref(null)
const meta = ref(null)

function openFilePicker() {
  if (meta.value || uploading.value) return
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) handleFile(file)
  // Reset input so same file can be re-selected
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) handleFile(file)
}

async function handleFile(file) {
  uploading.value = true
  uploadError.value = null
  try {
    const result = await uploadDataset(file)
    meta.value = result
    emit('upload-success', result)
  } catch (e) {
    uploadError.value = e.response?.data?.detail ?? e.message ?? 'Upload failed'
  } finally {
    uploading.value = false
  }
}

function resetUpload() {
  meta.value = null
  uploadError.value = null
}
</script>

<style scoped>
.card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 20px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
}

.active-badge {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 20px;
}
.active-badge.default { background: #1d4ed820; color: #60a5fa; border: 1px solid #1d4ed8; }
.active-badge.custom  { background: #06402020; color: #34d399; border: 1px solid #065f46; }

.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 700px) {
  .panels { grid-template-columns: 1fr; }
}

.panel {
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.15s;
  min-height: 130px;
}

.panel.active { border-color: #3b82f6; }

.upload-panel {
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.upload-panel:hover:not(.active) { border-color: #475569; }
.upload-panel.dragging {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.04);
}

.panel-header { margin-bottom: 2px; }
.panel-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #475569;
}

.panel-body { flex: 1; }

.file-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-row {
  font-size: 0.775rem;
  color: #94a3b8;
  line-height: 1.6;
}

.meta-row.dim { color: #475569; }

code {
  font-family: 'Menlo', 'Monaco', monospace;
  font-size: 0.72rem;
  background: #0f172a;
  padding: 1px 4px;
  border-radius: 3px;
  color: #93c5fd;
}

.panel-footer {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.active-indicator {
  font-size: 0.75rem;
  color: #3b82f6;
  font-weight: 600;
}

.btn-ghost {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  background: transparent;
  border: 1px solid #334155;
  padding: 4px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-ghost:hover { color: #e2e8f0; border-color: #475569; }
.btn-ghost.small { padding: 3px 9px; }

/* Drop hint (idle / dragging state) */
.drop-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 100%;
  min-height: 100px;
  text-align: center;
  padding: 8px;
}

.upload-icon {
  width: 28px;
  height: 28px;
  color: #475569;
}

.drop-label {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

.drop-sub {
  font-size: 0.7rem;
  color: #475569;
}

/* Uploading spinner */
.mini-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #334155;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Error state */
.error-state { cursor: default; }

.error-icon {
  width: 24px;
  height: 24px;
  color: #ef4444;
}

.error-msg {
  font-size: 0.75rem;
  color: #fca5a5;
  text-align: center;
  max-width: 220px;
  line-height: 1.4;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
