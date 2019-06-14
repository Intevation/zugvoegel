<template>
  <v-app id="inspire" light>
    <v-navigation-drawer v-model="drawer" clipped fixed app right>
      <v-list dense>
        <v-list-tile v-on:click>
          <v-list-tile-action>
            <v-icon>dashboard</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Dashboard</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile v-on:click>
          <v-list-tile-action>
            <v-icon>settings</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Settings</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar app absolute clipped-right color="purple">
      <v-spacer></v-spacer>
      <v-toolbar-title right>Turteltauben</v-toolbar-title>
      <v-toolbar-side-icon v-on:click.stop="drawer = !drawer"></v-toolbar-side-icon>
    </v-toolbar>
    <v-content>
      <Map></Map>
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
    drawer: null
  }),
  props: {
    source: String
  }
};
</script>