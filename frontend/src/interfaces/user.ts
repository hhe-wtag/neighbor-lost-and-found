export interface UserProfile {
  _id: string
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
