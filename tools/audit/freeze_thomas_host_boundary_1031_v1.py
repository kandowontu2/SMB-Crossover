"""Compact immutable source/control checkpoint for corrected host scratch."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-31/thomas-host-scratch-boundary-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();O.mkdir(parents=True)
 stages=[R/f'build/{n}/source-stage.json'for n in ['thomas-host-scratch-1031-v1','thomas-host-boundary-1031-v2','thomas-sparse-template-1031-v1']]
 receipts=[R/'build/thomas-host-scratch-oracle-1031-v1/controls.json',R/'build/thomas-actual-host-vectors-1031-v1/controls.json',R/'build/thomas-host-boundary-controls-1031-v1/controls.json']
 own_tools=[R/'tools/audit'/n for n in ['prepare_thomas_host_scratch_1031_v1.py','check_thomas_host_scratch_oracle_1031_v1.py','check_thomas_actual_host_vectors_1031_v1.py','prepare_thomas_host_boundary_1031_v1.py','check_thomas_host_boundary_1031_v1.py','prepare_thomas_sparse_template_1031_v1.py',Path(__file__).name]]
 own_tools+=[R/'tools/reference/thomas_host_boundary_1031_v1.s']
 bindings={};source=set(own_tools)
 for path in stages+receipts:
  data=json.loads(path.read_text(encoding='utf-8'))
  assert data.get('passed',data.get('result',data.get('status')))in[True,'PASS','SOURCE_LINKED_ISOLATED_TRUE_HOST_SCRATCH','SOURCE_LINKED_NATIVE_BOUNDARY_NOT_HOOKED']
  for p,h in data['bindings'].items():
   p=Path(p).resolve();assert sha(p)==h,(path,p,'binding drift')
   if str(p)in bindings:assert bindings[str(p)]==h
   bindings[str(p)]=h
  source.add(path)
 for directory in [R/'build'/n for n in ['thomas-host-scratch-1031-v1','thomas-host-boundary-1031-v2','thomas-sparse-template-1031-v1']]:
  source.update(p for p in directory.rglob('*')if p.is_file()and p.suffix.lower()not in['.o','.lst','.dep'])
 source.update([R/'build/thomas-host-boundary-1031-v1/source/host.s'])
 for p in list(source)+stages+receipts:bindings[str(p.resolve())]=sha(p)
 negatives=dict(frozen_literal00_07='Preserved predecessor10f119. Literal00..07 scratch and syntheticlabISR are not actuala126 scratch/interrupt proof. Actualhost03..0A is explicitlyrebound/testedinthissuccessor.',
  first_host_assembly='build/thomas-host-boundary-1031-v1/source/host.s retained missing.macpack longbranch compile-onlynegative. No linkedcandidate orproductverdict. Correctednewv2links5,105B.',
  old16_scope='Prior frozen91e756/old16-scope-negative retained; its simulated09hostfield was a labillustration. Actualhost09=R6, and actualnativeNMIowns00..02.')
 dump(O/'negative-clarifications.json',negatives);source.add(O/'negative-clarifications.json')
 (O/'README.md').write_text('''# Thomas corrected host-scratch and boundary source milestone

The a126 cartridge is unchanged. No menu/readiness/shared hook or Downloads change.

The frozen C2 predecessor used literal $00..$07. This successor imports actual
R0..R7=$03..$0A; $00..$02 remain native NMI scratch. Both original-code comparisons
and actual unchanged a126 NMI/IRQ vectors pass. All CPU execution uses NesMPU,
which preserves D while performing binary NES ADC/SBC.

The original accepted integrator is called once. New boundaries export its
position, query genuine native terrain, preserve original body/melee rectangles,
rebase after native contact correction, invoke native enemy defeat once, retain
original HP/underflow math and delegate native item progression. A two-phase
terrain API is not a claim that a natural shared Thomas game loop is integrated.

Outstanding: natural row/lifecycle/hook composition, fall/ceiling reconciliation,
sparse forced-blank loader/full cookie/epoch/5FFF retirement, native CHR/OAM/palette
publisher and original audio relocation/ownership. Thomas remains pending.

Measured template: 5 A3 code pages, 2 C2 metadata pages, 5 original body pages.
All other code/state pages are FF/zero fills. 12/16 granted pages are measured;
4 remain within the same grant. The original 1,983-byte audio region has not been
relocated, so no final two-page audio-fit claim is made. The 1,478-byte resident
lease is granted but has no emitted Thomas loader in this milestone.

Archive contains owned source, compiler recipes/text metadata, bounded isolated
binary templates and receipts; it contains no NES ROM, executable or object.
Existing parent ROM/DBG/object bindings remain external pinned dependencies.
''',encoding='utf-8');source.add(O/'README.md')
 manifest=[]
 with zipfile.ZipFile(O/'source-and-controls.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(source):
   assert p.suffix.lower()not in['.nes','.exe','.o']
   rel=p.relative_to(R).as_posix();z.write(p,rel);manifest.append(dict(path=rel,sha256=sha(p),bytes=p.stat().st_size))
 dump(O/'archive-manifest.json',manifest)
 owned=[str(p.relative_to(R)).replace('\\','/')for p in own_tools]
 (O/'owned-files.txt').write_text('\n'.join(owned+[str(O.relative_to(R)).replace('\\','/')+'/'])+'\n',encoding='utf-8')
 for p in [O/'source-and-controls.zip',O/'archive-manifest.json',O/'owned-files.txt',O/'negative-clarifications.json',O/'README.md']:bindings[str(p.resolve())]=sha(p)
 q=dict(passed=True,source_only=True,native=False,installed=False,Thomas_pending=True,host_sha256='a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c',
  component_sha256=sha(R/'build/thomas-host-boundary-1031-v2/component.bin'),code_bytes=5105,scratch=list(range(3,11)),
  controls=dict(original_cold=640,original_accepted_frames=2336,real_vectors_corrected_scratch=792,accepted_boundary_pairs=344,body_anchor_pairs=344,native_query_allflags=1344,earned_native_enemy_defeat=1,original_health_allflags=1024,native_powerup_pairs=32,additional_real_vectors=147,source_pose_pixels=161280),
  measured_CHR_pages=12,granted_CHR_pages=16,resident_granted_bytes=1478,resident_loader_emitted_bytes=0,
  stages={str(p):sha(p)for p in stages},receipts={str(p):sha(p)for p in receipts},archive_members=len(manifest),bindings=bindings)
 dump(O/'handoff.json',q)
 # Independent final reread of every source binding and every archive member.
 for p,h in q['bindings'].items():assert sha(p)==h,p
 with zipfile.ZipFile(O/'source-and-controls.zip')as z:
  for m in manifest:assert hashlib.sha256(z.read(m['path'])).hexdigest()==m['sha256']
 print(json.dumps(dict(result='FROZEN',handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),archive_members=len(manifest),zip_bytes=(O/'source-and-controls.zip').stat().st_size)))
if __name__=='__main__':main()
