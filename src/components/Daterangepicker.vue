<template>
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
      :id="season.title"
      v-model="dates"
      locale="de-DE"
      range
      no-title
      scrollable>
      <v-btn
        text
        color="primary"
        @click="resetDates()">
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
        @click="$refs.dialog.save(dates); setDateRange()">
        {{ phrases.dialogOk }}
      </v-btn>
    </v-date-picker>
  </v-dialog>
</template>

<script>
export default {
    props: {
        season: {type: Object, default(){return []}},
        phrases: {type: Object, default(){return {}}},
    },
    data: () => ({
        dates: [],
        modal: false,
    }),
    computed: {
        dateRangeText () {
            return this.dates.join(' ~ ')
        }
    },
    mounted() {
        this.resetDates()
        this.setDateRange()
    },
    methods: {
        setDateRange() {
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
            this.season.daterange = newDaterange;
        },
        
        resetDates() {
            let d2 = new Date();

            const years = this.season.title.split("/");
            let yearStart = Number(years[0]);
            let yearEnd = Number(years[1]);
            let yearNow = d2.getFullYear();

            if (yearStart <= yearNow <= yearEnd) {
              d2.setFullYear(yearStart);
            }
            

            let d1 = new Date(d2.valueOf() - (86400000 * this.season.defaultDaterangeDays));
            this.dates = [d1.toISOString().substr(0, 10), d2.toISOString().substr(0, 10)];
            return [d1, d2];
        },
    }
}
</script>