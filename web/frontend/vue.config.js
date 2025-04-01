module.exports = {
  outputDir: '../static/frontend',
  publicPath: process.env.NODE_ENV === 'production' ? '/static/frontend/' : '/',
  filenameHashing: false, // 禁用文件名哈希，使文件名保持一致
  css: {
    extract: true, // 确保CSS被提取到单独的文件
  },
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
};