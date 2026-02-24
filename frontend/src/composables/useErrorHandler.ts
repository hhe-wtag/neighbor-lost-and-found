import { AxiosError } from 'axios'

export const useErrorHandler = () => {
  const handleError = (error: unknown): string => {
    if (error instanceof AxiosError) {
      const apiError = error.response?.data

      if (apiError) {
        const { message } = apiError

        if (typeof message === 'string') {
          return message
        }

        if (typeof message === 'object' && message !== null) {
          return Object.entries(message)
            .map(
              ([field, errors]) =>
                `${field}: ${Array.isArray(errors) ? errors.join('. ') : errors}`,
            )
            .join('. \n')
        }
      }

      return 'An unexpected error occurred.'
    }

    if (error instanceof Error) {
      return error.message || 'An unknown error occurred.'
    }

    return 'An unexpected error occurred.'
  }

  return { handleError }
}
