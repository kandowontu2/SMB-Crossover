# Sonic public service admission, November 10

The source CPU overlay admits exactly raw37..43 to the current public/common
service and native-scene bounds. Raw43 selects the authenticated, aligned D100
Sonic service table. Both complete 16-byte headers remain mandatory. Corrupt
headers return nonblocking native head/side/feet results without executing
private code. Existing raw37..42 behavior, including Getsu42's fail policy,
remains exact in the paired checks below.

This report qualifies source CPU behavior. It does not claim a Mesen run,
installed nightly update, complete original Sonic animation/audio, all powers,
or the whole roster goal. No ROM, build file, capture, PNG, or backup was written.
No native helper platform or placement changes are part of this component.

## Frozen API and bindings

`tools/audit/check_sonic_public_admission_1110.py` provides:

- `proposal(raw) -> (image, record)`: checks actual shared preimages and applies
  only this component to an explicitly composed parent.
- `combined() -> (image, common_program, p, record)`: frozen rehearsal of the
  aligned Sonic packet, shared audio, shared feet, and this public component.

The rehearsal uses the source owner's a5 parent. Root owns the explicit 6d83
nightly rebase and frontend composition. `combined()` does not silently read
the changing Downloads ROM or repin its parent.

| Binding | SHA-256 |
| --- | --- |
| Aligned runtime before shared overlays | 44cf95d842bf52937705740e1e39a9c882e9c98d9d9da304225887ea4e1a7642 |
| Aligned + frozen audio + frozen feet, public overlay input | 072184b0f6d99a8ddddb03efcec9ed4b7d449937e45371e556da66574302b75e |
| Public overlay rehearsal image, in RAM only | 7de72fb7d315cd78288790e84ff0ff988e9f62906470edeb43a8ccf3104bf2ef |
| reference/sonic_public_admission_1110.s | 90f4fb8d341aaae8af0b9d0252271dea4a40e7b8d33558b92f87fc6bc72da607 |
| audit/check_sonic_public_admission_1110.py | b6c5c9499081a7290de7e442d6b480895e31b8fdd0a7628025a07edca7ae3257 |

The source owner's later scene-duty derivative requires fresh composition and
getter/lifetime checks; its new private image/cookie are not covered by this
7de72 receipt. The shared source API can be reused against matching preimages.

## Source funding and native ABI

| Region | Change |
| --- | --- |
| PRG65 A743..<A7C5, 130B | Exact37..43 public range and raw43 D1 selection; fixed cookie boundary preserved |
| PRG65 A800..<A817, 23B | C-only private Sh authentication and reject high-byte setup |
| PRG65 AB4F..<AB58, 9B | ROM reject helper dispatch; existing common restoration remains at AB58 |
| PRG65 B01C, 1B | Native scene upper bound6 to7 |
| PRG9 BC54..<BCAA, 86B lease | 35B ROM reject helper; remainder explicit NOPs |

The selector uses carry from comparing SelectedCharacter to38 to distinguish
Mini37, shares high-byte publication tails, and preserves the special Prince
and Mini routes. Four explicitly owned selector NOPs before the unchanged
DK cookie provide part of its funding. The selected36 test formerly repeated
in the Sh selector is retained in the full Sh authentication helper instead.

The private Sh auth wrapper's redundant AXYP save frame is retired. Its four
actual callers are A7A7, A8DD, ABDB, and AC8D: the common saved frame, native
Sh loader, Sh CHR publisher, and native Sh injury caller. All own their outer
AXYP frames. The loader and CHR paths overwrite temporary auth results; the
injury/death source initializers define their own actor registers. This helper
now explicitly has a C-only contract; it is not claimed to preserve AXYP as a
standalone external API. Every actual importing caller is paired below.
No standard published FarCall targets A800, and no fixed-bank direct call or
jump targets it. Both complete-header checks remain unchanged.

PRG9's disabled demo entry/data is an existing source-closed retirement from
`check_sonic_resident_funding_1110.retired_demo`: the compiled crossover menu
has no attract/demo path. The source checks its only former farcall and exact
86-byte preimage. Sonic's separate fixed demo-cookie lease stays untouched.
The live victory function begins after BCAA and remains unchanged.

The reject helper is ROM code, so it can run with either private header bad.
It uses a standard nested native FarCall. Five bytes below the saved common
frame account for the caller's JSR, saved bank, and native target JSR. The
helper clears C in saved P for every owner. Only raw43 receives saved A/X zero;
only its actual saved F5 foot target increments saved Y. The normal common
restoration then returns A0/X0, correct Y, C0 and native N/Z derived from A0.
Existing owners retain their original saved A/X/Y and fail policy. There is
no cached authentication, shortened fingerprint, or private-code fallback.

## Qualification on the frozen rehearsal image

The final `--section all` run passes all of the following in one bounded,
stdout-only invocation:

| Scope | Evidence |
| --- | --- |
| Sonic public getters | 66 head/side/feet cases match the frozen private handlers in registers, native outputs, private state and mappings |
| Header faults | 1,024 cases cover both16-byte headers, every bit, head/side and both foot inputs; no private entry or body/private mutation |
| Saved status flags | 1,024 additional cases cover all256 saved P values and four native getter inputs; correct A/X/Y/C/N/Z and preserved V/I/D |
| Full native callers | Actual fixed head, shared side, and fixed foot dispatchers pass; both damaged-header cases per dispatcher stay nonblocking |
| Native head effect | Real source ceiling cache through the fixed head getter into native PlayerHeadCollision; private actor and native Y remain correct |
| Prior six owners | Six cold pairs, 444 pairs across all37 actual published JMP veneers, and768 full-header reject pairs; Getsu42 fail result exact |
| Shinobi callers | Genuine menu/cold/60 updates; 16 loader,16 CHR and16 injury pairs across flags and C mappings; original-health-zero directed death;64 header rejects |
| Shinobi interrupts | Three actual importing-frame cuts, NMI and IRQ paired to original ISR, exact resumed state:12 paired ISR executions |
| Lifetime | Warm reuse0 PPU reads; either-header native-scene reload then original public frame; each reload18,386 PPU reads |
| Bounds/context | All256 selections at both public/scene bounds:512 decisions; six original cold-context negatives; public pause/resume |
| Public interrupts | 199 reached instruction cuts across healthy and invalid-header paths, real NMI and IRQ, plus nested IRQ during CLI lag NMI:798 paired ISR executions |

The directed callback and health fixtures are labeled as such. They are not
natural item, enemy-hit, or full-stage qualifications. The native IRQ/NMI checks
execute the actual cartridge handlers and compare register/live-stack/R0..7,
SMC, private/native state, mapper, PPU and audio behavior. They are source CPU
vector injections, not observations of physical scanline timing.

The Sonic owner independently ran ordinary controller input from the real
Gimmick-family Select3 menu through X200, camera88, two lives,81 original frames,
162 native foot queries and81 native head queries. That frontend-composed
image is separately pinned as bf24a8b7ca6b5341605cc58e5c189562e79b1e3011b8eed68ea517b6f62bb93a.
A longer source controller reached the 1-1 flag, then exposed a separate
private scene-duty getter/bounds issue in engine5. That issue belongs to the
source owner's new scene derivative and prevents a full-stage completion claim
for this rehearsal image.

All producers used Python `-B` and the bounded wrapper `--max-files 1`.
`build/sonic-public-admission-cpu-1110` remains absent. Root retains the sole
Mesen queue and owns the tested nightly/release composition.
