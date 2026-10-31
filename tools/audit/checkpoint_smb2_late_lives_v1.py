"""Export bounded late-lives source/proof checkpoint. Never stage or commit."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from finalize_ff_current_component_v3 import dependencies
O=R/'build/smb2-late-lives-palette-v6';J=O/'joint'
D=R/'docs/qa/checkpoints/2026-10-30/smb2-late-lives-palette-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 assert not p.exists(),p
 p.write_text(s,encoding='utf-8',newline='\n')
def verify(h):
 for p,v in h['bindings'].items():assert sha(p)==v,p
def main():
 h=json.loads((O/'handoff-qualified-v2.json').read_text())
 assert sha(O/'handoff-qualified-v2.json')=='cdaecb1a19548d1fa5de26885a9d5b636228d3d2ecfc1bb599a63f1c9b3d8c69'
 assert len(h['bindings'])==805;verify(h)
 assert not D.exists();D.mkdir(parents=True)
 tools=[R/'tools/audit'/f'prepare_smb2_late_lives_palette_v{v}.py'for v in range(1,7)]
 tools += [R/'tools/audit'/f'smb2_late_lives_controls_v{v}.py'for v in range(1,4)]
 tools += [R/'tools/audit'/f'smb2_late_lives_isr_v{v}.py'for v in range(1,3)]
 tools += [R/'tools/audit'/f'freeze_smb2_late_lives_v{v}.py'for v in range(1,3)]
 tools += [R/'tools/audit'/n for n in ['smb2_late_lives_retry_v1.py','smb2_late_lives_combined_controls_v1.py','prepare_smb2_lives_palette_diagnostic_v1.py','smb2_lives_first_dma_audit_v1.py','checkpoint_smb2_late_lives_v1.py']]
 tools += [R/'tools/reference/smb2_lives_palette_diagnostic_v1.lua']
 proofs={
  'handoff-qualified-v2.json':O/'handoff-qualified-v2.json',
  'first-handoff.json':O/'handoff.json',
  'source-proof.json':O/'source-proof.json',
  'source-stage.json':O/'source-stage.json',
  'source.patch':O/'source.patch',
  'controls.json':R/'build/smb2-late-lives-controls-v3/controls.json',
  'isr-controls.json':R/'build/smb2-late-lives-isr-v2/controls.json',
  'retry-controls.json':R/'build/smb2-late-lives-retry-v1/controls.json',
  'combined-controls.json':R/'build/smb2-late-lives-combined-controls-v1/controls.json',
 }
 for n,p in proofs.items():
  if n.endswith('controls.json'):
   d=json.loads(p.read_text());assert d['passed'];verify(d)
  (D/n).write_bytes(p.read_bytes());assert sha(D/n)==sha(p)
 paths=set(tools)|set(proofs.values())|set(dependencies(J/'component.dep'))
 paths|={O/n for n in['README.txt','component-build.json','final-link.json']}
 paths|={J/'private.cfg',J/'component.s'}
 for d in ['smb2-late-lives-palette-v2','smb2-late-lives-palette-v3','smb2-late-lives-palette-v4','smb2-late-lives-palette-v5','smb2-late-lives-controls-v1','smb2-late-lives-controls-v2','smb2-late-lives-isr-v1']:
  paths|={p for p in (R/'build'/d).glob('*.json')if p.is_file()}
 diag=R/'build/smb2-lives-palette-diagnostic-v1/class0'
 paths|={diag/'ready.json',diag/'observer.diff'}
 paths|={diag/'capture'/n for n in['palette-write-order.csv','candidate-controller.log','binding.json','trace.csv']}
 paths|={R/'build/smb2-lives-first-dma-audit-v1/audit.json'}
 native=R/'build/smb2-late-lives-native-v1/class0'
 binding=json.loads((native/'capture/binding.json').read_text())
 result=json.loads((native/'capture/result.json').read_text())
 assert binding['exit_code']==0 and result['passed'] and result['ROM_sha256']==h['candidate']
 assert result['frames']==570 and result['main_updates']==220 and result['actual_UI_DMA_checks']['lives']==17
 verify(binding)
 nativefiles={native/'ready.json',native/'controller.lua'}|{native/'capture'/n for n in ['binding.json','result.json','candidate-controller.log','trace.csv','select-lives-OAM.csv','main-cycles.csv']}
 paths|=nativefiles
 allowed={'.py','.s','.inc','.mac','.cfg','.json','.txt','.patch','.lua','.diff','.csv','.log'}
 assert all(p.is_file() and p.suffix.lower()in allowed and p.resolve().is_relative_to(R)for p in paths)
 archive=D/'source-only.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(paths):z.write(p,p.relative_to(R).as_posix())
 assert archive.stat().st_size<=4*1024*1024
 with zipfile.ZipFile(archive)as z:
  assert len(z.infolist())==len(paths)
  for p in paths:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 write(D/'README.md','''This incremental source-only checkpoint preserves the exact S2 late-lives fix f3a2c5a3 and immutable source handoff cdaecb1a (805 verified bindings). It depends on the already frozen combined remap/BG/eye source37210891. No ROM/object/debug/PNG binaries are included. No source, Git index, commit, download or native process was changed by this export.

Only206 ROM bytes differ: own S2MenuStatus71B and166B inside existing C80 CD25..<CE00 alignment padding. Original15B CD16..<CD25 helper, public PCs, header, CHR, other PRG and final125 mirror remain exact. Adopt only the two producer files named in the handoff, recompile the actual component and rebind current genuine importing owners; do not copy an old main/config/common tree. No new RAM/PRG/CHR ownership.

The root-executed native3721 failure is retained: ROM3 deferred SetupIntermediate's palette, native bulk installed Mario P0, portrait queued source colors, and actual WriteGameText overwrote that queue before first lives DMA. The source regression now reproduces that exact pending-ROM ordering. The genuine late A1/Y30 text callback appends the full original P0 plus black universal after the30B native text, invalidates ACK before retry, and preserves original AXYP/C, R0..7 and33 SMC operands. Lives remains black; actual entrance/gameplay remains native blue22.

CPU scope:8 actual pending-order cold/lives/entrance cohorts and64 Main TOTAL;1024 original nonlives full64-distinct-flag pairs;512 late palette/queue cases;128 real IRQ/lagNMI cuts;8 actual WriteGameText deferral/retry consumers. All relevant retained compile, ABI, distinct-flags, source-bound and diagnostic negatives are in the archive. The combined dfdb cart separately passed the same8 cold cohorts/64 Main TOTAL and8 real WriteGameText retry consumers; this is a source result, not native admission.

Root executed the unchanged bounded v6 native observer on exactf3a2: terminal exit0 at570 PPU frames,220 controlled Main,17 correct lives DMAs,220 blue-background checks and440 vector restore guards. Root reported visual review of all4 PNGs. This export binds that original native result/log/trace and source controller but omits PNGs and binaries; their original paths/hashes remain in the native binding. No level-clear or60Hz claim. Other classes and the later combined cart are outside this one native Mario result.
''')
 write(D/'retained-negatives.json',json.dumps(dict(native_wrong_first_lives_DMA=str(diag/'capture/palette-write-order.csv'),source1_guard_no_BSS_output_offset=True,source2_wrapper_overflow=True,source3_generic_local_label_collision=True,source4_name_SFC_observable_mismatch=str(R/'build/smb2-late-lives-controls-v1/controls.json'),source5_longbranch_range=True,controls2_interrupted=str(R/'build/smb2-late-lives-controls-v2/interrupted.json'),isr1_partial122cases=str(R/'build/smb2-late-lives-isr-v1/controls.json'),frozen_evidence_unchanged=True),indent=2)+'\n')
 own=[p.relative_to(R).as_posix()for p in tools]
 own += [p.relative_to(R).as_posix()for p in sorted(D.iterdir())]
 own += [(D/'owned-files.txt').relative_to(R).as_posix(),(D/'manifest.json').relative_to(R).as_posix()]
 write(D/'owned-files.txt','\n'.join(own)+'\n')
 manifest=dict(status='SOURCE_QUALIFIED_ONE_ROOT_NATIVE_MARIO_PASS_COMBINED_SOURCE_PASS',source_handoff=sha(O/'handoff-qualified-v2.json'),source_binding_count=805,candidate=h['candidate'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members={p.relative_to(R).as_posix():sha(p)for p in sorted(paths)},checkpoint_copies={n:dict(original=str(p),sha256=sha(p))for n,p in proofs.items()},native_mario=dict(result_path=str(native/'capture/result.json'),result_sha256=sha(native/'capture/result.json'),binding_sha256=sha(native/'capture/binding.json'),scope='One root-executed exactf3a2 Mario cold firstlook, not combined native or levelclear'),own_tools=[p.relative_to(R).as_posix()for p in tools],owned_files_list=(D/'owned-files.txt').relative_to(R).as_posix(),no_ROM_object_debug_in_archive=True,no_git_mutation=True)
 verify(h);verify(binding)
 write(D/'manifest.json',json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(checkpoint=str(D),manifest_sha256=sha(D/'manifest.json'),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members=len(paths),owned_files=str(D/'owned-files.txt'))),flush=True)
if __name__=='__main__':main()
