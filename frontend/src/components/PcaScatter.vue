<template>
  <div class="card chart-card">
    <div class="card-header">
      <h2 class="card-title">PCA Cluster Visualization</h2>
      <p class="card-desc">2D projection of [Log Return, Volatility, Momentum] via Principal Component Analysis</p>
    </div>
    <VChart class="chart" :option="option" :autoresize="true" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getClusterColor } from '../utils/colors.js'

const props = defineProps({
  pcaData: { type: Array, default: () => [] },
})

const option = computed(() => {
  // Group by cluster_name for separate series (correct legend + color per cluster)
  const groups = {}
  for (const d of props.pcaData) {
    if (!groups[d.cluster_name]) groups[d.cluster_name] = []
    groups[d.cluster_name].push([d.x, d.y, d.date, d.cluster_name])
  }

  const series = Object.entries(groups).map(([name, data]) => ({
    name,
    type: 'scatter',
    data,
    symbolSize: 4,
    itemStyle: { color: getClusterColor(name), opacity: 0.65 },
    emphasis: { itemStyle: { opacity: 1, symbolSize: 7 } },
    large: true,
    largeThreshold: 500,
  }))

  return {
    backgroundColor: 'transparent',
    animation: false,
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0', fontSize: 11 },
      formatter(params) {
        const [x, y, date, name] = params.data
        const color = getClusterColor(name)
        return `<b>${date}</b><br/>
          Regime: <span style="color:${color};font-weight:700">${name}</span><br/>
          PC1: ${x.toFixed(3)}<br/>PC2: ${y.toFixed(3)}`
      },
    },
    legend: {
      top: 0,
      right: 0,
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
    },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%' },
    xAxis: {
      type: 'value',
      name: 'PC1',
      nameTextStyle: { color: '#64748b' },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { lineStyle: { color: '#334155', opacity: 0.4 } },
    },
    yAxis: {
      type: 'value',
      name: 'PC2',
      nameTextStyle: { color: '#64748b' },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { lineStyle: { color: '#334155', opacity: 0.4 } },
    },
    series,
  }
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

.chart { height: 380px; width: 100%; }
</style>
