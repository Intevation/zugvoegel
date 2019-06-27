<template>
  <div id="map"></div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import csv2geojson from "csv2geojson";
import "leaflet-polylinedecorator";
import turfDistance from "@turf/distance";

const turfHelpers = require("@turf/helpers");

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
    urlTemplate: {},
    layerGroups: []
  }),
  computed: {
    season2018_2019() {
      return this.seasons[0].turtledoves;
    },
    season2017_2018() {
      return this.seasons[1].turtledoves;
    },
    season2016_2017() {
      return this.seasons[2].turtledoves;
    }
  },
  watch: {
    season2018_2019: {
      // because of array
      handler: function(newVal, oldVal) {
        // eslint-disable-next-line
        console.log("newVal:" + newVal, "oldVal:" + oldVal);
        for (const bird of this.season2018_2019) {
            var layerGroupObject = this.layerGroups.filter(e => e.data === bird.data);
          if (
            bird.active &&
            layerGroupObject.length == 0
          ) {
            this.paintBird(bird);
          } else if (
            !bird.active &&
            layerGroupObject.length > 0
          ) {
            var lg = this.layerGroups.filter(function(td) {
              return td.data == bird.data;
            })[0];
            lg.group.removeFrom(this.map);
            this.layerGroups = this.layerGroups.filter(item => item !== layerGroupObject[0]);
          }
        }
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
    this.map = map;
  },
  methods: {
    paintBird(sbird) {
      let bird = this.turtledoves.filter(function(td) {
        return td.name == sbird.name;
      })[0];

      bird.data = sbird.data;

      const geojsonMarkerOptions = {
        radius: 5,
        fillColor: bird.color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
      };

      let me = this;
      fetch(bird.data)
        .then(function(response) {
          return response.text();
        })
        .then(function(csv) {
          me.makeGeojson(csv, geojsonMarkerOptions, bird);
        })
        .catch(function(error) {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    makeGeojson(csvData, geojsonMarkerOptions, bird) {
      csv2geojson.csv2geojson(
        csvData,
        {
          latfield: "location_lat",
          lonfield: "location_long",
          delimiter: ","
        },
        (err, data) => {
          if (err) {
            // eslint-disable-next-line
            console.log(err);
          } else {
            var dummy = [];
            const coords = []; // define an array to store coordinates
            // removeEmpty(data);

            // points
            var points = L.geoJSON(data, {
              onEachFeature: function(feature, layer) {
                coords.push(
                  new L.LatLng(
                    feature.geometry.coordinates[1],
                    feature.geometry.coordinates[0]
                  )
                );
                var from;
                if (typeof dummy[0] !== "undefined" && dummy[0] !== null) {
                  from = turfHelpers.point(dummy[0]);
                } else {
                  from = turfHelpers.point([
                    Number(feature.geometry.coordinates[1]),
                    Number(feature.geometry.coordinates[0])
                  ]);
                }
                var to = turfHelpers.point([
                  Number(feature.geometry.coordinates[1]),
                  Number(feature.geometry.coordinates[0])
                ]);
                var distance = turfDistance(from, to, "kilometers");
                feature.properties["image"] = bird.image;
                feature.properties["name"] = bird.name;
                feature.properties["distance"] = Number(
                  Math.round(distance + "e2") + "e-2"
                );
                dummy[0] = [
                  feature.geometry.coordinates[1],
                  feature.geometry.coordinates[0]
                ];
              },
              pointToLayer: function(feature, latlng) {
                if (feature === data.features[data.features.length - 1]) {
                  // Image for endpoint
                  return L.marker(latlng, {
                    icon: L.icon({
                      iconSize: [38, 38],
                      iconUrl: bird.avatar
                    })
                  });
                } else {
                  return L.circleMarker(latlng, geojsonMarkerOptions);
                }
              }
            });

            // route/line
            var polyline = L.polyline(coords, { color: bird.color });
            var decorator = L.polylineDecorator(polyline, {
              patterns: [
                {
                  offset: 25,
                  repeat: 75,
                  symbol: L.Symbol.arrowHead({
                    pixelSize: 10,
                    pathOptions: {
                      color: bird.color,
                      fillOpacity: 1,
                      weight: 0
                    }
                  })
                }
              ]
            });
            var group = L.layerGroup([points, polyline, decorator]);
            group.addTo(this.map);
            this.layerGroups.push({ data: bird.data, group: group });

            // L.geoJSON(csv2geojson.toLine(data)).addTo(map);
          }
        }
      );
    }
  }
};
</script>

<style>
#map {
  height: 100%;
  width: 100%;
}
</style>