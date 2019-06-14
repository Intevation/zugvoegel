<template>
    <div id="map"></div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";

export default {
  data: () => ({
    map: {}
  }),
  mounted() {

    let map = L.map("map", {
      attributionControl: false,
      center: [50.15, 10.66],
      zoom: 5,
      maxZoom: 18,
      minZoom: 5,
      maxBounds: [[42, -46], [58, 67]],
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

    this.map=map;

  }
};
</script>

<style>
#map {
    height: 100%;
    width: 100%;
}
</style>
