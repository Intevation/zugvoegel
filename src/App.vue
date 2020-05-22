<template>
  <v-app>
    <v-navigation-drawer
      class="grey lighten-4 navi"
      app
      permanent
      :mini-variant.sync="mini"
      @mouseover.native="mini=false"
      @mouseleave.native="mini=true">
      <Navi
        :phrases="phrases"
        :seasons.sync="seasons"
        :turtledoves.sync="turtledoves"
        :backgroundmap.sync="backgroundmap"
        :language.sync="language" />
    </v-navigation-drawer>

    <Menu :mini.sync="mini" />

    <v-content>
      <Map
        :seasons.sync="seasons"
        :turtledoves.sync="turtledoves"
        :phrases="phrases"
        :backgroundmap.sync="backgroundmap"
        :mini.sync="mini" />
    </v-content>
  </v-app>
</template>

<script>
let seasons = require(process.env.VUE_APP_SEASONS);
let turtledoves = require(process.env.VUE_APP_BIRDS);
import phrasesEN from "./locales/phrasesEN.json";
import phrasesDE from "./locales/phrasesDE.json";
import Map from "./components/Map";
import Navi from "./components/Navi";
import "@mdi/font/css/materialdesignicons.css";
import Menu from "./components/Menu";

export default {
  name: "App",
  components: { Menu, Map, Navi},
  data: () => ({
    mini: true,
    phrases: {},
    phrasesDE: phrasesDE,
    phrasesEN: phrasesEN,
    backgroundmap: "streetmap",
    seasons: seasons,
    turtledoves: turtledoves,
    language: ""
  }),
  watch: {
    // function(newVal, oldVal)
    language: function(newVal) {
      if (newVal === "de") {
        this.phrases = this.phrasesDE;
      } else {
        this.phrases = this.phrasesEN;
      }
    },
  },
  created: function() {
    let language =
      (navigator.languages && navigator.languages[0]) ||
      navigator.language ||
      navigator.userLanguage;
    this.language = language.substring(0, 2);
    this.phrases = {
      de: this.phrasesDE,
      en: this.phrasesEN
    }[language=== "de" ? "de" : "en"];
  }
};
</script>

<style scoped>
.navi {
  transform: none !important;
  -webkit-transform: none !important;
}
</style>
