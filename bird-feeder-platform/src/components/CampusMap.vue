<template>
  <div class="campus-map">
    <div class="map-river river-a"></div>
    <div class="map-river river-b"></div>
    <div class="map-road road-a"></div>
    <div class="map-road road-b"></div>

    <div
      v-for="point in points"
      :key="point.name"
      class="map-point"
      :class="{ offline: point.status === '离线' }"
      :style="{
        left: `${point.x}%`,
        top: `${point.y}%`,
        '--size': `${Math.max(14, point.heat / 3)}px`
      }"
      role="button"
      tabindex="0"
      @click="emit('select', point)"
      @keydown.enter.prevent="emit('select', point)"
      @keydown.space.prevent="emit('select', point)"
    >
      <i></i>
      <span>{{ point.name }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { mapPoints, type MapPoint } from '@/data/mockData'

const emit = defineEmits<{
  select: [point: MapPoint]
}>()

const points = mapPoints
</script>

<style scoped>
.campus-map {
  position: relative;
  height: 100%;
  min-height: 280px;
  overflow: hidden;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background:
    linear-gradient(120deg, rgba(87, 255, 173, 0.08), transparent 32%),
    linear-gradient(35deg, transparent 0 42%, rgba(53, 232, 255, 0.08) 42% 45%, transparent 45%),
    radial-gradient(circle at 38% 48%, rgba(53, 232, 255, 0.18), transparent 18%),
    rgba(4, 18, 34, 0.88);
}

.campus-map::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(53, 232, 255, 0.09) 1px, transparent 1px),
    linear-gradient(90deg, rgba(53, 232, 255, 0.09) 1px, transparent 1px);
  background-size: 26px 26px;
  mask-image: radial-gradient(circle at center, black, transparent 82%);
}

.map-river,
.map-road {
  position: absolute;
  border-radius: 999px;
  transform-origin: center;
}

.map-river {
  height: 36px;
  background: linear-gradient(90deg, rgba(53, 232, 255, 0), rgba(53, 232, 255, 0.24), rgba(53, 232, 255, 0));
  filter: blur(0.2px);
}

.river-a {
  left: 8%;
  top: 53%;
  width: 82%;
  transform: rotate(-14deg);
}

.river-b {
  left: 24%;
  top: 24%;
  width: 50%;
  transform: rotate(22deg);
}

.map-road {
  width: 72%;
  height: 2px;
  background: rgba(255, 255, 255, 0.16);
}

.road-a {
  left: 13%;
  top: 36%;
  transform: rotate(18deg);
}

.road-b {
  left: 20%;
  top: 70%;
  transform: rotate(-12deg);
}

.map-point {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 7px;
  transform: translate(-50%, -50%);
  z-index: 2;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.map-point:hover,
.map-point:focus-visible {
  transform: translate(-50%, -50%) scale(1.06);
}

.map-point i {
  position: relative;
  width: var(--size);
  height: var(--size);
  border: 2px solid rgba(255, 255, 255, 0.86);
  border-radius: 999px;
  background: radial-gradient(circle, var(--green), var(--cyan));
  box-shadow: 0 0 18px rgba(53, 232, 255, 0.92);
}

.map-point.offline i {
  background: radial-gradient(circle, var(--danger), #593046);
  box-shadow: 0 0 18px rgba(255, 95, 134, 0.78);
}

.map-point i::after {
  content: '';
  position: absolute;
  inset: -10px;
  border: 1px solid rgba(53, 232, 255, 0.5);
  border-radius: inherit;
  animation: mapPulse 2.2s ease-out infinite;
}

.map-point span {
  padding: 4px 7px;
  border: 1px solid rgba(53, 232, 255, 0.24);
  border-radius: 6px;
  background: rgba(2, 11, 24, 0.76);
  color: #dffaff;
  font-size: 12px;
  white-space: nowrap;
}

@keyframes mapPulse {
  0% {
    opacity: 0.85;
    transform: scale(0.65);
  }
  100% {
    opacity: 0;
    transform: scale(1.55);
  }
}
</style>
