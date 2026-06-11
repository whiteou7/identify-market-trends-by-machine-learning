<template>
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">Cluster Interpretation</h2>
      <p class="card-desc">
        Phase 4: Centroid analysis — clusters are labelled by comparing avg return and volatility
      </p>
    </div>

    <div class="table-wrap">
      <table class="cluster-table">
        <thead>
          <tr>
            <th>Regime</th>
            <th>Days</th>
            <th>Share</th>
            <th title="Average daily log return">Avg Return</th>
            <th title="Average rolling volatility (std of log returns)">Avg Volatility</th>
            <th title="Average momentum (price change over window)">Avg Momentum</th>
            <th>Interpretation</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="stat in sortedStats"
            :key="stat.id"
            :style="{ '--c': getClusterColor(stat.name) }"
            class="cluster-row"
          >
            <td class="name-cell">
              <span class="color-dot" :style="{ background: getClusterColor(stat.name) }" />
              {{ stat.name }}
            </td>
            <td>{{ stat.count.toLocaleString() }}</td>
            <td>
              <div class="bar-wrap">
                <div class="bar" :style="{ width: stat.pct + '%', background: getClusterColor(stat.name) }" />
                <span>{{ stat.pct }}%</span>
              </div>
            </td>
            <td :class="stat.avg_return >= 0 ? 'positive' : 'negative'">
              {{ (stat.avg_return * 100).toFixed(3) }}%
            </td>
            <td>{{ (stat.avg_volatility * 100).toFixed(3) }}%</td>
            <td :class="stat.avg_momentum >= 0 ? 'positive' : 'negative'">
              {{ (stat.avg_momentum * 100).toFixed(2) }}%
            </td>
            <td class="interp-cell">{{ interpretations[stat.name] ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getClusterColor, CLUSTER_ORDER } from '../utils/colors.js'

const props = defineProps({ stats: { type: Array, default: () => [] } })

const interpretations = {
  'Bull Market':     'Rising prices, positive returns, moderate volatility',
  'Bear Market':     'Falling prices, negative returns, often high volatility',
  'High Volatility': 'Large price swings, uncertain direction, risk-off environment',
  'Sideways':        'Low momentum, tight range, market consolidation',
  'Weak Bull':       'Mildly positive trend, lower conviction than Bull',
  'Weak Bear':       'Mildly negative trend, lower conviction than Bear',
  'Transition':      'Regime change in progress, mixed signals',
  'Range Bound':     'Price oscillating within a defined band',
  'Accumulation':    'Low volatility, potential distribution or accumulation phase',
}

const sortedStats = computed(() => {
  return [...props.stats].sort((a, b) => {
    const ai = CLUSTER_ORDER.indexOf(a.name)
    const bi = CLUSTER_ORDER.indexOf(b.name)
    if (ai === -1 && bi === -1) return a.id - b.id
    if (ai === -1) return 1
    if (bi === -1) return -1
    return ai - bi
  })
})
</script>

<style scoped>
.card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 20px;
}

.card-header { margin-bottom: 16px; }

.card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
}

.card-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 2px;
}

.table-wrap { overflow-x: auto; }

.cluster-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.cluster-table th {
  text-align: left;
  padding: 8px 12px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.cluster-table td {
  padding: 11px 12px;
  border-bottom: 1px solid #1e293b;
  color: #cbd5e1;
  vertical-align: middle;
}

.cluster-row {
  border-left: 3px solid var(--c);
  transition: background 0.1s;
}

.cluster-row:hover td { background: rgba(255,255,255,0.025); }

.name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #f1f5f9;
  white-space: nowrap;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar {
  height: 6px;
  border-radius: 3px;
  min-width: 2px;
  max-width: 120px;
  opacity: 0.75;
}

.positive { color: #10b981; }
.negative { color: #ef4444; }

.interp-cell {
  font-size: 0.75rem;
  color: #64748b;
  max-width: 280px;
}
</style>
