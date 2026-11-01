# Karnov guarded host cache — source checkpoint

Progress only. The Downloads nightly remains the tested 85-character build.
The private candidate does not admit Karnov from the menu; all 36 cache service
rows explicitly reject until actual gameplay adapters exist.

The source/proof ZIP contains only the explicit current inputs and compact
receipts listed in files.json. It contains no ROM, object/debug image, capture
forest, or recursively restored dependency tree. The full game linker still
uses current 85-character objects from the retained baseline; this is a component packet,
not a standalone clean-build release.

The loader occupies 826 bytes of real bank 29 menu padding.
Its 4091-byte original actor/weapon kernel runs from
conditional RAM3/A000 with conditional RAM2/C000 state and the real foreground
R0/R1 at 3/4. It leaves NMI scratch 0..2 alone. CHR399..406 stores the 8KB
kernel; 407..411 holds the five original body pages.
All existing runtime symbols and ROM bytes outside the granted ranges remain
unchanged. Compile-time anonymous repeat names/farcall count may differ.

Verification: 12 forced-blank load combinations, 13 negative cases, 2112 full-cookie
checks, 148 typed dispatch cases, 33 retirement cases, 228 real host NMI/IRQ cuts,
12 normal/paused NMI cases, and 7808 donor-versus-linked CPU executions. Raster IRQ
intentionally changes the HUD CHR window; those actual ISR writes are recorded.
No native raster, terrain, earned powerup, sound or full-stage claim is made.

Active private output is build/karnov-host-resource-base-1101-v1. It remains
unqualified/mutable for the gameplay integration; this compact snapshot is
the immutable evidence for this stage. See handoff.json for the next work.
