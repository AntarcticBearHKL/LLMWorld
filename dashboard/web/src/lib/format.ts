export const countLabel = (value: number, singular: string): string =>
  `${value} ${value === 1 ? singular : `${singular}s`}`

export const formatMtime = (seconds: number | null): string =>
  seconds === null ? "never" : new Date(seconds * 1000).toLocaleString()
