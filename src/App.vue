<template>
  <v-app light>
    <v-navigation-drawer
      v-model="drawer"
      disable-resize-watcher
      clipped
      app
      right
      mobile-break-point="0"
    >
      <v-list v-model="phrases">
        <v-list-group value="true">
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>{{phrases.routes}}</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
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
              <v-list-tile>
                <v-list-tile-content>
                  <v-list-tile-title>{{phrases.journey}} {{ season.title }}</v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
            </template>

            <v-list-tile v-for="turtledove in season.turtledoves" :key="turtledove.name">
              <v-list-tile-content>
                <v-list-tile-title>{{ turtledove.name}}</v-list-tile-title>
              </v-list-tile-content>

              <v-list-tile-action>
                <v-checkbox v-model="turtledove.active"></v-checkbox>
              </v-list-tile-action>
            </v-list-tile>
          </v-list-group>
        </v-list-group>
        <v-list-group value="true">
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>{{phrases.who}}</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </template>
          <v-list>
            <template v-for="(td,index) in turtledoves">
             <v-divider v-if="td.divider" :key="index" :inset="td.inset" ></v-divider>
            <v-list-tile v-else :key="td.name" @click="openLink(td.blog)" avatar>
              <v-list-tile-avatar>
                <img :src="td.avatar">
              </v-list-tile-avatar>

              <v-list-tile-content>
                <v-list-tile-title v-html="td.name"></v-list-tile-title>
              </v-list-tile-content>

              <v-list-tile-action>
                <v-btn icon>
                  <v-icon :color="td.active ? 'teal' : 'black'">link</v-icon>
                </v-btn>
              </v-list-tile-action>
            </v-list-tile>
            </template>

          </v-list>
        </v-list-group>
        <v-list-group>
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>{{phrases.language}}</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </template>
          <v-radio-group v-model="radios" column>
            <v-list-tile>
              <v-list-tile-action @click="phrases=phrasesEN">
                <v-radio :label="phrases.en" value="radio-en"></v-radio>
              </v-list-tile-action>
            </v-list-tile>
            <v-list-tile>
              <v-list-tile-action @click="phrases=phrasesDE">
                <v-radio :label="phrases.de" value="radio-de"></v-radio>
              </v-list-tile-action>
            </v-list-tile>
          </v-radio-group>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar app absolute clipped-right color="#0068b4" dark>
      <v-spacer></v-spacer>
      <v-toolbar-title right>{{phrases.legend}}</v-toolbar-title>
      <v-toolbar-side-icon v-on:click.stop="drawer = !drawer"></v-toolbar-side-icon>
    </v-toolbar>
    <v-content>
      <Map :seasons="seasons" :turtledoves="turtledoves" :phrases="phrases"></Map>
    </v-content>
    <!--v-footer app fixed>
      <span>&copy; 2019</span>
    </v-footer-->
  </v-app>
</template>

<script>
import Map from "./components/Map";

export default {
  name: "App",
  components: { Map },
  data: () => ({
    drawer: null,
    locale: "",
    language: "",
    phrasesDE: {
      hello: "Hallo",
      map: "Karte",
      title: "Zugvögel auf Reisen",
      turtledoves: "Turteltauben",
      legend: "Legende",
      routes: "Flugrouten",
      journey: "Reise",
      who: "Wer ist wer?",
      language: "Sprache auswählen",
      en: "Englisch",
      de: "Deutsch",
      satellite: "Satellit",
      flightRoute: "Flugstrecke seit letzter Ortung:",
      nicolaFail: "Sender ist im August 2017 ausgefallen.",
      janFail: "Sender ist im September 2017 ausgefallen."
    },
    phrasesEN: {
      hello: "Hello",
      title: "Migratory birds travelling",
      turtledoves: "Turteldoves",
      legend: "Legend",
      routes: "Flight routes",
      journey: "Journey",
      who: "Who is who?",
      language: "Select langugage",
      en: "English",
      de: "German",
      map: "Map",
      satellite: "Satellite",
      flightRoute: "Distance from last location:",
      nicolaFail: "Transmitter was not operational anymore since August 2017.",
      janFail: "Transmitter was not operational anymore since September 2017."
    },
    phrases: {},
    radios: "",
    seasons: [
      {
        action: "gps_fixed",
        title: "2019 / 2020",
        active: true,
        turtledoves: [
          { name: "Melanie", active: true, data: "data/melanie2019_2020.csv" , opacity: 1},
          { name: "Luciano", active: true, data: "data/luciano2019_2020.csv", opacity: 1 },
          { name: "Cyril", active: true, data: "data/cyril2019_2020.csv", opacity: 1 },
          { name: "Jenny", active: true, data: "data/jenny2019_2020.csv", opacity: 1 },
          { name: "Francesco", active: true, data: "data/francesco2019_2020.csv", opacity: 1
          }
        ]
      },
      {
        action: "gps_fixed",
        title: "2018 / 2019",
        active: false,
        turtledoves: [
          { name: "Dana", active: false, data: "data/dana2018_2019.csv" , opacity: 1},
          {
            name: "Francesco",
            active: false,
            data: "data/francesco2018_2019.csv",
            opacity: 1
          }
        ]
      },
      {
        action: "gps_fixed",
        title: "2017 / 2018",
        active: false,
        turtledoves: [
          { name: "Dana", active: false, data: "data/dana2017_2018.csv" , opacity: 0.5},
          {
            name: "Francesco",
            active: false,
            data: "data/francesco2017_2018.csv",
            opacity: 0.5
          },
          { name: "Jan", active: false, data: "data/jan2017_2018.csv" },
          { name: "Nicola", active: false, data: "data/nicola2017_2018.csv" , opacity: 1}
        ]
      },
      {
        action: "gps_fixed",
        title: "2016 / 2017",
        active: false,
        turtledoves: [
          { name: "Nicola", active: false, data: "data/nicola2016_2017.csv" , opacity: 0.5 }
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
        avatar: "images/luciano.jpg",
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
        avatar: "images/jenny.jpg",
        blog: "https://blogs.nabu.de/zugvoegel/tag/jenny/"
      },
      {
        active: false,
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
    openLink(link){
       window.open(link, "_blank");
    }
  }
};
</script>