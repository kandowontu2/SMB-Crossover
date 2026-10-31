"""Freeze the incremental, private natural Thomas source/CPU milestone."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-31/thomas-natural-host-source-v3'
J=R/'build/thomas-natural-host-1031-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();O.mkdir(parents=True)
 stages=[R/f'build/{n}/source-stage.json'for n in ['thomas-physical-host-1031-v9','thomas-private-ingress-1031-v5','thomas-natural-host-1031-v6']]
 receipts=[R/f'build/{n}/controls.json'for n in ['thomas-physical-controls-1031-v5','thomas-physical-vectors-1031-v2','thomas-ingress-endpoints-1031-v5','thomas-natural-cold-controls-1031-v4','thomas-natural-foreign-1031-v2','thomas-natural-vectors-1031-v1','thomas-natural-original-controls-1031-v1','thomas-natural-render-controls-1031-v1','thomas-linked-closure-1031-v3']]
 bindings={};source=set(stages+receipts);tools=set()
 for path in stages+receipts:
  data=json.loads(path.read_text());assert data.get('passed')is True,path
  for key,h in data['bindings'].items():
   p=Path(key).resolve();assert sha(p)==h,(path,p,'binding drift')
   if str(p)in bindings:assert bindings[str(p)]==h
   bindings[str(p)]=h
   if p.suffix in['.s','.inc','.py','.json','.cfg','.mac']:source.add(p)
 for prefix in ['prepare_thomas_physical_host_1031_v','prepare_thomas_private_ingress_1031_v','prepare_thomas_natural_host_1031_v','check_thomas_physical_host_1031_v','check_thomas_physical_vectors_1031_v','check_thomas_ingress_endpoints_1031_v','check_thomas_natural_','check_thomas_linked_closure_1031_v','diagnose_thomas_natural_walk_1031_v']:
  tools.update((R/'tools/audit').glob(prefix+'*.py'))
 tools.update([Path(__file__)])
 for pattern in ['thomas_resident_1031_v*.s','thomas_cache_host_1031_v*.s','thomas_hot_render_1031_v*.s']:
  tools.update((R/'tools/reference').glob(pattern))
 source.update(tools)
 # Include exact current Main and own assembler textual dependency closure.
 # ca65 escapes spaces but retains ordinary Windows path backslashes.
 depfiles=[]
 for directory in [R/'build/thomas-physical-host-1031-v9',R/'build/thomas-private-ingress-1031-v5',J]:
  for dep in directory.glob('*.dep'):
   depfiles.append(dep);line=dep.read_text().splitlines()[0]
   if ':\t'not in line:continue
   for value in re.split(r'(?<!\\)\s+',line.split(':\t',1)[1].strip()):
    p=Path(value.replace('\\ ',' '))
    if not p.is_absolute():p=(directory/'source' if directory.name=='thomas-physical-host-1031-v9' else R)/p
    p=p.resolve();assert p.is_file(),(dep,p)
    if p.suffix.lower()not in['.nes','.exe','.o']:source.add(p)
  source.update(p for p in directory.rglob('*')if p.is_file()and p.suffix.lower()in['.s','.inc','.cfg','.json','.bin','.chr','.dep'])
 # Retain finite diagnostic/source/fixture failures exactly; they are not PASS.
 negatives=[]
 for pattern in ['thomas-natural-cold-controls-1031-v*','thomas-natural-foreign-1031-v*','thomas-linked-closure-1031-v*','thomas-natural-walk-diagnostic-1031-v*']:
  for directory in (R/'build').glob(pattern):
   for p in directory.glob('*.json'):
    source.add(p)
    data=json.loads(p.read_text())
    if isinstance(data,dict)and(data.get('passed')is False or 'diagnostic'in directory.name):negatives.append(str(p.relative_to(R)).replace('\\','/'))
 grants=[R/'docs/qa/checkpoints/2026-10-31/thomas-first-host-resource-v1/resource-contract.json',R/'docs/qa/checkpoints/2026-10-31/thomas-host-scratch-boundary-source-v1/handoff.json',R/'build/future-start-masks-1031-v1/source-stage.json']
 source.update(grants)
 integration=dict(source_cart=str(J/'candidate.nes'),ROM_sha256=sha(J/'candidate.nes'),baseline='a126, not root later a441/campaign/frontend source',
  actual_Main_recipe=str(J/'main-build.json'),actual_link_recipe=str(J/'final-link.json'),actual_config=str(J/'candidate.cfg'),
  genuine_own_objects=['component.o','dependencies.o','boundary.o','banks.o','metadata.o','cache.o','resident.o','tables.o','carrier.o'],
  shared_rebuilt_objects=['main.o','union.o','bt-api.o','bt-loader.o','bt-stream.o','mirror.o','dmc-clones.o'],
  funding=['X5OwnMovement49B','HotPlayerGraphics226B','HotNewCharacterDraw226B','KbDrawDispatch50B','RyuSourceBodyAfterBGBridge49B operand only','Nr97B public capsules preserve entries; two equal 5B bank tables shared with linker assertions','Named internal Hu suffix helpers source-rebound; A79 exactly2592/2592','Root405 helper copied byteexact; no Thomas menu filler or ZP allocation'],
  public_ABI='All36 public16B Hu rows, B020 service ABI, Nr public starts, named Hot/Kb/X5/Ryu/loader PCs retained. Internal Hu helpers in moved-symbols.json deliberately moved and actual imported objects/carrier rebuilt.',
  selected='SelectedCharacter10 and(FmAlts&44hex)==40hex; Ryu/Shinobi/illegal44 retain old routes',
  current_scratch=list(range(3,11)),state='SelectedC2 source000..817 plus host818..84D and metadataD000; all below grant, no globals',
  resident=dict(bank=85,start='B33A A alias /D33A C load',end='B8DC',used=1442,grant=1478),
  CHR=dict(grant=[426,442],code=[426,432],metadata=[432,434],body=[434,439],unused_retained=[439,442]),
  constructors='Actual MenuResolve ThRetireÃ¢â€ â€™BwMenuResolve; actual InitScreen BwSceneÃ¢â€ â€™S2/Qw/Ar/Fw/nativeMove once then forcedblank ThLoad. Typed Fresh15 retains actual BmFresh/native/Ic/Qw chain then invalidates own cache. ThEnsure publishes context last on first genuine actor entry.',
  original_projection='Original constructor/movement/jump/melee instruction bodies retained. Clear six omitted donor enemy active slots87..8C after constructor, preserve original player8D; native SMB actors own world contacts.',
  terrain='Single original B6 integrator (27px jump); unsupported fall uses genuine native MovePlayerVertically once; real PlayerBGCollision once; sole post-BG reconciles actual support and ceiling stop through original jump-reset.',
  host_join_requirements=['Do not replace later root405/campaign menu or a441 CF changes with old main.o. Graft source and rebuild actual current Main.','Regenerate genuine current typed union target groups and actual imports against moved Hu exports, including cached BT world operand/cookie/stream.','Regenerate119/120/125 from same final127 and declared donor DMC/manager producers.','Root native cold select/lives/first-game visual/palette/raster/controls qualification required before any install/count increase.'])
 dump(O/'integration-api.json',integration);source.add(O/'integration-api.json')
 dump(O/'negative-clarifications.json',dict(
  original_frozen_lab='Literal00..07 predecessor remains lab-only; current source imports trueR0..7=03..0A and uses genuine host vectors.',
  native_renderer='v1/v2 source retained: wrong native descriptor order, viewport high byte and missing completedNMI were diagnosed before current42pose PASS.',
  stale_union='Earlier private ingressv3 compiled a new union but retained old link input; caught before qualification, fixed actualproducer in v4/v5.',
  stale_BT_import='Earlier v4 failed cached HuWorld closure; v5 rebuilds actualBTapi/loader/stream/cookie. No postlink patch.',
  blocked_walk='Naturalv4 original boss slot8C active with omitted enemy-distance producer blockedwalking. Clearing only omitted actor flags in v6 is explicit hostprojection, not a physics rewrite.',
  wrong_P2_fixture='Coldcontrols v3 put keys only in player1 input for CurrentPlayer1. v4 follows real controller2 path.',
  Arthur_fixture='Foreignv1 inherited FF-only ISR immutablepayload assertion rejected authenticArthurRAM2clock. v2 preserves and comparesactualNMIwrites parent/child.',
  closure_fixture='Linkedclosurev1 guessed farcall operand+6 instead of emitted+4; v2 interpreted an SBC immediate20 as JSR. v3 uses actualca65instruction spans and preservednumericdata coincidences.',
  retained_paths=negatives));source.add(O/'negative-clarifications.json')
 (O/'README.md').write_text('''# Thomas natural source/CPU milestone

Private source cart3fe86832, derived from exacta126. No native run, install,
Git/index or Downloads operation. Private Thomas ready branch is a reviewed
source-proof gate, not an installed playable-count increase.

Real menuÃ¢â€ â€™Start405Ã¢â€ â€™native parser/forcedblank loaderÃ¢â€ â€™100 foreground GameLoops
passes for each player. All200 Main calls consume one original accepted actor
frame, native terrain pass, post-contact reconciliation and native source body.
534 actual normalNMIs complete. Additional238 real IRQ/lagNMI cuts preserve
all33SMC, actual03..0A scratch/maps/page1 and resumed source state/nativeOAM.
Original donor actor oracle matches480 frames under explicit omitted-enemy
projection; all42 poses match source indices/foot anchor/nativephysicalCHR/P0.

Five foreign cold/parser scenes and60 completeMain pairs preserve gameplay,
completedPPU and authenticownerNMI state through1790 normalNMIs. Actual Main
cost changes in this finite controller: Mario+98, Bill+171, Ryu+1114,
Arthur+1124, Rash+67CPU. These costs are disclosed, not a cadence claim.
3072 HotRender targets/flag cases and90048 Nr/Only/typed foreign endpoints
pass. Actual final imported objects and cachedBTworldoperand/cookie/stream
are rebound; other foreign cached images stay exact. All119/120/125 mirror
source consumes the same final127.

Outstanding: root latera441/campaign/current shared-source composition;
native menu/lives/gameplay pixel/palette/firstflush/raster proof; full1-1,
fall/ceiling under played obstacles, pipes/water/vine/death/continue and
original KungFu audio ownership. Original source queue fields are retained,
but the original audio driver has not been acquired. Original27px jump is
unchanged; this milestone does not claim every SMB obstacle is traversable.

Archive is incremental source, templates/assets, actual recipes/dependencies,
controls and retained negatives. It contains noNES/object/executable/DBG.
The pinned source/ROM/DBG/objects from the parent remain external inputs.
''',encoding='utf-8');source.add(O/'README.md')
 owned=sorted(str(p.relative_to(R)).replace('\\','/')for p in tools)
 owned+=[str(p.relative_to(R)).replace('\\','/')+'/'for p in[R/'build/thomas-physical-host-1031-v9',R/'build/thomas-private-ingress-1031-v5',J,O]]
 (O/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8');source.add(O/'owned-files.txt')
 manifest=[];external=[]
 with zipfile.ZipFile(O/'source-and-controls.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(source):
   p=p.resolve();assert p.is_file()
   if not p.is_relative_to(R):external.append(dict(path=str(p),sha256=sha(p)));continue
   assert p.suffix.lower()not in['.nes','.exe','.o','.dbg','.zip']
   rel=p.relative_to(R).as_posix();z.write(p,rel);manifest.append(dict(path=rel,sha256=sha(p),bytes=p.stat().st_size))
   bindings[str(p)]=sha(p)
 dump(O/'archive-manifest.json',manifest)
 for p in[O/'source-and-controls.zip',O/'archive-manifest.json']:bindings[str(p)]=sha(p)
 q=dict(passed=True,status='PRIVATE_NATURAL_SOURCE_CPU_PROOF',native=False,installed=False,Thomas_installed_pending=True,private_ready_gate=True,ROM_sha256=sha(J/'candidate.nes'),source_stage_sha256=sha(J/'source-stage.json'),
  code_bytes=5855,resident_bytes=1442,resident_granted=1478,CHR_pages_used=13,CHR_pages_granted=16,scratch=list(range(3,11)),
  controls=dict(actual_Main=200,actual_normalNMI_natural=534,foreign_wholeMain=60,foreign_actual_normalNMI=1790,real_active_IRQ_lagNMI=238,original_actor_pairs=480,original42pose_native_pixels=42,fullflags_cookie_poison=2048,foreign_endpoint_pairs=90048,Thomas_true_rows=4288,Hot_allraw_flags=3072),
  archive_members=len(manifest),external_sources=external,stages={str(p):sha(p)for p in stages},receipts={str(p):sha(p)for p in receipts},bindings=bindings)
 dump(O/'handoff.json',q)
 for p,h in bindings.items():assert sha(p)==h,p
 with zipfile.ZipFile(O/'source-and-controls.zip')as z:
  for m in manifest:assert hashlib.sha256(z.read(m['path'])).hexdigest()==m['sha256']
 print(json.dumps(dict(result='FROZEN',handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),archive_members=len(manifest),ZIP_bytes=(O/'source-and-controls.zip').stat().st_size)))
if __name__=='__main__':main()
