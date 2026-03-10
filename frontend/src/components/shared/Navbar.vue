<template>
  <nav
    class="sticky top-0 z-40 border-b border-stone-200/60 bg-[#f5f2ee]/90 backdrop-blur-md font-[DM_Sans]"
  >
    <div class="mx-auto max-w-7xl px-4 sm:px-8">
      <div class="flex h-14 items-center justify-between">
        <!-- Brand -->
        <router-link to="/items" class="flex items-center gap-2 shrink-0">
          <span class="font-['Playfair_Display'] text-lg font-bold text-stone-900 leading-none">
            Neighbour
          </span>
          <span
            class="text-[0.6rem] font-medium uppercase tracking-widest text-stone-400 leading-none mt-0.5"
          >
            Lost & Found
          </span>
        </router-link>

        <!-- Nav links -->
        <ul class="hidden sm:flex items-center gap-1">
          <li>
            <router-link
              to="/items"
              :class="[
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium uppercase tracking-widest transition-all',
                isActive('/items') && !isActive('/items/search')
                  ? 'bg-stone-900 text-stone-50'
                  : 'text-stone-500 hover:text-stone-900 hover:bg-stone-100',
              ]"
            >
              <Package class="h-3.5 w-3.5" />
              Items
            </router-link>
          </li>
          <li>
            <router-link
              to="/items/search"
              :class="[
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium uppercase tracking-widest transition-all',
                isActive('/items/search')
                  ? 'bg-stone-900 text-stone-50'
                  : 'text-stone-500 hover:text-stone-900 hover:bg-stone-100',
              ]"
            >
              <MapPin class="h-3.5 w-3.5" />
              Nearby
            </router-link>
          </li>
        </ul>

        <!-- Auth section -->
        <div v-if="userStore.isAuthenticated" class="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger
              class="flex items-center gap-2 rounded-xl border border-stone-200 bg-white/70 px-2.5 py-1.5 shadow-sm hover:border-stone-300 hover:bg-white transition-all outline-none"
            >
              <Avatar class="h-7 w-7 shrink-0">
                <AvatarFallback class="bg-stone-200 text-stone-700 text-xs font-semibold">
                  {{ firstLetter }}
                </AvatarFallback>
              </Avatar>
              <span
                class="hidden sm:block text-xs font-medium text-stone-700 max-w-[100px] truncate"
              >
                {{ name }}
              </span>
              <ChevronDown class="h-3 w-3 text-stone-400 shrink-0" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-52 bg-[#fffcf9] border-stone-200 shadow-lg">
              <!-- Greeting -->
              <div class="px-3 py-2.5 border-b border-stone-100">
                <p class="text-[0.65rem] uppercase tracking-widest text-stone-400">Signed in as</p>
                <p class="text-sm font-medium text-stone-900 truncate mt-0.5">{{ name }}</p>
              </div>

              <div class="py-1">
                <DropdownMenuItem
                  class="flex items-center gap-2 px-3 py-2 text-sm text-stone-600 hover:text-stone-900 cursor-pointer"
                  @click="router.push('/my-items')"
                >
                  <Package class="h-4 w-4 text-stone-400" />
                  My Items
                </DropdownMenuItem>
                <DropdownMenuItem
                  class="flex items-center gap-2 px-3 py-2 text-sm text-stone-600 hover:text-stone-900 cursor-pointer"
                  @click="router.push('/profile')"
                >
                  <User class="h-4 w-4 text-stone-400" />
                  Profile Settings
                </DropdownMenuItem>

                <!-- Mobile-only nav links in dropdown -->
                <DropdownMenuItem
                  class="flex sm:hidden items-center gap-2 px-3 py-2 text-sm text-stone-600 hover:text-stone-900 cursor-pointer"
                  @click="router.push('/items')"
                >
                  <Package class="h-4 w-4 text-stone-400" />
                  Items
                </DropdownMenuItem>
                <DropdownMenuItem
                  class="flex sm:hidden items-center gap-2 px-3 py-2 text-sm text-stone-600 hover:text-stone-900 cursor-pointer"
                  @click="router.push('/items/search')"
                >
                  <MapPin class="h-4 w-4 text-stone-400" />
                  Nearby
                </DropdownMenuItem>
              </div>

              <DropdownMenuSeparator class="bg-stone-100" />

              <div class="py-1">
                <DropdownMenuItem
                  class="flex items-center gap-2 px-3 py-2 text-sm text-red-500 hover:text-red-600 hover:bg-red-50 cursor-pointer"
                  @click="handleLogout"
                >
                  <LogOut class="h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <!-- Unauthenticated -->
        <div v-else class="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            class="text-xs font-medium uppercase tracking-widest text-stone-500 hover:text-stone-900"
            @click="router.push('/login')"
          >
            Login
          </Button>
          <Button
            size="sm"
            class="bg-stone-900 text-stone-50 hover:bg-stone-800 text-xs font-medium uppercase tracking-widest active:scale-[0.98] transition-all"
            @click="router.push('/register')"
          >
            Register
          </Button>
        </div>
      </div>
    </div>
  </nav>
</template>
<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { LogOut, User, MapPin, Package, ChevronDown } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

onMounted(async () => {
  try {
    await userStore.fetchUserProfile()
  } catch (error) {
    console.error('Error occurred:', error)
  }
})

const firstLetter = computed(() => userStore.profile?.name?.[0]?.toUpperCase() ?? '?')
const name = computed(() => userStore.profile?.name || 'User')

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}
</script>
