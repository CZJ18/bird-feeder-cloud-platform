<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon><Odometer /></el-icon>
        <span>智能喂鸟器</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        class="sidebar-menu"
        router
        background-color="#1a1a2e"
        text-color="#8b8ba3"
        active-text-color="#00d4ff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/manage/devices">
          <el-icon><Monitor /></el-icon>
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="/manage/events">
          <el-icon><Camera /></el-icon>
          <span>鸟类识别记录</span>
        </el-menu-item>
        <el-menu-item index="/manage/history">
          <el-icon><Document /></el-icon>
          <span>历史识别结果</span>
        </el-menu-item>
        <el-menu-item index="/manage/statistics">
          <el-icon><PieChart /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
        <el-menu-item index="/manage/config">
          <el-icon><Setting /></el-icon>
          <span>远程参数设置</span>
        </el-menu-item>
        <el-menu-item index="/manage/logs">
          <el-icon><Tickets /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <h1 class="title">智能喂鸟器云端管理平台</h1>
        <div class="header-right">
          <el-badge :value="3" :max="99" class="badge-item">
            <el-icon size="20px"><Bell /></el-icon>
          </el-badge>
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  Monitor,
  Camera,
  Document,
  PieChart,
  Setting,
  Tickets,
  Bell,
  User,
  Odometer
} from '@element-plus/icons-vue'

const route = useRoute()
const currentRoute = computed(() => route.path)
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  background:
    radial-gradient(circle at 72% 8%, rgba(93, 224, 230, 0.1), transparent 26%),
    radial-gradient(circle at 18% 88%, rgba(124, 247, 167, 0.08), transparent 24%),
    linear-gradient(135deg, #060a13 0%, #0b1120 48%, #101827 100%);
}

.sidebar {
  background: rgba(9, 14, 26, 0.82);
  backdrop-filter: blur(18px);
  border-right: 1px solid rgba(133, 232, 255, 0.12);
  overflow-x: hidden;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.3);
    border-radius: 3px;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  color: #00d4ff;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  
  .el-icon {
    font-size: 32px;
  }
}

.sidebar-menu {
  border-right: none;
  
  :deep(.el-menu-item) {
    height: 56px;
    line-height: 56px;
    margin: 4px 12px;
    border-radius: 8px;
    transition: all 0.3s;
    
    &:hover {
      background: rgba(0, 212, 255, 0.1) !important;
    }
    
    &.is-active {
      background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.05)) !important;
      border-left: 3px solid #00d4ff;
    }
  }
}

.header {
  background: rgba(9, 14, 26, 0.72);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(133, 232, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
}

.title {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(90deg, #00d4ff, #00ff88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
  
  .badge-item {
    cursor: pointer;
    color: #8b8ba3;
    transition: color 0.3s;
    
    &:hover {
      color: #00d4ff;
    }
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #8b8ba3;
    cursor: pointer;
    transition: color 0.3s;
    padding: 8px 12px;
    border-radius: 8px;
    
    &:hover {
      color: #00d4ff;
      background: rgba(0, 212, 255, 0.1);
    }
  }
}

.main-content {
  padding: 24px;
  overflow-y: auto;
  background: transparent;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.3);
    border-radius: 4px;
  }
}
</style>
