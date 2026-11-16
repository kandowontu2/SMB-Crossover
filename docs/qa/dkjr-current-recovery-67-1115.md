# DK Jr. public packet recovery on official67

The installed67 nightly contains the older **public DK Jr. packet**, rather
than private769 or the later one-way/floor-entry proposals. The November11
delivered full-stage pass remains valid for its recorded version. A private
3040 handoff failure does not establish a failure of the current nightly.
This recovery executes no gameplay and claims no fresh current full-stage pass.

## Exact current identity

Read-only checker `tools/audit/recover_dkjr_current_identity_67_1115.py`
reads Downloads once and requires exact
`67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5`.
Its terminal aggregate receipt SHA256 is
`86f73a3300b55346c311e07a582695bd89226accb394b29c4c27c72be4f8b7ce`.

- Eleven 1KB carriers:817,833,847,856,867,881,882,883,959,960,961.
- Complete11264-byte payload SHA256:
  `30b1118ac41a70e81c2eda030f5d93a5f56b57feb8600415f860e6007dfffc83`.
- Owner cookie at file534485:
  `a7280130b1118ac41a70e81c2eda030f`, independently recomputed from the payload.
- The five original public native spans also match exactly: file6515/87B,
  5199/3B,5911/11B,482667/26B and482789/26B. In particular, the public
  RunLargePlatform call remains `20 8E B9`; private769 uses `20 7F B9`.
- Payload, cookie and those five spans total11433 bytes. Concatenated in the
  checker's declared order, their SHA256 is
  `9eda92c47548d0b5b8fa39efb0555367b61d9139ca45ecce2ca7f632093fbfff`.

The payload identity is the same full-stage public source authenticated in
[dkjr-current-powerups-1113.md](dkjr-current-powerups-1113.md). No retained
private ROM was read; no historical image was regenerated to obtain it.

The unchanged authored helper rows for **Donkey Kong Jr.**, selected from
Donkey Kong by one Select press, are below. These are initial placements,
not new current native spawn/carry observations. All are stage1-1.

| Actor | Initial left X / center X | Initial top Y | Width |
|---|---|---:|---:|
| Stock vertical25 |416/432,480/496,560/576,624/640|192|32|
| Stock vertical25 |688/704,752/768,880/896,944/960|192|32|
| Stock horizontal28, second gap |1408/1432|208|48|
| Stock vertical25, fifth-pipe ascent/descent |2576/2592,2640/2656|192|32|
| Stock vertical25, sixth-pipe ascent |2832/2848|192|32|
| Stock vertical25, final descent |3040/3056|192|32|

There are12 vertical actors and one horizontal actor. The private additional
Mushroom helper at left336/center352 is absent. The detailed placement authority
remains [helper-platform-inventory-1101.md](helper-platform-inventory-1101.md).
No helper or terrain bytes changed in this recovery.

## Versioned gameplay evidence

The older [actual Downloads full pass](dkjr-full-nightly-delivery-1111.md)
used ROM
`b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576`
and receipt
`0d8861c3102a5a1fb721b3ce6fe3dfde8feec385c2b0a6807e4d5c57c07d88fc`.
It traversed six pipes/three gaps, reached flagMain9605, then entered active1-2
with both lives. It did **not** require25 returned living grounded1-2 updates.

The private native769 image
`769afe8d7fcdb58bed5f9f43109d7aabab3d93b1a7afb0535926e51cffce94ff`
was never installed. Its frozen replay clears six stairs but fails during
the final3040 handoff. The later passive native proof identified the first
incorrect original landing at A8DD while source3 was still rising, before
native carry. The native one-way e98 successor subsequently failed earlier
at pipe5 because native static-floor clamping was not imported to the original
source Y. These remain distinct private negatives; see
[dkjr-final-handoff-1114.md](dkjr-final-handoff-1114.md).

## Floor/entry source inventory and limits

The root grant
[dkjr-floor-entry-fit-1114.json](allocations/dkjr-floor-entry-fit-1114.json)
still hashes to
`3ba6f0b10fe1e91265991a9240ee78fd41cef6a04a1c4b596bc6ebd9ddaeaaa7`.
All seven frozen measured-source hashes in it still match. It grants five
existing DK logical spans,1073 bytes total, over private09b, with a strict
production composition parent1daca. It grants no current67 composition or
native installation. No new RAM, carrier or epoch cache is included.

The recipe APIs remain present and frozen:

- `compose_dkjr_floor_entry_1114.proposal(exact09b)` gives private60d4;
  `inverse(exact60d4)` returns09b.
- `compose_dkjr_floor_entry_current_1114.proposal(exact1daca)` gives CAB;
  its `inverse(exactCAB)` is a distinct production-source boundary.
- `replay_dkjr_floor_entry_1114.private_controller/current_controller` bind
  those exact images and relocated observations. Their old late-flag controls
  are not a qualified full-stage policy.

Four floor-fragment preimages match public67, but **body_guard does not**:
current public10B SHA256
`9f08ad0681705d0d03d9067b27b486ead1b281761fcaf48dd60199715815c936`
versus private09b
`f040ee5dd7da1ac708c6e822ed3ac5b430fe4ebef803574ef9bb866b5296f769`.
None of the five current fragments matches its floor-proposed hash. Therefore
copying only those1073 bytes over current67 is invalid: the earlier complete
head/retire/direct/one-way component is part of the private source contract.

Root's original compact-primitive gates cover17408 translations,26112 flag
cases,160 original draws,3328 context cases,238 moved labels/34 SMC writers
and506 IRQ+1012 busy-NMI cuts. They are versioned source evidence, not newly
executed here. Private60d4 source cleared all stairs/final helper but its
late flag launch hit the existing flag base; no native60d4/CAB full pass exists.
CurrentCAB full route, fresh production inverse and complete cold/read-failure/
header/death/foreign lifecycle remain open as recorded in
[dkjr-floor-entry-source-1114.md](dkjr-floor-entry-source-1114.md).
The retained lifecycle checker is unexecuted work, not a passing receipt.
The additional roughly504 draw cycles are not a lag improvement.

## Next root replay and typed source plan

The smallest next test uses unchanged current public game bytes, before
reviving a private repair. The checker recovers the two pure retained Lua
text transforms through AST extraction, without importing their historical
producer/dependency graph. The reconstructed old controller's LF SHA256 is
`dab0b8b34ec501f53bd680b3bc80c8d9ca1e99af343db415cc4c7ba159baae74`.
Windows CRLF serialization reproduces the actual delivered controller exactly:
`96b6aa7760e0d9567aed999405d5aa359357f9cf86aa2f9e99f45f427e6daced`.
The first recovery invocation rejected the LF/CRLF mismatch; correcting only
that explicit serialization assertion produced the authenticated result.

Native-ready **binding-only** API:
`recover_dkjr_current_identity_67_1115.controller(raw67, kind='delivered-public-67')`.
It authenticates the entire owning packet and exact whole input, then adds
only an exact67 ROM-env assertion to the recovered text. Removing that
assertion recovers the historical LF body byte-for-byte. Lua compile and two
strict wrong-kind/dirty-input rejection gates pass. New LF SHA256:
`43b51e99c2e05c101a697f35bbf4a154deb6a3a3b4edf455f58bf586badb500d`.
Root must supply `SMB_STDOUT_ROM_SHA=67e3…`, `SMB_TEST_VARIANT=0` and
`SMB_DKJR_FAST_ROUTE=1`. No native run is performed by this helper. This replay
retains the original active1-2 endpoint; a separate successor must add actual
completed-return/+25-grounded qualification before upgrading that scope.

If private repair work is required after observing the actual current route,
use a **new** strict67 input/component composer. Authenticate the complete
11433-byte public preimage and source-reconstruct the canonical private60d4
packet through its existing exacte73/14ae/769/09b recipe boundaries (no mutable
metal-slot input), then request root's explicit current rebase allocation.
Preserve every unowned current byte, including all Prince/carry/Bub/Gimmick
repairs, and prove a portable inverse to exact67. Do not widen frozen1daca,
421 or old private APIs. Rebind moved hooks, finish lifecycle and a genuine
ordinary flag/+25-grounded1-2 source route before new candidate/native work.
No geometry, fractional projection or auth-cache change is inferred or funded.

All recovery invocations used absent `build/dkjr-current-recovery-67-1115`,
max-files1/600 seconds, and created zero files. No source mount, ordinary CPU
route, ROM composition, archive extraction, capture or native run occurred.
