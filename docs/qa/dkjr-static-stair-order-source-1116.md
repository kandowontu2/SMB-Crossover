# DK Jr static stair order: read-only source contract

This establishes the existing current code's order and geometry. It does not
replay the natural stair prefix, identify a new game defect, add controls or
authorize a repair. Root owns the per-query camera/terrain witness. CPU image
is source-only a3fb
`a3fb2dd448961ca1f7b7abc1c82175f3177da62207271c18ad87819d0dddda1a`;
its strict383-byte composition preserves every other current91dc byte.

`tools/audit/inspect_dkjr_static_order_1116.py` authenticates the original
source fragments against the actual payload and exercises only existing public
callbacks after compiled cold, with declared component inputs. Final receipt:
`25420cb525af3bb8afacc4d5556e8a18e4c421487774efbc8030a4879bbb5f0c`.

## Original ground support comes before X advance

Current Move at A2E8 calls Bounds before selecting ground/vine/jump/fall.
Ground at A311 queries vine and then support at A318. A support miss writes
phase4 at A321 and returns; it never enters GroundMove A443 for that update.
A support hit first calls original DA14, then GroundMove, whose right/left
origin calculation precedes the original pose publisher E9EE. Thus holding
Right cannot close a one-pixel horizontal support gap during the ground update
that already rejected support.

These whole fragments reassemble byte-exact:

| Current fragment | Bytes | SHA256 |
|---|---:|---|
| Move A2E8..A311 |41|`0b15ec3286089bc949e8f6b26b496ba242f515cd8d8370c80c35ed331e0e7d99`|
| Ground A311..A330 |31|`f26ad4ec6e0e9a3e72b994294cdda8b0fc060e89ec4686eddbb600404daea863`|
| GroundMove A443..A484 |65|`134c826b0678049a8b54e841736d70970068bb3910fc2f1960b2292daa496fb4`|
| Right/left stride A484..A4C8 |68|`df7d6c5303c5ee5bc4b78e5f12189980729b3b4f54767270413c349c0e4ab576`|

The authenticated jumping shape at B015 is `[9,0,25,15]`; ground at B005 is
`[7,0,24,15]`. With sourceX72, jump left/right is81/97 and ground79/96.
In native world coordinates those are respectively anchor+1..+17 and−1..+16.
The jump-to-ground change therefore retracts the right support edge by1 pixel
without requiring an X writer. This exactly permits the shape-only numerical
explanation of root's earlier47-event trace, but does not substitute for its
missing per-query camera and rebuilt terrain list.

## Actual current native callback order

The current native PlayerCtrl has resident fusions beyond the retained
`src/player.s` text. Actual literal calls are:

1. Player bank A118 → PlayerMovementSubs A5D7.
2. A13C → VvScrollBridge ED65.
3. A142 → RelativePlayerPosition8A8C.
4. A147 → existing RdNativeBGGate B969, then JMP A16B after that gate.

The bytes between Relative and the fused gate are just `A2 00` (LDX0).
The actual gate prefix is `a9a78d6c01a9af8d6d01a9dd4c`, targeting the existing
DD:AFA7 service. Executing this existing public gate after one actual owning
HuMovement callback observes DK FullBox D6A7 followed by native BG9B5B, in that
order. This is a declared component continuation at the opening, not a natural
stair contact. It proves movement/source export precedes scroll, while the
source-derived native box and native terrain phase follow scroll.

An initial binding check incorrectly expected the retained source's direct
GetPlayerOffscreenBits and full-box/BG JSRs. It rejected because the current
caller uses an offscreen bridge and fused gate. The final proof authenticates
the actual current calls and executes that gate; no game code changed.

## Native raw40 side probe and clamp

Actual authenticated HuAdder returns Y2/Cset, selecting native profile index14:

| Field | head | left foot | right foot | left side1 | left side2 | right side1 | right side2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| X adder |8|3|12|2|2|13|13|
| Y adder |18|32|32|24|24|24|24|

Each declared side query at indices17..20 executes the actual native
BlockBufferColli_Side958B once. These four opening queries return the raw zero
tile from that native leaf. The
query components use the real opening block buffers, with no terrain writes;
they establish dispatch/offsets, not a contact with the late stair.

For raw40/engine8 the actual wall-call chain is StopPlayerMove9D20 →
SamusStopAtWall E801 → LmWallGate AD25 (physical93) → Z2WallLegacy AA8A →
CrossoverSourceWallDispatch A277 (physical10) → SamusStopAtWallBanked A290.
It returns Cset, so the ordinary one-pixel ImpedePlayerMove fallback is not
executed. For R0=1 its existing right clamp computes
`floor((worldX+14)/16)*16 - 15`, zeroes native X speed/scroll and legacy
MmXFraction (not the original DK source gravity fraction), and
sets SideCollisionTimer16. The native X store is physicalPRG10:A2DC/SP207;
the preceding12 bytes are `489829f0a40388d00b38e90f`.

Declared forced-contact inputs2130 and2143 both return2129. Inputs2127..2129
would return2113 if a contact were artificially supplied there; those are not
claims that the actual2144 tile is reached by the +13 probe at those inputs.
For a real right tile whose left edge is2144, the shared clamp's limit is2129,
not2127. Root's first one-pixel source support miss therefore cannot be assigned
to this generic native clamp solely because its terminal world X is2127.

No natural prefix, new controls, tile/actor/health seed, ROM/game-code write,
Mesen or output file was produced. The bounded absent root is
`build/dkjr-static-stair-order-contract-1116`, max-files1/600seconds; final
invocation is terminal and root remains absent. The first small descriptor
read a second mutable input only for an inverse assertion; final code reads
Downloads once and uses that immutable parent. Earlier b8cab/0f9d component
receipts are superseded by the final receipt above.
