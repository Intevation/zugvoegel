<template>
  <v-dialog
    v-model="dialog"
    transition="dialog-bottom-transition"
    width="80%">
    <v-card>
      <v-toolbar
        dark
        class="primary">
        <v-btn
          icon
          dark
          @click.native="dialog = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Settings</v-toolbar-title>
        <v-spacer />
        <v-toolbar-items>
          <v-btn
            dark
            flat
            @click.native="dialog = false">
            Save
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-media
        src="https://vuetifyjs.com/static/doc-images/cards/desert.jpg"
        height="200px" />
      <v-card-title primary-title>
        <div>
          <h3 class="headline mb-0">
            Kangaroo Valley Safari
          </h3>
          <div>Located two hours south of Sydney in the <br>Southern Highlands of New South Wales, ...</div>
        </div>
      </v-card-title>
      <v-card-actions>
        <v-btn
          flat
          class="orange--text">
          Share
        </v-btn>
        <v-btn
          flat
          class="orange--text">
          Explore
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    dialog: Boolean
  }
};
</script>

<style>
div.v-dialog__content.v-dialog__content--active {
	z-index: 900 !important;
}
</style>