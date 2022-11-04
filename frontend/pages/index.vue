<template>
  <div id="map-wrap" style="height: 100vh">
    <client-only>
      <l-map :zoom=13 :center="markers[0]" @click="clickMap">
        <l-tile-layer url="http://{s}.tile.osm.org/{z}/{x}/{y}.png"></l-tile-layer>
        <l-marker
          v-for="marker in markers"
          :key="marker[0]"
          :lat-lng="marker"
        >
          <l-popup content="Marker" />
        </l-marker>
        <l-polygon :lat-lngs="polygon.latlngs" :color="polygon.color">
          <l-popup content="Polygon" />
        </l-polygon>
      </l-map>
    </client-only>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'nuxt-property-decorator'

@Component
export default class IndexPage extends Vue {
  markers = [[55.75049686624561, 37.62439727783204]]
  polygon ={
    latlngs: [[55.75049686624561, 37.62439727783204], [55.72049686625561, 37.92439797783204], [55.97049686623561, 37.87439727784204], [55.35049686624561, 37.62439727783204]],
    color: 'black'
  }

  clickMap (e: { latlng: { lat: number; lng: number } }) {
    const latlng = e.latlng
    for (const marker of this.markers) {
      if (marker[0] === latlng.lat || marker[1] === latlng.lng) return
    }
    this.markers.push([e.latlng.lat, e.latlng.lng])
  }
}
</script>
