# Sonic and Super Sonic sprites

The current art packet uses the standing poses for both forms from
*Sonic the Hedgehog Improvement*, Vol. 2 1.7. Rayan64_C uploaded the rip.
The sheet credits Terwilf and Jabu for the original sprites.
[Source sprite sheet](https://www.spriters-resource.com/nes/sonicthehedgehogimprovement/asset/504880/)

The source PNG is 800×512. The checked-in packer verifies its SHA-256,
removes both teal backgrounds, and packs each right-facing pose into the
existing 16×32 body canvas. The normal Sonic conversion combines the two
source blues so red shoes and light details retain their own colors. The
Super Sonic conversion uses all three source shades. Each body occupies
four 8×16 pairs at tiles `$00/$02/$20/$22`. The same cells serve the
existing menu, lives and gameplay rendering paths.

Normal Sonic uses CHR224. The planned Super Sonic selection uses CHR226.
Both pages retain the existing Sonic ring HUD, world ring, sparkle and
scattered ring cells at their original indices. The packer recomputes
the shared Sonic transport cookie after all caller edits and art binding.

The normal art candidate
`5f89d5c96a1a602e823355fd6bcd2fad0e1b793f65befec9cfcb7edade6abb55`
passes the existing Mesen ring pickup, loss and OAM regression with
receipt `eb8bf5fcb78aa677aa39e26bf67d4fa565be005c9e650e01e9e93756fbecd897`.
The controller-only 1-1 route reaches the native flag, castle and active
1-2 on the same ROM. Its receipt is
`f2cc5206d7c198237a3274950d783121f18aef915ec162c6f52d014cf9e12e06`.
The native menu and stage ingress work for Super Sonic is in progress.
Additional movement poses and any Super Sonic-specific mechanics
require separate integration and verification. This art packet is private.
