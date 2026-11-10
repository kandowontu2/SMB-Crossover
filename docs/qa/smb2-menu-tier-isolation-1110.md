# SMB2 preview health stays on the character-select screen

The MMC5 Downloads nightly is
`9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97`.
Its parent was
`49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7`.
The 2,099,510-byte IPS is
`bfc6266979f6e5ecef0344b4f7266d308b58edaefb86d59afd766662f7fb75a7`.

The old menu initialized SMB2’s private health record and immediately
exported it to the shared SMB player state. That export wrote power tier 1
at PRG 118, CPU `$AF8A`. After moving to Mr. Gimmick and selecting Sonic,
the player therefore entered 1‑1 powered up. The same sequence now starts
Sonic at tier 0.

The source change keeps the same 58-byte range in PRG 118 and changes
24 bytes. The shared initializer publishes the private preview record while
on the title screen. It exports the gameplay record in non-title modes.
The NewLife entry and subsequent code addresses are unchanged. The first
active SMB2 movement update still exports the large form and tier 1.

The compiled menu audit reproduced the old contamination, then checked all
100 names and Start/A availability against the corrected build. For all
eight SMB2 and Doki Doki previews it compared sprite OAM, CHR publication,
the palette and name VRAM commands, and the private 31 health and large
form. All eight reached active 1‑1 and ran 60 ordinary gameplay updates
with two lives, the same health and the large form.

Mesen replayed the old ROM from Downloads. The controller visited all
eight previews, moved to Mr. Gimmick and selected Sonic. It observed
seven title-mode power-tier exports and Sonic entering 1‑1 at tier 1.
The same route on the candidate and installed ROM observed zero title
exports and Sonic entering at tier 0. Separate Mesen runs selected SMB2
Mario and Lina, observed the first active-frame tier export and reached
X100 with two hearts, the large form and two lives. The title replay and
two opening runs use normal input and produce no captures.

| Physical evidence | SHA-256 |
| --- | --- |
| Controller | `99e7a5cc2b8ef6f33b960b9fe0196bced1015488aa5b04bbc17d18c05ca531b6` |
| Old Downloads, leaked Sonic start | `7576d15350c266e87038a8d8ebbe0b398908a0b17db4a4a15fec0e884367cbc2` |
| Corrected candidate and Downloads, Sonic start | `483e6d7127bf43cd914e0accf04ccefabf0a764b7479991df1a477b22ae61fdf` |
| Corrected candidate and Downloads, SMB2 Mario opening | `c05a01c4391f0bcfda23142af7ac751023be948f322a973fefc4e9e98fc1aee1` |
| Corrected candidate and Downloads, Lina opening | `6718cddadc3058ceb6de92ea24401de501ad953e799723fc6a21e8c7701d603c` |

The installer checks the IPS round trip and the Downloads automatic patch
guard before and after delivery. No backup ROM or helper platform is
added. The previous [Sonic mushroom and injury replay](sonic-earned-injury-delivery-1110.md)
documents the preceding fix. Full stages and earned upgrades for all
eight SMB2 and Doki Doki characters remain in testing.
