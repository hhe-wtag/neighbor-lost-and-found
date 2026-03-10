export interface UserProfile {
  id: number
  name: string
  email: string | null
}

export interface Address {
  street: string | null
  city: string | null
  state: string | null
  zipCode: string | null
  country: string | null
}
