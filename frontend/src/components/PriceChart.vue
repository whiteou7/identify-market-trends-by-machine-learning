<template>
  <div class="card chart-card">
    <div class="card-header">
      <h2 class="card-title">Bitcoin Price &amp; Market Regimes</h2>
      <p class="card-desc">Background colors indicate the cluster assigned to each time period</p>
    </div>
    <VChart class="chart" :option="option" :autoresize="true" />
    <div class="legend-row">
      <span
        v-for="stat in uniqueRegimes"
        :key="stat.name"
        class="legend-item"
      >
        <span class="legend-dot" :style="{ background: getClusterColor(stat.name) }" />
        {{ stat.name }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getClusterColor } from '../utils/colors.js'

const props = defineProps({
  priceData: { type: Array, default: () => [] },
  regions: { type: Array, default: () => [] },
})

const toTs = d => new Date(d).getTime()

const uniqueRegimes = computed(() => {
  const seen = new Set()
  return props.regions
    .filter(r => { if (seen.has(r.cluster_name)) return false; seen.add(r.cluster_name); return true })
    .map(r => ({ name: r.cluster_name }))
})

const option = computed(() => ({
  backgroundColor: 'transparent',
  animation: false,
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross', label: { backgroundColor: '#334155' } },
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#e2e8f0', fontSize: 12 },
    formatter(params) {
      const p = params[0]
      if (!p) return ''
      const d = p.data
      const ret = typeof d.log_return === 'number' ? (d.log_return * 100).toFixed(2) : 'N/A'
      const vol = typeof d.volatility === 'number' ? (d.volatility * 100).toFixed(3) : 'N/A'
      const color = getClusterColor(d.cluster_name)
      const price = Number(p.value[1]).toLocaleString('en-US', { maximumFractionDigits: 0 })
      return `<div style="line-height:1.8">
        <b>${p.axisValueLabel}</b><br/>
        Price: <b>$${price}</b><br/>
        Regime: <span style="color:${color};font-weight:700">${d.cluster_name ?? 'N/A'}</span><br/>
        Log Return: ${ret}%<br/>
        Volatility: ${vol}%
      </div>`
    },
  },
  grid: { left: '7%', right: '3%', top: '6%', bottom: '18%' },
  dataZoom: [
    {
      type: 'slider',
      bottom: 8,
      height: 24,
      borderColor: '#334155',
      fillerColor: 'rgba(59,130,246,0.1)',
      handleStyle: { color: '#3b82f6' },
      textStyle: { color: '#64748b' },
    },
    { type: 'inside' },
  ],
  xAxis: {
    type: 'time',
    axisLabel: { color: '#94a3b8', fontSize: 11 },
    axisLine: { lineStyle: { color: '#334155' } },
    splitLine: { show: false },
  },
  yAxis: {
    type: 'log',
    name: 'Price (USD)',
    nameTextStyle: { color: '#64748b', fontSize: 11 },
    axisLabel: {
      color: '#94a3b8',
      fontSize: 11,
      formatter: v => v >= 1000 ? `$${(v / 1000).toFixed(0)}K` : `$${v}`,
    },
    axisLine: { lineStyle: { color: '#334155' } },
    splitLine: { lineStyle: { color: '#334155', opacity: 0.4 } },
  },
  series: [
    {
      type: 'line',
      name: 'BTC/USD',
      data: props.priceData.map(d => ({
        value: [toTs(d.date), d.close],
        cluster_name: d.cluster_name,
        log_return: d.log_return,
        volatility: d.volatility,
      })),
      lineStyle: { width: 1.5, color: '#94a3b8' },
      showSymbol: false,
      emphasis: { disabled: true },
      markArea: {
        silent: true,
        data: props.regions.map(r => [
          {
            xAxis: toTs(r.start),
            itemStyle: { color: getClusterColor(r.cluster_name), opacity: 0.13 },
          },
          { xAxis: toTs(r.end) },
        ]),
      },
    },
  ],
}))
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

.chart { height: 400px; width: 100%; }

.legend-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #334155;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.775rem;
  color: #94a3b8;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}
</style>
