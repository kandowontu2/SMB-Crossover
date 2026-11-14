# Donkey Kong mushroom graphics: verified nightly delivery

The Downloads nightly is now
`1daca93f837e894a3ee5b3d8cef54622336726f4df243c6bfb997130323f3baa`,
2,097,168 bytes, at
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`.
It equals the tested flag-slot candidate byte for byte. This successor changes
only three granted Donkey Kong renderer operands from82ec; the shared world
CHR reset and all earlier fixes remain intact. Mushroom graphics no longer
share DK's barrel tile window. Body/barrel artwork, palettes, physics and
helper placements are unchanged.

Source qualifications and their explicit limits are in
`dk-private-sprite-window7-1114.md`. The exact grant is
`allocations/dk-private-sprite-window7-1114.json`. Parent-parity checks retain
the existing source first-pipe stall and death/restart limitation; those
probes are not successful gameplay routes or newly introduced defects.
Prince's collision and private sprite issues remain open.

## Private Mesen image acceptance

Root67126 passes the frozen `cf40a25c...` controller on the private candidate:
747 physical frames / 690 completed Main updates, two lives, power0. The
actual compiled menu selects slot27/raw28. A live Goomba, naturally emerged
mature mushroom and an ordinary B-emitted barrel produce three in-memory
PNGs. Root viewed all three: Goomba is retained, the mushroom is now visible
and correct, and barrel/body/mushroom coexist. Receipt:
`93758ca3c721d793c2be8708ad90bbf543fd144028603449acc5c12c004f5922`.

| Image | Bytes | PNG SHA256 |
| --- | ---: | --- |
| Live Goomba |2654|`120a0ebac0c651bc92c4b593f8bc04723f3fdef1018c542d33e6bfb34543c1a3`|
| Natural mature mushroom |2772|`4f5848db3c760505a51d5524df028e37fd343c21d4a8c04577b1bb957adb01c9`|
| Ordinary emitted barrel |2806|`43ce86a7fc91c4e36f2bf718a5796d529bb9c3c4f719e6ae911c62ba66b3dc53`|

An independent post-run read of the exact candidate compares eight actual
native pattern-pair observations across six distinct pairs: Goomba17 at
offsets544/576, mushroom16 at960/992, barrel823 at448/480. Every byte matches.
Actual barrel tiles DD/DF select odd sprite window7; native mushroom7C/7E
retain window1. The Goomba PNG is identical to the corrected82ec baseline.
This proves this rendering scope, not all DK abilities or a full-stage clear.

## Direct Downloads installation and replay

Metadata8526 authenticates the exact candidate, source modules and strict
portable inverse. The GB Pit regression adapter changes only the structured
ROM pin/hook-bank metadata; its controller body is byte-identical to the
qualified82ec route. Its LF SHA256 is
`b4ac5e21e7fca02bda67764f1ef3ca1e2b3050150f02e41635c42848198ec26a`.

Root17738 completes with exit0. The installer replaces the official Downloads
file directly, then launches that exact Downloads path for both checks:

- DK repeats the private747/690 result, the exact receipt above and all three
  exact PNG hashes.
- GB Pit completes5589 physical frames /4386 Main entries=returns,2822 actual
  ability-update calls and63 in1-2. Full nonshortcut flag/castle/entrance then
  25 living grounded1-2 updates finish atX40/Y176/high1/native0/lives2/power0/
  Star0/variant1. Counts equal82ec. Receipt:
  `f3643c87728b1423f2643287aa807de7807491a13339fd85895683b582562ea2`.

Pre/post sidecar patch guards pass with no associated IPS/BPS/UPS. Installed
bytes remain exact to the tested candidate after both replays. No backup,
patch, release, video, image file, state dump or receipt file is produced.
The rollback-on-failure path was not exercised; it restores the authenticated
parent directly from memory without making a backup file.

All delivery work resumes the existing two-file
`build/smb2-flag-native-1113` slot, max-files2. It now contains1daca and the
last GB regression controller b4ac. Root's single Mesen queue is free after
terminal17738. GitHub releases must remain empty. Overall roster and natural
powerup qualification remain incomplete.
