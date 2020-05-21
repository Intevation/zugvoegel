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