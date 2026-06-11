import { createApp } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, ScatterChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkAreaComponent,
  MarkPointComponent,
  MarkLineComponent,
  DataZoomComponent,
  TitleComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import App from './App.vue'

use([
  CanvasRenderer,
  LineChart,
  ScatterChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkAreaComponent,
  MarkPointComponent,
  MarkLineComponent,
  DataZoomComponent,
  TitleComponent,
])

const app = createApp(App)
app.component('VChart', VChart)
app.mount('#app')
