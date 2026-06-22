<template>
  <aside class="left-panel">
    <section class="brand-block">
      <div class="brand-mark">HUNAU</div>
      <div>
        <p>智慧校园生态数据中心</p>
        <h1>湖南农业大学鸟类监测平台</h1>
      </div>
    </section>

    <HeaderStats @select="emit('selectStat', $event)" />

    <section class="screen-panel panel-block species-block">
      <h2 class="panel-title">物种组成与多样性分析</h2>
      <SpeciesBars @select="emit('selectSpecies', $event)" />
    </section>

    <section class="screen-panel panel-block network-block">
      <h2 class="panel-title">数据采集信息</h2>
      <DataNetwork @select="emit('selectNode', $event)" @select-hub="emit('selectHub')" />
    </section>
  </aside>
</template>

<script setup lang="ts">
import HeaderStats from './HeaderStats.vue'
import SpeciesBars from './SpeciesBars.vue'
import DataNetwork from './DataNetwork.vue'
import type { NetworkNode, OverviewStat, SpeciesBar } from '@/data/mockData'

const emit = defineEmits<{
  selectStat: [item: OverviewStat]
  selectSpecies: [item: SpeciesBar]
  selectNode: [node: NetworkNode]
  selectHub: []
}>()
</script>

<style scoped>
.left-panel {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) minmax(190px, 0.74fr);
  gap: 14px;
  min-height: 0;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 78px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 70px;
  height: 54px;
  border: 1px solid rgba(53, 232, 255, 0.38);
  border-radius: 8px;
  color: var(--green);
  background: rgba(53, 232, 255, 0.08);
  box-shadow: 0 0 24px rgba(53, 232, 255, 0.14);
  font-family: 'Orbitron', monospace;
  font-size: 13px;
  font-weight: 800;
}

.brand-block p {
  margin: 0 0 4px;
  color: var(--text-muted);
  font-size: 12px;
}

.brand-block h1 {
  margin: 0;
  color: var(--text-main);
  font-size: clamp(19px, 1.45vw, 30px);
  line-height: 1.16;
  font-weight: 900;
  text-shadow: 0 0 20px rgba(53, 232, 255, 0.35);
}

.panel-block {
  min-height: 0;
  padding: 16px;
}

.species-block,
.network-block {
  display: flex;
  flex-direction: column;
}
</style>
