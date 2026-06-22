<template>
  <section class="screen-panel chart-card">
    <div class="card-head">
      <h2 class="panel-title">{{ title }}</h2>
      <button v-if="actionLabel" type="button" @click="emit('action')">{{ actionLabel }}</button>
    </div>
    <div class="chart-body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  actionLabel?: string
}>()

const emit = defineEmits<{
  action: []
}>()
</script>

<style scoped>
.chart-card {
  display: flex;
  min-height: 0;
  flex-direction: column;
  padding: 14px;
}

.chart-body {
  flex: 1;
  min-height: 0;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card-head .panel-title {
  margin-bottom: 10px;
}

.card-head button {
  height: 26px;
  border: 1px solid rgba(53, 232, 255, 0.28);
  border-radius: 6px;
  background: rgba(53, 232, 255, 0.08);
  color: var(--cyan);
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.card-head button:hover {
  border-color: rgba(87, 255, 173, 0.58);
  color: var(--green);
}
</style>
