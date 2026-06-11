<template>
  <div class="card config-panel">
    <div class="config-row">

      <div class="control-group">
        <label class="control-label">Algorithm</label>
        <div class="toggle-group">
          <button
            :class="['toggle-btn', config.model === 'kmeans' && 'active']"
            @click="emit('change', { ...config, model: 'kmeans' })"
          >K-Means</button>
          <button
            :class="['toggle-btn', config.model === 'gmm' && 'active']"
            @click="emit('change', { ...config, model: 'gmm' })"
          >GMM</button>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label">Clusters K = <strong>{{ config.k }}</strong></label>
        <div class="slider-wrap">
          <input
            type="range"
            min="2"
            max="8"
            :value="config.k"
            @input="emit('change', { ...config, k: +$event.target.value })"
          />
          <div class="tick-row">
            <span v-for="n in 7" :key="n" :class="config.k === n + 1 ? 'tick active' : 'tick'">
              {{ n + 1 }}
            </span>
          </div>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label">Volatility Window</label>
        <div class="toggle-group">
          <button
            v-for="w in [7, 14, 21]"
            :key="w"
            :class="['toggle-btn', config.window === w && 'active']"
            @click="emit('change', { ...config, window: w })"
          >{{ w }}d</button>
        </div>
      </div>

      <button class="analyze-btn" :disabled="loading" @click="emit('analyze')">
        <svg v-if="loading" class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
        {{ loading ? 'Analyzing…' : 'Run Analysis' }}
      </button>

    </div>
  </div>
</template>

<script setup>
defineProps({ config: Object, loading: Boolean })
const emit = defineEmits(['change', 'analyze'])
</script>

<style scoped>
.card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 20px 24px;
}

.config-row {
  display: flex;
  align-items: flex-end;
  gap: 32px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 140px;
}

.control-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #64748b;
}

.toggle-group {
  display: flex;
  gap: 4px;
}

.toggle-btn {
  padding: 6px 14px;
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
}

.toggle-btn:hover { border-color: #3b82f6; color: #e2e8f0; }
.toggle-btn.active { background: #1d4ed8; border-color: #3b82f6; color: #fff; }

.slider-wrap { display: flex; flex-direction: column; gap: 4px; }

input[type="range"] {
  width: 180px;
  accent-color: #3b82f6;
  cursor: pointer;
}

.tick-row {
  display: flex;
  justify-content: space-between;
  width: 180px;
  padding: 0 2px;
}

.tick {
  font-size: 0.65rem;
  color: #475569;
  width: 16px;
  text-align: center;
}

.tick.active { color: #3b82f6; font-weight: 700; }

.analyze-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 24px;
  background: #1d4ed8;
  border: 1px solid #3b82f6;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  margin-left: auto;
}

.analyze-btn:hover:not(:disabled) { background: #2563eb; }
.analyze-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.spin-icon {
  width: 14px;
  height: 14px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
