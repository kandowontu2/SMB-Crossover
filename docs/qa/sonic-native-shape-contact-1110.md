# Sonic native 16px shape/contact source qualification

PASS, in memory only, against public ROM SHA256 `c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`. No ROM, emulator run or build artifact was produced. Both `build/sonic-native-shape-contact-1110` and `build/sonic-shape-census-1110` are absent. The following new source files are frozen at the qualified hashes; subsequent work must use a derivative.

| Source | SHA256 |
|---|---|
| `tools/reference/sonic_sms_native_shape_contact_1110.py` | `ceea5507300f07bbe1da0339a109af90067ac1b37c8a0f92d6b2488c8ec9c602` |
| `tools/audit/check_sonic_native_shape_contact_1110.py` | `d1ceb668bbb5ab078edeed086646a8621067a5e52b80eb83aa6ac42e07de3f2f` |

The adapter assembles to 441 bytes, SHA256 `4d963e3ecb5198e268cf200822fc0bbcd98f2ad152c23b935664d93921472b4d`. Proposed test code is RAM3 `[B780,B939)`, with eight context bytes RAM2 `[C0B4,C0BC)`: Mode, Status, Kind, Axis, Negative, Edge, DX, DY. These are explicit test signatures, **not code or RAM grants**. The frozen 5,526-byte core remains SHA256 `e3606c66ae062243e669809a54edce4019586f2097858480a60da834b3c2657d`; the frozen 365-byte PointRead remains SHA256 `82ee77ec5d6923e2e28e7bec31c9fb8a9b55922ec72dd525b1be74e61749771d`. No instruction in either was changed.

## Geometry and return contract

For a leading integer probe P, let B be the donor clipping base `P & $FFE0`, and O the actual native cell origin `P & $FFF0`. Rightward/downward contact uses shape offset `O-B`, either 0 or 16. Leftward/upward contact uses `(O+16)-B`, either 16 or 32. Those inputs cause the **unchanged original** contact expression `(P & $FFE0) + signedOffset - edge` to land on the exact near/far native16px boundary, including carry across32px and256px seams.

The adapter uses original contact factor-table index0, whose magnet, horizontal-slide and vertical-slide entries are all zero. It is an explicit flat-host shape input to the contact API, not a claim that donor tileflag0 is solid. Original shape/animation tables and all original32px mode behavior remain intact. The native mode does not synthesize slopes, water or one-way behavior.

`SonicShapeHorizontal` and `SonicShapeVertical` read the genuine body dimensions24x32 or24x24 and canonical signed24-bit velocity, form the same leading-edge/midpoint probes as the source, call the qualified PointRead, and enter original contacts at A5E1/A5EA. Clipping changes the original integer coordinates while retaining both original fraction bytes, zeros all three bytes of the contacted velocity and leaves the orthogonal velocity unchanged for flat geometry. Horizontal contact clears/sets source flag40; downward ground contact clears/sets flag80. Ceiling contact clears ground flag80 and returns Kind4; no invented source ceiling flag is added. All other source flag bits survive.

- Mode0 tail-enters original HorizontalTerrain A7AE or VerticalTerrain A7B4, preserving the original returned AXYP/SP and all256 state bytes. Its carry remains the original source result; it is not the native availability contract.
- Mode1 returns C1/A0 when the native point and geometry are available, including valid empty geometry. Kind is0 empty,1 right wall,2 left wall,3 floor or4 ceiling.
- Native OOB, unsupported geometry or malformed input returns C0/A=Status/Kind0 **before changing any original actor or core scratch byte below C0B4**. It must not be interpreted as an empty traversable floor. PointRead reasons1..6 are retained;7 means unsupported metatile,8 unsupported mode,9 noncanonical velocity,10 coordinate overflow and11 unsupported body.

## Actual native metatile policy

The classifier preserves exact PointRead metatile/attribute outputs. It does not assume the SOLID bit alone establishes physical geometry. Current fixed native predicates and the real struck-block producer are bound by exact ROM bytes in the checker:

- C2/C3 coins are dispatched by CheckForCoinMTiles before native clipping. They and transient blank23 use pass-through background geometry. Coin award/removal and the separately represented animated block actor remain future native transactions; none is performed here.
- Climb/flagpole/vine cells24/25/26/6D, hidden blocks5F/60 and springs67/68 return unsupported. Their native actions and conditional geometry are not replaced with generic walls.
- Sideways pipe tops1C/6B return unsupported horizontally, matching the native side consumer's explicit exceptions. Their vertical full-cell geometry remains available; pipe entry is not implemented by this adapter.
- Other cells use the exact native attribute's solid bit for flat16px geometry. Native effect transactions, slopes, water, moving supports and actor carrying remain outside this source component.

## Qualification

The complete stdout run passed 630,946 actual6502 invocations, counting candidate calls, original-contact references and negative controls:

| Check | Cases |
|---|---:|
| Original32px mode differential pairs | 262,144 |
| Native16px full geometry/fraction cases | 49,152 |
| All256 metatile classifications across axes/directions/body sizes/cell phases | 4,096 |
| Zero, subpixel and original cap-velocity contact leaves | 22 |
| Naive SOLID-bit classification negative controls for23/C2/C3 | 24 |
| Explicit OOB/parser/velocity/body/mode/overflow failure leaves | 62 |
| Sequential X-then-recomputed-Y corner cases | 32 |

Original mode exhausts all64 masked source classes, all256 flag-byte values, all32 orthogonal shape ordinates and all32 contact phases in both axes/directions. Full original state, returned AXYP/SP and four private SMC operands match. The test selector adds exactly10 cycles; minimumSP is218. Original motor, cap, animation, integration and contact byte ranges remain identical.

Native geometry covers both body heights, both cell phases in the donor32px base, all16 within-cell axis/orthogonal positions, fraction bytes0/1/127/255 and world pages0/1/255. Original-contact CPU references and independent world-cell boundary arithmetic agree. Each of the four contact kinds occurs12,288 times. The metatile matrix yields3,952 available and144 explicit unsupported cases. Valid full-solid native calls cost1,165..1,200 cycles, minimumSP220. No host ZP, mapper, SMC, native buffer, header or shared mailbox write is introduced; only original private state, proposed context/PointRead scratch and return stack can change. The retired C800..D7FF/D800 fixture regions are never read by these entries.

All32 corner cases retain horizontal clipping before forming the vertical point from the resulting X position. Swapping the two calls fails every corner control, covering left/right walls with floors/ceilings, both heights, both world-buffer pages and zero/nonzero fractions. These are contact passes on a post-integration state, not a new OrdinaryFrame hook.

The context census covers634 actual state-operand sites and99 distinct bytes; the highest is C0B3. Its ten indexed sites are C071/C072,Y with Y limited to0/3, or C020..C022,X with X limited to0/40. Literal contact control flow and executed cases verify those index domains. Valid source indirect read-pointer producers address carrier shape/animation tables or the retired fixture map, not the proposed tail context. This establishes source disjointness only; it does not grant a native lifetime.

Reproduction, writing zero files:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/sonic-native-shape-contact-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_sonic_native_shape_contact_1110.py --output build/sonic-native-shape-contact-1110
```

## Budget and next seam

Core + PointRead + adapter contain6,332 bytes. The test layout has125 alignment-gap bytes and ends at B939, leaving711 loaded bytes before the current seven-row boot limitBC00; contiguous packing would leave836. Neither capacity figure is an allocation. Boot D25E, cold headers and shared DFD0..DFD2 mailbox remain untouched.

Future integration seams remain B4D2/B4D5 for query/horizontal terrain and B4EF/B4F2 for the recomputed query/vertical terrain. They are **not patched**. A frame bridge must handle unavailable geometry explicitly and distinguish geometry from native earned effects. It must retain original ordering, motor, caps and source fractions; this task adds no constructor, renderer, clock or public admission.

These entries retain the donor's single endpoint probe per axis. They do not perform a swept old-to-new search: an original hard-cap velocity of16 plus a fraction can cause a17-integer-pixel displacement and skip an isolated16px cell. A future frame bridge needs an old-position witness and earliest-crossed-boundary handling, or must explicitly reject that larger-step case. The cap-velocity leaves here verify contact reaction on a supplied post-integration point, not continuous movement through the intervening world. Ordinary normal/shoes X limits3/6 and terminalY8 are smaller, but no full native-frame or route claim follows from this component.
