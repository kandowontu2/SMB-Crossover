Metal Storm: selected-player palette adaptation, revision 9

This is a source/CPU component, not a selectable character or native emulator
admission. It changes only Metal's pattern indices, shot palette bits and P0
queue. The parent selected red/white/black after reviewing the comparison.

The original body uses P0 [0F,26,0F,15], and original shots use P1
[0F,21,20,01]. Native world sprites need their existing P1/P2/P3. Both Metal
sets and all three native sets use three real nontransparent colors. Five
distinct full three-color sets cannot fit four sprite palettes by reindexing
alone. The underground and castle fixture contains thirteen distinct colors
even when 20/30 white are normalized. No native world palette is merged.

The chosen P0 is [0F,26,20,0F]. Body indices map [0,1,2,3] to [0,1,3,1];
shots map [0,1,2,3] to themselves and use palette0. Of 10,946 opaque pixels
across 144 unique body patterns, all 6,087 black pixels and 3,719 dominant-red
pixels retain their original NES color. The 1,140 dark-red pixels become red.
Of 316 opaque pixels across five shot patterns, 116 white pixels retain their
color; 126 blue pixels become red and 74 deep-blue pixels become black. These
are unique-pattern counts, not animation-duration weighted counts. All shapes,
transparent masks, cell order/positions, facing/gravity flips and native-world
pattern bytes are exact. This is an intentional NES palette adaptation, not an
exact original two-palette reproduction.

Native P1/P2/P3 remain byte-for-byte unchanged. Twelve combined native producer
fixtures keep the green Koopa, Goomba, Piranha, mushroom, Podoboo and firebar
pixels exact in all four area palette contexts, with no hidden actors and at
most eight sprites per scanline. The native CHR initializer is the real
[18,20,21,22,23,24,25,26,4,5,6,7] logical list, matched to current ROM bytes;
the old renderer-only synthetic sequential bank fixture is not used for these
world-shape comparisons.

Two existing world objects share player P0 during phase0 of their color cycle:
the star (122 opaque pixels) and flower's upper part (100 pixels). Actual
DrawPowerUp uses (FrameCounter >> 1) & 3, so these change color for two frames
of each eight-frame cycle. That existing cycle is retained and the changed
pixels are disclosed. Bricks use native P3; a used block uses P3 on ground and
P1 in other areas. Actual linked DrawBlock/DrawPowerUp CPU fixtures confirm
these caller values. No enemy, green plant, mushroom, firebar or terrain palette
is silently substituted to fund Metal.

Reproduction (one output; every producer must use the bounded runner):

    python tools/audit/run_bounded_build_v1.py --output build/metal-storm-coexistence-1101-v9 --resume --timeout 180 -- python tools/audit/prepare_metal_storm_palette_host_1101_v9.py
    python tools/audit/run_bounded_build_v1.py --output build/metal-storm-coexistence-1101-v9 --resume --timeout 180 -- python tools/audit/check_metal_storm_palette_host_1101_v9.py

The frozen output cannot be resumed. Use a new owned root for a future revision
and adapt its OUT constants. The capture tool reuses its scoped witness after
one authorized current-debug read; it does not need to reread or copy the full
debug. Audit/compile dependencies remain external frozen v7/v8 lab objects and
their compact packets, not recursively duplicated trees.

The source adapter macros insert AND #FC before the original shot flip OR and
emit only the six-byte 3F11 palette packet. It retains the conservative original
queue guard X<72 and changes the packet copy count from 12 to 6. The emitted
renderer is 2,350 bytes, four bytes smaller than v8. The actor is 8,083 bytes;
only its two-byte JSR operand for the relocated MsObjectLifecycle changes.
Its constructor, source fractions/gravity, terrain and projectile ordering
remain exact in 576 original-donor differential frames after real native OAM
production, including both gravity directions and 285 frames with shots.

Host integration still must relink the callback and regenerate/authenticate a
new shared C2/C3 cookie covering the changed actor, renderer and packed CHR.
Invalidate both old headers before copying; source Ready cannot replace full
header authentication. The v8 cold loader's slot1023 is now Karnov HUD and
MUST NOT be retained. Proposed replacement500 and all other proposed carrier,
body, PRG and RAM leases still require global consumer closure and root grant.
This component writes no current ROM, menu, shared source, nightly or Git ref.

Pending gates: physical CHR500/global publication and handoff closure; actual
resource grant/loader/Main+ISR qualification; source health/death/hurt blink,
GravityFire, scenes, audio and native combat; controller-driven stage/shortcut
and every-powerup checks. No 60Hz, full-stage, hardware or complete-character
claim follows from this packet.
