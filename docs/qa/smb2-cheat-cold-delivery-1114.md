# SMB2 cheat cold-route delivery preparation, November 14

The exact candidate is `fa66fa915d91ed125cf947b5c15d517c2919c62941378e10d62b0fdf184cdaae`.
It retains the granted 64 changed owner bytes and the two separately granted
E037 operands over installed `12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
The strict inverse order remains cold-mirror fa66 → e8, then owner e8 → 12397.
The failed e8 parent and both frozen grants remain unchanged. No release or
patch asset is authorized; GitHub releases must remain empty.

## Readonly controllers and source evidence

`replay_smb2_cheat_cold_regress_1113.controller(raw)` produces
`6594ac1c8056b9b4c7be7ecd3f636faee2649fb6a9443fb6c1de8ac50dc82223`.
This is a strictly ROM-pin-only rebind of frozen ordinary Luigi controller
`ff9bc7b38a268d8cc211b57d76340b51baa4840791bf55905b206be28a8bd58f`;
the original inputs, authentication payloads and complete endpoint are exact.

The source replay passed 3,768 scheduler passes and 3,767 observed Main returns:
full non-shortcut 1-1, flag, castle, next entrance, and 25 quiet grounded 1-2
updates. CheatInvincible remained 0, HP31/lives2/Star0; terminal x40/Y176,
engine8/world0/level1. The next-area passive trace counted 350 entries,
canonical targets, far-call returns and resident returns with no drops.
These are source scheduler counts, not physical video timing.

`replay_smb2_invincible_contact_1113.controller(raw)` produces
`da1fd6ad6bb4bab273ec638d84186b50204602f59e400f659aaf1c97eb9226d9`.
This separate contact fork retains the complete actual title/options/Inv1
opening of frozen full controller `9f693d9f667bb92bda9f4b8ffb060a7a1b550486e5e12568f67303b00b23f625`.
It uses ordinary Right and neutral input, without actor, position, health,
ability or cheat-flag writes. It requires an actual carry-set branch from
PlayerCollisionCore and positive published native bounding-box intersection
with a living Goomba, grounded HP31/lives2/Star0, walking beyond its contact
position and 30 quiet grounded updates. It is deliberately a partial contact
endpoint, not a full-stage clear.

Its source replay passed with 10 positive contacts, first Main177 at x297/Y176
against Goomba x305/Y184. Native rectangles `[114,187,124,208]` and
`[123,198,133,204]` overlap 1×6 pixels. Endpoint x376/Y176, HP31/lives2/Star0;
257 source scheduler passes and 256 observed Main returns. The source frontend
uses the actual compiled CheatsMenuInput unit with explicit UI mailboxes before
the real Start/constructor. The bus lacks a real vblank clock, so this source
unit does not qualify the complete title/options opening. Native evidence below
is the authority for that opening. The source Lua adapter supports the retained
passive exec/write observers and retains multiple callbacks per event.

All source producers ran with `python -B` through the bounded runner using the
absent `build/smb2-cheat-delivery-source-1114` output root and a one-file budget.
The tests generated no files; no emulator was run by the helper.

## Actual native evidence reported by root

Root37792 passed the original complete real UI Inv1/1-1/1-2 route on exactfa66
and Lua9f69, receipt
`b53258a15a7aaaf183ea845e413221ccc962976d8551abe65343bf205135b655`.
It observed 4,705 physical frames/3,768 Main updates, HP31/lives2 and 25 grounded
1-2 updates; 3,581 entries = canonical targets = far-call returns = resident
returns, obsolete targets0, 43 bounded records and zero drops. This avoidance
route alone was not immunity evidence.

Root30224 separately passed actual real UI Inv1 Goomba body contact on exactfa66
and Luada1f, receipt
`badec2132dee4fde2a42c23af204c08f101b042e464ea87ecc8b9d55024fb777`.
It observed 728 physical frames/255 Main updates, 10 positive carry-confirmed
overlaps, first Main176/frame635 at x297/Y176 against x305/Y184 with the same
1×6 native rectangle intersection. HP31/lives2/Star0 persisted through x376/Y176
and 30 quiet grounded updates. This proves the stated Inv1 ground-Goomba
contact scope; it does not qualify every cheat trigger or natural Star pickup.

Root34570 passed the ordinary no-cheat full6594 route on exactfa66, receipt
`be4760a0f150645431f4d01d716feb7674ecb24eb9f372cc1bf4b1fca4abe411`.
It observed 4,521 physical frames/3,768 Main updates, HP31/lives2, full flag,
castle, entrance and 25 grounded 1-2 updates at x40/Y176/engine8. Those counts
match the prior public12397 ordinary Luigi baseline. All three private native
scopes are closed. Actual Downloads-context verification remains required
after root executes the direct installer; no helper installs or runs Mesen.

## Explicit current-input handling

`current_smb2_cheat_input_1114.normalize(raw, kind='cheat-fa66')` requires exact
fa66 bytes and the strict two-stage inverse. `kind='postbg12397'` is a separate
exact type. There is no auto-detection, fallback or widening of frozen factory
PINs. The object retains original bytes/hash, normalized12397 bytes and inverse
provenance. Normalization is for source/metadata reuse and is not delivery.

For a component composition, `CurrentInput.preserve(legacy_result,
legacy_result_SHA256=PIN, allowed_component_offsets=qualified_offsets)` requires
an exact legacy result and caller-qualified ownership. It rejects ownership
overlap with the complete owner spans and all four 45-byte cold gates, requires
every legacy difference to belong to the component, and restores all 66 current
fix bytes. Every current byte outside the component stays exact. The returned
combined result remains explicitly unqualified and uninstalled.

The final typed ownership-unit check passed exact identity roundtrip and 20
rejections, including wrong/missing kinds, forged provenance, wrong legacy
result hash, unowned legacy differences, overlap with every protected complete
envelope, and dirty legacy preimages. One explicitly synthetic in-memory byte
difference was used only to test ownership enforcement; it is no gameplay
candidate and was never written to disk.

The optional actual frozen DK16c composition check separately passed in memory:
legacy `16c71bc6fb6427ddb0c43dc41d687e768bb4f86015a23204398023fbf3856bd1`
plus the 66 preserved fa66 fixes yields
`a5942300cd677a9c62b1f3ff312552216766de8fcca8d93f8939143f3f650625`.
All 846 DK differences are owned; all current bytes outside the DK component
and complete cheat envelopes are exact. This proves source composition only.
That combined image was not written, run natively, installed or qualified.

The new source-route CLI defaults to strict12397; a later installed fa66 needs
explicit `--input-kind cheat-fa66`. Root owns live runner integration. Existing
DK, Mini and SMB2 native runner defaults and their unknown-image rejection are
unchanged by this helper. New native candidates must preserve all current fixes.

## Delivery command and required post-install verification

After checkpointing these sources, root may run:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-cheat-delivery-source-1114 --max-files 1 --timeout 300 -- python -B tools/audit/install_smb2_cheat_cold_nightly_1114.py --metadata
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-cheat-delivery-source-1114 --max-files 1 --timeout 300 -- python -B tools/audit/install_smb2_cheat_cold_nightly_1114.py
```

The installer requires the exact tested private fa66 bytes in the existing Bub
slot, exact installed12397 bytes, strict inverse equality, both frozen replay
factories/controller hashes, and a clean same-name IPS/BPS/UPS guard before and
after. It writes the sole Downloads ROM directly and compares all installed
bytes against the tested candidate. It makes no backup, patch or release.
The helper's readonly installer metadata preflight passed on installed12397:
all exact source/controller/inverse checks passed and the guard found no
same-name patch. Its receipt explicitly reported `installed=false`.
Its receipt explicitly leaves actual Downloads launch required. Root must
launch the installed path itself with the exact6594 ordinary controller, then
record that native receipt and both guard results before claiming delivery.

No helper/platform placements changed in this task.
