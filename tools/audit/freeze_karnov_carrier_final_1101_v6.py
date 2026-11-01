"""Freeze the compact current-owner allocation proof; remove duplicate outputs."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from audit_karnov_carrier_final_1101_v6 import O,PIN,sha,save

def main():
 a=argparse.ArgumentParser();a.add_argument('--prune',action='store_true');v=a.parse_args()
 names=['main-reproduction.json','current-reproduction.json','compiled-writers.json','cf-current-binding.json','finite-writer-domains.json','scene-publication.json','interrupt-publication.json']
 proofs={n:json.loads((O/n).read_text())for n in names}
 assert sha(O/'candidate.nes')==PIN and all(q['passed']for q in proofs.values())
 assert proofs['scene-publication.json']['identities']==90 and proofs['scene-publication.json']['ready']==86
 assert proofs['finite-writer-domains.json']['compiled_writers']==845 and proofs['finite-writer-domains.json']['indirect_writers']==123
 assert proofs['compiled-writers.json']['unclassified']==proofs['finite-writer-domains.json']['unclassified']==proofs['cf-current-binding.json']['unclassified']==[]
 assert len(proofs['cf-current-binding.json']['actual_writers'])==19
 assert proofs['finite-writer-domains.json']['all_non_Karnov_CHR_resource_bytes_identical']
 assert proofs['interrupt-publication.json']['genuine_partial_pair_busy_NMI_IRQ_cuts']==5
 assert proofs['interrupt-publication.json']['forbidden_page_writes']==0
 for n in ['cf-current-binding.json','finite-writer-domains.json','scene-publication.json','interrupt-publication.json']:
  assert proofs[n]['bindings'][str((R/'tools/audit/check_karnov_carrier_domains_1101_v6.py').resolve())]==sha(R/'tools/audit/check_karnov_carrier_domains_1101_v6.py')
 grants=dict(passed=True,carrier_granted=True,grant_kind='Old-owner CHR resource ownership; source/compiled proof with finite CPU witnesses',base_ROM_sha256=PIN,
  physical_CHR_pages=[1019,1020],physical_CHR_byte_interval=[1019*1024,1021*1024],NES_file_byte_interval=[1048592+1019*1024,1048592+1021*1024],
  source_named_emission_gap='SMB3Plus atlas pages969..1018, exact50KB; named final padding begins1019. Allocation is based on closed selector/writer ownership, not padding/zero bytes alone.',
  previous_open_gates_now_closed=dict(current_image_exact_relink=True,all_compiled_writers=845,all_indirect_writers=123,CF_private_compiled_writers=19,CF_private_indirect=1,unclassified=0,
   typed_publisher_callers=43,all_non_Karnov_CHR_resources_equal_f641=True,actual_menu_identities=90,ready_identities=86,actual_Main=14964,normal_NMI=15054,IRQ=15054,
   FF_profile_pose_publications=432,genuine_partial_pair_lag_NMI_IRQ=5,ZeldaII_pane_restores=14),
  retained_shadow_induction=[
   'Cold init and native admission clear all12 ordinary modes before restoring native first8 lowbytes; source owner changes cannot retain foreign upper3.',
   'All upper3 physical API callers and direct high3 tags are immutable authenticated families: FF756..787, Pit808..812, MAAA813..815, Gimmick816/818, DK820..823, Bowser824..826, Parodius832..867, Arthur868..880, Benjamin901..914, Battletoads915..918, ContraForce959..968, SMB3Plus969..1018. Other typed upper bits0..2 are safe for every lowbyte.',
   'Special and HUD override upper bits remain0..2, including temporary HUD flag bits. Any lowbyte therefore maps below768.',
   'Legacy native body table writes use native lowbytes; the potentially dangerous FF low251/252 stores are paired by the source FF publisher with upper2. Completed native PlayerBankReady aliases the same admitted low byte.',
   'GameLoop owns NmiDisableFF until completed-frame publication. For selectedFF22, actual lag NMI skips ordinary banks; actual in-flight low-before-mode seams preserve old hardware. IRQ writes only low0 to5128 and cannot map1019/1020 under any upper latch.',
   'Scene setup clears only bounded zero ranges and native area-low tables; it either preserves admitted source pairs or rebuilds them. ZeldaII pane backs up and restores the exact same window11 low/mode pair while its transaction is blank; no owner changes while paused.',
   'Opaque CF carrier935..958 is matched byte-for-byte to all260 original private segments. Its19 compiled possible writers are bounded, including the only indirect score storeC06E..C073; renderer only uses959..968 and restores world windows1..3 to native modezero.',
   'Every conservative absolute-indexed alias has an explicit finite source ABI domain. The123 indirect store sites are bounded to block buffers, owned source RAM/audio history, own WRAM copies or fixed sound-test variant targets; zero clears cannot introduce a forbidden selector.'
  ],
  integration_conditions=[
   'Grant applies to the exact0162 original-owner graph. Integrator must compare successor changes against owned Karnov/menu/code ranges and preserve all other owners, their resource tables and public PCs.',
   'New combat loader must copy/read back1019..1020 while forced blank and before both source/cache cookies publish. Its new graphics API must not map payload as visible art.',
   'The conditional Karnov C2C900..CDFF code/load destination and new resident placement, full actual Main stack/IRQ reserve, cookies and native gameplay must be verified by integrator. This old-owner resource grant alone does not qualify a successor ROM or authorize nightly delivery.'
  ],
  baseline_source_checkpoint='docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4/source.zip',
  prior_proofs={str(p.relative_to(R)):sha(p)for p in[R/'build/karnov-carrier-closure-1101-v4/closure.json',R/'build/karnov-carrier-loader-bounds-1101-v5/loader-bounds.json']if p.is_file()},
  evidence={n:sha(O/n)for n in names},
  limits=['Finite source CPU/mapper/PPU model, no Mesen, no native/full-stage/audio/video qualification. Existing stack-frame aliases rely on the established12-byte reserve ABI; the new combat Main reserve is separately owned by root.','Resolved instruction/source witnesses and complete reproducible compiler/link recipes are kept; duplicate ROM, full39MB debug,13MB object/listing and sideimages are disposable and excluded.'])
 save(O/'carrier-grant.json',grants)
 handoff='''# Karnov CHR1019/1020 owner closure — v6\n\n**Granted for the exact0162287e original-owner graph.**\n\nThe private current-source relink reproduced the published ROM byte-for-byte. The full compiler census closes845 writer spans and123 indirect stores; the separate CF carrier closes19 further writers, including its only score indirect. All original non-Karnov CHR resources are identical to f641, where the original atlas/header/selector families were authenticated.\n\nThe actual90-identity/86-ready menu/Start/entrance sweep executes14,964 Main calls and15,054 normal NMI/IRQ pairs. The432 FF pose cases also run actual in-flight lag NMI/IRQ at five dangerous low-before-mode seams. Fourteen complete ZeldaII pane transactions restore their original pairs. No test maps1019/1020.\n\n`carrier-grant.json` states the inductive source-owner argument and integration conditions. This is a resource ownership grant, not successor/native delivery qualification. Root must still verify new forcedblank copy/readback/cookie publication, composed Main interrupt stack, final allowed diff and native combat.\n\nThe packet contains only compact source, resolved writer witnesses, aggregate receipts and compiler/link recipes. The huge private reproduction files are intentionally removed after freezing. The exact baseline source checkpoint is `docs/qa/checkpoints/2026-11-01/karnov-pickup-nightly-v4/source.zip`; the exact indexed legacy inputs remain in the existing recovery archive. No broad dependencies were rehydrated.\n'''
 (O/'HANDOFF.md').write_text(handoff,encoding='utf-8')
 include=[R/'tools/audit/audit_karnov_carrier_final_1101_v6.py',R/'tools/audit/check_karnov_carrier_domains_1101_v6.py',Path(__file__),*[O/n for n in names],O/'carrier-grant.json',O/'HANDOFF.md',O/'candidate.cfg',O/'main-build.json',O/'full-link.json']
 packet=O/'source-and-proof.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in include:z.write(p,p.relative_to(R).as_posix())
 grant_hash=sha(O/'carrier-grant.json');packet_hash=sha(packet)
 disposable=[p for name in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','candidate.cv3-mirror.json','main.o','main.lst','main.dep']if(p:=O/name).is_file()]
 disposable+=list((O/'sideoutputs').rglob('*'))if(O/'sideoutputs').is_dir()else[]
 removed=[]
 if v.prune:
  for p in disposable:
   if p.is_file():
    assert p.resolve().is_relative_to(O.resolve());removed.append(dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size));p.unlink()
  if(O/'sideoutputs').is_dir()and not any((O/'sideoutputs').iterdir()):(O/'sideoutputs').rmdir()
 save(O/'publication.json',dict(passed=True,carrier_granted=True,base_ROM_sha256=PIN,grant=dict(path=str(O/'carrier-grant.json'),sha256=grant_hash),packet=dict(path=str(packet),sha256=packet_hash,bytes=packet.stat().st_size,members=len(include)),sources={str(p.relative_to(R)):sha(p)for p in include[:3]},removed=removed,pruned_duplicate_bytes=sum(q['bytes']for q in removed)))
 print(json.dumps(dict(carrier_granted=True,grant_sha256=grant_hash,packet_sha256=packet_hash,packet_bytes=packet.stat().st_size,pruned_bytes=sum(q['bytes']for q in removed))))
if __name__=='__main__':main()
