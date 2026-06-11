<template>
  <div class="dashboard">
    <AppHeader />

    <div class="main-content">
      <DatasetUploader
        :active-source="activeSource"
        @upload-success="onUploadSuccess"
        @use-default="onUseDefault"
      />

      <ConfigPanel
        :config="config"
        :loading="loading"
        @change="Object.assign(config, $event)"
        @analyze="runAnalysis"
      />

      <div v-if="error" class="error-banner">
        <strong>Error:</strong> {{ error }}
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <div class="loading-text">
          <p>Running analysis…</p>
          <p class="loading-sub">
            {{ activeSource === 'custom' ? 'Custom dataset' : 'coin_Bitcoin.csv' }}
            · {{ config.model === 'gmm' ? 'GMM' : 'K-Means' }} K={{ config.k }}
          </p>
        </div>
      </div>

      <template v-else-if="analysis">
        <StatsCards :analysis="analysis" />
        <PriceChart :price-data="analysis.price_data" :regions="analysis.regions" />
        <div class="charts-row">
          <PcaScatter :pca-data="analysis.pca_data" />
          <ElbowChart :elbow-data="elbowData" :current-k="config.k" />
        </div>
        <ClusterTable :stats="analysis.cluster_stats" />
      </template>

      <div v-else-if="!loading && !error" class="empty-state">
        Click <strong>Run Analysis</strong> to start.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { fetchAnalysis, fetchElbow } from '../api/index.js'
import AppHeader from '../components/AppHeader.vue'
import DatasetUploader from '../components/DatasetUploader.vue'
import ConfigPanel from '../components/ConfigPanel.vue'
import StatsCards from '../components/StatsCards.vue'
import PriceChart from '../components/PriceChart.vue'
import PcaScatter from '../components/PcaScatter.vue'
import ElbowChart from '../components/ElbowChart.vue'
import ClusterTable from '../components/ClusterTable.vue'

const config = reactive({ k: 4, model: 'kmeans', window: 7 })
const analysis = ref(null)
const elbowData = ref([])
const loading = ref(false)
const error = ref(null)
const activeSource = ref('default')  // 'default' | 'custom'

async function runAnalysis() {
  loading.value = true
  error.value = null
  const useUploaded = activeSource.value === 'custom'
  try {
    const [analysisResult, elbowResult] = await Promise.all([
      fetchAnalysis({ k: config.k, model: config.model, window: config.window, use_uploaded: useUploaded }),
      fetchElbow({ k_max: 10, window: config.window, use_uploaded: useUploaded }),
    ])
    analysis.value = analysisResult
    elbowData.value = elbowResult.data
  } catch (e) {
    error.value = e.response?.data?.detail ?? e.message ?? 'Failed to connect to backend'
  } finally {
    loading.value = false
  }
}

function onUploadSuccess(_meta) {
  activeSource.value = 'custom'
  runAnalysis()
}

function onUseDefault() {
  activeSource.value = 'default'
  runAnalysis()
}

onMounted(runAnalysis)
</script>

<style scoped>
.dashboard { min-height: 100vh; background: #0f172a; }

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px 60px;
  display: grid;
  gap: 20px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 900px) {
  .charts-row { grid-template-columns: 1fr; }
}

.error-banner {
  background: #450a0a;
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 60px 24px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #334155;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

.loading-text p { color: #e2e8f0; font-weight: 600; }
.loading-sub { font-size: 0.8rem; color: #64748b; font-weight: 400; margin-top: 4px; }

.empty-state {
  text-align: center;
  padding: 60px;
  color: #64748b;
  font-size: 0.9rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
