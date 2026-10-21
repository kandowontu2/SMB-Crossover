# Samus and Scrooge collision/graphics corrections

V17 fixes the reported armored crouch in Samus's suitless form. The two
suitless poses come from Crossover2.02's Samus003 skin using its original
timeline/masks and foot origin. Hair/gun colors keep the existing suitless
form's palette roles. The extra body data uses previously blank logicalCHR$80;
the original death and Scrooge reservations stay in place. OAM remains at the
existing14-part maximum.

`samus-crouch-power-forms.lua` drives real Down/B input in explicit flat-ground
fixtures, then reconstructs actualDMA OAM and mappedCHR on both mappers. It
checks all three forms, both facings, crouch and crouched firing. The suitless
oracle is frozen directly from source skin cells by an independent crop script,
without using the production extractor/CHR packer. V16 fails specifically on
the suitless form; V17 passes both mappers.

The head displacement is reproducible at a ceiling edge: a center-only head
probe misses the tile while the later side probe pushes Samus seven pixels
sideways. Samus now checks center, left and right head points. Temporary probe
coordinates are restored before returning. The struck block uses the actual
probe's world column/page, including edge and page-crossing contacts; projectile
attacks keep their existing authored origins.

`samus-head-displacement.lua` covers432 explicit brick/question-block cases
across three forms, three directions, three ceiling heights, isolated/continuous
roofs and four horizontal/page-seam positions. Every arena must execute a real
head/block contact. It checks bounded per-frame motion and the actual struck
block origin. V15/V16 fail the isolated edge negative; V17 passes both mappers.
These are collision arenas, not controller-only level-clear evidence.

Scrooge's pinned DuckTales ROM gives a body centered at canonical(PlayerX+8,
PlayerY+20), with half-width10 and half-height12. V17 aligns the visible artwork
with that center and adds separate standing/crouch body boxes. The pogo uses
the source's narrower strict-horizontal contact, only while descending, rather
than the former16-pixel-radius bomb area. Terrain probes now use head8 and
vertical sides9/31; horizontal terrain remains the shared SMB two-point scheme.

V17 body/art,69 pogo edge cases,88 mirrored/page-seam corner recoveries and
the earlier Scrooge corner fixture pass both mappers. A new durable-target
fixture exposes one remaining contact-priority defect on collision parity1:
the narrower correct pogo damages/rebounds, then ordinary body contact can
injure Scrooge in that same update. V17 is therefore not a final accepted
checkpoint. A narrowly scoped same-target rebound acknowledgment is pending
V18; it must not grant a general injury/invincibility timer.

Evidence: `build/verification/samus-scrooge-v17-summary.json`,
`samus-head-v15-negative`, `samus-crouch-v16-negative`, and
`build/checkpoints/roster-audit-v17/manifest.json`. The full V17 suite is tracked
separately and may reveal further regressions. No final roster recording is
claimed here.
