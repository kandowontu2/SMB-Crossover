# Prince WorldMaterial repair research, November 14

This is source research, not a fitted repair or a candidate. The ordinary
first-pipe failures and exact native receipts remain in
`prince-pipe-usability-current-1114.md`. The installed nightly is now common
CHR-reset `82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63`.
Research uses the explicit authenticated common-reset inverse to recover exact
421. Frozen 421 controller factories and their defaults are unchanged. No ROM
has been reconstructed or written by this research.

Root's research lease
`allocations/prince-worldmaterial-research-1114.json`, SHA256
`0731c7526f8f181b33855ce7d09d3992f1ec29bea30f2c677c0ea6453a9ec482`,
owns only decoded RAM3 BDE2..BFA3, 449 bytes. Independently reconstructed
preimage SHA256 is
`c4377287449f719ccbc64a2721c9b6039c784566173114080881deced7ef088d`.
Public entries BDE2/BDE5 are the only genuine outside literal references;
nine other word candidates are decoded opcode/operand overlaps. Nearby
relative branches, immutable renderer data and the cold boundary are closed.
The original scripts B400..BAE5 remain exact and all 15 indirect command
targets lie outside this function. The pinned inspector is unchanged.

## Retained rejections

The 63-byte wall-only and 69-byte coupled filters remain rejected as described
in the usability QA. The later ungated 93-byte roof filter also remains
rejected. Its initial 1024 primitive vectors passed, but the expanded 4096
vectors expose four genuine wide-platform losses: a player at native X256
has real support on the wide pipe at Y160, while the sampled donor column
is beyond its physical body. The filter incorrectly changes floor1 to empty0.
Expanded receipt SHA256:
`4383b6bc1c90432860484acf59da50558c06117dffd8e3d39f1ad2ef74012ed7`.
The other 24 expanded changes remove unsupported higher floors and are not
the four losses. Do not treat a material0 baseline Surface as a floor.

The passive original four-pipe source route completes 1724 Main updates,
terminal962/176/HP4/lives2. Its Lua SHA256 is
`f512feaa697ed89c7eb3ce229337144d233c877fa31b9cde48c611e125bfb242`.
It identifies 31 distinct legitimate hang/climb contexts that the ungated
filter would reject. Examples include first-pipe action24/mode2/foot203 and
action10/mode1/feet202 or195, and third-pipe action10 poses135..139. These are
real original controls, not seeded abilities. Actual CPU point-reader and
WorldTile observations map PRG126 at8000, RAM3 atA000, RAM2 atC000 and PRG127
atE000. That is source scheduling evidence, not a hardware IRQ/DMC closure.

## Concrete design and current fit deficit

`tools/reference/prince_worldmaterial_research_1114.s` retains the original
floor scan and TopLoop. Normal current-row wall samples are accepted only
when their native 16px cell intersects the current source-derived physical
body, sourceX−8 through sourceX+7. The full two-byte distance handles page
crossings; stale native exports and variable sprite widths are not inputs.

After TopLoop finds the actual candidate top, the original exposed near-foot
floor is retained. A higher top must have real native support at sourceX−6
or sourceX+5 (native floor feet +2/+13) at that top. This retains the wide-pipe
case while refusing the distant pipe's false Y160 floor. Off-current-row
queries, hanging modes2/6, action10 climbing and action24 hanging are exempt.
No gravity, walking speed, jump, input mapping, room geometry or automatic
climb behavior is changed.

The first equivalent internal compaction reduces the baseline449→381 bytes.
The complete correction currently assembles to **551 bytes, 102 over the
lease**, so it cannot be mounted. Source SHA256:
`db97d57afd6cf2bd9abd16e364764e6df3edf16b5714fa4df918cd5690b7d3b2`;
proposed BDE2 assembly SHA256:
`a46c789ad81a736b16c77bc5cf404b2a8344387d99fb403386161e80439cf3e8`.
It has35 checked short and4 long branches. Its hypothetical end C009 would
overwrite protected constructor/cookie/state bytes and is explicitly refused.

| Region | Offset | Bytes |
|---|---:|---:|
| Entry/initial decisions |0|51|
| Falling sweep |51|67|
| Above-row adjustment |118|14|
| Context gate/minimum initialization |132|42|
| Wall read/refinement |174|35|
| Scan initialization |209|12|
| Scan/read |221|45|
| Original top walk |266|30|
| Higher-top support validation |296|81|
| Minimum/found handling |377|17|
| Advance scan |394|22|
| Next column |416|25|
| Material choice |441|37|
| Output and caller restore |478|32|
| Full-width body-cell predicate |510|41|

Root separately approved an isolated **flat primitive CPU** relocation at
virtual6000 solely to test this oversize design. It is not a physical RAM
grant. The old449 instruction bytes are poisoned in that separate fixture;
the new routine makes zero reads from them. No new code is mounted in NesBus,
the decoded packet or ordinary gameplay. The original PointRead/Prepare/Hand
instructions execute against a fixed mapped-memory snapshot with no I/O.

The first1024 vectors pass against an explicit CPU semantic reference, using
both public entries and C/V input combinations. The512 flat-floor/pit/empty
preservation vectors have zero mismatches. The correction makes112 intended
far-wall material changes and rejects92 unsupported raised-column floors.
Return X/Y/SP/P (apart from final material N/Z), material, Surface/SurfaceRow
and translated Cell match the reference. Virtual assembly SHA256:
`d25727ef93ad6b201b68ccb00c6e96a79e5ecc77f31b81e72393b339184cc583`.
Receipt SHA256:
`c3b55f4e565a9776d72bb63c8cf3be38833bfdd85cdf455a0434187fa85abe50`.

PointRead calls are6616→7112 over1024 vectors. Whole-WorldTile added CPU
cycles are min3/max349/total92834 (about90.7 per vector); this is not a Main
frame or native lag measurement. The expanded551-byte design subsequently
passes7168 vectors, including6144 preservation vectors, with no mismatches or
former-address reads. Receipt:
`703420c8a8592a1cf8df958797bf447030846ccd690109192d9c96e91b9ecfd7`.

## Fitted two-span source proposal

Equivalent compaction reduces the complete standalone routine to474 bytes,
still25 over the lease. X/Y hold the scan until a surface is found; PointRead
preserves both. BestTop's sentinel replaces a floor counter, the original
two-column sample's invariant bit4 replaces its counter, and the existing CPU
stack preserves callerX/Y. Carry-sensitive instructions use explicitly proven
incoming carry. The standalone474 code is
`db1fb9fb425c6e182f55b11b87ea6644acd94930fa5554fe1e7ff73144eff67d`,
source
`bfdcbcf6f5a28c8fc138d55bc04c2b3726f1b269cdad5951d61d4f4e60c00c6b`.
Its7168-vector flat proof again has zero mismatches; receipt:
`e81132910a4882ddd2c817d9fac0f0fdc02dd4f5f666b8e105ffedd973063eab`.

Root then authorized research into equivalent compaction of other existing
Prince code, without granting placement. The following **fitted layout is
still flat research only**, pending root's exact two-span placement review:

| Envelope | Original | Proposed | SHA256 of proposed complete envelope |
|---|---:|---:|---|
| RAM3 BDE2..BFA3, decoded stream0[7650:8099] |449|446 code+3EA|`18d18cfe53f4942e7658152177634736a984046233c55f0be2846de0538bb3f9`|
| RAM2 C552..C606, decoded stream2[1186:1366] |180|151 Prepare+29 FirstFoot|`7b3ddaec5eb963001a7d8143b8fd2f2fb53c914db2641165031e879fa54150f3`|

The third decoded stream stages atC100 and cold-copies **80 decimal bytes**
lower to liveC0B0. The second envelope's staging range isC5A2..C656, ending
nine bytes before the unchanged cold prefixC65F. This is code compaction,
not a claim that a zero-filled source-state gap is free.

The original180-byte Prepare atC552..C606 rebuilds exactly from the retained
v8 source, preimage SHA256
`e5e6159d7d7bf7c18b28afa243e549664528a3cd1e338f3ba91348a1d860c29d`.
It already calculates QueryFoot=sourceY+Origin+signedDelta+roomOffset.
Its repeated Baseline arithmetic is identically QueryFoot+signed(3−Delta).
The actual current signed7 decoder atBD4F executes all256 possible input
bytes and yields the complete domain−64..63, so3−Delta fits signed8.
Cold zero0, constructor3 and that decoder are the Delta writers; inherited
original-source direct/indexed/finite-indirect exclusion protects the owned
geometry fields. A register-based row shift saves further bytes. Prepare
still returns X0 and the same Y/A/P, with the unchanged final QueryX arithmetic
setting its flags; it allocates no temporary field.

The151-byte Prepare hash is
`9a8c12848c727cc0941f642ca7d847284552a1f53ebef8245220d5809ad98867`.
The outlined first-foot setup is29 bytes atC5E9..C606, hash
`cd967b922edcbd3114af1612296a2f368933f9719be0ecf5e542d781e79d5407`.
It preserves original queryX inX/Y, sets the actual left foot and candidate
top, then returns to the unchanged actual PointRead call. The446-byte World
code hash is
`faf4361953c415b29013dce2d0e51160f9632d89d389a63be7129ffbfad98754`.

Combined flat proof passes1024 Prepare ABI/geometry pairs over all128 signed
Delta values, source index/row, projection wrap, signed room and world-page
vectors. It compares every fieldC078..C0A6, QueryX/Y and A/X/Y/P/SP. It also
passes the7168 World vectors/6144 preservation cases, using both entries and
C/V/D/I input combinations on a decimal-disabled NES CPU. Former World code
reads remain0, and all164 intended material/result changes remain unchanged.
Receipt:
`684b5516f863e353046407c2d927ce9424f0bd9f48db27cde47c7d4a73b77702`.
Whole-call added cycles are min−359/max177/total−1078644 over7168 vectors;
Prepare alone saves57..63 cycles per tested call. These are primitive CPU
costs, not an idle or physical frame-rate claim. The earlier receipt's top-level
474/false fields describe the standalone routine; the fitted446/two-envelope
fields describe the tested layout. The current checker labels them separately.

Prepare's outside-word candidates are classified: only the original JSR to
C552 is an executable entry. A318/A5E8 are opcode/operand overlaps in
STA C6C5; D9C3 is BEQ D98A, not a C5F0 pointer. Cold operands copy staged
code/data and are not execution transfers. MetadataC800..C9DE contains239
immutable format-tag/relative-offset words whose actual data startsC9DE;
remaining apparent pointers throughD46E are immutable packed pose data.
Their existing bounded metadata consumers and data are unchanged. Cell
C4FF..C552 rebuilds exactly, endsRTS and branches only within itself. The
upper staging cold prefix is unchanged and has no edge into the changed
staging span. The following liveC606..C800 region is source state/data outside
the granted executable slot and remains untouched.

The retired private Floor/ScanY/Top-high/BestTop-high/SavedX/SavedY/counter
fields have no outside literal data operands. Seven outside C08D-looking
words are decoded opcode/operand overlaps in STA C4C0 or STA C6C0. The
inherited complete original indexed/indirect field exclusion and unchanged
bounded native consumers remain applicable. No caller-visible field used
outside the function is retired; Prepare's entire geometry field comparison
also remains exact.

`prince_prepare_funding_research_1114.plan(raw)` returns the exact source,
assembled two-span bytes, hashes and caller census in memory. Independent
primitive verification command (root owns any later overlays/native work):

```text
python -B tools/audit/run_bounded_build_v1.py --output build/prince-worldmaterial-root-flat-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_worldmaterial_research_1114.py --expanded --fitted
```

Placement review, ordinary controls, actual cold/IRQ and native proof remain
required. No usable repair or renewed first-try pipe success is claimed.

All source runs use bounded absent output roots and create zero build files.
No Mesen, image/capture, candidate, installation, backup, patch or release is
created here. Protected progress JSON and Steve QA are untouched.
