<template>
  <div class="stats-grid">

    <div class="stat-card">
      <div class="stat-label">Silhouette Score</div>
      <div class="stat-value" :style="{ color: silColor }">
        {{ analysis.silhouette_score.toFixed(3) }}
      </div>
      <div class="stat-desc">{{ silDesc }}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">Algorithm</div>
      <div class="stat-value">{{ analysis.model === 'gmm' ? 'GMM' : 'K-Means' }}</div>
      <div class="stat-desc">{{ analysis.model === 'gmm' ? 'Soft clustering' : 'Hard clustering' }}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">Clusters (K)</div>
      <div class="stat-value">{{ analysis.k }}</div>
      <div class="stat-desc">Market regimes identified</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">Days Analyzed</div>
      <div class="stat-value">{{ analysis.total_days.toLocaleString() }}</div>
      <div class="stat-desc">After feature computation</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">Date Range</div>
      <div class="stat-value date-value">{{ analysis.date_range.start }}</div>
      <div class="stat-desc">→ {{ analysis.date_range.end }}</div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ analysis: Object })

const silColor = computed(() => {
  const s = props.analysis.silhouette_score
  if (s >= 0.5) return '#10b981'
  if (s >= 0.3) return '#f59e0b'
  return '#ef4444'
})

const silDesc = computed(() => {
  const s = props.analysis.silhouette_score
  if (s >= 0.5) return 'Good separation'
  if (s >= 0.3) return 'Fair separation'
  return 'Poor separation'
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

@media (max-width: 1100px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 16px;
}

.stat-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: #64748b;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-top: 6px;
  line-height: 1;
}

.date-value { font-size: 0.9rem; padding-top: 4px; }

.stat-desc {
  font-size: 0.72rem;
  color: #475569;
  margin-top: 6px;
}
</style>
