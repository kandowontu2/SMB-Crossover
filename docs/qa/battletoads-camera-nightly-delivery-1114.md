# Battletoads camera repair — November 14 native qualification

Candidate `f11a25b892779cb0d5192457f7feff548f35019818cd75dfef5bdf3f2419b865`
adds exactly52 changed bytes over verifiedcf7:40 bytes in the existing
Battletoads cache and12 existing cookie digest bytes. Two small bridges
publish the native pre-step screen position and actual horizontal movement
delta. This repairs the X239 scrolling clamp for Rash and Zitz. Existing
source physics, artwork, levels, helpers and other roster bytes stay exact.
Gimmick's192-byte graphics repair and all earlier fixes are preserved.

Source gates, exact allocation and frozen adapters are in
`battletoads-camera-candidate-1114.md`, commit3de43c67, and
`allocations/battletoads-camera-handoff-1114.json`. Actual cold copying,
8192-byte readback/new fingerprint, stale-cookie rejection, foreign owners,
retirement, full routes and reached ISR cuts passed. RAM-only research and
old controller negatives remain separately recorded; they are not native
results or game-code changes.

## Private native runs

Both runs use the bounded existing `build/smb2-flag-native-1113` two-file
slot with `--resume --max-files 2 --timeout 600`; Mesen has its capture
watchdog. Only the candidate and controller are replaced. Zero capture files,
videos, images, backups, patches or release assets are produced. The actual
Downloadscf7 bytes/sidecar guards remain exact before and after these runs.

| Identity | Root session | Lua SHA256 | Receipt SHA256 | Physical / completedMain |
|---|---:|---|---|---:|
| Rash |53541 |`c5539dc5f7655ccb7f8f375e22e2467648094fca6b0b8d563f285583415924ac` |`f64ec257be8f7dec5c59b10bc7fb26f1519fbc328b6cf2f10b506e314197b48b` |6464 /4359 |
| Zitz |98906 |`c1bfc6d1079069c6f697d2f492163ba41d407d31fd56d8c41928b3a90d25372d` |`48619365f3fbb73a02c9c205df2a8330d602d82049b4645e836d3ec4f1397579` |6485 /4380 |

Both PASS the full non-shortcut1-1, actual flagpole/castle/entrance sequence
and25 living grounded1-2 updates. Each executes2799 genuine BtCoreStep calls,
including58 in1-2. Terminal40/Y176/high1/native0/engine8, HP35/lives2,
death-timer0/power0/Star0. Actual variant is0 for Rash and32 for Zitz; Zitz
is reached through the real Select alternate. Initial source life is47;
ordinary enemy contact damage is retained, not replaced with invincibility.

Rash first active Main272/frame296; flag3012/4603, castle3075/4698,
entrance3762/5719. Zitz first active293/317; flag3033/4624, castle3096/4719,
entrance3783/5740. Source-model4003Main/HP43 is a different timing model;
neither its counters nor its health are relabeled as native results.

These stage receipts do not measure idle FPS, establish zero lag or close
the complete natural-item/ability/audio/visual audit. A separate empty-view
idle/walk profile is in progress. No helper placement changes occur.

The delivery installer pins both exact native receipts and controllers and
must repeat them using the actual Downloads file after direct replacement.
Until that terminal result is appended, the native section alone is not a
delivery claim.

## Actual Downloads delivery

Root47036, bounded existing two-file flag slot, terminal exit0: directly
replaced `C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes` with
the exact2097168B testedf11 candidate. Both actual Downloads full-stage
replays PASS with precisely the private Lua/receipt hashes, counters and
endpoints above. No rollback was needed. Installed bytes equal the tested
candidate before and after both launches; pre/post patch guards are clear.

There are no backups, patch assets, releases or capture files. Source through
8f187ecc was pushed before installation. A final independent CLI patch check
confirms f11 with no same-name sidecars; GitHub releases API returns0.
Shared preflight is build2873625401B/19996files, within5GB/20000. Remaining
natural-item, idle-performance, ability, sound and visual gates stay open;
this is a verified functional camera/stage update, not full-goal completion.
