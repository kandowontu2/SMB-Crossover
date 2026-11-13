# Current roster direction check — November 13

Checked the actual Downloads ROM
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`.
The native menu input, Select cycles, portrait renderer and NMI produced all
101 named identities across the32 roster slots. Root visually reviewed the
single resulting contact sheet: directional silhouettes and colored previews
face right; intrinsically frontal poses remain frontal. This includes Sonic,
Super Sonic, Link, the Mario groups, Bowser, Chip/Dale, Thomas and Goku.

The prior sheet mentioned in `menu-facing-1112.md` had been cleaned up. It was
not treated as a live artifact. This check generated one new current sheet at
`build/menu-facing-1112/roster.png`,116186bytes, SHA256
`0987b3ed80e4f7e2326b805c4c9ae91bec4e73e5205819b9ea155633c524f99f`.
The101 identity/portrait/silhouette receipt rows hash to
`f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7`
using sorted-key JSON. No ROM bytes, patches or backups were written.

Validation ran through the bounded builder with the existing
`build/menu-facing-1112` output root and a one-file cap. These are actual native
menu/OAM/CHR results in the CPU peripheral model plus visual inspection. This
check does not claim a new physical raster/flicker test, or that the shared
gray icon changes to individual alternate artwork.
