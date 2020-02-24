<template>
  <v-app>
    <v-navigation-drawer
      class="grey lighten-4 navi"
      app
      permanent
      :mini-variant.sync="mini"
      @mouseover.native="mini=false"
      @mouseleave.native="mini=true"
    >
      <v-list v-model="phrases">
        <v-list-group value="true" no-action>
          <template v-slot:activator>
            <v-list-item-icon>
              <v-icon>mdi-crosshairs-gps</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{phrases.routes}}</v-list-item-title>
            </v-list-item-content>
          </template>
          <v-list-group
            v-for="season in seasons"
            :key="season.title"
            v-model="season.active"
            :prepend-icon="season.action"
            no-action
            sub-group
          >
            <template v-slot:activator>
              <v-list-item-title>{{phrases.journey}} {{ season.title }}</v-list-item-title>
            </template>
            <v-list-item v-for="turtledove in season.turtledoves" :key="turtledove.name">
              <v-list-item-content>
                <v-list-item-title>{{ turtledove.name}}</v-list-item-title>
              </v-list-item-content>
              <v-list-item-action>
                <v-switch inset v-model="turtledove.active"></v-switch>
              </v-list-item-action>
            </v-list-item>
          </v-list-group>
        </v-list-group>

        <v-list-group prepend-icon="mdi-twitter-circle" no-action>
          <template v-slot:activator>
            <v-list-item-title>{{phrases.who}}</v-list-item-title>
          </template>
          <v-list-item
            v-model="turtledoves"
            v-for="(td, index) in turtledoves"
            :key="index"
            inactive
            ripple
            @click="openLink(td.blog)"
          >
            <v-divider v-if="td.divider"></v-divider>
            <v-list-item-avatar v-if="td.avatar">
              <v-img :src="td.avatar"></v-img>
            </v-list-item-avatar>
            <v-list-item-content v-if="td.name">
              <v-list-item-title v-text="td.name"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-group>

        <v-list-group prepend-icon="mdi-layers" no-action>
          <template v-slot:activator>
            <v-list-item-title>{{phrases.backgroundmap}}</v-list-item-title>
          </template>
          <v-list-item>
            <v-radio-group v-model="backgroundmap" column>
              <v-radio :label="phrases.satellite" value="satellite"></v-radio>
              <v-radio :label="phrases.streetmap" value="streetmap"></v-radio>
            </v-radio-group>
          </v-list-item>
        </v-list-group>

        <v-list-group prepend-icon="mdi-translate" no-action>
          <template v-slot:activator>
            <v-list-item-title>{{phrases.language}}</v-list-item-title>
          </template>
          <v-list-item>
            <v-radio-group v-model="radios" column>
              <v-radio :label="phrases.en" value="radio-en"></v-radio>
              <v-radio :label="phrases.de" value="radio-de"></v-radio>
            </v-radio-group>
          </v-list-item>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>

    <Menu :mini.sync="mini"></Menu>
    <v-content>
      <Map
        :seasons="seasons"
        :turtledoves="turtledoves"
        :phrases="phrases"
        :backgroundmap="backgroundmap"
        :mini.sync="mini"
      >
      </Map>
    </v-content>
    <!--v-footer app fixed>
      <span>&copy; 2019</span>
    </v-footer-->
  </v-app>
</template>

<script>
import seasons from "./config/seasons.json";
import turtledoves from "./config/turtledoves.json";
import phrasesEN from "./config/phrasesEN.json";
import phrasesDE from "./config/phrasesDE.json";
import Map from "./components/Map";
import "@mdi/font/css/materialdesignicons.css";
import Menu from "./components/Menu";

export default {
  name: "App",
  components: { Menu, Map },
  data: () => ({
    mini: true,
    locale: "",
    language: "",
    phrasesDE: phrasesDE,
    phrasesEN: phrasesEN,
    phrases: {},
    radios: "",
    backgroundmap: "streetmap",
    seasons: seasons,
    turtledoves: turtledoves
  }),
  created: function() {
    this.language =
      (navigator.languages && navigator.languages[0]) ||
      navigator.language ||
      navigator.userLanguage;
    this.locale = this.language.substring(0, 2);
    this.phrases = {
      de: this.phrasesDE,
      en: this.phrasesEN
    }[this.locale === "de" ? "de" : "en"];
    this.radios = "radio-" + this.locale;
  },
  watch: {
    // function(newVal, oldVal)
    radios: function(newVal) {
      if (newVal === "radio-de") {
        this.phrases = this.phrasesDE;
      } else {
        this.phrases = this.phrasesEN;
      }
    },
    // function(newVal, oldVal)
    phrases: function() {
      //console.log("newVal:" + newVal.janFail, "oldVal:" + oldVal.janFail);
      let jan = this.turtledoves.filter(function(td) {
        return td.name == "Jan";
      })[0];
      jan.note = this.phrases.janFail;
      let nicola = this.turtledoves.filter(function(td) {
        return td.name == "Nicola";
      })[0];
      nicola.note = this.phrases.nicolaFail;
    }
  },
  methods: {
    openLink(link) {
      window.open(link, "_blank");
    }
  }
};
</script>

<style scoped>
.navi {
  transform: none !important;
  -webkit-transform: none !important;
}
</style>
