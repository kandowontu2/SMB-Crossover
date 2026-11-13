# Steve wave carrier proposal: Excitebike blank739

Full CHR row739 (1024bytes) can be retired from Excitebike through an exact
blank alias before new Steve contents occupy it. This is an in-memory proposal,
pending root grant and final current-owner review. No shared allocator,
installed ROM, emulator or generated file was changed.

The retained source packet `2026-11-02/excitebike-source-v1/inputs.zip`, SHA256
`19deba8a9c45e1e23cc38cc5bedd46903fb4e14fa9bf27705a7336d4414c6e2d`,
declares reclaimed rows728..738 and explicitly unused739 in consumer-closure.
Its body-native.chr is exactly the current3072bytes at736..738. All23 original
pose records have maximum8x16 pair90, below the fourth1024-byte quarter.
Current739 is allzero, SHA256
`5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef`.
The old finite-domain ledger broadly labels739 as Excitebike body, although the
actual source emitter uses only736..738. No other one of its88 finite domains,
or inherited private writer chunk, lists739. Current legacy map and compiled
special readers also exclude739; current allocationJSONs contain no page739
reservation. The legacy ledger has ten changed/retired table locations on the
current ROM; this proposal does not misrepresent a complete54-table rebinding
of that historical ledger. Root must retain its current other-owner exclusions
when granting739. The new alias test closes the actual Excitebike consumer.

ExHostGraphics still publishes736..739. Rebinding its fourth window to existing
canonical blank21 preserves every possible pixel in that whole window, even
for native actors outside the body pose set. The source-owned EX_HOST/CODE gap
AF7A..AFFF is134bytes; the delivered original powerup tick occupies its first18.
Current AF8C..AFFF remains116zero bytes at the exact linker gap. A24-byte loop
atAF8C uses modes82/82/82/80. The original loop entryAD18 is replaced by a JMP
and the fourth ExBodyLow value atAD65 changesE3→15. The loop rejoinsAD28 under
the existing saved public ABI. No allocation grows. The Ex cookie is rebuilt
from its actual11-row source/art image:
`a7250288fd2e7241d6b176e36679e09b`→`a72503f6e4938f326baa12f2df77b97a`.

`audit_steve_wave_carrier_1113.proposal(raw)` returns only the Ex alias image
and exact layout edits. On installeda3c5fa63 its alias image is
`cab43af183b95985f9c699de90cdf9db655f1ba95041d9ad9077072014b07f58`.
It leaves739 unchanged. `reverse(image)` restores the exact parent with forward
recomposition; the full Steve inverse must first restore its739 payload to the
original zeros. The helper can then store192wave-art bytes plus832cold-stream
bytes in739 after root grants it. The new source is
`tools/reference/steve_wave_blank_alias_1113.s`.

Bounded zero-output CPU qualification exits0 on exact installeda3c5fa63:

- Both parent and alias run actual cold menu/Start/parser/Main and60 ordinary
  input updates as Excitebike37, keeping both lives and the same position.
- All1024retired739 bytes are deliberately poisoned in the candidate fixture.
  All12 actual published hardware windows remain byte-identical to the parent;
  slot7 publishes21 instead of739. This closes the whole blank window.
- Actual public HuDraw keeps OAM and AXYP identical.
- Eight IRQ and eight lag-NMI cuts through the new loop preserve execution and
  mapper state, minimumSP168.
- Exact inverse restores all bytes; no output files are generated.

```
python -B tools/audit/run_bounded_build_v1.py --output build/steve-wave-space-1113 --max-files 1 --timeout 240 -- python -B tools/audit/audit_steve_wave_carrier_1113.py
```

The eventual Steve cold loader, arbitrary739 carrier contents, all-owner
transitions and actual gameplay remain the owning Steve helper's gates.
