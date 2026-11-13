# SMB2/Doki pipe priority — November 13

Private, source-qualified rendering successor, with a newly exposed priority
lifetime issue. It is **not installed**. Current Downloads is tested Bub f88;
GitHub releases remain empty. Root owns the native queue, reports and delivery.
No ROM/capture/receipt/object or extracted tree was written by this helper.

## Actual cause and exact source binding

Frozen2c62 fixes the native feet halt and walks into the outdoor1-2 pipe, but
cannot keep the native pipe latch. Root's actual trace
`12e9ce45243f78a14d52fff84420bff700aa1ff460c468e9949a7a2132918476`
shows native1269CFD writing PlayerSprAttrib0→32 at frame4037/Main3217/X147,
then S2Graphics B6A5 writing32→0 in the **same Main**. The pattern repeats72
times; ChangeAreaTimer160 does not count down. No motor or controller fix is
indicated.

Shared `src/smb2_roster_render.s` is an older USA unit. The actual Ready85
archive render member SHA78ee206b221df9d8ad49de67d57fc51a403acd3b1ffac575ec37ca55604c8ffb
and Doki draw member SHAad294b97516974279f1195a7496e1db36f9cfc371f61a3434f552963f344c2e4
are read as exact members in memory, never expanded to a tree. The initial
19B NativePaletteOffset-table idea was withdrawn/rejected: that old table
already does not exist in the current Doki pointer. It granted nothing.

The fresh source in `smb2_pipe_priority_1113.s` has SHA
53e6a38c1a47d36996ea1e5d4e9ec36bcbd62086113f91dca46570a19c13b76e.
Root's conditional grant `allocations/smb2-pipe-priority-1113.json` names only:

| Current owned envelope | File offset / size | Parent preimage |
|---|---|---|
|Graphics B62F|972351/144|608cbaff10ef768615097577f71ad5cf1d384ad19ec8f4898dd2e49860b67df7|
|PalettePointer B7EF|972799/63|e0b026cefbcfa9c55d0525a048874e5c3ec8487c20442dd12d6c8ca6231a1df1|
|Body init B762|972658/6|a90085068508|
|Doki standing Meta JMP|974799/3|4c9bb6→4c9ab6|
|Doki standing SetBody JMP|974826/3|4c8bb6→4c8ab6|

Entire original144B Graphics,63B PalettePointer and unchanged134B Doki builder
are reproduced byte-exact from the current source. The pointer becomes55B plus
an8B helper atB826..B82D. Actual two-ASL class offsets cannot carry; lowE9+12
and2E+12 remain within a page. Reusing variant X and removing redundant carry
work funds8B. PalettesB82E and OriginalRole1B83E stay fixed. The helper masks
the RAM latch to20 and supplies R3 to the real renderer. Graphics offsets its
extra byte by the original Doki builder's proved C0 return. Body preserves R3
and zeros R5 from actual PublishBody/X5SetPhysicalChr's Y0. No RAM, CHR, actor,
palette color, physics, helper or allocation outside these envelopes changes.

## Frozen APIs and source tests

`compose_smb2_pipe_priority_1113.proposal(exact2c62)` produces
`dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be`.
Only132bytes differ in the five declared envelopes. `inverse` restores exact
2c62 and authenticates the full roundtrip without reading Downloads. Candidate
and original flag/mirror APIs are separately pinned; no old negative is retagged.

The pure `replay_smb2_pipe_priority_1113.controller(candidate,4)` has Lua SHA
`f4b9ebfaee4cd75245ecd3cb0e38b5d4ab6c00127fc2a9f125270448a5ddf5cc`.
Only the expected ROM label changes from a6e3; all movement and complete
flag/castle/25grounded-underground assertions remain intact.

Zero-output modes in `check_smb2_pipe_priority_1113.py` use the existing bounded
root. For example:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_pipe_priority_1113.py --render
```

- `--pointer`:2048 pointer AXYP/all-RAM pairs across every variant byte and
  valid native class0..3, plus510 foreign-owner pairs. USA/FDS pointer data and
  all output registers/flags/scratch match the parent.
- `--domains`: the actual161B ResetTransient source and its sole bounded8-row
  NativeCharacter writer are reproduced;8 genuine menu constructors give
  native map0,3,2,1,0,1,2,3. Real Select cycles0..7→0.352 actual Doki builder
  calls return C0 and256 real PublishBody calls preserve Y0 and R3/R5.
- Corrected `--render`:2112 Graphics AXYP/pose/CHR pairs and2112 native renderer
  OAM pairs, including1216 active priority cases. All8 real cold seeds, both
  sizes/facings/holding and all11 animations are used; post-Ensure assertions
  prove the input pose was not reset. Color/facing/packet/geometry and every
  other OAM byte stay exact. These are synthetic directed rendering inputs.
  The first run used the stale Doki5..7 native map and could reset those pose
  fixtures; its old1408 priority count/all8 coverage is superseded by the
  corrected run. Candidate bytes never changed.
- `--references`: actual40B Doki standing source reproduces both true JMPs.
  Other-bank matches652957/32781 remain untouched. The apparent B820 word at
  968289 is the opcode/operand start of actual S2N8A52 `JSR A9B8`; a literal
  producer at1019254 targets bankCF, not S2 bankF6. Private moved No/USA/high
  entries have no external S2 transfer/data producer. Graphics No/Foreign/
  animation anchors remain exact.
- `--foreign`:1530 non25 Graphics/Body/Palette guard AXYP/all-RAM pairs and8
  actual menu preview OAM/VRAM/CHR pairs pass. Foreign private physics is not
  executed from an uninitialized synthetic owner byte.
- `--vectors`:302 reached changed-code or R3-live renderer points,302 realIRQ
  plus302 realbusy-lagNMI, minimum SP172. An actual ordinary injury starts the
  source sample at Main185/X301/Y176/HP15/bank120. All302 busy cases have real
  music advance exactly paired against the original ISR, with no masked clock
  or audio field. Full native/overlay RAM, SMC, scratch, AXYP/live stack/maps
  and the new foreground continuation compare exactly. Attribute/pose fixtures
  are explicit; sample waveform and native deadlines are not inferred.

## Native success and remaining lifetime defect

Root's actual ordinary Mario run reaches25 grounded underground1-2 updates:
4484physical/3597Main, HP15/lives2, receipt
`a8092c7c38c1537185c96be94e8e54ef618e54c89c8cff91a18e351efed98395`.
The reviewed in-memory pipe PNG shows proper occlusion. No capture file exists.

The underground image and tag also show PlayerSprAttrib32 still present in
normal engine8 at nextUpdates21. Preserving that priority forever can place
normal play behind background art. This is a genuine remaining lifetime
defect; dadb/f4b9 are frozen and must not be delivered as the final fix.
Current native1/A176..A191 independently authenticates the original policy:
Y>=64, engine not5/7 and engine>=4 clears priority bit20 before the hole pass.
S2MainPlayer bypasses that native controller path. A separately measured owned
MainWorld successor will restore the visible engine8 subset, preserving the
pipe/end/above-HUD handoff and documenting offscreen pages. It is not funded
by an invented table or an unowned tail. No foreground successor claim is
included in this checkpoint. All8 complete stages still require separate
ordinary controller/native coverage; other abilities/items remain open.
