<template>
  <section class="screen-panel filter-panel">
    <h2 class="panel-title">监测筛选与数据上传</h2>
    <label>
      <span>摄像头选择</span>
      <select v-model="camera">
        <option value="CAM-01">摄像头 1 号（ID:1）</option>
        <option value="CAM-02">摄像头 2 号（ID:2）</option>
        <option value="EDGE-01">识别终端 1 号（ID:3）</option>
      </select>
    </label>

    <div class="time-range">
      <label>
        <span>开始时间</span>
        <input v-model="startTime" type="datetime-local" />
      </label>
      <label>
        <span>结束时间</span>
        <input v-model="endTime" type="datetime-local" />
      </label>
    </div>

    <div class="upload-row">
      <label class="file-button">
        {{ fileName || '选择文件' }}
        <input type="file" accept="image/*,video/*" @change="onFileChange" />
      </label>
      <button type="button" @click="upload">开始上传</button>
    </div>

    <div class="action-row">
      <button type="button" class="ghost-button" @click="applyFilter">应用筛选</button>
      <p>{{ statusText }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  apply: [payload: { camera: string; startTime: string; endTime: string }]
  upload: [payload: { camera: string; fileName: string }]
}>()

const camera = ref('CAM-01')
const startTime = ref('2026-06-16T08:00')
const endTime = ref('2026-06-16T18:00')
const fileName = ref('')
const statusText = ref('等待筛选或上传操作')

const onFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  fileName.value = input.files?.[0]?.name ?? ''
  statusText.value = fileName.value ? `已选择：${fileName.value}` : '等待筛选或上传操作'
}

const applyFilter = () => {
  const payload = { camera: camera.value, startTime: startTime.value, endTime: endTime.value }
  statusText.value = `已应用 ${camera.value} 的时间筛选`
  emit('apply', payload)
}

const upload = () => {
  if (!fileName.value) {
    statusText.value = '请先选择图片或视频文件'
    return
  }
  statusText.value = `${fileName.value} 已加入上传队列`
  emit('upload', { camera: camera.value, fileName: fileName.value })
}
</script>

<style scoped>
.filter-panel {
  display: grid;
  gap: 10px;
  padding: 14px;
}

label {
  display: grid;
  gap: 6px;
  color: var(--text-muted);
  font-size: 12px;
}

select,
input {
  width: 100%;
  height: 34px;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 6px;
  outline: none;
  background: rgba(2, 12, 26, 0.72);
  color: var(--text-main);
  padding: 0 10px;
}

select:focus,
input:focus {
  border-color: rgba(87, 255, 173, 0.72);
}

.time-range {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.upload-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
}

.file-button,
button {
  display: grid;
  place-items: center;
  min-width: 0;
  height: 36px;
  border: 1px solid rgba(53, 232, 255, 0.34);
  border-radius: 6px;
  background: linear-gradient(90deg, rgba(21, 108, 255, 0.82), rgba(53, 232, 255, 0.72));
  color: #f3fdff;
  cursor: pointer;
  font-weight: 700;
  box-shadow: 0 0 16px rgba(53, 232, 255, 0.16);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-button:hover,
button:hover {
  box-shadow: 0 0 24px rgba(53, 232, 255, 0.34);
}

.ghost-button {
  background: rgba(53, 232, 255, 0.08);
}

.file-button input {
  display: none;
}

.action-row {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.action-row p {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
