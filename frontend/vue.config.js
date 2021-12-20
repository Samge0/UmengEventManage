module.exports = {

    // 设置打包（npm run build）后存放位置，这里存放的位置供django配置index页面
    outputDir: "../server/api/templates",
    assetsDir: "static",

    devServer: {
        open: true,
        host: "0.0.0.0",
        port: 8080,
        https: false,
        hotOnly: false,
        // http 代理配置
        proxy: {

            '/api': {
                target: 'http://localhost',
                changeOrigin: true,
                secure: false,
                pathRewrite: {
                    '^/api': '/'
                }
            }
        },
        before: (app) => {}
    },
    css: {
        sourceMap: true,
    },
}
