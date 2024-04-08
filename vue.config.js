process.env.VUE_APP_VERSION = require('./package.json').version
const {gitDescribeSync} = require('git-describe');
process.env.VUE_APP_GIT_HASH = gitDescribeSync().hash

module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "./" : "/",
  configureWebpack: {
    devtool: "source-map"
  },
  transpileDependencies: ["vuetify"],
  productionSourceMap: false,
  lintOnSave: "error",
  devServer: {
        disableHostCheck: true
  }
};