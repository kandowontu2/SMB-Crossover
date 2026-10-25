# Supplied1-4 firebar screenshot

The two empty mounts in the guide screenshot are intentional. Original SMB1
and the pinned hosted Crossover1.x and2.02 layouts activate these positions
in6-4, rather than1-4. The cartridge's character Easy/Hard option does not
replace SMB's later-world `SecondaryHardMode` actor gate.

The screenshot is Bass's historical MMC3 recording at emulator frame15122,
camera1238, player worldX1350. Native mount origins1280/64 and1472/144 use
hard-only enemy records `$04,$DB` and `$C9,$5D`. The mounts at1344/144 and
1408/64 are ordinary active bars. The supplied frame correctly shows those
two ordinary bars and the two empty later-world mounts.

Independent audit of the frozen private NT MMC5 checkpoint compared its full
castle actor stream with the user's original SMB1 cartridge and both hosted
Crossover layouts. Four diagnostic cases,1-4/6-4 by character Easy/Hard, confirm
two versus four bars. Eligible parts reach actual DMA OAM, retain their native
CHR bytes, and have nontransparent rows admitted by NES sprite scanline rules.
256hardware frames,1024owner checks and139,520CHR-byte checks passed.

The arena seeded public settings and player/scroll state at a native boundary;
it did not inject actors, sprite cache, OAM, CHR, CPU or ROM contents. This is
diagnostic evidence, not a controller-only clear. It resolves the reported
screenshot; it does not certify every castle or every previous disappearance
report. No level, firebar engine, public ROM or guide image was changed to
populate those intentionally empty mounts.

Source/ROM/file hashes and full proof pointers:
`build/verification/firebar-nt-audit/manifest.json`, SHA256
`7226a4b1f8ffc8b0c595996319b26a8128b8da407d6c85db8d523c2fa086bee6`.
Lossless diagnostic screenshots and source/reference evidence remain under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-firebar-nt-audit/verified`.

## Current PC recheck

The unchanged diagnostic also passes all four cases on current PC ROM
`37ad64c6f5e8859a29fc1982df6851a8f462292b3b44743c0283497774239af7`.
This is fresh hardware evidence:256 completed DMA frames,1,024 owner checks
and139,520 mapped native CHR byte checks. The actual linked39-byte castle
actor stream remains byte-exact with original SMB and the previous audit.
Seven of eight tracked source files are unchanged; the later metasprite
changes are covered by the fresh native tests instead of reused old evidence.

Additional read-only direct console captures retain actual PPU frame1254
in1-4and1341in6-4, with raw ARGB and independent RGB/PNG round trips.
Root inspected both direct images. Easy and Hard give identical corresponding
direct pixels: two active owners in1-4, four in6-4. The original asynchronous
diagnostic PNGs are retained separately.

Current proof and static source/actor comparison:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-firebars-ph/current-v1/proof.json`
and `current-source.json`. No gameplay source or public ROM was changed.
These remain seeded parser/render diagnostics, not ordinary castle clears.
