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
    phrasesDE: {
      backgroundmap: "Hintergrundkarte",
      hello: "Hallo",
      streetmap: "Karte",
      title: "Zugvögel auf Reisen",
      turtledoves: "Turteltauben",
      legend: "Legende",
      routes: "Flugrouten",
      journey: "Reise",
      who: "Wer ist wer?",
      language: "Sprache",
      en: "Englisch",
      de: "Deutsch",
      satellite: "Satellit",
      flightRoute: "Flugstrecke seit letzter Ortung:",
      nicolaFail: "Sender ist im August 2017 ausgefallen.",
      janFail: "Sender ist im September 2017 ausgefallen."
    },
    phrasesEN: {
      backgroundmap: "Background map",
      hello: "Hello",
      title: "Migratory birds travelling",
      turtledoves: "Turteldoves",
      legend: "Legend",
      routes: "Flight routes",
      journey: "Journey",
      who: "Who is who?",
      language: "Language",
      en: "English",
      de: "German",
      streetmap: "Map",
      satellite: "Satellite",
      flightRoute: "Distance from last location:",
      nicolaFail: "Transmitter was not operational anymore since August 2017.",
      janFail: "Transmitter was not operational anymore since September 2017."
    },
    phrases: {},
    radios: "",
    backgroundmap: "streetmap",
    seasons: [
      {
        action: "mdi-crosshairs-gps",
        title: "2019 / 2020",
        active: true,
        turtledoves: [
          {
            name: "Melanie",
            active: true,
            data: "data/melanie2019_2020.csv",
            opacity: 1
          },
          {
            name: "Luciano",
            active: true,
            data: "data/luciano2019_2020.csv",
            opacity: 1
          },
          {
            name: "Cyril",
            active: true,
            data: "data/cyril2019_2020.csv",
            opacity: 1
          },
          {
            name: "Jenny",
            active: true,
            data: "data/jenny2019_2020.csv",
            opacity: 1
          },
          {
            name: "Francesco",
            active: true,
            data: "data/francesco2019_2020.csv",
            opacity: 1
          }
        ]
      },
      {
        action: "mdi-crosshairs-gps",
        title: "2018 / 2019",
        active: false,
        turtledoves: [
          {
            name: "Dana",
            active: false,
            data: "data/dana2018_2019.csv",
            opacity: 1
          },
          {
            name: "Francesco",
            active: false,
            data: "data/francesco2018_2019.csv",
            opacity: 1
          }
        ]
      },
      {
        action: "mdi-crosshairs-gps",
        title: "2017 / 2018",
        active: false,
        turtledoves: [
          {
            name: "Francesco",
            active: false,
            data: "data/francesco2017_2018.csv",
            opacity: 0.5
          },
          { name: "Jan", active: false, data: "data/jan2017_2018.csv" },
          {
            name: "Nicola",
            active: false,
            data: "data/nicola2017_2018.csv",
            opacity: 1
          }
        ]
      },
      {
        action: "mdi-crosshairs-gps",
        title: "2016 / 2017",
        active: false,
        turtledoves: [
          {
            name: "Nicola",
            active: false,
            data: "data/nicola2016_2017.csv",
            opacity: 0.5
          }
        ]
      }
    ],
    turtledoves: [
      {
        active: true,
        name: "Melanie",
        color: "#87d5fb",
        avatar: "images/melanie.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/melanie/"
      },
      {
        active: true,
        name: "Luciano",
        color: "#ffff01",
        avatar: "images/luciano_flor.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/luciano/"
      },
      {
        active: true,
        name: "Cyril",
        color: "#8102b3",
        avatar: "images/cyril.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/cyril/"
      },
      {
        active: true,
        name: "Jenny",
        color: "#05ab03",
        avatar: "images/jenny_flor.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/jenny/"
      },
      {
        active: true,
        name: "Francesco",
        color: "#0b7ac1",
        avatar: "images/francesco.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/francesco/"
      },
      { divider: true },
      {
        active: false,
        name: "Dana",
        color: "#daa97e",
        avatar: "images/dana_flor.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/dana/"
      },
      {
        active: false,
        name: "Jan",
        color: "#6b7a1f",
        avatar: "images/jan_flor.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/jan/"
      },
      {
        active: false,
        name: "Nicola",
        color: "#303028",
        avatar: "images/nicola_flor.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/nicola/"
      }
    ]
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
    radios: function(newVal, oldVal) {
      if (newVal === "radio-de") {
        this.phrases = this.phrasesDE;
      } else {
        this.phrases = this.phrasesEN;
      }
    },
    phrases: function(newVal, oldVal) {
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
