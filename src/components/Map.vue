<template>
  <div id="map"></div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// delete L.Icon.Default.prototype._getIconUrl;
//https://github.com/KoRiGaN/Vue2Leaflet/issues/28

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

export default {
  props: {
    seasons: Array,
    turtledoves: Array,
    phrases: Object
  },
  data: () => ({
    map: {},
  }),
  computed: {
    season2019_2020() {
      return this.seasons[0].turtledoves;
    },
    season2018_2019() {
      return this.seasons[1].turtledoves;
    }
  },
  watch: {
    season2018_2019: {
      // because of array
      handler: function(newVal, oldVal) {
        // eslint-disable-next-line
        console.log("newVal:" + newVal, "oldVal:" + oldVal);
        this.nicola.addTo(this.map);
      },
      // because of array
      deep: true,
      //On "Startup"
      immediate: true
    }
  },
  mounted() {
    let map = L.map("map", {
      attributionControl: false,
      center: [28, 14],
      zoom: 5,
      maxZoom: 18,
      minZoom: 5,
      //maxBounds: [[42, -46], [58, 67]],
      fadeAnimation: false,
      zoomControl: false
      // renderer: L.canvas()
    });

    L.tileLayer(
      "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}",
      {
        attribution:
          'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: "mapbox.streets",
        accessToken:
          "pk.eyJ1IjoiYmpvZXJuc2NoaWxiZXJnIiwiYSI6InRzOVZKeWsifQ.y20mr9o3MolFOUdTQekhUA",
        noWrap: true
      }
    ).addTo(map);

    let nicola = L.geoJson(null, {
      onEachFeature: function(feature, layer) {
        layer.bindTooltip(
          String("<b>" + feature.properties["timestamp"] + "</b>"),
          {}
        );
      }
    });
    fetch("data/2016/nicola.geojson")
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        nicola.addData(json);
      })
      .catch(function(error) {
        // eslint-disable-next-line
        console.log(error);
      });

    this.nicola = nicola;
    this.map = map;
  }
};
</script>

<style>
#map {
  height: 100%;
  width: 100%;
}
</style>