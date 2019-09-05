<template>
  <v-btn
    v-model="drawer"
    dark
    absolute
    fab
    bottom
    medium
    left
    color="#0068b4"
    v-on:click.stop=onClickButton
    id="hamburger"
  >
    <v-icon>mdi-menu</v-icon>
  </v-btn>
</template>

<script>
export default {
  data: () => ({
    drawer: true
  }),
  methods: {
    onClickButton (event) {
      this.$emit('clicked', this.drawer=!this.drawer)
    }
  }
};
</script>

<style>
#hamburger {
  bottom: 10px;
  z-index: 9999;
}

@media only screen and (min-device-width: 320px) and (max-device-width: 640px) {
  #hamburger {
    bottom: 10vh;
    z-index: 9999;
  }
}
</style>