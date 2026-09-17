export const nounLabel = (value: number, singular: string): string =>
  value === 1 ? singular : `${singular}s`

export const countLabel = (value: number, singular: string): string =>
  `${value} ${nounLabel(value, singular)}`

export const formatMtime = (seconds: number | null): string =>
  seconds === null ? "never" : new Date(seconds * 1000).toLocaleString()
