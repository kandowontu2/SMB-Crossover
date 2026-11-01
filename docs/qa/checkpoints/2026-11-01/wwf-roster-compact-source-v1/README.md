# Complete WWF roster: compact source components

This is preparation for all six wrestlers. The installed nightly remains the
76-character28693c0b build; the other five wrestlers are still coming soon.

The new source package preserves all195 original poses and both facings. Its
group directory supports all original frames, including the six-frame groups.
Packed tile/role bytes and implicit group counts reduce all six metadata sets
plus reserved cookie slots to8182 bytes. The largest individual metadata set
is1685 bytes, fitting the existing1687-byte selected slot.

The actual6502 decoder passes688 pose/facing/clamp cases. Those tests caught
Bam Bam's17-cell poses overwriting the old64-byte buffer. A69-byte buffer fixes
the overwrite and grows the conditional WWF layout by five bytes. This changed
layout is source-tested; it is not yet linked into the host ROM.

The original music driver is relocated as actual6502 code. All16 command
handlers are recovered from source control flow. All six themes pass2400ticks
each with identical ordered APU writes, channel state and return registers.
The current8088-byte version keeps its ten scratch bytes in its own RAM bank,
restoring the host's two borrowed pointer bytes after every indirect read.
It leaves104 bytes in its8KiB bank. NativeNMI routing, sound-effect priorities,
audible playback and performance remain unverified. Worst-case source timing
is in the handoff; do not describe this as a60Hz result.

The measured storage plan uses113 of115 existing owner pages, preserving
Thomas's16 pages. Three common C2 pages are zeros. A single shared zero page
can simplify the loader while still leaving one spare page. This is a storage
fit, not a completed loader or a native playable-roster qualification.

Next: source-link the conditional layout, shared sparse cache, per-wrestler
metadata/cookies, cold portraits, palette/HUD tables and original theme routing
onto28693c0b. Retain the character-select timing repair. Validate every real
Select/Start transition, original-source movement/attacks and native graphics,
interrupts, scrolling and contacts before enabling the five menu alternates.
Then replace the one Downloads nightly without a backup and push the results.
