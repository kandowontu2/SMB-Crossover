# Steve armor native allocation audit

No ready512–1024-byte native PRG interval was identified. A concrete33-byte
native trampoline interval is available for root review: physical PRG5,
CPU `BFDF..BFFF`, file `BFEF..C00F` (half-open `BFEF..C010`). No allocator,
shared source, ROM, mapper, or emulator process was changed by this audit.

The initial inspection authenticated installed15a683. Root installed the Karnov
successor during the work; the final bounded audit authenticated
`318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d`.
PRG5 is identical on both, SHA256
`8dae80bf93754db1ced3fb5e9e6a3589014ed7d65f4ca97edda24b76a4f3d1ec`.

`src/sophia_source_terrain.s` defines SophiaWallAttached at BFC2. Its actual
29-byte terminal worker is
`2078BF90034C3EBBAD02608D6A01A9908D6C01A9A28D6D01A98A4C5A01`.
It ends exactly at BFDF. The last instruction tailcalls FarCallCommon at015A;
it cannot fall through into the proposed interval. The remaining33 bytes
are FF. The retained symbol-bearing native linker map agrees with that
endpoint, and current PRG5 has no direct JSR/JMP operand into the interval.
All224 current Rogue lower/upper raw-ROM page mappings exclude PRG5. This
checks source endpoint and actual competing page ownership, beyond a byte
padding observation.

Root can reserve this exact33-byte interval for an injury/service trampoline
if its adapter fits. The owning source/linker should cap Sophia's predecessor
at BFDF. The new service still requires exact preimages, its ordinary native
caller and returned AXYP/SP contract, current owner authentication, foreign
fallback, cold/restore and interrupt checks. This note is a placement
recommendation, not a grant or implementation qualification.

The full image already contains128 physical8KiB PRG banks. A current byte
census found54 FF runs of at least16 bytes,1,646 bytes total; the largest is
105 bytes. Those totals are not free-space totals. The apparent largest
candidates are occupied source/data views:

| Physical range | Bytes | Actual owner |
| --- | ---: | --- |
| PRG80 +1C97..1CFF |105|Rogue audio page24, inside a complete256-byte raw reader mapping|
| PRG80 +1EBD..1EFF |67|Rogue audio page26, same complete-page ownership|
| PRG94 +13B3..13F8 |70|RdBodyIndex1/RdWeaponIndex0 typed index contents in Rogue art|
| PRG87 +1F05..1FFF |251 zero bytes|Rogue audio page94; constant bytes retain the complete-page read contract|
| PRG66 +1F00..1FFF |256 mixed/zero bytes|Rogue relocation page7; this is linked source data|

The old PRG65 A800..AE00 proposal is also occupied current owner code, as
independently reported by the Steve helper. No span above is granted here.
Retained source config comments describing old padding do not supersede the
current linked intervals and new owner packets.

The scalable runtime route remains conditional raw WRAM1 at A000..BFDF,
with raw2 continuing at C000. The Steve helper's current
`check_steve_armor_lifecycle_1112.py --bank1` proves fixture-loaded188-byte
lifecycle execution through actual FarCallCommon,100 original clock cases,
raw3 restoration,20 IRQ and20 lag-NMI cuts. Its full cold mounting and source
storage remain separate work. That helper owns the integration. Larger native
execution requires actual repacking or retirement of an existing owner; an
unqualified zero/FF run does not provide it.

`tools/audit/audit_steve_native_space_1113.py` repeats this current-byte,
source-endpoint, target and page-map census without writing artifacts:

```
python -B tools/audit/run_bounded_build_v1.py --output build/steve-native-space-1113 --max-files 1 --timeout 180 -- python -B tools/audit/audit_steve_native_space_1113.py
```

The completed run exited0 and generated zero files. No historical source tree
was extracted. It does not claim a global proof that every possible unused
instruction/data byte has been found, or any new Main/ISR/gameplay proof.

An additional26-byte native interval is source-qualified on installed65ee:
physical PRG8, CPU `BFE6..BFFF`, file half-open `11FF6..12010`.
`src/megaman_rush.s:112` defines the final GUEST worker
MegaManRushBusterSpawn atBFDE: `A90120CBA14CD6A1`. Its final JMPA1D6
cannot fall through beyondBFE6. The linked symbol and current eight bytes
agree, the26-byte suffix isFF, no direct bank8 JSR/JMP targets that suffix,
and all224 actual Rogue raw-ROM page mappings exclude bank8. Bank8 SHA256:
`6cd11962cbc95527cfcfd860e88e788007fa473e767e0b153ca3d9e090ce4ca0`.
The updated zero-output bounded audit exits0 on exact Downloads65ee.
This provides a second restore/status shim proposal for root's allocation;
the Steve helper owns its ABI, transport and interrupt qualification.
