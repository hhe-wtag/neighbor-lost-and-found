export type ClaimStatus = 'pending' | 'approved' | 'rejected'

export interface ClaimSender {
  id: number
  name: string
  email: string
}

export interface ClaimMessage {
  id: number
  claim_id: number
  sender_id: number
  body: string
  created_at: string
  sender: ClaimSender
}

export interface ClaimItem {
  id: number
  title: string
}

export interface ClaimClaimant {
  id: number
  name: string
  email: string
}

// Owner list item shape
export interface ClaimListItem {
  id: number
  item_id: number
  claimant_user_id: number
  status: ClaimStatus
  created_at: string
  claimant: ClaimClaimant
  item: ClaimItem
  last_message: ClaimMessage | null
}

// Claimant's own claim shape
export interface MyClaimResponse {
  id: number
  item_id: number
  status: ClaimStatus
  created_at: string
  updated_at: string | null
  item: ClaimItem
  messages: ClaimMessage[]
}

export type ClaimListResponse = ClaimListItem[]

export interface ClaimCreate {
  opening_message: string
}

export interface ClaimMessageCreate {
  body: string
}

export interface ClaimStatusUpdate {
  status: ClaimStatus
}
