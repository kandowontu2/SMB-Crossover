"""Compact immutable files-only P1 experiment checkpoint. Never stage/commit."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-source-experiment-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 assert not O.exists();O.mkdir()
 dirs=['contra-force-p1-kernel-v1','contra-force-p1-cart-v1','contra-force-p1-cart-v2','contra-force-p1-native-first-controls-v1','contra-force-p1-native-first-controls-v2','contra-force-p1-native-first-controls-v3','contra-force-p1-stale-palette-ppu-v1','contra-force-p1-stale-palette-ppu-v2','contra-force-p1-group-ppu-controls-v1','contra-force-p1-group-ppu-controls-v2','contra-force-p1-native-restore-proposal-v1','contra-force-p1-native-restore-proposal-v2','contra-force-p1-restore-arena-v1','contra-force-p1-restore-arena-v2','contra-force-p1-restore-arena-controls-v1','contra-force-p1-restore-arena-controls-v2','contra-force-p1-restore-arena-controls-v3','contra-force-p1-restore-arena-api-vectors-v1','contra-force-p1-restore-arena-api-vectors-v2','contra-force-p1-restore-vector-diagnostic-v1','contra-force-p1-restore-vector-diagnostic-v2','contra-force-p1-coherent-join-plan-v1','contra-force-p1-join-plan-v2']
 allowed={'.py','.s','.inc','.cfg','.json','.md','.txt','.diff','.dep','.lst'};files=set()
 for name in dirs:
  d=R/'build'/name;assert d.is_dir(),d
  files.update(p for p in d.iterdir()if p.is_file()and p.suffix.lower()in allowed)
  if(d/'joint').is_dir():files.update(p for p in(d/'joint').iterdir()if p.is_file()and p.suffix.lower()in allowed)
 tools=sorted({p for pat in['contra_force_p1_*.py','prepare_contra_force_p1_*.py']for p in(R/'tools/audit').glob(pat)}|{Path(__file__)})
 refs=sorted(set((R/'tools/reference').glob('contra_force_p1_*.s'))|{R/'tools/reference'/n for n in['contra_force_host_runtime_v10.s','contra_force_host_render_v5.s','contra_force_host_palette_names_v3.s','contra_force_a2_router_v7.s']});files.update(tools+refs)
 stage=R/'build/contra-force-p1-cart-v2/source-stage.json';sd=json.loads(stage.read_text())
 for p,h in sd['bindings'].items():assert sha(p)==h,p
 names=['contra-force-p1-native-first-controls-v3','contra-force-p1-stale-palette-ppu-v2','contra-force-p1-group-ppu-controls-v2','contra-force-p1-restore-arena-controls-v3','contra-force-p1-restore-arena-api-vectors-v1','contra-force-p1-restore-arena-api-vectors-v2']
 scope=dict(status='FROZEN_PRIVATE_SOURCE_RESEARCH_FINITE_POSITIVES_AND_RETAINED_NEGATIVES',native=False,ready=False,admitted=False,installed=False,private_cart=sd['candidate'],restore67_linked_in_cartridge=False,current_installed68='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9',controls={n:sha(R/'build'/n/'controls.json')for n in names},
  positives=['123unique authenticated shot frames/246realDraw+normalNMI: exact finalCHR/palette/opaque/priority/wholegroups with realOAMrotation and worldP2P3 preserved','Corrected67Bsourcev2 in synthetic real-SFC arena: six valid finalAXYP/SMC/sourceRAM/OAM pairs and16stale-cookie nativePPU restores/no-guest; NOT cartridge placement','320allflag/marker API executions before later vector-oracle failures; AXYP/SMC/sourceRAM scope only'],
  retained_negatives=['0b16 C1 then poison: nativeDrawonce/no guest but staleCFyellow survives realnormalNMI','Nativefirstv1 forcedP3Goomba fixture; v2 safeC0 overassertion; v3 genuineC1failure','PPUv1 nonexistentBus.palette; v2 actualVRAM stale failure','Groupv1 assumedlinearOAM; v2 realphysicalrotation passes','Restorev1 macroprecedence emittedC2 forB020+18 and BRKdC234; UNADOPTABLE. Correctv2sourcea75','Validstatev2 overasserted inactive lowerstack; v3 liveupperpage1/33SMC/sourceRAM valid','Vectorv1 ignored actualnativeaudio/IRQ effects; v2 still READS emulated2007 in global snapshot. NO vector/fullPPU pass; rawRAMsnapshot successor required','Diagnosticv1 duplicatekind TypeError; v2 actualnativeISR effect attribution only','Planv1 nonzero Rogue __M3_GFX_SIZE__ consumer; v2 preserves13FD via linker expressions. Main already256segments: distinctsuffix not yet feasible; rootRODATAreuse audit pending','Proposed93AFA7 interval conflicts liveHOST_BBOX_LOCAL79B; withdrawn/noadoption'],
  hardware=dict(normal_limit=8,maximum_demand=12,crowded_finite_cases=192,total_finite_cases=246,all_hardware_visible_pixels_claimed=False),
  next='Root/transport owner compose current68+qualifiede54+finalCFBTcommon and source-owned67B A91AE97..AEDA, preserve allactualPCs/metadata/remaining331B, then actualmerged queue/lifecycle/ISR/PPU controls before native/readiness.')
 put(O/'scope-and-negatives.json',scope)
 (O/'README.md').write_text("""# Contra Force P1 private source experiment

This packet preserves finite source results and all meaningful failed states. Private0b16 is NOT ready: rejecting a damaged cache after a spell epoch leaves stale yellow P1 on visible native objects. Corrected67B ROM restore source passes an isolated genuine-SFC CPU arena; it has NOT been linked into a cartridge or run natively.

The123-frame/246-Draw test checks authenticated atlas patterns, NES colors, opaque pixels, priority, complete groups, final hardware CHR and real OAM rotation. It does not prove hardware shows every pixel:192 finite scenes demand over8sprites/line, max12.

Vector research is a retained negative. Whole-global snapshots READ emulated I/O and cannot establish a PPU/vector pass. AXYP/SMC/sourceRAM allflag subsets remain separately valid. A raw-RAM/event-observer successor is required.

Join-planv2 preserves the real Rogue audio assertion's complete13FD graphics footprint. Main already has256segment categories: its distinct suffix is NOT adoptable until root's existing-empty-category reuse audit completes. The67B interval requires genuine qualified M3 factoring. Oldlive tables and the withdrawn liveBBox interval are untouched.

source-only.zip contains text source, recipes, finite controls and retained negatives. NES,objects,executables,largeDBG,compiledcarrier/cookie assets and wholeparentZIPs are excluded. Actual source/prerequisite closure remains pinned by the complete private source-stage; its6989+ priorbindings are rehashed by this freeze tool. No staging,commit,install,native launch or allocation occurs here.
""")
 files.update([O/'scope-and-negatives.json',O/'README.md']);members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)};put(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for rel in members:z.write(R/rel,rel)
 with zipfile.ZipFile(O/'source-only.zip')as z:
  assert set(z.namelist())==set(members)
  for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 external=[stage,R/'build/contra-force-p1-cart-v2/joint/candidate.nes',R/'build/contra-force-p1-cart-v2/joint/candidate.dbg',R/'build/contra-force-p1-cart-v2/joint/cf-stream.bin',R/'build/contra-force-p1-cart-v2/joint/cf-cookie.bin',R/'build/contra-force-p1-restore-arena-v2/worker.bin']
 hand=dict(**scope,archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,prior_stage_bindings_verified=len(sd['bindings']),bindings={str(p.resolve()):sha(p)for p in sorted(files)|set(external)if False})if False else dict(**scope,archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,prior_stage_bindings_verified=len(sd['bindings']),bindings={str(p.resolve()):sha(p)for p in sorted(files|set(external)|{O/'source-only.zip',O/'source-members.json'})})
 put(O/'handoff.json',hand)
 owned=[*tools,*refs,*[O/n for n in['handoff.json','README.md','scope-and-negatives.json','source-only.zip','source-members.json','owned-files.json']]]
 put(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in owned],do_not_stage_or_commit_by_agent=True,immutable_after_creation=True))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),members=len(members),bytes=(O/'source-only.zip').stat().st_size,owned=str(O/'owned-files.json'),owned_sha256=sha(O/'owned-files.json'))),flush=True)
if __name__=='__main__':main()
