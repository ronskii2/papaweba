/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ]
  },
  // Добавляем настройки для внешнего доступа
  webpackDevMiddleware: config => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  },
  // Отключаем строгую проверку источников в режиме разработки
  experimental: {
    appDir: true,
  }
}

module.exports = nextConfig
