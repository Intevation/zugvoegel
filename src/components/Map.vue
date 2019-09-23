<template>
  <div v-resize="onResize" id="map"></div>
</template>

<script>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import csv2geojson from "csv2geojson";
import "leaflet-polylinedecorator";
import turfDistance from "@turf/distance";
import Popup from "./Popup";

const turfHelpers = require("@turf/helpers");

//https://github.com/KoRiGaN/Vue2Leaflet/issues/28

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

export default {
  components: { Popup },
  props: {
    seasons: Array,
    turtledoves: Array,
    phrases: Object,
    backgroundmap: String,
    mini: Boolean
  },
  data: () => ({
    map: {},
    urlTemplate: {},
    layerGroups: [],
    dialog: false,
    streetmap: L.tileLayer(
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
    ),
    satellite: L.tileLayer.wms("https://tiles.maps.eox.at/?", {
      layers: "s2cloudless_3857",
      attribution:
        '<a href="https://s2maps.eu" target="_blank">Sentinel-2 cloudless - https://s2maps.eu</a> by <a href="https://eox.at/" target="_blank">EOX IT Services GmbH</a> (Contains modified Copernicus Sentinel data 2017 & 2018)'
    })
  }),
  watch: {
    backgroundmap: {
      handler: function(newVal, oldVal) {
        if (newVal === "streetmap") {
          this.satellite.remove();
          this.streetmap.addTo(this.map);
        } else {
          this.streetmap.remove();
          this.satellite.addTo(this.map);
        }
      },
      immediate: false
    },
    // Layertree logic
    layerGroups: {
      handler: function(newVal, oldVal) {
        this.fitMapBounds(newVal);
      }
    },
    seasons: {
      handler: function() {
        for (const season of this.seasons) {
          for (const bird of season.turtledoves) {
            var layerGroupObject = this.layerGroups.filter(
              e => e.data === bird.data
            );
            if (bird.active && layerGroupObject.length == 0) {
              this.processBird(bird);
            } else if (!bird.active && layerGroupObject.length > 0) {
              var lg = this.layerGroups.filter(function(td) {
                return td.data == bird.data;
              })[0];
              lg.group.removeFrom(this.map);
              lg.group.clearLayers();
              this.layerGroups = this.layerGroups.filter(
                item => item !== layerGroupObject[0]
              );
            }
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
      center: [35.5322, 21.09375],
      zoom: 4,
      maxZoom: 18,
      minZoom: 2,
      //maxBounds: [[42, -46], [58, 67]],
      //maxBounds: [[0, -180], [0, 180]],
      fadeAnimation: false,
      zoomControl: false
      // renderer: L.canvas()
    });

    this.map = map;

    this.map.addControl(
      L.control.attribution({
        position: "bottomright",
        prefix: false
      })
    );

    L.control.scale({ position: "bottomright" }).addTo(this.map);

    this.streetmap.addTo(this.map);

    if (L.Browser.mobile) {
      map.tap.disable();
      map.on("click", function(e) {
        console.log("klick");
        this.mini = true;
      });

    //// Debugging
    //map.on("move", function(e) {
    //  console.log(map.getZoom());
    //  console.log(map.getCenter());
    //});
    }

    // var hash = new L.Hash(map);
    // map.on("moveend", function() {
    //   console.log(map.getCenter());
    // });
  },
  methods: {
    fitMapBounds(newBounds) {
      if (newBounds.length > 0) {
        var bounds = L.latLngBounds();
        for (const route of newBounds) {
          bounds.extend(route.group.getBounds());
        }
        // For debugging of bounding boxes.
        //var latlngs = L.rectangle(bounds).getLatLngs();
        //L.polyline(latlngs[0].concat(latlngs[0][0])).addTo(this.map);
        this.map.invalidateSize(true);
        this.map.fitBounds(bounds);
        //this.map.setMaxBounds(bounds);
      } else {
        if (L.Browser.mobile) {
          this.map.setView([37.7185, 13.18359], 3);
        } else {
          this.map.setView([35.5322, 21.09375], 4);
        }
      }
    },
    onResize() {
      if (this.map instanceof L.Map) {
        this.map.invalidateSize({"pan":false});
        //this.fitMapBounds(this.layerGroups);
      }
    },
    processBird(sbird) {
      // Get metadata
      let bird = this.turtledoves.filter(function(td) {
        return td.name == sbird.name;
      })[0];

      // Add data url to metadata
      bird.data = sbird.data;
      bird.opacity = sbird.opacity;

      let me = this;
      fetch(bird.data)
        .then(function(response) {
          return response.text();
        })
        .then(function(csv) {
          me.paintBird(csv, bird);
        })
        .catch(function(error) {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    paintBird(csvData, bird) {
      let ph = this.phrases;
      const geojsonMarkerOptions = {
        radius: 5,
        fillColor: bird.color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: bird.opacity
      };
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
            var previousPoint = [];
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
                if (
                  typeof previousPoint[0] !== "undefined" &&
                  previousPoint[0] !== null
                ) {
                  from = turfHelpers.point(previousPoint[0]);
                } else {
                  // First / Start point
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
                previousPoint[0] = [
                  feature.geometry.coordinates[1],
                  feature.geometry.coordinates[0]
                ];
                layer.bindTooltip(
                  String(
                    "<b>" +
                      feature.properties["name"] +
                      "</b> (" +
                      feature.properties["timestamp"] +
                      " )<br>" +
                      ph["flightRoute"] +
                      " <b>" +
                      feature.properties["distance"] +
                      " km</b>"
                  ),
                  {}
                );
              },
              pointToLayer: function(feature, latlng) {
                if (feature === data.features[data.features.length - 1]) {
                  // Image for endpoint
                  return L.marker(latlng, {
                    icon: L.icon({
                      iconSize: [38, 38],
                      iconUrl: bird.avatar,
                      className: "endpoint"
                    })
                  });
                } else {
                  return L.circleMarker(latlng, geojsonMarkerOptions);
                }
              }
            });

            // route/line
            // Adding a polyline. Define an array of Latlng objects (points
            // along the line) then use it to make a polyline
            var polyline = L.polyline(coords, {
              color: bird.color,
              opacity: bird.opacity
            });

            // create a decorator
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

            var group = L.featureGroup([points, polyline, decorator]);
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
.endpoint {
  border-radius: 50%;
}

#map {
  width: 100% !important;
  height: 100% !important;
  z-index: 0;
}
</style>
