"""Compact genuine rebuild/freeze of the private GB-Pit alternate; never install."""
from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from sunny_integrated_controls_v1 import sha
O=R/'build/pit-retold-host-v2';P=R/'build/kamikaze-mario-host-v4'

def verify(rows):
 for p,h in rows.items():assert sha(Path(p))==h,p

def deps(path):
 out={}
 for word in re.split(r'(?<!\\)\s+',path.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve()
  assert p.is_file(),p;out[str(p)]=sha(p)
 return out

def run(command):
 z=subprocess.run(command,cwd=R,capture_output=True,text=True)
 assert not z.returncode,(command,z.stdout[-2000:],z.stderr[-2000:])

def build():
 assert not(O/'closure.json').exists()
 source=json.loads((O/'build-proof.json').read_text());verify(source['actual_dependencies'])
 parent=json.loads((P/'source-closure.json').read_text());verify(parent['actual_dependencies'])
 before={str(p):sha(p)for p in[O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl']}
 commands=[];actual={}
 for name,command in zip(['main','skin','gb'],source['commands'][:3]):
  command=command[:]
  command[command.index('-o')+1]=str(O/(name+'-independent.o'))
  command[command.index('--create-full-dep')+1]=str(O/(name+'-independent.d'))
  run(command);commands.append(command);actual.update(deps(O/(name+'-independent.d')))
 assert actual==source['actual_dependencies']
 link=source['commands'][-1][:]
 for i,value in enumerate(link):
  for name in['main','skin','gb']:value=value.replace(str(O/(name+'.o')),str(O/(name+'-independent.o')))
  for ext in['nes','lbl','dbg']:value=value.replace(str(O/('candidate.'+ext)),str(O/('independent.'+ext)))
  link[i]=value
 run(link);commands.append(link)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'independent.nes')
 assert sha(O/'independent.nes')==source['candidate']
 # Only five sparse source leaves, not a source/runtime tree clone.
 shutil.copyfile(O/'entrypoint.s',O/'src/entrypoint.s')
 ordinary={}
 for mode in['mmc3','mmc5']:
  out=O/('ordinary-'+mode+'.nes')
  command=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(O),'--flag-off',mode,'--output',str(out)]
  run(command);commands.append(command)
  expected=json.loads((P/('ordinary-'+mode+'.build.json')).read_text())['sha256']
  assert sha(out)==expected
  ordinary[mode]=dict(sha256=expected,exact_parent=True,bytes=out.stat().st_size)
 verify(before);verify(actual)
 files=[Path(__file__),R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',Path(sys.executable),P/'c-full.o',O/'src/entrypoint.s',R/'smb1base.cfg',R/'build_options.ini',O/'independent.nes',O/'independent.lbl',O/'independent.dbg']
 for command in commands:
  files.append(Path(command[0]))
 for mode in['mmc3','mmc5']:
  files.extend([O/('ordinary-'+mode+suffix)for suffix in['.nes','.lbl','.dbg','.map','.build.json','.build.log']])
 out=dict(passed=True,native_run=False,source_CPU_only=True,independent_fresh_assembly_and_link_exact=True,actual_dependencies=actual,commands=commands,ordinary=ordinary,bindings={str(p.resolve()):sha(p)for p in files})
 (O/'closure.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ASM_dependencies=len(actual),independent=sha(O/'independent.nes'),ordinary=ordinary)))

def freeze():
 assert not(O/'handoff.json').exists()
 controls=[];all_bindings={}
 for name in['build-proof.json','closure.json','controls-core-frozen.json','controls-gameplay-frozen.json']:
  path=O/name;data=json.loads(path.read_text())
  assert data.get('passed',data.get('assembled')),name
  for key in['actual_dependencies','actual_imports','bindings']:
   verify(data.get(key,{}));all_bindings.update(data.get(key,{}))
  controls.append(data)
  all_bindings[str(path.resolve())]=sha(path)
 for before,after,label in[(R/'src/expanded.s',O/'src/expanded.s','src/expanded.s'),(P/'overlay/src/character_select.s',O/'src/character_select.s','src/character_select.s'),(P/'overlay/src/entrypoint.s',O/'entrypoint.s','src/entrypoint.s'),(P/'overlay/smb1base-mmc5-expanded.cfg',O/'smb1base-mmc5-expanded.cfg','smb1base-mmc5-expanded.cfg')]:
  patch=''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='parent/'+label,tofile='private/'+label))
  with (O/'source-complete.patch').open('a')as f:f.write(patch)
  all_bindings[str(before.resolve())]=sha(before);all_bindings[str(after.resolve())]=sha(after)
 core=controls[2]['checks'];game=controls[3]['checks'];rows=game['actual_Main_normalNMI_gameplay_preservation']['rows']
 report=R/'docs/qa/pit-retold-host-source-2026-10-29.txt'
 summary=dict(source_CPU_only=True,native_run=False,candidate=controls[0]['candidate'],parent=controls[0]['parent'],PRG_changed_bytes_by_physical_bank=controls[0]['changes'],CHR_pages=[808,812],CHR_bytes=5120,render_end=controls[0]['render_end'],menu_end=controls[0]['menu_end'],normal_pose_CPU_delta=core['normal_Pit_all252_full_pose']['CPU_delta'],alternate_full_DrawAll_CPU=core['alternate_all_poses_real_DrawAll_pixels']['DrawAll_CPU'],paired_complete_Main_CPU_delta=[min(r[5]for r in rows),max(r[5]for r in rows)],paired_normal_NMI_CPU_delta=[min(r[7]-r[6]for r in rows),max(r[7]-r[6]for r in rows)],source_controls=dict(old_Pit_pose_ABI=2016,alternate_actual_DrawAll_pixel_cases=2016,foreign_complete_Main=88,helper_IRQ_lagNMI_seams=790,paired_Main_normalNMI_updates=192,normal_Pit_Main=24,lives_portraits=12,palette_backdrop_callers=16),basis='Retold-patch-plus-authentic-local-base art adaptation; no author GoodNES full-ROM match.',limitations=['No native Mesen/cold-menu/lives/gameplay/PPU timing or actual visual qualification yet.','Existing Pit physics/gear/audio/palettes and old host animation aliases/composites retained; no invented wing or animation.','Five copied record pairs repair source crouch top-row placement; all original252 records/CHR remain untouched.','Normal Pit full pose adds8CPU. Alternate timing is source benchmark only, not native FPS.','Typed CPU arenas include legal tiers/maps/menu state; no naturally earned source gameplay or complete route claim.','Alternate P/Y pushes change consumed dead stack cells, explicitly recorded; live return and interrupted frames are checked.'])
 lines=['Private GB-style Pit Select alternate — source handoff, 2026-10-29','',json.dumps(summary,indent=2),'','Integration: five sparse private leaves are src/expanded.s, src/character_select.s, entrypoint.s, smb1base-mmc5-expanded.cfg and component.s; link separate component object with pit-retold.chr. Apply source-complete.patch to exact737d parent, not unrelated current preimages. Preserve genuine Kamikaze KmQueueName chain. No shared source installed.','', 'PitVariant=$5FE0: actual compiled old consumers are menu16-byte clear/save/restore only. New cold Select hook toggles owner6 0/1; other identities fall through unchanged. Variant1 appends only new approved31:DDE6 and66:B600 tails and body window0 direct physical808..812. Final ends DF69/B67C.','', 'Native retained body metadata: HpNativeDrawLo/Hi[0] contain actual selected SmPosePtr; all192 reached native DrawMetasprite body consumers are checked. R0/R1 differing final bytes independently retain their matching body-pointer byte; later equal native R0-only work is not masked. All six actor descriptor slots remain exactly compared.','', 'Preserved negatives: layout-v1 pure-CHR conflicts; first Y+1 scanout oracle; V1 redundant-write oracle; real V1 d0c stale CHR alias cache bug; V2 overstrict original-pointer equality and whole-final-pointer oracle. Frozen original tool preimages accompany each receipt. V2 changes only cache alias ordering; subsequent fixes were oracle-only.','', 'Provenance: build/pit-retold-assets-v1/handoff.json and docs/qa/pit-retold-art-basis-2026-10-29.txt bind the patch literals, 8 corroborated untouched original bytes, real native OAM direction/anchor data and limitations. No patched full source ROM produced.','', 'Native prerequisite: root reviews immutable handoff and cold Select/lives/gameplay on this exact ROM/DBG/LBL. Existing standard sprite limit and outline option remain unchanged.']
 report.write_text('\n'.join(lines)+'\n')
 extra=[Path(__file__),report,O/'source-complete.patch',O/'component.s',O/'pit-retold.chr',O/'pose-layout.json',O/'source-pose-sheet.png',R/'tools/prepare_pit_retold_host_v1.py',R/'tools/prepare_pit_retold_host_v2.py',R/'tools/audit/pit_retold_host_controls_v1.py',R/'tools/audit/pit_retold_host_controls_v2.py',R/'tools/audit/pit_retold_host_gameplay_v1.py',R/'build/pit-retold-assets-v1/handoff.json',R/'docs/qa/pit-retold-art-basis-2026-10-29.txt',R/'build/pit_retold_layout_plan_v2.json',R/'tools/audit/pit_retold_layout_plan_v2.py']
 for directory in[R/'build/pit-retold-host-v1',O]:
  for pattern in['controls*.json','gameplay*.json','*negative-tool.py','*first-tool.py','*first-dispatcher.py']:
   extra+=list(directory.glob(pattern))
 for p in extra:all_bindings[str(p.resolve())]=sha(p)
 verify(all_bindings)
 handoff=dict(passed=True,native_run=False,summary=summary,bindings=all_bindings,source_closure=sha(O/'closure.json'),actual_ASM_dependencies=len(controls[0]['actual_dependencies']),owned_publication_files=[str(p.relative_to(R)).replace('\\','/')for p in[Path(__file__),report,R/'tools/prepare_pit_retold_host_v1.py',R/'tools/prepare_pit_retold_host_v2.py',R/'tools/audit/pit_retold_host_controls_v1.py',R/'tools/audit/pit_retold_host_controls_v2.py',R/'tools/audit/pit_retold_host_gameplay_v1.py']],immutable_ROM_DBG_LBL={str(O/('candidate.'+e)):sha(O/('candidate.'+e))for e in['nes','dbg','lbl']})
 (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n')
 print(json.dumps(dict(passed=True,handoff=sha(O/'handoff.json'),bindings=len(all_bindings),summary=summary)))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['build','freeze'],required=True);a=ap.parse_args()
 (build if a.phase=='build'else freeze)()
