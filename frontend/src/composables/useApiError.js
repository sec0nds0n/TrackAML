import { ref } from 'vue';

export function useApiError() {
  const error = ref(null);
  const isLoading = ref(false);

  const handleApiError = (apiError) => {
    console.error('API Error:', apiError);
    
    // Map common HTTP status codes to user-friendly messages
    const errorMessages = {
      400: 'Invalid request. Please check your input.',
      401: 'Invalid credentials. Please try again.',
      403: 'Access denied. You don\'t have permission to perform this action.',
      404: 'The requested resource was not found.',
      409: 'Conflict. The resource already exists.',
      422: 'Validation error. Please check your input.',
      429: 'Too many requests. Please try again later.',
      500: 'Server error. Please try again later.',
      502: 'Bad gateway. The server is temporarily unavailable.',
      503: 'Service unavailable. Please try again later.',
      504: 'Gateway timeout. The request took too long to process.',
    };

    // Extract status code from error message or use default
    let statusCode = null;
    if (apiError.message) {
      const statusMatch = apiError.message.match(/status:\s*(\d+)/);
      if (statusMatch) {
        statusCode = parseInt(statusMatch[1]);
      }
    }

    // Set user-friendly error message
    if (statusCode && errorMessages[statusCode]) {
      error.value = errorMessages[statusCode];
    } else if (apiError.message) {
      error.value = apiError.message;
    } else {
      error.value = 'An unexpected error occurred. Please try again.';
    }

    return error.value;
  };

  const clearError = () => {
    error.value = null;
  };

  const setLoading = (loading) => {
    isLoading.value = loading;
  };

  return {
    error,
    isLoading,
    handleApiError,
    clearError,
    setLoading,
  };
}