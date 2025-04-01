<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h1>LLM评测系统</h1>
          </div>
          <el-menu mode="horizontal" :router="true" :default-active="activeMenu">
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/tasks">评测任务</el-menu-item>
          </el-menu>
          <div class="user-info">
            <el-dropdown>
              <span class="user-dropdown">
                管理员 <el-icon><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人设置</el-dropdown-item>
                  <el-dropdown-item>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <!-- 确保路由视图是唯一的主要内容 -->
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
      
      <el-footer>
        <div class="footer-content">
          <p>© 2025 LLM评测系统 - 基于Django和Vue.js构建</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { ArrowDown } from '@element-plus/icons-vue';

export default {
  name: 'App',
  components: {
    ArrowDown
  },
  computed: {
    activeMenu() {
      return this.$route.path;
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}
.app-container {
  min-height: 100vh;
}
.el-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}
.logo h1 {
  margin: 0;
  font-size: 20px;
  color: #409EFF;
}
.user-info {
  display: flex;
  align-items: center;
}
.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
}
.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}
.el-footer {
  background-color: #fff;
  color: #606266;
  text-align: center;
  line-height: 60px;
  border-top: 1px solid #e6e6e6;
}
.footer-content {
  font-size: 14px;
}
</style>