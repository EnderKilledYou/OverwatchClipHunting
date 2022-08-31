const {defineConfig} = require('@vue/cli-service')
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
module.exports = defineConfig({
    transpileDependencies: true,
    outputDir: '../static',
    devServer: {
        proxy: 'https://hotface.city'
    },
    configureWebpack: {
        plugins: [new MiniCssExtractPlugin()]
    }

})
