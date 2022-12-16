<template>
  <v-btn
    id="hamburger"
    v-model="btn"
    absolute
    fab
    top
    color="primary"
    medium
    right
    @click="toggle()">
    <v-icon>mdi-menu</v-icon>
  </v-btn>
</template>

<script>
export default {
  props: {
    mini: Boolean
  },
  computed: {
    btn: function (){
      return !this.mini
    }
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