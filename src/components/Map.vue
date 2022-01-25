<template>
  <div
    id="map"
    v-resize="onResize" />
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
    seasons: {type: Array, default(){return []}},
    turtledoves: {type: Array, default(){return []}},
    phrases: {type: Object, default(){return {}}},
    backgroundmap: {type: String, default(){return "osm"}},
    mini: Boolean
  },
  data: () => ({
    map: {},
    urlTemplate: {},
    layerGroups: [],
    dialog: false,
    osm: new L.TileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution:
        'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors, ' + process.env.VUE_APP_GIT_HASH
    }),
    satellite: L.tileLayer.wms("https://tiles.maps.eox.at/?", {
      layers: "s2cloudless_3857",
      attribution:
        '<a href="https://s2maps.eu" target="_blank">Sentinel-2 cloudless - https://s2maps.eu</a> by <a href="https://eox.at/" target="_blank">EOX IT Services GmbH</a> (Contains modified Copernicus Sentinel data 2017 & 2018), '+process.env.VUE_APP_GIT_HASH
    })
  }),
  watch: {
    backgroundmap: {
      // function(newVal, oldVal)
      handler: function(newVal) {
        if (newVal === "osm") {
          this.satellite.remove();
          this.osm.addTo(this.map);
        } else {
          this.osm.remove();
          this.satellite.addTo(this.map);
        }
      },
      immediate: false
    },
    //// Layertree logic
    //layerGroups: {
    //  // function(newVal, oldVal)
    //  handler: function(newVal) {
    //    this.fitMapBounds(newVal);
    //  }
    //},
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
      center: [58, 45],
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

    this.osm.addTo(this.map);

    if (L.Browser.mobile) {
      map.tap.disable();
      // map.on("click", function(e)
      map.on("click", function(error) {
        if (error){
          // eslint-disable-next-line
          console.log(error);
        }
        this.$emit("update:mini", !this.mini);
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
        //this.map.fitBounds(bounds);
        this.map.panTo(bounds.getCenter())
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
        this.map.invalidateSize({ pan: false });
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
        color: "#000000",
        weight: 1,
        opacity: 1,
        fillOpacity: bird.opacity
      };

      // age "decay" of lines. Set dashOldOnes to true for activation
      // lines between data will become more transparent according to timestamp
      // age and the below definitions (30, 60, 90 days)
      var dashOldOnes = true;
      const now = new Date().valueOf();
      const monthOld = now - (86400000 * 30);
      const older = now - (86400000 * 60);
      const veryOld = now - (86400000 * 90);
      csv2geojson.csv2geojson(
        csvData,
        {
          latfield: "location_lat",
          lonfield: "location_long",
          delimiter: ","
        },
        (error, data) => {
          if (error) {
            // eslint-disable-next-line
            console.log(error);
          } else {
            var previousPoint = [];
            // define arrays to store coordinates
            const coords = []; //solid
            const coordsOld = []; // dash 3 5
            const coordsOlder = []; // dash 2 7
            const coordsVeryOld = []; // dash 1 10
            // removeEmpty(data);
            data.features = data.features.filter( // "visible: 0.0" indicates outlier value
              d => d.properties.visible !== "0.0" );
            // points
            var points = L.geoJSON(data, {
              onEachFeature: function(feature, layer) {
                const latlon = new L.LatLng(
                    feature.geometry.coordinates[1],
                    feature.geometry.coordinates[0]
                );
                const timestamp = new Date(feature.properties.timestamp).valueOf();
                if ( dashOldOnes && timestamp < veryOld) {
                  coordsVeryOld.push(latlon);
                } else if (dashOldOnes && timestamp < older) {
                  if (!coordsOlder.length && previousPoint[0]) {
                    coordsOlder.push(previousPoint[0])
                  }
                  coordsOlder.push(latlon);
                } else if (dashOldOnes && timestamp < monthOld) {
                  if (!coordsOld.length && previousPoint[0]) {
                    coordsOld.push(previousPoint[0])
                  }
                  coordsOld.push(latlon);
                } else {
                  if (!coords.length && previousPoint[0]) {
                    coords.push(previousPoint[0])
                  }
                  coords.push(latlon);
                }
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
                  distance.toFixed(2)
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
                  var ep = "endpoint " + "color-" + bird.color.substr(1);
                  return L.marker(latlng, {
                    icon: L.icon({
                      iconSize: [32, 32],
                      iconUrl: bird.avatar,
                      color: bird.color,
                      className: ep
                    })
                  });
                } else {
                  return L.circleMarker(latlng, geojsonMarkerOptions);
                }
              }
            });
            var featuregroup = [points];
            var decOptions = {
              patterns: [
                {
                  offset: 25,
                  repeat: 75,
                  symbol: L.Symbol.arrowHead({
                    pixelSize: 10,
                    pathOptions: {
                      color: bird.color,
                      fillOpacity: bird.opacity,
                      weight: 0
                    }
                  })
                }
              ]
            };
            var decorator = L.polylineDecorator(polyline, decOptions);
            featuregroup.push(decorator);
            if (coordsVeryOld.length >1) {
              var polylineVeryOld = L.polyline(coordsVeryOld, {
                color: bird.color,
                opacity: 0.5,
                dashArray: "1 10"
              });
              featuregroup.push(polylineVeryOld);
              featuregroup.push(L.polylineDecorator(polylineVeryOld, decOptions));
            }
            if (coordsOlder.length >1) {
              var polylineOlder = L.polyline(coordsOlder, {
                color: bird.color,
                opacity: 0.65,
                dashArray: "2 7"
              });
              featuregroup.push(polylineOlder);
              featuregroup.push(L.polylineDecorator(polylineOlder, decOptions));
            }
            if (coordsOld.length >1) {
              var polylineOld = L.polyline(coordsOld, {
                color: bird.color,
                opacity: 0.7,
                dashArray: "3 5"
              });
              featuregroup.push(polylineOld);
              featuregroup.push(L.polylineDecorator(polylineOld, decOptions));
            }
            var polyline = L.polyline(coords, {color: bird.color,opacity: 1});
            featuregroup.push(polyline);
            featuregroup.push(L.polylineDecorator(polyline, decOptions));
            var group = L.featureGroup(featuregroup);
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
  border-radius: 18px;
  border-style: solid;
  border-width: medium;
}

.color-000000 { border-color: #000000;}
.color-FFFF00 { border-color: #FFFF00;}
.color-1CE6FF { border-color: #1CE6FF;}
.color-FF34FF { border-color: #FF34FF;}
.color-FF4A46 { border-color: #FF4A46;}
.color-008941 { border-color: #008941;}
.color-006FA6 { border-color: #006FA6;}
.color-A30059 { border-color: #A30059;}
.color-FFDBE5 { border-color: #FFDBE5;}
.color-7A4900 { border-color: #7A4900;}
.color-0000A6 { border-color: #0000A6;}
.color-63FFAC { border-color: #63FFAC;}
.color-B79762 { border-color: #B79762;}
.color-004D43 { border-color: #004D43;}
.color-8FB0FF { border-color: #8FB0FF;}
.color-997D87 { border-color: #997D87;}
.color-5A0007 { border-color: #5A0007;}
.color-809693 { border-color: #809693;}
.color-DEAFD6 { border-color: #DEAFD6;}
.color-1B4400 { border-color: #1B4400;}
.color-4FC601 { border-color: #4FC601;}
.color-3B5DFF { border-color: #3B5DFF;}
.color-4A3B53 { border-color: #4A3B53;}
.color-FF2F80 { border-color: #FF2F80;}
.color-61615A { border-color: #61615A;}
.color-BA0900 { border-color: #BA0900;}
.color-6B7900 { border-color: #6B7900;}
.color-00C2A0 { border-color: #00C2A0;}
.color-FFAA92 { border-color: #FFAA92;}
.color-FF90C9 { border-color: #FF90C9;}
.color-B903AA { border-color: #B903AA;}
.color-D16100 { border-color: #D16100;}
.color-DDEFFF { border-color: #DDEFFF;}
.color-000035 { border-color: #000035;}
.color-7B4F4B { border-color: #7B4F4B;}
.color-A1C299 { border-color: #A1C299;}
.color-300018 { border-color: #300018;}
.color-0AA6D8 { border-color: #0AA6D8;}
.color-013349 { border-color: #013349;}
.color-00846F { border-color: #00846F;}

#map {
  width: 100% !important;
  height: 100% !important;
  z-index: 0;
}

</style>
