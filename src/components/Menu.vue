<template>
  <v-btn
    v-model="mini"
    dark
    absolute
    fab
    top
    medium
    right
    color="#0068b4"
    v-on:click="toggle()"
    id="hamburger"
  >
    <v-icon>mdi-menu</v-icon>
  </v-btn>
</template>

<script>
export default {
  props: {
    mini: Boolean
  },
  methods: {
    toggle() {
      this.mini = !this.mini;
      this.$emit("update:mini", this.mini);
    }
  }
};
</script>

<style>
#hamburger {
  top: calc(var(--vh, 1vh) * 1);
  z-index: 9999;
}
</style>