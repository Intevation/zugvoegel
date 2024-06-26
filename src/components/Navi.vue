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
          <v-list-item-title>
            {{ phrases.journey }} {{ season.title }}
          </v-list-item-title>
        </template>
        <v-list-item>
          <v-list-item-content>
            <v-dialog
              ref="dialog"
              v-model="modal"
              persistent
              width="290px">
              <template v-slot:activator="{ on, attrs }">
                <v-textarea
                  v-model="dateRangeText"
                  label="Zeitraum"
                  prepend-icon="mdi-calendar"
                  rows="2"
                  readonly
                  v-bind="attrs"
                  v-on="on" />
              </template>
              <v-date-picker 
                v-model="dates"
                locale="de-DE"
                range
                no-title
                scrollable>
                <v-btn
                  text
                  color="primary"
                  @click="resetDates(season)">
                  {{ phrases.dialogReset }}
                </v-btn>
                <v-spacer />
                <v-btn
                  text
                  color="primary"
                  @click="modal = false">
                  {{ phrases.dialogCancel }}
                </v-btn>
                <v-btn
                  text
                  color="primary"
                  @click="$refs.dialog[0].save(dates); setDateRange(season)">
                  {{ phrases.dialogOk }}
                </v-btn>
              </v-date-picker>
            </v-dialog>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-btn
              @click="toggleBirds(season, !isBirdActive(season))">
              <v-icon>
                {{ isBirdActive(season) ? 'mdi-eye-off' : 'mdi-eye' }}
              </v-icon>
            </v-btn>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          v-for="turtledove in season.turtledoves"
          :key="turtledove.name">
          <v-list-item-content>
            <v-list-item-title>{{ turtledove.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ turtledove.id }}</v-list-item-subtitle>
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
      prepend-icon="mdi-help-circle"
      no-action>
      <template v-slot:activator>
        <v-list-item-title>{{ phrases.who }}</v-list-item-title>
      </template>
      <div
        v-for="(td, index) in turtledoves"
        :key="index">
        <v-list-item
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
            <v-list-item-subtitle v-text="td.id" />
          </v-list-item-content>
        </v-list-item>
        <div
          v-if="td.extraInfo"
          class="extrainfo">
          {{ td.extraInfo }}
        </div>
      </div>
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
            :label="phrases.osm"
            value="osm" />
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

export default {
  props: {
    seasons: {type: Array, default(){return []}},
    turtledoves: {type: Array, default(){return []}},
    phrases: {type: Object, default(){return {}}},
    backgroundmap: {type: String, default(){return "osm"}},
    language: {type: String, default(){return ""}}
  },
  data: () => ({
    menu: false,
    modal: false,
    dates: [],
  }),
  computed: {
      dateRangeText () {
        return this.dates.join(' ~ ')
      }
  },
  watch: {
    backgroundmap: {
      // function(newVal, oldVal)
      handler: function(newVal) {
        if (newVal === "osm") {
          this.$emit("update:backgroundmap", "osm");
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
  mounted() {
    for (const season of this.seasons) {
      this.resetDates(season)
      this.setDateRange(season)
    }
  },
  methods: {
    openLink(link) {
      if (link){
        window.open(link, "_blank");
      }
    },
    isBirdActive(season) {
      return season.turtledoves.find(d => d.active) ? true: false;
    },
    toggleBirds(season, newState) {
      for (const bird of season.turtledoves) {
        bird.active = newState;
      }
    },
    setDateRange(season) {
      if (this.dates.length != 2) {
        // eslint-disable-next-line
        console.error("Range does not consist of two dates.");
        return
      }
      let newDaterange = this.dates.sort().map(v => new Date(v));
      newDaterange[1].setHours(23);
      newDaterange[1].setMinutes(59);
      newDaterange[1].setSeconds(59);
      // eslint-disable-next-line no-console
      console.log("SETTING DATERANGE: " + newDaterange);
      season.daterange = newDaterange;
    },
    
    resetDates(season) {
      let d2 = new Date();
      let d1 = new Date(d2.valueOf() - (86400000 * season.defaultDaterangeDays));
      this.dates = [d1.toISOString().substr(0, 10), d2.toISOString().substr(0, 10)];
      return [d1, d2];
    }
  }
};
</script>

<style scoped>
.navi {
  transform: none !important;
  -webkit-transform: none !important;
}
.extrainfo {
  margin-left: 25px;
  font-weight: thin;
  font-style: italic;
  color: black;
}
.v-list-item__title {
    white-space: pre-line;
}
.v-list-item__subtitle {
    font-size: small;
}
</style>
