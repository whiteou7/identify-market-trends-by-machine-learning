<template>
  <header class="app-header">
    <div class="header-inner">
      <div>
        <h1 class="title">Bitcoin Market Regime Classifier</h1>
        <p class="subtitle">
          K-Means &amp; GMM clustering on BTC/USD daily data · Feature engineering: Log Return, Volatility, Momentum
        </p>
      </div>
      <div class="badge-row">
        <span class="badge">Phases 1–5</span>
        <span class="badge">PCA Visualization</span>
        <span class="badge">2013 – 2021</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: #1e293b;
  border-bottom: 1px solid #334155;
  padding: 20px 0;
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin-top: 4px;
}

.badge-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: #0f172a;
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 3px 10px;
  border-radius: 20px;
}
</style>
