<template>
  <div class="card chart-card">
    <div class="card-header">
      <h2 class="card-title">Optimal K Selection</h2>
      <p class="card-desc">Elbow Method (inertia ↓) + Silhouette Score (↑ better). Vertical line = current K.</p>
    </div>
    <VChart class="chart" :option="option" :autoresize="true" />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  elbowData: { type: Array, default: () => [] },
  currentK: { type: Number, default: 4 },
})

const option = computed(() => {
  const ks = props.elbowData.map(d => String(d.k))
  const inertias = props.elbowData.map(d => +d.inertia.toFixed(2))
  const silhouettes = props.elbowData.map(d => +d.silhouette.toFixed(4))

  return {
    backgroundColor: 'transparent',
    animation: false,
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
      formatter(params) {
        const k = params[0].axisValueLabel
        const lines = params.map(p =>
          `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color};margin-right:6px"></span>${p.seriesName}: <b>${p.value}</b>`
        )
        return `<b>K = ${k}</b><br/>${lines.join('<br/>')}`
      },
    },
    legend: {
      top: 0,
      right: 0,
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 14,
      itemHeight: 3,
    },
    grid: { left: '12%', right: '12%', top: '14%', bottom: '8%' },
    xAxis: {
      type: 'category',
      data: ks,
      name: 'K',
      nameTextStyle: { color: '#64748b' },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: 'Inertia',
        nameTextStyle: { color: '#f59e0b', fontSize: 11 },
        axisLabel: { color: '#94a3b8', fontSize: 10, formatter: v => v > 999 ? `${(v/1000).toFixed(1)}K` : v },
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { lineStyle: { color: '#334155', opacity: 0.4 } },
      },
      {
        type: 'value',
        name: 'Silhouette',
        nameTextStyle: { color: '#10b981', fontSize: 11 },
        min: 0,
        max: 1,
        axisLabel: { color: '#94a3b8', fontSize: 10 },
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: 'Inertia',
        type: 'line',
        yAxisIndex: 0,
        data: inertias,
        smooth: true,
        lineStyle: { color: '#f59e0b', width: 2 },
        itemStyle: { color: '#f59e0b' },
        symbol: 'circle',
        symbolSize: 6,
        markLine: {
          silent: true,
          symbol: 'none',
          data: [{ xAxis: String(props.currentK), lineStyle: { color: '#3b82f6', type: 'dashed', width: 1.5 } }],
          label: { formatter: `K=${props.currentK}`, color: '#3b82f6', fontSize: 10 },
        },
      },
      {
        name: 'Silhouette Score',
        type: 'line',
        yAxisIndex: 1,
        data: silhouettes,
        smooth: true,
        lineStyle: { color: '#10b981', width: 2 },
        itemStyle: { color: '#10b981' },
        symbol: 'circle',
        symbolSize: 6,
        markPoint: {
          data: [{ type: 'max', name: 'Best K', label: { color: '#10b981', fontSize: 10 } }],
          symbol: 'pin',
          symbolSize: 28,
          itemStyle: { color: '#10b981' },
        },
      },
    ],
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
