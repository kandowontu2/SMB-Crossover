# CF P1 work marker — design for review, not implemented

This is a read-only design against exact current bc5, not a byte proposal,
allocation, source mount or cadence result. The earlier06a4 router/P1 arrays
and separate shared-tail1e2a array remain frozen. Root requested checking
whether the existing C2DF work/phase byte can avoid the full empty P1 pass.

## Current meaning and required new invariant

The actual byte is `CfShotPaletteOwned` / `CfP1Tag`, physical RAM2:C2DF.
It is currently **per-part scratch**, not a persistent dirty flag:

- Body writes0 before rendering.
- An accepted shot writes0 or8 according to its yellow-loan metadata.
- Part publication ORs the whole byte directly into OAM attributes.
- EarlyTag ORs80 after native-attribute snapshots/tagging.
- The guarded public BE53 entry tests bit80 and then clears the entire byte.
- Constructor bulk-zero and explicit same-player area reset also clear it.

Therefore simply setting a spare bit is unsafe: bit40 would become OAM
horizontal flip, and later Body/Shot writes would erase pending work. Actual
empty-Main48307 observes three writes: RAM3:B402→0, BE4B→80, BE60→0. It also
authenticates the fixed native `Bitmasks` table at PRG126:8C7B/file1035403,
bytes`0102040810204080` (no changing bank needed). Receipt
`398d68b8c3a9dc3913989bb5349f17c63294380f49d4a517bf1dfe45fa8d67dc`.

Proposed interpretation, requiring root review and complete producer closure:
bit80 remains the existing late-phase token, bit08 the current part loan tag,
and bit40 means **a full cleanup may be needed**. It is conservative, not
"there are no actors": any accepted shot, any native tag producer, and cold/
area acquisition sets40. Every intermediate writer preserves it. Only the
consuming late pass clears it. A frame without draw creates no new marker;
pending marker state carries across skipped or incomplete draws.

Work=false may take a fast late path only after proving that all64 OAM tag
bits18 are already zero. It must still restore24 original native attributes,
set Visible/Choice0, preserve the alternation Turn, and run the ordinary full
native palette packet. This correctly reverts a prior shot-colored packet;
it does not skip palette publication or integrity checks.

## Candidate in-place funding, not yet assembled or proved

All locations below are existing CF-owned blocks in the actual retained DBG.
They are potential envelopes, not grants or padding claims.

| Existing block | RAM3 CPU range | Bytes | Proposed funding |
| --- | --- | ---: | --- |
| Host renderer | B34C..B5E7 | 668 | 636 code +32 retained table bytes; loop/CLC rewrite saves10B, body/attribute changes need7B |
| Native EarlyTag | BDFE..BE52 | 85 | Mask classifier saves4B, existing fixed mask table removes local4B; native dirty OR needs8B |
| Late entry/scan/paint | BE53..BEFE | 172 | Shared saved P/A, moved initialization and a smaller scan classifier fund a flag fast path |
| Acquire | BF44..BF54 | 17 | Conditional redundancy below could fund dirty initialization; consumer proof is essential |
| Area reset | A898..A8DB | 68 | A contiguous zero run saves3B; moving clear to final dirty initialization needs2B net |

No body atlas, CHR growth, global field or new RAM byte is proposed. Updating
the payload would require the normal two complete-cookie digest views. Exact
old/new bytes, hashes and changed counts do **not yet exist** for this design.

### Renderer

1. Body keeps40 while clearing phase/loan; its RenderSlot remains0. This needs
five additional bytes.
2. Accepted shot's existing `LDA #0/#8` immediates become40/48, so any active
shot conservatively marks work even if all parts clip or use another palette.
These immediates need no additional bytes. Invalid/inactive exits leave the
pending marker unchanged.
3. Part publication becomes `(flag & 08) OR record_attribute`; the two added
bytes prevent the work bit from flipping sprites.
4. `CfHostRenderShot` **already stores its input X into CfRenderSlot before
any validity test**. RenderAll can walk the same wrapped12 actor indices,
recover X from that existing field after each call, and stop when X reaches
the original start index held in CfRenderTurn. Restore X0 at completion.
This saves eight loop bytes plus one from LDX12→TAX. The modulo exit already
has C0 from its BCC, making the following CLC redundant (one more byte).

The exact12-slot order and final Turn/Slot/X/AXYP must be compared. Intermediate
Turn updates disappear, and incoming A/C of the internal shot call can differ;
its entry STX/CPX/loads must prove those values dead before use. This is not an
assumed public ABI change. No whole renderer replacement should be mounted
without those proofs. The32-byte source-window table remains at B5C8.

### Native tag producer

The actual25-byte native-mask reader at BE14 can implement the same0/2/tail
mapping in21 bytes: TYA/BEQ handles zero; the saved-P restore followed by
ORA0 has the same A/N/Z as reloading the just-stored mask. All C/V/I/D and
the temporary mask stay exact. This must pass all Y/status primitive cases.
The local4-byte Bits table has one indexed reader; use the existing fixed
native Bitmasks[0..3] instead. These eight bytes fund OR40 at the point where
native SprObject attributes actually receive marker10. Offscreen or unused
native objects may over-mark work, which is safe and simply slower.

Every other selected31 OAM-tag producer, including direct native publishers,
must be classified; an untracked writer invalidates this design. References
from foreign private renderers need their real owner exclusions. No blanket
"all native attributes are zero" claim is permitted.

### Late entry

On a real phase token, compare the loaded flag toC0 before clearing it,
retaining dirty in carry. Save original caller P/A exactly once; initialize
Visible and Choice while A0 already clears the token, then restore the24
attributes. The restore loop does not consume carry. The leaf may use that
carry to choose full scanning or the fast native packet path.

The full scan no longer needs its two existing LDA0/STA initializations.
Its8/16 classification can share three right shifts, saving three bytes;
the later choice comparison and complete paint still establish all consumed
flags. Fastpath loads the actual last cleared OAM attribute and sets X0,
giving the original gate A/C/N/Z; a guaranteed BEQ can reach the unchanged
final JMP gate within one page. The tentative arithmetic fits172 bytes.
All public AXYP/SP, gate inputs, full/hidden tagged scenes, token rejection,
packet validity-last publication and all new reached ISR cuts remain required.

### Acquisition and area/life transitions

Constructor bulk-zero already sets Choice0 before its sole actual Acquire
call. Acquire must preserve the **early Pending0 publication**. Dropping its
redundant Choice store and its early LastBlue0 store could fund LDA40/STAflag,
with one byte left. This is permissible only if all actual readers prove
LastBlue unread until the unchanged packet commit while Pending0 and Main is
busy. Source IRQ/NMI/audio, alternate owners and direct Acquire ingress must
be examined; do not assume the LastBlue change harmless.

AreaReset can replace the four contiguous LastVY/NativeX/Page/Y zero stores
with a short X3 indexed loop plus INX back to0. Removing the early flag0 store
and setting40 immediately before HostImport costs two bytes net, funded by
that three-byte saving. This changes zero-store order and delays phase
clearing; actual foreground/ISR consumers must prove no use before reset
converges. HostImport/public reset AXYP must remain exact. Every same-pose,
pipe, death/life/player reconstruction and owner entry must mark conservatively.
Retired/inactive cache contents may remain stale only when no consumer can use
them, and every subsequent acquisition must republish work.

## Required next scope

Bind all actual compiled flag aliases/producers, the two introduced lifecycle
write changes, and the exact Pending/LastBlue readers. Preserve each old
negative. Only after that contract/funding review should a separately named
detached array descriptor be generated. A source overlay and candidate would
still require a new explicit root lease, actual mounted ABI/ISR/art/lifecycle/
all-four-class source checks, then root-only native timing and route testing.
The current source estimate does not establish any physical cadence gain.
