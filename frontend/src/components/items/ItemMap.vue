<template>
  <div ref="mapRef" class="w-full h-64 rounded-lg z-0"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
  lat: number
  lng: number
  locationName: string | null
  description: string | null
}>()

const mapRef = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null

const buildPopup = () =>
  `<strong>${props.locationName ?? 'Location'}</strong><br/>${props.description ?? ''}`

const initMap = () => {
  if (!mapRef.value) return

  // Destroy any stale instance that may be bound to this element
  if (map) {
    map.remove()
    map = null
    marker = null
  }

  map = L.map(mapRef.value, { zoomControl: true }).setView([props.lat, props.lng], 15)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
  }).addTo(map)

  const icon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  })

  marker = L.marker([props.lat, props.lng], { icon }).addTo(map).bindPopup(buildPopup()).openPopup()

  nextTick(() => map?.invalidateSize())
}

// onMounted guarantees the mapRef div is in the DOM
onMounted(initMap)

onBeforeUnmount(() => {
  map?.remove()
  map = null
  marker = null
})

// Re-init when the item changes (navigating between detail pages)
watch(
  () => [props.lat, props.lng] as const,
  async ([lat, lng]) => {
    if (!map) {
      // Map was never initialised (e.g. prop arrived after mount)
      await nextTick()
      initMap()
      return
    }
    map.setView([lat, lng], 15)
    marker?.setLatLng([lat, lng]).bindPopup(buildPopup()).openPopup()
    map.invalidateSize()
  },
)
</script>
