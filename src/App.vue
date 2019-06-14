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
      <v-list>
        <v-subheader>Flugrouten</v-subheader>
        <v-list-group
          v-for="item in items"
          :key="item.title"
          v-model="item.active"
          :prepend-icon="item.action"
          no-action
        >
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>{{ item.title }}</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </template>

          <v-list-tile v-for="subItem in item.items" :key="subItem.title" @click>
            <v-list-tile-content>
              <v-list-tile-title>{{ subItem.title }}</v-list-tile-title>
            </v-list-tile-content>

            <v-list-tile-action>
              <v-checkbox v-model="subItem.active"></v-checkbox>
              <v-icon>{{ subItem.action }}</v-icon>
            </v-list-tile-action>
          </v-list-tile>
        </v-list-group>
        <v-subheader>Wer ist wer?</v-subheader>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar app absolute clipped-right color="#0068b4" dark>
      <v-toolbar-title right>Zugvögel auf Reisen</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-toolbar-title right>Turteltauben</v-toolbar-title>
      <v-toolbar-side-icon v-on:click.stop="drawer = !drawer"></v-toolbar-side-icon>
    </v-toolbar>
    <v-content>
      <Map :items=items></Map>
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
    items: [
      {
        action: "gps_fixed",
        title: "Reise 2019 / 2020",
        active: true,
        items: [
          { title: "Adele", active: true },
          { title: "Joris", active: true },
          { title: "Teelke", active: true }
        ]
      },
      {
        action: "gps_fixed",
        title: "Reise 2018 / 2019",
        active: false,
        items: [
          { title: "Adele", active: false },
          { title: "Joris", active: false },
          { title: "Teelke", active: false }
        ]
      }
    ]
  }),
  props: {
    source: String
  }
};
</script>