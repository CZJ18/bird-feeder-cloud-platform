<template>
  <div class="species-bars">
    <button
      v-for="item in items"
      :key="item.name"
      type="button"
      class="species-row"
      :class="{ active: selectedName === item.name }"
      @click="selectItem(item)"
    >
      <div class="species-meta">
        <span>{{ item.name }}</span>
        <strong class="digital">{{ item.value }}</strong>
      </div>
      <div class="bar-track">
        <span class="bar-fill" :style="{ width: `${maxValue ? (item.value / maxValue) * 100 : 0}%` }"></span>
      </div>
    </button>
    <p v-if="!items.length" class="empty-text">暂无真实物种事件</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { speciesBars, type SpeciesBar } from '@/data/mockData'

const emit = defineEmits<{
  select: [item: SpeciesBar]
}>()

const items = ref<SpeciesBar[]>([])
const selectedName = ref('')
const maxValue = computed(() => Math.max(0, ...items.value.map(item => item.value)))

const loadSpecies = async () => {
  const res = await request<ApiResponse<{ regionData: Array<{ name: string; value: number }> }>>({
    url: '/species/distribution',
    params: { top: 7 }
  })
  if (!res.data.regionData.length) {
    items.value = speciesBars
    selectedName.value = items.value[0]?.name || ''
    return
  }
  items.value = res.data.regionData.map(item => ({
    name: item.name,
    value: item.value,
    latin: '--',
    confidence: 0,
    protection: '真实 MQTT 事件聚合'
  }))
  selectedName.value = items.value[0]?.name || ''
}

const selectItem = (item: SpeciesBar) => {
  selectedName.value = item.name
  emit('select', item)
}

onMounted(loadSpecies)
</script>

<style scoped>
.species-bars {
  display: grid;
  gap: 10px;
}

.species-row {
  display: grid;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  padding: 4px;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.species-row:hover,
.species-row:focus-visible,
.species-row.active {
  border-color: rgba(53, 232, 255, 0.28);
  background: rgba(53, 232, 255, 0.08);
}

.species-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #cbe8f3;
  font-size: clamp(12px, 0.78vw, 14px);
}

.species-meta strong {
  color: var(--green);
  font-size: 14px;
  text-shadow: 0 0 12px rgba(87, 255, 173, 0.42);
}

.bar-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(29, 62, 83, 0.72);
}

.bar-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #1477ff, #35e8ff 56%, #57ffad);
  box-shadow: 0 0 14px rgba(53, 232, 255, 0.68);
}

.empty-text {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}
</style>
