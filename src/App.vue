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
        <v-subheader>{{phrases.routes}}</v-subheader>
        <v-list-group
          v-for="season in seasons"
          :key="season.title"
          v-model="season.active"
          :prepend-icon="season.action"
          no-action
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
        <v-subheader>{{phrases.who}}</v-subheader>
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
                <v-radio :label=phrases.en value="radio-en" ></v-radio>
            </v-list-tile-action>
          </v-list-tile>
          <v-list-tile>
            <v-list-tile-action @click="phrases=phrasesDE">
                <v-radio :label=phrases.de value="radio-de" ></v-radio>
            </v-list-tile-action>
          </v-list-tile>
              </v-radio-group>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar app absolute clipped-right color="#0068b4" dark>
      <v-toolbar-title right>{{phrases.title}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-title right>{{phrases.turtledoves}}</v-toolbar-title>
      <v-toolbar-side-icon v-on:click.stop="drawer = !drawer"></v-toolbar-side-icon>
    </v-toolbar>
    <v-content>
      <Map :seasons="seasons"></Map>
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
        title: "2018 / 2019",
        active: false,
        turtledoves: [{ name: "Francesco", active: false }]
      },
      {
        action: "gps_fixed",
        title: "2017 / 2018",
        active: false,
        turtledoves: [
          { name: "Dana", active: false },
          { name: "Francesco", active: false },
          { name: "Nicola", active: false }
        ]
      },
      {
        action: "gps_fixed",
        title: "2016 / 2017",
        active: false,
        turtledoves: [{ name: "Nicola", active: false }]
      }
    ]
  }),
  created: function() {
    //this.polyglot= new Polyglot();
    this.language =
      (navigator.languages && navigator.languages[0]) ||
      navigator.language ||
      navigator.userLanguage;
    this.locale = this.language.substring(0, 2);
    this.phrases = {
      de: this.phrasesDE,
      en: this.phrasesEN
    }[this.locale === "de" ? "de" : "en"];
    this.radios ="radio-"+this.locale;
  }
};
</script>