const {defineConfig} = require('@vue/cli-service')
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
module.exports = defineConfig({
    transpileDependencies: true,
    outputDir: '../templates',
    devServer: {
        proxy: 'http://localhost:5000'
    },
    configureWebpack: {
        plugins: [new MiniCssExtractPlugin()]
    }

})
