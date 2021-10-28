module.exports = {

    devServer: {
        open: true,
        host: 'localhost',
        port: 8080,
        https: false,
        hotOnly: false,
        // http 代理配置
        proxy: {

            '/api': {
                target: 'http://127.0.0.1',
                changeOrigin: true,
                pathRewrite: {
                    '^/api': '/'
                }
            }
        },
        before: (app) => {}
    }
}
