"""Freeze the compact, explicitly ungranted Karnov carrier design."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-combat-carrier-design-1101-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 d=json.loads((O/'design.json').read_text())
 c=json.loads((O/'other-consumer-closure.json').read_text())
 assert d['passed'] and c['passed']
 assert not d['carrier_lease_granted'] and not c['carrier_granted']
 assert not d['other_owner_campaign_runtime_closure'] and not c['complete_other_owner_closure']
 assert d['body_unused_bytes']==448 and d['loader_helper_bytes']==70
 assert d['C2_code']==[0xc900,0xcd10] and d['proposed_C2_copy_range']==[0xc900,0xce00]
 assert len(d['native_copy_verify_CPU'])==6
 assert sum(x['success'] for x in d['native_copy_verify_CPU'])==1
 assert c['examined_unique_sources']==690 and len(c['source_writer_inventory'])==76
 assert len(c['closed_selector_groups'])==15
 assert not c['unavailable_declared_sources'] and not c['changed_since_compiled']
 for proof in[d,c]:
  for p,h in proof['bindings'].items():assert sha(p)==h,p
 # Preserve source references as hashes, not a recursively restored tree.
 # Exact indexed objects have already been verified by the consumer auditor.
 assert all(q['sha256'] and q['path'] for q in c['source_refs'])
 text=f'''# Karnov carrier proposal: unallocated, frozen source audit

**Carrier granted: false.** This packet changes no ROM, menu, native loader,
shared service, installed nightly or allocation. The current whole-host source
inventory is bound to `{c['current_ROM_sha256']}`. The earlier design/menu
fixtures are explicitly bound to frozen85 `f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1`;
all other CHR bytes match the current image outside Karnov399..411.

## Established bounds

- Karnov body407..411 has448 unused bytes, in relative runs0+32,896+160,
  1984+96,3040+32,4000+128. All256 original poses,64 host profiles, the
  original cold portrait and seven8x16 shot patterns are included. Original
 134 patterns are32-byte8x16 pairs, not16-byte tiles.1040B cannot fit there.
- Proposed selected-C2 worker C900..CD0F is1040B. A1280-byte transfer would
  lease C900..CDFF including240 zero padding. Audited original actor/options,
  clear/weapons/health/pickup state operands do not reachC900 even with a
  conservative full0..255 indexed domain. Context endsC864, metadata beginsD000.
- Proposed pages1019 and1020 follow the exact50-page SMB3Plus emission969..1018.
  Its3584 legal selector combinations and90 existing menu identities avoid
  those pages. Zero fill and segment absence are supporting facts only.
-690 exact declared source units were read;76 writer units and15 legal typed
  selector groups are catalogued in other-consumer-closure.json. Indexed
  recovery objects were read in memory and are retained by path/hash only.

## Loader source fragment and bounded evidence

Rows0..7 retain CHR399..406 to A3 bank3 C000..DFFF. Row8 proposes CHR1019
to C2 C900..CCFF; row9 proposes CHR1020 first256B to C2 CD00..CDFF. No
unverified RAM opcode executes during cold loading.

The helper source assembles to70B. Replacing old destination setup with a
three-byte helper call reclaims5B before water-table alignment; replacing the
old mapper prefix reclaims10B. Existing copy/verify loops use a row-specific
page count and ten rows.70B of helper/tables would fit the genuine802B ROM29
tail beside713B pickups, leaving19B. The pre-table85B gap would fit66B of
pickup helper, leaving19B. These are measured funding proposals, not grants.

The190B prototype extracts the original byte-copy, verify and final cookie
publication owners and links the70B helper at the proposed old tailBC8E. It
executes in an explicit synthetic mapper image: one success plus five injected
readback failures. All10 readbacks precede paired-cookie publication; failures
deny both cookies. Success performs18964 buffered reads in296908 CPU cycles,
minimum foreground SP218. It omits the real outer guard/save/PPU restoration.

## Exact remaining closure before any allocation

1. Run the actual current ArCacheEnsure/ArCacheLoad carrier into the mapper,
   then enumerate every201 cached descriptor header CHR field and the fallback
   input path. Exact indexed source is
   build/arthur-physical-clock-v1/joint/arthur/cache-runtime.s:40 and173..185;
   descriptor pointer roots areC000/C094/C128. ArCachePublishFast reads field1
   through(R0),Y and publishes mode83. Nominal Arthur868..880 emission is not
   sufficient evidence. Keep this a single aggregate receipt, not201 files.
2. Close every transitive live producer of CurrentCHRBank and X5ChrMode into
   X5WidePublication/X5Direct0..11, including copied RAM kernels and retained
   inactive-window shadows across scene/death/pause/character transitions.
   The generic publisher can represent all1024 pages. Exact current source is
   build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s.
3. Close SsChrActive/SsChrPhysical/X5SpecialChrUpper into X5Write4 and
   InvHudActive/InvHudPhysical/X5HudChrUpper into X5Write8, including every
   producer and cancellation transition. Typed Parodius tables are bounded;
   that does not establish all persistent override values.
4. Complete reachable publication inventory for ARTHUR_CACHE_EXEC, QW_STREAM,
   FF_STREAM, BT_STREAM, BW_STREAM and CF_CARRIER. The15 typed groups prove
   their listed legal selectors only; a writer search is not transitive closure.

Only after1019/1020 is proved unreferenced may root allocate it, integrate the
real forced-blank loader, authenticate the added worker in a new cookie
revision, and test cold/warm/rejected readback and PPU/bank restoration. Actual
Main depth and all live IRQ/NMI seams still need measurement. Combat's earlier
service-entry SP224/minimum ISR SP136 is13B above SMC7B at that entry only;
it does not qualify deeper Main call paths. Root owns integration/native queue.

No donor ROM, full PRG, dependency source tree, per-frame state or emulator
capture is included. This is source/CPU design evidence, not native gameplay
or nightly qualification.
'''
 (O/'HANDOFF.md').write_text(text,encoding='utf-8')
 source=[Path(__file__).resolve(),R/'tools/audit/design_karnov_combat_carrier_1101_v3.py',R/'tools/audit/audit_karnov_carrier_consumers_1101_v3.py',R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc']
 files=source+[O/n for n in['prototype.s','helpers.s','bindings.s','prototype.cfg','prototype.bin','helpers.bin','prototype.lbl','prototype.dbg','commands.json','design.json','other-consumer-closure.json','HANDOFF.md']]
 save(O/'handoff.json',dict(passed=True,frozen=True,design_only=True,carrier_granted=False,complete_other_owner_closure=False,root_modified=False,installed=False,native_qualified=False,current_source_inventory_ROM_sha256=c['current_ROM_sha256'],proposed_CHR_pages=[1019,1020],body_unused_bytes=448,proposed_C2_code=[0xc900,0xcd10],proposed_C2_copy_range=[0xc900,0xce00],loader_helper_bytes=70,pre_alignment_bytes_reclaimed=15,proof_counts=dict(source_units=690,writer_units=76,typed_selector_groups=15,menu_identities=90,SMB3Plus_selector_cases=3584,copy_verify_cases=6),remaining_gates=c['uncertain_consumers'],bindings={str(p.resolve()):sha(p)for p in files}))
 files.append(O/'handoff.json')
 z=O/'source-and-proof.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as out:
  for p in files:out.write(p,p.relative_to(R).as_posix())
 result=dict(passed=True,carrier_granted=False,path=z.as_posix(),sha256=sha(z),bytes=z.stat().st_size,members=len(files),source_files={p.relative_to(R).as_posix():sha(p)for p in source},root_modified=False,installed=False)
 save(O/'publication.json',result)
 print(json.dumps(result))

if __name__=='__main__':main()
