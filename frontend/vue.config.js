module.exports = {

    // 设置打包（npm run build）后存放位置，这里存放的位置供django配置index页面
    outputDir: "../api/templates",
    assetsDir: "static",
    //生产环境是否生成 sourceMap 文件，一般情况不建议打开
    productionSourceMap: false,

    devServer: {
        open: true,
        host: "0.0.0.0",
        port: 8080,
        https: false,
        hotOnly: false,
        // http 代理配置
        // proxy: 'http://localhost:8000',
        proxy: {
            '/': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
                pathRewrite: {
                    '^/': '/'
                }
            }
        },
        before: (app) => {}
    },
    css: {
        sourceMap: false,
    },
}
