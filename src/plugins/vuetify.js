import '@mdi/font/css/materialdesignicons.css' // Ensure you are using css-loader
import Vue from 'vue';
import Vuetify from 'vuetify/lib';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        base: "#0068b4",
        primary: "#0068b4",
        secondary: "#0068b4",
        accent: "#0068b4"
      }
    }
  },
  icons: {
    iconfont: 'mdi' // default - only for display purposes
  }

});
