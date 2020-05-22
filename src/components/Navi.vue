<template>
  <v-list v-model="phrases">
    <v-list-group
      value="true"
      no-action>
      <template v-slot:activator>
        <v-list-item-icon>
          <v-icon>mdi-crosshairs-gps</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ phrases.routes }}</v-list-item-title>
        </v-list-item-content>
      </template>
      <v-list-group
        v-for="season in seasons"
        :key="season.title"
        v-model="season.active"
        :prepend-icon="season.action"
        no-action
        sub-group>
        <template v-slot:activator>
          <v-list-item-title>{{ phrases.journey }} {{ season.title }}</v-list-item-title>
        </template>
        <v-list-item
          v-for="turtledove in season.turtledoves"
          :key="turtledove.name">
          <v-list-item-content>
            <v-list-item-title>{{ turtledove.name }}</v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-switch
              v-model="turtledove.active"
              :color="turtledove.color"
              inset />
          </v-list-item-action>
        </v-list-item>
      </v-list-group>
    </v-list-group>

    <v-list-group
      prepend-icon="mdi-twitter-circle"
      no-action>
      <template v-slot:activator>
        <v-list-item-title>{{ phrases.who }}</v-list-item-title>
      </template>
      <v-list-item
        v-for="(td, index) in turtledoves"
        :key="index"
        v-model="turtledoves"
        inactive
        ripple
        @click="openLink(td.blog)">
        <v-divider v-if="td.divider" />
        <v-list-item-avatar v-if="td.avatar">
          <v-img :src="td.avatar" />
        </v-list-item-avatar>
        <v-list-item-content v-if="td.name">
          <v-list-item-title v-text="td.name" />
        </v-list-item-content>
      </v-list-item>
    </v-list-group>

    <v-list-group
      prepend-icon="mdi-layers"
      no-action>
      <template v-slot:activator>
        <v-list-item-title>{{ phrases.backgroundmap }}</v-list-item-title>
      </template>
      <v-list-item>
        <v-radio-group
          v-model="backgroundmap"
          column>
          <v-radio
            :label="phrases.satellite"
            value="satellite" />
          <v-radio
            :label="phrases.streetmap"
            value="streetmap" />
        </v-radio-group>
      </v-list-item>
    </v-list-group>

    <v-list-group
      prepend-icon="mdi-translate"
      no-action>
      <template v-slot:activator>
        <v-list-item-title>{{ phrases.language }}</v-list-item-title>
      </template>
      <v-list-item>
        <v-radio-group
          v-model="language"
          column>
          <v-radio
            :label="phrases.en"
            value="en" />
          <v-radio
            :label="phrases.de"
            value="de" />
        </v-radio-group>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>

<script>
import "@mdi/font/css/materialdesignicons.css";

export default {
  props: {
    seasons: {type: Array, default(){return []}},
    turtledoves: {type: Array, default(){return []}},
    phrases: {type: Object, default(){return {}}},
    backgroundmap: {type: String, default(){return "streetmap"}},
    language: {type: String, default(){return ""}}
  },
  data: () => ({
  }),
  watch: {
    backgroundmap: {
      // function(newVal, oldVal)
      handler: function(newVal) {
        if (newVal === "streetmap") {
          this.$emit("update:backgroundmap", "streetmap");
        } else {
          this.$emit("update:backgroundmap", "satellite");
        }
      },
      immediate: false
    },
    // function(newVal, oldVal)
    language: function(newVal) {
      if (newVal === "de") {
        this.$emit("update:language", "de");
      } else {
        this.$emit("update:language", "en");
      }
    },
  },
  methods: {
    openLink(link) {
      if (link){
        window.open(link, "_blank");
      }
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
