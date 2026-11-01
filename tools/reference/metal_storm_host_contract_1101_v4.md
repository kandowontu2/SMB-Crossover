# Metal Storm: native host contract, November 1

This is a concrete source component, not a playable admission. It reuses the
frozen original-component-v3 packet and does not edit the current shared build.
The output is `build/metal-storm-host-contract-1101-v4`.

The original6,323-byte actor now assembles at A3:A000 with C2:C000 source state
and foregroundR0/R1=$03/$04. The unchanged actor,113-byte service header and
323-byte adapters occupy6,759 bytes, leaving1,401 bytes before the BFE0 cookie.
The separate45-byte cold menu fragments have no native ROM lease yet.

`MsHostStep` preserves AXYP except carry and runs the original actor once per
accepted native FrameCounter. Duplicate epochs and pause return zero movement
deltas without replaying the source. It never writes generic Mega Man velocity
or jump variables. Source fractions, gravity, animation and jump clock remain
in the original actor. `MsHostReadDelta` provides exact world displacement for
a future native bridge; it does not apply native terrain/camera effects.

Two source-wrapper details are now explicit. Original controller polling follows
the actor, so current NES input is queued into source31 **after** the step and
has the original one-update latency. Original DCAE/FF27 owns INC53; do not add
another frame tick. The donor's frame600 area bound is **07E4=2020**, not merely
its low byte228. `MsHostSetBounds` takes the real host area's16-bit extent.
Source Y uses signed240-pixel pages; all65,536 input pairs are checked against
the exact linear conversion. A native constructor must establish a consistent
body origin and source support state rather than repeatedly overwriting its
coordinates/fractions after each update.

The CPU receipt compares480 legal donor frames against both the rebased actor
and the typed host step, with external API effects recorded/replayed at explicit
ports. Both gravity directions agree, arbitrary incoming foreground pointers
are restored, and NMI scratch00..02 stays untouched. This is not an ISR proof:
native NMI/IRQ, SMC/bank restoration and the real12-byte Main stack reserve still
require qualification in the composed candidate.

The original208 body contexts compress to33 base packets,64 frame-map entries
and exact facing/gravity order tables in1,002 bytes. The decoder reproduces
original cell order, attributes and all144 original8x16 patterns. Reflection
axes are X=24-dx and Y=18-dy. Each pose uses at most two of the five body pages;
a native renderer can map them to P0 windows0/1 and retain world windows4..7.
Native DrawMetasprite reverses packet records, so the supplied order tables are
already reversed appropriately. Source palette0/1 both need explicit native
palette ownership; this component does not recolor shared enemy palettes or
claim a working PPU/OAM renderer. The512-byte body tail may hold original shots
if their actual recovered graphics fit; that has not been established.

Slot11/FmAlts&2 remains pending. Raw11 is Sophia and must retain its vehicle,
portrait and inventory behavior. The proposed new runtime owner is **35**.
The cold fragments demonstrate the exact remap and bit retention. Before any
readiness change, root must add a complete typed service route for35, extend
the genuine high-ID gate only after that route exists, and provide ROM-only
name/colors/portrait callbacks before cache loading. A rejecting RAM row is not
permission to fall through to an old twelve-owner table with raw35.

The conditional C2/A3 banks can be shared exclusively with other selected-owner
caches only through two complete identity/revision signatures and cold verified
copy/readback. `MsHostReady=A7` is an internal state marker, not authentication.
Source pointer savesC7FE/C7FF must remain reserved from any recovered audio API.
New game/life/scene/player transitions need the actual source constructor and
documented persistence; no donor RAM snapshot is supplied as a fake constructor.

`host-contract.json` records an **ungranted**14-page storage candidate: kernel
247..250 and827..830, metadata831, body1019..1023. It checks their emitted-owner
history and current zero preimages, but source/runtime-selector closure remains
required before changing them. In particular, prove Bowser only selects824..826
and SMB3PLUS only969..1018, and audit original low-CHR consumers247..250. The
kernel loader would need a scatter descriptor. No space in Karnov's now-busy
ROM29 lease is assumed free. Factor an authenticated loader with per-owner
descriptors or perform a new source-backed compaction; do not overlap its lease.

The next real grafts are the original constructor; FF1E tile-flag translation;
FF33/FF36 gravity-aware contacts; original FF27 clock/slot2/3 projectile leaves;
camera/platform/scene adapters; original projectile art; native palette/OAM;
health/death/armor/Gravity Fire/earned upgrades; audio; and total cold/runtime
dispatch. The ten source callbacks are declared CPU boundaries, not fabricated
native implementations. Complete native cold Select/Start, interrupts, scene
transitions and1-1/powerup checks before enabling this owner in a nightly.
