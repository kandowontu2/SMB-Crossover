# Original Doki Doki Panic physics audit

This source-only research supersedes the earlier **skins-only** scope. Imajin, Lina, Papa and Mama require the original Doki player/control behavior. Mama is not an unchanged Luigi skin, and Doki does not acquire SMB2U B-running.

The exact local131000-byte FDS donor is pinned in scope.json. The primary disassembly is pinned at1c7327e4. A genuine guarded175-object build reproduces23 of27 extracted files. Four whole-file differences remain explicit; no full reproduction pass is claimed. The actual1168-byte player slice at8441..88D1,69-byte carry prefix atA956..A99B, original TEMP statistics and all four832-byte character CHR files do reproduce. Tests execute the extracted original donor bytes.

192 jump contexts run on original Doki, original SMB2U and actual installed-a441 S2 leaves (576 executions).32 horizontal contexts,4 timed lift contexts and48 carry contexts also run on all three engines. S2 follows final SMB2U in these tested leaves. Mama's six launch constants are two Q4 units less negative, giving51px versus Luigi56px on the long-held from-rest case; Lina keeps60-update float. Doki has no B speed boost. Its carry offsets and always-large presentation differ from final SMB2U.

These are finite collisionless/declared carry CPU cases, not whole-game or native admission. No game/shared source, Mesen, Git index or Download was changed. The full-rebuild mismatch and all four fixture negatives are retained. The source ZIP excludes ROM/FDS/object/executable/debug/binary assets; original donors remain local and hash-bound. Root owns scope reconciliation and any later private resource/port authorization.
