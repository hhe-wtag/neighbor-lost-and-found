import { z } from 'zod'

// Replace with dynamic type if needed
export const itemTypes = ['lost', 'found'] as const
export const itemStatuses = ['open', 'resolved'] as const

// If categories come from API, you can override dynamically later
export const defaultCategories = ['electronics', 'documents', 'pets', 'clothing', 'other'] as const

export const itemValidationSchema = z.object({
  type: z.enum(itemTypes, { errorMap: () => ({ message: 'Type must be lost or found' }) }),

  title: z
    .string()
    .min(3, 'Title must be at least 3 characters long')
    .max(100, 'Title cannot exceed 100 characters')
    .nonempty('Title is required')
    .trim(),

  description: z
    .string()
    .min(10, 'Description must be at least 10 characters long')
    .max(1000, 'Description cannot exceed 1000 characters')
    .nonempty('Description is required')
    .trim(),

  category: z.string().refine((val) => val.length > 0, 'Category is required'), // optional: refine to match API categories dynamically

  location_name: z
    .string()
    .min(3, 'Location name must be at least 3 characters')
    .max(100, 'Location name cannot exceed 100 characters')
    .nonempty('Location name is required'),

  lat: z
    .number({ invalid_type_error: 'Latitude is required' })
    .min(-90, 'Latitude must be between -90 and 90')
    .max(90, 'Latitude must be between -90 and 90'),

  lng: z
    .number({ invalid_type_error: 'Longitude is required' })
    .min(-180, 'Longitude must be between -180 and 180')
    .max(180, 'Longitude must be between -180 and 180'),

  status: z
    .enum(itemStatuses, { errorMap: () => ({ message: 'Invalid status value' }) })
    .default('open'),

  endTime: z
    .string()
    .optional()
    .refine((value) => {
      if (!value) return true
      const endDate = new Date(value)
      const currentDate = new Date()
      return endDate > currentDate
    }, 'End time must be in the future'),
})

export type ItemFormValues = z.infer<typeof itemValidationSchema>
export default itemValidationSchema
