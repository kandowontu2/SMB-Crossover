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
frame or native lag measurement. Expanded raised-foot, wide-pipe, off-row and
climb vectors are pending. Query scratch consumer closure, legal code fit,
ordinary controls, cold/IRQ and native proof remain required. No usable repair
or renewed first-try pipe success is claimed.

All source runs use bounded absent output roots and create zero build files.
No Mesen, image/capture, candidate, installation, backup, patch or release is
created here. Protected progress JSON and Steve QA are untouched.
