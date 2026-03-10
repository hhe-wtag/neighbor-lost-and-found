<template>
  <div class="min-h-screen bg-[#f5f2ee] font-[DM_Sans]">
    <div class="relative z-10 mx-auto max-w-7xl px-4 py-8 sm:px-8">
      <!-- Header -->
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 class="font-['Playfair_Display'] text-3xl font-bold text-stone-900">Nearby Items</h1>
          <p class="mt-1 text-sm text-stone-400">Find lost & found reports around your location</p>
        </div>
        <Button
          variant="ghost"
          class="gap-2 text-xs font-medium uppercase tracking-widest text-stone-500 hover:text-stone-900 self-start"
          @click="router.push('/items')"
        >
          <ArrowLeft class="h-4 w-4" /> Back to Items
        </Button>
      </div>

      <!-- Controls -->
      <Card class="mb-6 border-0 bg-white/60 shadow-sm backdrop-blur-sm">
        <CardContent class="flex flex-col gap-4 p-5 sm:flex-row sm:items-end">
          <!-- Radius slider -->
          <div class="flex-1 space-y-2">
            <div class="flex items-center justify-between">
              <Label class="text-[0.68rem] uppercase trac king-widest text-stone-400"
                >Search Radius</Label
              >
              <span class="text-xs font-medium text-stone-700">{{ radius }} km</span>
            </div>
            <input
              v-model.number="radius"
              type="range"
              min="1"
              max="50"
              step="1"
              class="w-full accent-stone-900 cursor-pointer"
            />
            <div class="flex justify-between text-[0.65rem] text-stone-300">
              <span>1 km</span><span>50 km</span>
            </div>
          </div>

          <!-- Type filter -->
          <div class="flex-1 space-y-1.5">
            <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400">Type</Label>
            <Select v-model="typeFilter">
              <SelectTrigger class="border-stone-200 bg-white">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="lost">Lost</SelectItem>
                <SelectItem value="found">Found</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <Button
              class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
              :disabled="!userLocation || itemStore.loading"
              @click="search"
            >
              <Loader2 v-if="itemStore.loading" class="mr-2 h-4 w-4 animate-spin" />
              <MapPin v-else class="mr-2 h-4 w-4" />
              Search
            </Button>
            <Button
              variant="outline"
              class="border-stone-200 text-stone-500 hover:text-stone-900 transition-all"
              :disabled="locationLoading"
              @click="detectLocation"
            >
              <Loader2 v-if="locationLoading" class="mr-2 h-4 w-4 animate-spin" />
              <LocateFixed v-else class="mr-2 h-4 w-4" />
              {{ userLocation ? 'Relocate' : 'Detect Location' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <!-- Location error -->
      <div v-if="locationError" class="mb-4 space-y-3">
        <Alert variant="destructive">
          <AlertCircle class="h-4 w-4" />
          <AlertDescription>{{ locationError }}</AlertDescription>
        </Alert>

        <!-- Manual coordinate entry fallback -->
        <Card class="border-0 bg-white/60 shadow-sm backdrop-blur-sm">
          <CardContent class="p-5 space-y-3">
            <p class="text-xs font-medium uppercase tracking-widest text-stone-400">
              Enter coordinates manually
            </p>
            <div class="flex gap-3">
              <div class="flex-1 space-y-1.5">
                <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400"
                  >Latitude</Label
                >
                <Input
                  v-model.number="manualLat"
                  type="number"
                  step="any"
                  placeholder="e.g. 23.8103"
                  class="border-stone-200 bg-white text-sm"
                />
              </div>
              <div class="flex-1 space-y-1.5">
                <Label class="text-[0.68rem] uppercase tracking-widest text-stone-400"
                  >Longitude</Label
                >
                <Input
                  v-model.number="manualLng"
                  type="number"
                  step="any"
                  placeholder="e.g. 90.4125"
                  class="border-stone-200 bg-white text-sm"
                />
              </div>
              <div class="flex items-end">
                <Button
                  class="bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
                  :disabled="!manualLat || !manualLng"
                  @click="applyManualLocation"
                >
                  <MapPin class="mr-2 h-4 w-4" /> Use
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- No location yet -->
      <div
        v-if="!userLocation && !locationLoading"
        class="flex flex-col items-center gap-3 py-16 text-stone-400"
      >
        <MapPin class="h-12 w-12 text-stone-200" />
        <p class="text-sm">Click "Detect Location" to find items near you.</p>
      </div>

      <!-- Detecting -->
      <div
        v-else-if="locationLoading"
        class="flex flex-col items-center gap-3 py-16 text-stone-400"
      >
        <Loader2 class="h-8 w-8 animate-spin text-amber-700/60" />
        <p class="text-sm">Getting your location…</p>
      </div>

      <!-- Map + Results -->
      <div v-else-if="userLocation" class="flex flex-col gap-6 animate-in fade-in duration-500">
        <!-- Map -->
        <Card class="overflow-hidden border-0 bg-stone-100 shadow-md">
          <div ref="mapRef" class="w-full h-[480px]" />
        </Card>

        <!-- Results summary -->
        <div class="flex items-center justify-between">
          <p class="text-sm text-stone-500">
            <span class="font-medium text-stone-800">{{ itemStore.items.length }}</span>
            item{{ itemStore.items.length !== 1 ? 's' : '' }} found within
            <span class="font-medium text-stone-800">{{ radius }} km</span>
          </p>
          <p v-if="itemStore.loading" class="text-xs text-stone-400 flex items-center gap-1">
            <Loader2 class="h-3 w-3 animate-spin" /> Updating…
          </p>
        </div>

        <!-- Empty -->
        <div
          v-if="!itemStore.loading && itemStore.items.length === 0"
          class="flex flex-col items-center gap-3 py-12 text-stone-400"
        >
          <PackageSearch class="h-10 w-10 text-stone-200" />
          <p class="text-sm">No items found in this area. Try increasing the radius.</p>
        </div>

        <!-- Item cards strip -->
        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <Card
            v-for="item in itemStore.items"
            :key="item.id"
            class="group flex flex-col overflow-hidden border-0 bg-[#fffcf9] shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer"
            :class="{ 'ring-2 ring-stone-900': highlightedItemId === item.id }"
            @click="focusItem(item)"
            @mouseenter="highlightedItemId = item.id"
            @mouseleave="highlightedItemId = null"
          >
            <div class="relative h-36 w-full overflow-hidden bg-stone-100">
              <img
                :src="item.photo_url ?? placeholderImage"
                class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                alt=""
                @error="(e) => ((e.target as HTMLImageElement).src = placeholderImage)"
              />
              <Badge
                :class="[
                  'absolute left-2 top-2 backdrop-blur-sm border text-[0.65rem]',
                  item.type === 'lost'
                    ? 'bg-red-50/90 text-red-600 border-red-200'
                    : 'bg-emerald-50/90 text-emerald-700 border-emerald-200',
                ]"
              >
                {{ item.type === 'lost' ? 'Lost' : 'Found' }}
              </Badge>
            </div>
            <CardHeader class="pb-1 pt-3 px-3">
              <CardTitle
                class="font-['Playfair_Display'] text-sm font-bold text-stone-900 line-clamp-1"
              >
                {{ item.title }}
              </CardTitle>
              <CardDescription class="text-xs line-clamp-2 text-stone-400">
                {{ item.description || 'No description.' }}
              </CardDescription>
            </CardHeader>
            <CardContent class="px-3 pb-3 mt-auto">
              <div class="flex items-center justify-between">
                <span class="text-[0.65rem] text-stone-400 truncate max-w-[60%]">
                  {{ item.location_name || 'Unknown location' }}
                </span>
                <Button
                  size="sm"
                  class="h-7 text-xs bg-stone-900 text-stone-50 hover:bg-stone-800 active:scale-[0.98] transition-all"
                  @click.stop="router.push(`/items/${item.id}`)"
                >
                  View
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useItemStore } from '@/stores/item'
import type { ItemListResponse } from '@/interfaces/item'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import {
  ArrowLeft,
  MapPin,
  LocateFixed,
  Loader2,
  AlertCircle,
  PackageSearch,
} from 'lucide-vue-next'

import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import placeholderImage from '@/assets/product-placeholder.jpg'
import Input from '../ui/input/Input.vue'

const router = useRouter()
const itemStore = useItemStore()

// ── Location state ──
const userLocation = ref<{ lat: number; lng: number } | null>(null)
const locationLoading = ref(false)
const locationError = ref('')
const radius = ref(5)
const typeFilter = ref('all')
const highlightedItemId = ref<number | null>(null)

// ── Manual location fallback ──
const manualLat = ref<number | null>(null)
const manualLng = ref<number | null>(null)

const applyManualLocation = async () => {
  if (!manualLat.value || !manualLng.value) return
  locationError.value = ''
  userLocation.value = { lat: manualLat.value, lng: manualLng.value }
  await nextTick()
  initMap(manualLat.value, manualLng.value)
  await search()
}

// ── Map ──
const mapRef = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let userMarker: L.Marker | null = null
let radiusCircle: L.Circle | null = null
// item id → marker so we can highlight on card hover
const itemMarkers = new Map<number, L.Marker>()

const markerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

const userIcon = L.divIcon({
  className: '',
  html: `<div class="w-4 h-4 rounded-full bg-stone-900 border-2 border-white shadow-lg"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

const initMap = (lat: number, lng: number) => {
  if (!mapRef.value) return

  if (map) {
    map.remove()
    map = null
  }

  map = L.map(mapRef.value, { zoomControl: true }).setView([lat, lng], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
  }).addTo(map)

  // User location dot
  userMarker = L.marker([lat, lng], { icon: userIcon })
    .addTo(map)
    .bindPopup('<strong>Your Location</strong>')

  // Radius circle
  radiusCircle = L.circle([lat, lng], {
    radius: radius.value * 1000,
    color: '#1c1917',
    fillColor: '#1c1917',
    fillOpacity: 0.04,
    weight: 1.5,
    dashArray: '6 4',
  }).addTo(map)

  nextTick(() => map?.invalidateSize())
}

const updateRadiusCircle = () => {
  if (!radiusCircle || !userLocation.value) return
  radiusCircle.setRadius(radius.value * 1000)
  // Fit map to circle bounds
  map?.fitBounds(radiusCircle.getBounds(), { padding: [24, 24] })
}

const clearItemMarkers = () => {
  itemMarkers.forEach((m) => m.remove())
  itemMarkers.clear()
}

const plotItemMarkers = (items: ItemListResponse[]) => {
  clearItemMarkers()
  items.forEach((item) => {
    if (!item.lat || !item.lng || !map) return

    const isLost = item.type === 'lost'
    const dot = L.divIcon({
      className: '',
      html: `<div style="
        width:12px;height:12px;border-radius:50%;
        background:${isLost ? '#dc2626' : '#16a34a'};
        border:2px solid white;
        box-shadow:0 1px 4px rgba(0,0,0,0.3);
      "></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    })

    const marker = L.marker([item.lat, item.lng], { icon: dot })
      .addTo(map!)
      .bindPopup(buildItemPopup(item), { maxWidth: 240 })

    marker.on('click', () => {
      highlightedItemId.value = item.id
    })

    itemMarkers.set(item.id, marker)
  })
}

const buildItemPopup = (item: ItemListResponse): string => {
  const typeColor = item.type === 'lost' ? '#dc2626' : '#16a34a'
  const typeLabel = item.type === 'lost' ? 'Lost' : 'Found'
  const img = item.photo_url
    ? `<img src="${item.photo_url}" style="width:100%;height:80px;object-fit:cover;border-radius:6px;margin-bottom:8px;" />`
    : ''

  return `
    <div style="font-family:'DM Sans',sans-serif;min-width:180px;">
      ${img}
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:4px;">
        <strong style="font-size:13px;color:#1c1917;line-height:1.3;">${item.title}</strong>
        <span style="
          font-size:10px;font-weight:600;letter-spacing:0.05em;
          padding:2px 8px;border-radius:20px;white-space:nowrap;
          background:${typeColor}18;color:${typeColor};border:1px solid ${typeColor}40;
        ">${typeLabel}</span>
      </div>
      <p style="font-size:11px;color:#78716c;margin:0 0 8px;line-height:1.4;">${item.location_name ?? ''}</p>
      <a href="/items/${item.id}" style="
        display:block;text-align:center;
        background:#1c1917;color:#fafaf9;
        font-size:11px;font-weight:500;
        padding:5px 12px;border-radius:8px;
        text-decoration:none;
      ">View Details →</a>
    </div>
  `
}

const focusItem = (item: ItemListResponse) => {
  highlightedItemId.value = item.id
  const marker = itemMarkers.get(item.id)
  if (marker && map) {
    map.setView(marker.getLatLng(), 16, { animate: true })
    marker.openPopup()
  }
}

// ── Geolocation ──
const detectLocation = () => {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation is not supported by your browser.'
    return
  }
  locationLoading.value = true
  locationError.value = ''

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      locationLoading.value = false
      await nextTick()
      initMap(pos.coords.latitude, pos.coords.longitude)
      await search()
    },
    (err) => {
      locationLoading.value = false
      const messages: Record<number, string> = {
        1: 'Location access denied. Please allow location access in your browser settings.',
        2: 'Your location could not be determined. This is common in simulators or VPNs — enter your coordinates manually below.',
        3: 'Location request timed out. Please try again or enter coordinates manually.',
      }
      locationError.value = messages[err.code] ?? 'Unable to retrieve your location.'
    },
    { enableHighAccuracy: true, timeout: 10000 },
  )
}

// ── Search ──
const search = async () => {
  if (!userLocation.value) return
  await itemStore.fetchAllItems({
    lat: userLocation.value.lat,
    lng: userLocation.value.lng,
    radius: radius.value,
    type: typeFilter.value === 'all' ? undefined : typeFilter.value,
    limit: 100,
    offset: 0,
  })
  plotItemMarkers(itemStore.items)
  updateRadiusCircle()
}
// Re-search when radius changes (debounced)
let radiusTimer: ReturnType<typeof setTimeout> | null = null
watch(radius, () => {
  if (radiusTimer) clearTimeout(radiusTimer)
  radiusTimer = setTimeout(() => {
    if (userLocation.value) search()
  }, 500)
})

// Highlight matching marker when card is hovered
watch(highlightedItemId, (id) => {
  if (!id) return
  const marker = itemMarkers.get(id)
  if (marker && map) {
    marker.openPopup()
  }
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');
</style>
