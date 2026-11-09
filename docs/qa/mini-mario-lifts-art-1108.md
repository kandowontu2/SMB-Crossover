# Mini Mario 1-1 lifts and Game Boy Color fireballs

The November 8 MMC5 candidate is `fc7d4554fed204e8efa4c4489ee70cd5c6529ce95e0d606ffee1cda525188ec5`.

## Traversal

Mini uses his original jumping and no longer grabs or jumps off walls. Three
native `$25` vertical girders supply the height needed for the 1-1 pipes at
X608, X736 and X912. Each girder is 32 pixels wide and starts at top Y192.
Their left edges are X560, X688 and X864. Their centers are X576, X704 and
X880. The original native actor owns motion, culling and sprite rendering.
Mini's downward source collision recognizes the live actor's top. Both the
actor manager and the support check verify the native slot before using it.

The controller replay boards and jumps off all three girders, passes all four
pipes and all three gaps, and reaches active 1-2 with both lives. The same
candidate earns and collects the first mushroom through normal gameplay.

## Fireball appearance

The pinned Game Boy Color ROM supplies the two 6×6 moving tiles and both
impact tiles. Moving frames follow the donor order, including the two-axis
mirrors and independent four-update phase clock. NES palette slot 2 maps the
source white, orange and red pixels to its existing colors. The two native
projectile slots, 4×4 collision boxes, bounce physics and impact lifetime
remain the host implementation. The impact frames fit that native lifetime.

The physical CHR page used for those tiles doubles as Mini metadata storage.
Cold loading reconstructs the original 256-byte metatile table in RAM before
publishing the owner cookies. The assembler and CPU check compare that full
table and both cookies against the exact bound data. No additional physical
CHR page is needed.

Mesen's powered fixture checks two distinct live shots in the same DMA in
both directions and upward, a rejected third shot, native bouncing, all four
moving phases, and the two impact tiles after hitting a staged Goomba.

## Timing

On the current candidate, the empty-area replay has 180 idle updates in 180
video frames. Walking both ways, braking, jumping and landing also register
one update per video frame with zero skipped NMIs and zero missing controller
polls. Powered idle is 60 updates in 60 frames. The active portion of the full
1-1 route is 2,597 updates in 3,084 video frames, with 1,132 skipped NMIs. Busy
scenes and some two-shot action still exceed the frame budget.

The isolated performance candidate `9855a47a` reduces the older same-controller
1-1 route from 1,157 to 1,069 skipped NMIs. This uses the older wall route, so
the counts are separate from the new lift route. The revised baseline sample
at X1518 attributes 30,962 foreground cycles and 37,326 elapsed cycles. The
normal NMI workload also consumes part of the NTSC frame budget.

The separate Goomba draw prototype preserves OAM output in CPU tests and
saves 90–97 cycles per ordinary actor. Its shared entry adds 12 cycles per
visible actor for other characters and is still private.

## Receipts

- `build/mini-current-delivery-1108/verified-delivery.json`
- `build/mini-fireball-gbc-route-1108/capture/result.json`
- `build/mini-fireball-gbc-idle-1108/capture/timing.json`
- `build/mini-fireball-gbc-power-1108/capture/result.json`
- `build/mini-fireball-gbc-impact-1108/capture/result.json`
- `build/mini-lift-admission-cpu-1108/proof.json`
- `build/mini-lift-v2-CPU-1108/floor-CPU.json`
- `build/mini-goomba-draw-1108-v1/goomba-funded-v2.json`
