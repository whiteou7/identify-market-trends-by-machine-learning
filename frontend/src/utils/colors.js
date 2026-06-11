export const CLUSTER_COLORS = {
  'Bull Market':     '#10b981',
  'Bear Market':     '#ef4444',
  'High Volatility': '#f59e0b',
  'Sideways':        '#3b82f6',
  'Weak Bull':       '#34d399',
  'Weak Bear':       '#f87171',
  'Transition':      '#a78bfa',
  'Range Bound':     '#60a5fa',
  'Accumulation':    '#818cf8',
}

export function getClusterColor(name) {
  return CLUSTER_COLORS[name] ?? '#94a3b8'
}

// Preferred display order for cluster table rows
export const CLUSTER_ORDER = [
  'Bull Market',
  'Bear Market',
  'High Volatility',
  'Sideways',
  'Weak Bull',
  'Weak Bear',
  'Transition',
  'Range Bound',
  'Accumulation',
]
