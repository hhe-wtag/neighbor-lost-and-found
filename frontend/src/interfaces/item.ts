export type ItemType = 'lost' | 'found'

export type ItemStatus = 'open' | 'claimed' | 'resolved' | 'removed'

export interface ItemListResponse {
  id: number
  user_id: number
  type: ItemType
  title: string
  description: string
  category: string
  lat: number
  lng: number
  location_name: string | null
  status: ItemStatus
  created_at: string
  photo_url: string | null
}

export interface ItemOwnerResponse {
  id: number
  name: string | null
  email: string
}

export interface ItemResponse {
  id: number
  user_id: number
  type: ItemType
  title: string
  description: string | null
  category: string
  date_occurred: string | null
  lat: number
  lng: number
  location_name: string | null
  status: ItemStatus
  resolved_at: string | null
  created_at: string
  updated_at: string | null
  user: ItemOwnerResponse
  photo_url: null
}

export interface ItemCreate {
  type: ItemType
  title: string
  description?: string | null
  category: string
  date_occurred?: string | null
  lat: number
  lng: number
  location_name?: string | null
}

export interface ItemUpdate {
  title?: string | null
  description?: string | null
  category?: string | null
  date_occurred?: string | null
  lat?: number | null
  lng?: number | null
  location_name?: string | null
  status?: ItemStatus | null
}

export interface ClaimCreate {
  message: string
}

interface IClaimant {
  id: number
  email: string
  name: string
}

export interface ClaimListResponse {
  id: number
  item_id: number
  claimant: IClaimant
  message: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface MyClaimResponse {
  id: number
  item_id: number
  message: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}
