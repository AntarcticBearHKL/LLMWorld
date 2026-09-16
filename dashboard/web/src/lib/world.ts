// Generated ids read as `<prefix>_<word>` (e.g. world_fish, district_harbor) so they are
// memorable and sayable instead of an opaque hex suffix. The word list is deliberately
// curated — short, lowercase, unambiguous English nouns.

const WORDS: readonly string[] = [
  // nature & water
  "acorn", "amber", "aspen", "aurora", "basalt", "blossom", "breeze", "brook", "canyon", "cedar",
  "cinder", "clover", "coral", "creek", "cyclone", "dawn", "delta", "dew", "dune", "dusk",
  "ember", "fern", "flint", "frost", "glacier", "granite", "grove", "harbor", "haze", "hollow",
  "island", "lagoon", "larch", "lava", "lily", "lotus", "lunar", "maple", "marble", "meadow",
  "mist", "monsoon", "moss", "oak", "ocean", "orchid", "pebble", "petal", "pine", "plateau",
  "pond", "prairie", "quartz", "rain", "reef", "ridge", "river", "sage", "sand", "savanna",
  "shore", "slate", "snow", "spruce", "stone", "storm", "stream", "summit", "swan", "thunder",
  "tide", "timber", "valley", "vapor", "willow", "wind", "winter", "zenith",
  // animals
  "badger", "beaver", "bison", "crane", "crow", "dolphin", "dove", "eagle", "falcon", "finch",
  "fox", "gazelle", "heron", "koala", "lark", "lemur", "lynx", "marlin", "moth", "otter",
  "owl", "panda", "puffin", "quail", "raven", "robin", "salmon", "seal", "sparrow", "stork",
  "swallow", "tiger", "trout", "turtle", "walrus", "whale", "wolf", "wren", "yak", "zebra",
  // places, craft & objects
  "anchor", "atlas", "bakery", "beacon", "bridge", "cabin", "camera", "canvas", "castle", "cellar",
  "compass", "cottage", "engine", "garden", "hatch", "helmet", "hive", "kettle", "kite", "ladder",
  "lantern", "lighthouse", "lodge", "lyric", "market", "meteor", "mirror", "nebula", "orchard", "postcard",
  "quill", "ribbon", "saddle", "sail", "signal", "sketch", "sonnet", "spindle", "studio", "telescope",
  "trellis", "tunnel", "velvet", "vine", "violin", "voyage", "whistle",
]

const pick = <T>(list: readonly T[]): T => list[Math.floor(Math.random() * list.length)] as T

export const randomName = (prefix: string, taken: Iterable<string> = []): string => {
  const used = new Set(taken)
  const pool = [...WORDS]
  while (pool.length > 0) {
    const word = pool.splice(Math.floor(Math.random() * pool.length), 1)[0]
    const candidate = `${prefix}_${word}`
    if (!used.has(candidate)) return candidate
  }
  const base = `${prefix}_${pick(WORDS)}`
  let suffix = 2
  while (used.has(`${base}_${suffix}`)) suffix += 1
  return `${base}_${suffix}`
}

export const randomWorldId = (taken: Iterable<string> = []): string => randomName("world", taken)

export const randomDistrictId = (taken: Iterable<string> = []): string =>
  randomName("district", taken)
