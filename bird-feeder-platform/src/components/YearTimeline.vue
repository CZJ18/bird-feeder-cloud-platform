<template>
  <div class="year-timeline">
    <div class="timeline-line">
      <span></span>
    </div>
    <button
      v-for="year in years"
      :key="year"
      type="button"
      :class="{ active: year === selectedYear }"
      @click="selectYear(year)"
    >
      <i></i>
      <span class="digital">{{ year }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { years } from '@/data/mockData'

const emit = defineEmits<{
  select: [year: number]
}>()

const selectedYear = ref(2025)
const selectYear = (year: number) => {
  selectedYear.value = year
  emit('select', year)
}
</script>

<style scoped>
.year-timeline {
  position: relative;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 4px;
  padding: 12px 4px 0;
}

.timeline-line {
  position: absolute;
  left: 9%;
  right: 9%;
  top: 22px;
  height: 2px;
  background: rgba(53, 232, 255, 0.18);
}

.timeline-line span {
  display: block;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, var(--blue), var(--cyan), var(--green));
  box-shadow: 0 0 12px rgba(53, 232, 255, 0.55);
}

button {
  position: relative;
  z-index: 1;
  display: grid;
  justify-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}

button:hover,
button:focus-visible {
  color: var(--cyan);
  transform: translateY(-1px);
}

button i {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(53, 232, 255, 0.72);
  border-radius: 999px;
  background: #071426;
  box-shadow: 0 0 12px rgba(53, 232, 255, 0.36);
}

button.active {
  color: var(--green);
}

button.active i {
  background: var(--green);
  border-color: rgba(255, 255, 255, 0.85);
  box-shadow: 0 0 18px rgba(87, 255, 173, 0.8);
}
</style>
