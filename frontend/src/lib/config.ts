export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
}

export const endpoints = {
  analyzePdf: `${config.apiUrl}/analyze-pdf`,
  health: `${config.apiUrl}/health`,
  criteria: `${config.apiUrl}/criteria`,
}