<template>
  <v-btn
    v-model="btn"
    absolute
    fab
    top
    color="primary"
    medium
    right
    v-on:click="toggle()"
    id="hamburger"
  >
    <v-icon>mdi-menu</v-icon>
  </v-btn>
</template>

<script>
export default {
  computed:{
    btn: function (){
      return !this.mini
    }
  },
  props: {
    mini: Boolean
  },
  methods: {
    toggle() {
      this.$emit("update:mini", !this.mini);
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