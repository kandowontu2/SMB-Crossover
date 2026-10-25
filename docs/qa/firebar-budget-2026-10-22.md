# Firebars disappearing in crowded scenes

The renderer always allocated firebars after every ordinary object. When the sprite list filled, the same low-priority firebars were rejected on every update. The OAM priority ring rotates already-allocated records, so it could not recover an object that never entered the list.

Firebars now take the existing shuffled object-list position0. The player retains its reservation, weapons retain their first allocation, and every ordinary object retains exactly one turn. The original live-owner/firebar-ID checks and all native collision parts remain unchanged. Crowded scenes share admission over time; the NES hardware limits still require flicker when overloaded. Sparse scenes retain every firebar part.

## Evidence

An authored dense native-renderer scene contains Bowser's two halves, a long firebar with its duplicate slot, two short firebars, nine hammers, block effects and projectiles. No OAM, ROM, CPU or hardware registers are patched; borrowed render fields are restored at the actual completed-draw return. This is a stress fixture, not a controller-only castle clear.

In64 completed lists on each old mapper build, both short firebars receive zero records every time; the long bar receives only8/12 parts. With the repair, the two short bars receive complete allocation in37/64 and50/64 lists, and the long bar in58/64. All17 ordinary authored objects still receive exactly one draw call. All64 observed DMA payloads match actual hardware sprite RAM, and every one of the24 firebar parts receives a nontransparent mapped sprite row within the eight-sprite scanline limit during the observation window.

The final aggregate has26 scoped native checks: admission ID/flag edges, sparse short/long firebars across the roster, native castle source pixels, Bill overload, Mega Man overload, real Bill/Link/Simon projectile wrappers, cannon cooldown, Cheats UI, score anchors and terrain publication, on both mappers. The original failed CE matrix is retained. One failure was a helper run without its required character wrapper. An independent observer proved the MMC3 buster test was sampling NSF music during NMI at the same CPU address; balanced interrupt guards correct the sampling while retaining the16/16 foreground-part visibility requirement.

The code adds18 renderer bytes and no RAM. Rebuilt baseline ROMs, headers and CHR are unchanged. In this full-list fixture, mean inclusive render time rises from26308 to26493 cycles on MMC3 and25409 to25591 on MMC5. These measurements include interrupt variance; they are not a general lag improvement. No claim is made that all flicker or lag is solved.

Final receipt: `build/verification/firebar-budget-ci/summary.json`. Checkpoint: `build/checkpoints/firebar-budget-ci/manifest.json`. Before/after native screenshots are retained with the test inputs and logs under `build/verification/firebar-budget-ce/`.

Later-castle traversal remains unverified. Ordinary menu-selected diagnostic drivers for4-4 fail at the initial ceiling/pit sequence; the2-4 Bill driver reaches x499 before a later pit. Those failures are retained. Existing1-4 actor evidence and this rendering repair do not certify every castle layout. The original full all-character abilities, source fidelity, SFX, optimization, final recordings and natural Hard showcase requests remain active.
