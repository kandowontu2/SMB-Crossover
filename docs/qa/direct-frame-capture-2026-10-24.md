# Capture timing correction and OJ route coverage

The accepted private OJ ROM is `88906bd9b21a65c2a09128730599a4683ff6123a655386c1b55d3e0ec1ef3b8a`.
The final roster/item goal is incomplete. OV is a separate, unaccepted rendering
optimization experiment; none of its results counts as an OJ route pass.

## Correction to earlier screenshot evidence

An exact-input Mike Hard replay reproduced variable one- or two-frame delay in
`emu.takeScreenshot()` output. A saved PNG's filename therefore does not prove
that it depicts that physical PPU frame. Earlier reports' complete-lossless-PNG
counts establish file retention, not unique or aligned physical-frame coverage.
All old PNGs, failed reports and diagnostic candidates remain preserved.

This qualification applies to earlier route overviews, transient-background
scans and sampled frame observations that used that API. It does not invalidate
exact native controller/trace comparisons, hardware DMA/CHR observations,
stack/SMC guards, CPU/IRQ differentials or their stated separate limits. It does
not establish that every earlier visual conclusion is wrong, either.

The original 53-route diagnostic scan decoded 258,578 retained PNG files. Its
one Mike candidate was investigated; the red rectangles were the scanner's
annotations, while the actual block changed through ordinary palette cycling.
That scan is not exhaustive physical-frame or human visual certification.

## Verified replacement

`capture_direct_replay_ot.py` records `emu.getScreenBuffer()` during each actual
PPU end-frame callback. It asserts the PPU frame identifier, retains a lossless
ARGB record archive, decodes every saved PNG and compares its RGB pixels to the
corresponding direct buffer. The temporary uncompressed stream is removed only
after independently verifying a complete gzip round trip. Original evidence is
not removed.

Independent full OJ replays now pass for Mike Hard (3,821 frames to the endpoint,
3,621 direct captures) and Bass Easy (7,317 frames, 7,117 direct captures), with
zero deaths, movable 1-2 and byte-identical original inputs/trace. Fifteen Mike
PNGs, PPU frames 1,996–2,010, additionally match a separate raw-ARGB timing probe
pixel for pixel. Total direct coverage is 10,738 physical frames, from frame 200
through each endpoint minus one. Menus before frame 200 are outside this claim.

Root inspected those 15 Mike frames and five Bass frames, 3,029–3,033. Bass's
trace sample at 3,031 is positively identified as a temporary block-probe origin;
the direct body frames do not teleport. The adjacent brick is destroyed and the
score increases normally. This selected visual inspection is not a whole-route
human pixel review, and it does not certify all body poses or every item.

Mike still has real render catch-up: published scroll advances five pixels at
PPU 1,998, 2,003 and 2,009 after skipped publications. Logical camera bounds do
not remove this actual rendered stutter. The capture correction is not a game
lag fix; performance work remains required.

Evidence is external under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-direct-capture-ot/`.
`independent-review-v1/proof.json` binds the raw comparison, source receipts,
selected contact sheets and retained five-pixel scroll observations.

## Exact-hash roster ledger

`summarize_roster_ou.py` joins the unchanged native receipts: all 37 identities
have been attempted in both modes on OJ. There are 53 independently replayed
pairs with the original strict motion, visible-scroll, CHR and zero-death clear
checks; 21 pairs still have no clean independent replay. Positive guarded
observations resolve only the specific Bill, Rygar, Bass and Sophia temporary
probe samples. Raw traces and original rejection reports remain unchanged.

The ledger explicitly retains all negative attempts. A failed controller can
need better controls, a game fix, or both; it is not counted as a pass or
automatically classified as a game defect. Every-item delivery/use/SFX,
remaining source fidelity and music, gameplay lag, all required direct visual
review and the completed full-roster mapper releases remain unfinished.
