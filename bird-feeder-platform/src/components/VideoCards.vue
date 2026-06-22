<template>
  <div class="video-grid">
    <article v-for="item in videos" :key="item.title" class="video-card" :class="`tone-${item.tone}`">
      <button type="button" class="video-cover" @click="emit('open', item)">
        <video v-if="item.videoUrl" :src="item.videoUrl" muted preload="metadata" playsinline />
        <img v-else :src="item.image" :alt="item.title" loading="lazy" />
        <div class="scan-line"></div>
        <span>{{ item.camera }}</span>
        <strong>{{ item.species }}</strong>
      </button>
      <div class="video-caption">{{ item.title }}</div>
      <div class="video-controls">
        <button type="button" class="play-button" :aria-label="isPlaying(item) ? '暂停' : '播放'" @click="toggle(item.title)">
          {{ isPlaying(item) ? 'Ⅱ' : '▶' }}
        </button>
        <span class="digital">{{ isPlaying(item) ? '0:08' : '0:00' }} / {{ item.duration }}</span>
        <button type="button" class="icon-button" aria-label="打开图片" @click="emit('open', item)">⤢</button>
        <button type="button" class="icon-button" aria-label="标记精彩" @click="markFavorite(item.title)">★</button>
      </div>
      <div class="progress">
        <span :style="{ width: isPlaying(item) ? '38%' : favoriteTitle === item.title ? '100%' : '0%' }"></span>
      </div>
    </article>
    <p v-if="!videos.length" class="empty-text">暂无真实精彩瞬间</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import request, { resolveAssetUrl } from '@/api/request'
import type { ApiResponse } from '@/types'
import { videoCards, type VideoCard } from '@/data/mockData'

interface MomentApiRow {
  id: number
  title: string
  videoUrl?: string
  coverImage?: string
}

const emit = defineEmits<{
  open: [item: VideoCard]
}>()

const videos = ref<VideoCard[]>([])
const playingTitle = ref('')
const favoriteTitle = ref('')

const isPlaying = (item: VideoCard) => playingTitle.value === item.title

const toggle = (title: string) => {
  playingTitle.value = playingTitle.value === title ? '' : title
}

const markFavorite = (title: string) => {
  favoriteTitle.value = favoriteTitle.value === title ? '' : title
}

const loadMoments = async () => {
  const res = await request<ApiResponse<{ regionData: MomentApiRow[] }>>({ url: '/moments', params: { limit: 3 } })
  if (!res.data.regionData.length) {
    videos.value = videoCards
    return
  }
  videos.value = res.data.regionData.map(item => ({
    title: item.title,
    duration: '0:00',
    tone: 'cyan',
    camera: `MOMENT-${item.id}`,
    species: '--',
    time: '--',
    image: resolveAssetUrl(item.coverImage || ''),
    videoUrl: resolveAssetUrl(item.videoUrl || ''),
    description: item.videoUrl ? `视频地址：${item.videoUrl}` : '管理员添加的真实精彩瞬间'
  }))
}

onMounted(loadMoments)
</script>

<style scoped>
.video-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  min-height: 0;
}

.video-card {
  overflow: hidden;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background: rgba(5, 16, 31, 0.78);
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.video-card:hover {
  border-color: rgba(87, 255, 173, 0.56);
  box-shadow: 0 0 24px rgba(53, 232, 255, 0.16);
  transform: translateY(-2px);
}

.video-cover {
  position: relative;
  display: block;
  width: 100%;
  height: clamp(82px, 10.8vh, 128px);
  overflow: hidden;
  border: 0;
  background: #071426;
  cursor: zoom-in;
  padding: 0;
}

.video-cover img,
.video-cover video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  filter: saturate(1.08) contrast(1.04) brightness(0.78);
  transition: transform 0.35s ease, filter 0.35s ease;
}

.video-cover:hover img,
.video-cover:focus-visible img {
  transform: scale(1.05);
  filter: saturate(1.14) contrast(1.05) brightness(0.92);
}

.video-cover::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 100% 7px;
  opacity: 0.28;
  z-index: 1;
}

.video-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(3, 9, 21, 0.08), rgba(3, 9, 21, 0.62));
  z-index: 1;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 2px;
  background: var(--cyan);
  box-shadow: 0 0 14px rgba(53, 232, 255, 0.9);
  animation: scan 3s linear infinite;
  z-index: 2;
}

.video-cover span,
.video-cover strong {
  position: absolute;
  z-index: 2;
}

.video-cover span {
  left: 10px;
  top: 8px;
  color: var(--green);
  font-family: 'Orbitron', monospace;
  font-size: 11px;
}

.video-cover strong {
  right: 10px;
  bottom: 8px;
  color: #f2fdff;
  font-size: 13px;
}

.video-caption {
  padding: 8px 10px 4px;
  color: #e9fbff;
  font-size: clamp(11px, 0.74vw, 13px);
  font-weight: 700;
}

.video-controls {
  display: grid;
  grid-template-columns: 24px 1fr 22px 22px;
  gap: 6px;
  align-items: center;
  padding: 4px 10px 8px;
  color: var(--text-muted);
  font-size: 10px;
}

.play-button,
.icon-button {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border: 0;
  border-radius: 999px;
  background: rgba(53, 232, 255, 0.18);
  color: var(--cyan);
  cursor: pointer;
}

.icon-button {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-muted);
}

.play-button:hover,
.icon-button:hover {
  color: #ffffff;
  background: rgba(87, 255, 173, 0.22);
}

.progress {
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
}

.progress span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--blue), var(--cyan), var(--green));
  transition: width 0.25s ease;
}

.empty-text {
  grid-column: 1 / -1;
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

@keyframes scan {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(128px);
  }
}
</style>
