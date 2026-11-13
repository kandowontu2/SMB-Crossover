# Prince original reach and natural block access

Parent ROM: `cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
Qualified in-memory derivative: `3b7990bc59b490a1c5e488133a7c65d05526944d63b7e987f0b3f44df733343d`.
Identity: Prince of Persia, raw38. No helper platform or other actor was added.
Root owns the Mesen queue, candidate file, installation and release operations.
This helper wrote source/report files only and generated no build outputs.

## Original source and current failure

The SHA-pinned original ROM is
`5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`.
Actual original SetAction/AdvanceActor execution reconfirms action3's six-pixel
hop and action4's fourteen-pixel anchor rise. Action14's animation keeps rawY128
and reaches pose78. No jump height, action script, source velocity, terrain
response or source actor position was changed.

The retained, original-renderer-derived atlas is SHA
`477c6856e7d349aab73aedef65cc69b233714e1809e1fdbf2322f9977a223a8b`.
Its opaque pixels, rather than just sprite-cell bounds, put idle pose15's top
at anchor−37 and pose78's raised hands at anchor−48. Pose78's physical sole
delta is zero, so the current sole−32 native body origin is sixteen pixels
below that pose's top.

An actual cold/native PlayerCtrlRoutine fixture uses floor208, a brick row
X320..399/top144 and a question at X336..351/top144. Neutral X333 followed by
real Up input selects action14. At update60, rawY128/anchor205/pose78/nativeY173
and DY251 coexist with thirteen opaque hand pixels inside the question cell.
Both facing directions produce180 native head returns, all zero, and no native
block effect. The isolated-question control instead climbs and reaches one
ordinary native C1 collision later at nativeY157. These are explicit CPU
terrain/starting-position fixtures, not naturally played stage receipts.

## Small native head projection

The current authenticated Prince HuHead vector is RAM2 `DF81..DF84`, whose
preimage is `4C8795`. It now points to a31-byte leaf at RAM3 `B0FE..B11D`.
The declared funding interval is `B0FE..B11F`: the unused tail of the existing
question-ledge coordinate wrapper, within its previously repurposed source
branch. The current wrapper ends with JMP A917 or JMP C40B before that tail.
The new check verifies no existing absolute call/jump, nearby relative branch
or original animation vector enters this interval. The native material provider
still returns only0/1/20. Zero-filled content alone was not the funding argument.

For pose78 and nativeY>=48, the leaf saves nativeY, queries the existing raw
native getter with Y−16, restores nativeY and returns its genuine R3 tile.
Other poses use the old getter. The ordinary caller still owns the rising-speed,
low-nibble, water, bounce-timer, hurt and material checks and invokes the actual
native PlayerHeadCollision. Native BumpBlock retains its ordinary DY reset.
The source actor and its movement code remain unchanged.

The same staged full-row fixture then returns C1 once at update60/X333 and
enters PlayerHeadCollision with restored nativeY173 and R4=13. Source positions,
actions, poses, modes and opaque geometry match the negative episode throughout.
This is a pose-height projection using the native center-X convention. It is
not a pixel-accurate hand probe: at right-facing X342 the highest opaque hands
lie to the right of the native center. That horizontal approximation remains
an explicit limitation.

## Cold staging funding and reversibility

The original codec recipe is unchanged. Adding the leaf produces compressed
streams6428/5940/1231 bytes; the old runtime staging capacity was6400. The new
decoder wraps to C280 rather than C300 using two immediate changes and remains
254 bytes. Stage adds four bytes at C190 to set its pointer's low byte to80,
with its code/data references and relative branches relocated. The loader grows
446→450 bytes; its worker ends C261, below C280. Source cursor/configuration
offsets account for the four-byte insertion.

Runtime staging now covers C500..DBFF followed by C280..C4FF:6528 bytes, with100
bytes spare. The full payload is45375 of the existing46080 carrier bytes,
leaving705 bytes. There are no new RAM banks or carrier pages. Pose data,
foreign CHR pages and all PRG outside the Prince cookie are byte-identical.

`prince_cold_packet_1111.extract` authenticates both446/450-byte loader formats;
`rebuild` derives the configuration offset from the authenticated header length.
Both formats passed extract/rebuild round-trips. The scoped forward interface is
`transform(raw) -> (image, chunks, layout)`. `reverse(raw) -> parent_image_bytes`
reverses the leaf, vector, loader relocation and decoder immediates, and exactly
reconstructs the cebb parent. Forward after reverse exactly reconstructs3b7990.
Cookie: `a72602ef59ee4b58b224fe37a78747a9`.

## CPU qualification

Final receipt: `880febb14a36b53d4bb5d1ecf03a76218bf03171d5a02a5284dbedc6e3e854e6`.

The complete current resident/PPU staging, independent reread, all three
decoders, finalizer, constructor and authentication execute successfully.
All6428/5940/1231 input bytes are consumed; the minimum unread-input margins
are404 for metadata and131 for state. Actual live runtime and metadata match
the intended decoded buffers and both headers match the new cookie.
Cold CPU8027547/minimumSP180;31330 PPU reads.

All193 forced-blank NMI cuts at changed/relocated cold instructions pass
(minimumSP159). All15 actual IRQ and15 lag-NMI cuts through the live head
projection pass (minimumSP152), preserving the reached native continuation,
registers, private RAM, scratch, mapping and OAM.

```powershell
python tools/audit/run_bounded_build_v1.py --output build/prince-pickup-reach-1112 --max-files 1 --timeout 120 -- python -B tools/audit/check_prince_pickup_reach_1112.py --summary --interrupts
```

The audit produces zero output files. Failed intermediate harness attempts
involved stale labels/addresses or a result-shape assumption; the final receipt
uses actual current decoder operands and the verified current DF81 vector.

## Root's physical controller observations

Root reports the same3b7990 candidate passed full1-1 into active1-2 at frame16374,
terminal HP5/lives2. The route takes injuries earlier; this is not a no-injury
claim. Receipt `7e0c5e0b240534db58fd7085ae1157205128bc16333c98ccd60b9120b73a442b`;
script `9ca6e81186d62096b7d818fd14986dd23c435bc2fabb70d9261fe3e1c15d1037`.

Root's separate controller-only natural acquisition run reveals a kind0
mushroom at X336, observes emergence and mature state80, and chases it until
the actor is consumed. At frame2159/X417/Y176, status1/HP5/lives2/sword0 verify
the collected mushroom and the existing progression bridge. Receipt
`18c9539b5e514daefee470a677e9cdd95f45578f256aac2cbb41bac25f33c1db`;
script `700a13aa79ea500b86cdbfb139b56f3fd35a635f9196b2849bd0846650a7c6f9`.
Natural flower acquisition remains separate. Installation and release results
must be recorded by root after testing the Downloads launch context.
