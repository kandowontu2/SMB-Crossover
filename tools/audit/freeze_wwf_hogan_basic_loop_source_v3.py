"""Freeze private first-Hogan source proof; root owns composition/native/install."""
from pathlib import Path
import difflib,hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2]
from freeze_wwf_native_proxy_lab_v1 import local_imports
from check_tmnt_render_oa import load,address,location
J=R/'build/wwf-hogan-natural-source-v15/joint';P=R/'build/contra-force-world-roles-1031-v2/joint'
O=R/'build/wwf-hogan-basic-loop-qualified-v3';D=R/'docs/qa/checkpoints/2026-10-31/wwf-hogan-basic-loop-source-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
 assert not O.exists()and not D.exists();O.mkdir();D.mkdir(parents=True)
 stage=J.parent/'source-stage.json';s=json.loads(stage.read_text())
 assert s['source']and s['candidate']==sha(J/'candidate.nes')=='99b9026588e772e93cdc95e845ab3617ff4376260ad0a111b68c3d92925cbd27'
 names=['wwf-hogan-owner-rebind-v1','wwf-hogan-natural-controls-v9','wwf-hogan-menu-source-controls-v5','wwf-hogan-typed-api-controls-v5','wwf-hogan-pose-contact-controls-v5','wwf-hogan-palette-closure-v6','wwf-hogan-live-vectors-v6','wwf-hogan-whole-main-stack-probe-v3','wwf-hogan-foreign-scene-controls-v1','wwf-hogan-foreign-draw-controls-v5','wwf-hogan-valid-cf-palette-rebind-v3']
 tests=[R/'build'/n/'controls.json'for n in names];reports=[json.loads(p.read_text())for p in tests]
 assert all(q['passed']and q['candidate']==s['candidate']for q in reports)
 external=set()
 for q in[s,*reports]:
  for p,h in q['bindings'].items():assert sha(p)==h,p;external.add(Path(p).resolve())
 dependency_files=set()
 for p in[J/'host-main/main.dep',J/'union.dep',J/'bt-router.dep']:
  line=p.read_text().splitlines()[0].split('\t',1)[1]
  dependency_files|={Path(n.replace('\\ ',' ')).resolve()for n in re.split(r'(?<!\\)\s+',line.strip())}
 assert all(p.is_file()for p in dependency_files);external|=dependency_files
 b=load(J/'candidate.nes');old=load(P/'candidate.nes')
 # Exact physical closure was asserted by the guarded true-source builder.
 assert b['raw'][:16]==old['raw'][:16]
 segments=[]
 for line in(J/'candidate.dbg').read_text().splitlines():
  if not(line.startswith('seg\t')and'name="WF_'in line):continue
  n=re.search(r'name="([^"]+)"',line)[1];a=int(re.search(r'start=(0x[0-9a-fA-F]+)',line)[1],16);z=int(re.search(r'size=(0x[0-9a-fA-F]+)',line)[1],16)
  segments.append(dict(name=n,start=a,end=a+z,bytes=z))
 sg={x['name']:x for x in segments};assert sg['WF_DETACHED_STATE']['start']==0xdfc1 and sg['WF_DETACHED_STATE']['end']==0xdfd6
 assert sg['WF_PALETTE_STATE']['start']==0xde98 and sg['WF_PALETTE_STATE']['end']==0xdebc
 resident=sum(sg[n]['bytes']for n in['WF_ROM_A','WF_RESIDENT_PROXY','WF_RUNTIME_A','WF_ROM_C'])
 c2=sum(x['bytes']for x in segments if 0xc000<=x['start']<0xe000 and x['name']not in['WF_ROM_C'])
 pages=[]
 for raw,n in[(1,'a1.bin'),(2,'c2.bin'),(3,'a3.bin')]:
  data=(J/n).read_bytes();assert len(data)==8192
  for i in range(8):
   v=data[i*1024:(i+1)*1024];pages.append(dict(raw_bank=raw,page=i,classification='zero'if v==bytes(1024)else'FF'if v==bytes([255])*1024 else'nonuniform',sha256=hashlib.sha256(v).hexdigest()))
 save(O/'physical-fit.json',dict(source=True,segments=segments,resident_emitted=resident,resident_granted=5834,A_resident_end=sg['WF_RUNTIME_A']['end'],A_limit=0xbd00,stable_C_copier=[sg['WF_ROM_C']['start'],sg['WF_ROM_C']['end']],C2_emitted_including_BSS_cookie=c2,C2_non_cookie_end=0xdfd6,C2_cookie=[0xdfe0,0xdff0],C2_remaining_before_cookie=10,A3_original_VM_scripts=7726,A3_cookie=16,template_pages=pages,A1='Inactive nonexecuting zero bank; original WWF audio is unbuilt.'))
 # Explicit final source integration inventory, never a wholesale old Main.
 parents={
  'host-main/entrypoint.s':R/'build/bt-p2-cf-menu-source-1031-v2/joint/entrypoint.s',
  'host-main/src/character_select.s':R/'build/contra-force-menu-admission-1031-v2/joint/src/character_select.s',
  'host-main/src/full_roster_menu.s':R/'build/contra-force-menu-admission-1031-v2/joint/src/full_roster_menu.s',
  'host-main/src/full_roster_menu_art.inc':R/'build/contra-force-menu-admission-1031-v2/joint/src/full_roster_menu_art.inc',
  'host-main/src/new_roster_dispatch.s':R/'build/bt-ready-menu-1031-v2/joint/src/new_roster_dispatch.s',
  'host-main/src/screen_render.s':R/'build/bt-p2-cf-menu-source-1031-v2/joint/src/screen_render.s',
  'union.s':R/'build/bt-ready-menu-1031-v2/joint/union.s',
  'bt-router.s':R/'build/bt-jmp-row-cold-source-v1/joint/bt/router.s',
  'ff-palette.s':R/'build/contra-force-p1-coherent-cart-v2/joint/ff-palette.s',
 }
 patches=[]
 for rel,parent in parents.items():
  patches+=difflib.unified_diff(parent.read_text().splitlines(True),(J/rel).read_text().splitlines(True),fromfile=parent.relative_to(R).as_posix(),tofile=(J/rel).relative_to(R).as_posix())
 (O/'source-hooks.patch').write_text(''.join(patches))
 mask=R/'build/future-start-masks-1031-v1/joint/src/cf_menu_body.inc';assert(J/'host-main/src/cf_menu_body.inc').read_text()==mask.read_text()
 hooks=[]
 for n,z in [('FwNativeDrawAll',59),('MenuResolveCharacter',34),('InitScreen',25),('GmOnlyCommon',address(old,'GmOnlyLegacy')-address(old,'GmOnlyCommon')),('BtRouter',114),('FmPending',248)]:
  a=location(old,n);v=location(b,n);assert a==v
  hooks.append(dict(symbol=n,PC=address(b,n),physical_file_offset=a,bytes=z,old=list(old['raw'][a:a+z]),new=list(b['raw'][v:v+z])))
 api=dict(source=True,native=False,installed=False,root_admission_pending=True,base_sha256=s['parent'],candidate=s['candidate'],joint=str(J),source_stage=str(stage),
  menu=dict(slot=28,raw=29,FmGroups_mask=7,original_wrestler_ID=5,Hogan_only=True,other_five_pending=True,private_ready_profiles=75,installed_parent_profiles=74,actual_profiles=86,root405_mask_source=str(mask)),
  entries={n:dict(PC=address(b,n),raw_ROM_bank=((location(b,n)-16)//8192)|128)for n in['WfLoad','WfCheck','WfConstructCold','WfRetire','WfScene','WfMenuRetire','WfResolve','WfMovement','WfGraphics','WfDrawBody','WfColdPortrait','WfColors','WfStatusName','WfP1LateDispatch','WfP1Retire','WfDetachRuntime']},
  selected_data={n:dict(C2_address=address(b,n),execution_raw_bank=2)for n in['WfState','WfHostReady','WfRenderBuffer','WfPaletteState','WfPaletteStateEnd','WfDetachedFrame','WfDetachedFrameEnd','WfOwnerCookie']},
  cookie=s['cookie'],true_recipes={n:str(J.parent/(n+'.json'))for n in['main-build','union-build','bt-router-build','shared59-build','final-link']},
  main='Actual current a126 Main is reassembled with only explicit funded hook hunks and genuine zero-byte exports. Do not replace later root a441/campaign/Main with this older entrypoint or object.',
  transport='Same public Hu/Nr/B020 PCs. Hu and Nr classify29; B020 gate accepts27/29/31/33 in its224B span. WfResolve accepts only selected29/group0 and returns genuine per-service ROM targets; every other owner delegates to genuine BwBtResolve. All36 public source callback paths/all64flags are compared with their genuine direct targets.',
  scene='Actual InitScreen farcall target WfScene; old Bw→S2→Qw→Ar→Fw/nativeMove chain once. Foreign Wf palette/cookie retirement occurs BEFORE entering that chain. Its sole genuine SFC-worker caller is proven before reusing the old worker frame; arbitrary direct WfScene calls are not an API. Own load/constructor reuse one existing save frame. Native19 directly calls JnResetDispatch once; own transient reset happens in authenticated forcedblank scene, retaining source health/clock.',
  retirement='MenuResolve34B calls WfMenuRetire BEFORE Selected publication, then genuine CfRetire and existing Bw/S2/Qw/Ar/Fw resolver chain. WfScene foreign path retires BEFORE inner foreign writes. WfLoad clears C2 first/raw3 second before overwrite, readbacks24KiB, publishes full valid-last. External direct overwrite APIs still have an explicit prior-owner retirement contract.',
  stack='Only five mutable SFC operands are saved on stack, plus8 scopedR0..7/AXYP/C/reload19bytes. Full33 image is checked at vectors. Authenticated active movement/graphics/draw temporarily detach that exact serial frame into own C2DFC1..<DFD6, then restore it exactly; no recursive detached entry is reachable and IRQ/NMI never dispatches selected29 foreground APIs. Old unpublished zero-consumer WfReset prototype is retired. Foreground source state/code/cookies outside these21 transport bytes remain exact in direct/typed comparisons.',
  controls='A→genuine native SMB jump/gravity/support; B→originalA punch; Down+B consumesDown→originalB kick; applicable directions retained; plainA does not punch. Original falling/gravity/hurt displacement and ring-depth state remain separate. Native platformer jump is an explicit adaptation, not original WWF jump fidelity.',
  contact='Real original authored punch damage lowers serial native-one-HP proxy200→198 and rechecked native identity/epoch invokes genuine ShellOrBlockDefeat once. Native SMB enemies retain their AI; source opponent AI runs only for actual proxy query. Snapshot/Commit cannot cross an external slot reuse without Notify; no uninstalled epoch hook is inferred. Incoming contact is explicit one-native-life WIP; authentic WWF endurance threshold integration remains unqualified.',
  palette='WWF owns only measured C2DE98..<DEBC state. Actual P0/P1 original roles are queued and whole own/native P1 groups alternate only on complete packets. Full queues hide competing groups and retry. Native-only FwMuxNativeSelect retirement clears Pending first, patches only complete queued own3F15 commands through bounded native command parsing, then publishes complete PRE-native restore last. CF remains genuine selected31-only and its state/carrier/cookie is unchanged.',
  limits=['No Mesen/native run, install, final root source composition or campaign qualification.','Original A1 music/SFX engine is unbuilt; only source cue class/value requests are recorded.','Other five wrestlers, advanced grapples/ring progression/endurance, all upgrades, two-player campaign and full1-1 remain unqualified.','This parent is exact a126. Root must surgically merge later a441/CF contact/CHR/campaign/menu changes; no whole old main/cfg overlay.'])
 save(O/'integration-api.json',api)
 save(O/'hook-bytes.json',dict(source=True,hooks=hooks,shared59=s['shared59'],native_public_PC_checks=s['all_stable_parent_interfaces_exact'],actual_main_dependency_files=len(dependency_files),root405_source_text_exact_normalized_line_endings=True))
 negative_names=['wwf-hogan-retirement-probe-v1','wwf-hogan-cold-stack-probe-v1','wwf-hogan-cold-stack-probe-v2','wwf-hogan-cold-stack-probe-v3','wwf-hogan-cold-stack-probe-v4','wwf-hogan-whole-main-stack-probe-v1','wwf-hogan-native-injury-probe-v1','wwf-hogan-palette-closure-v1','wwf-hogan-palette-closure-v2','wwf-hogan-palette-closure-v3','wwf-hogan-pose-contact-controls-v1','wwf-hogan-pose-contact-controls-v2','wwf-hogan-typed-api-controls-v4']
 negatives=[R/'build'/n/'controls.json'for n in negative_names]
 save(O/'verification-summary.json',dict(source=True,passed=True,native=False,candidate=s['candidate'],receipts={n:dict(path=str(p),sha256=sha(p))for n,p in zip(names,tests)},preserved_negatives={p.parent.name:dict(path=str(p),sha256=sha(p))for p in negatives},source_parser_Main=dict(full_native_parser_frames=167,controlled_Main_frames=180,standing_no_drift_frames=70,native_jump_apex_pixels=60,real_punch_native_defeats=1),menus=dict(profiles=86,prior74_exact=True,private_Hogan_only_ready=75,Start_masks_all64flags=2048),pose_face_cases=62,native_one_life_fullflag_cases=192,typed_native_callback_cases=2304,foreign_native_DrawAll_pairs=576,valid_CF_normalNMI_pairs=16,foreign_scene_pairs=97,actual_vectors=305,cold_minimum_ISR_SP=124,active_minimum_ISR_SP=130,active_nested_IRQ_SP=125,resident_bytes=resident,C2_bytes=c2))
 (O/'README.txt').write_text('''PRIVATE FIRST-HOGAN BASIC LOOP SOURCE PROOF — NOT INSTALLED OR NATIVE QUALIFIED

Exact candidate99b90265 on a126, in build/wwf-hogan-natural-source-v15/joint. One Hogan is privately ready; other five WWF profiles stay pending and all74 prior profiles remain unchanged. Root owns later source composition, emulator slot, admission, Downloads and Git. This delta must not overwrite later a441/CF/campaign changes.

Real menu/preview/Start/native full parser/entrance feeds180 controlled Main frames without code/Ready preload or parser-task shortcut.70 neutral frames remain stationary, Right moves, A uses genuine native SMB jump/gravity (60px in the18-held-frame sample), B runs original punch action15. A separate legal native-enemy ABI arena reaches the actual authored damage opcode200→198 and genuine native defeat once. Native enemies retain their own AI. No prerecorded trajectories, generic substitute punch or executable lab callback traps exist. Native incoming contact deliberately uses one native life as a labelled basic-WIP policy; source endurance is unfinished.

31original Hogan poses/2faces62cases preserve the actual native OAM geometry, bitplanes, physical pages, roles and opaque colour pixels. P0/P1 use original28/27/17 and16/05/0F. Whole native/own P1 groups alternate fairly; actual normal-NMI palette/CHR publication, full-queue retry, first-guest authentication and retirement-before-Selected publication pass. All WWF palette state is own selected C2; no CF workspace or generic CF request API is used.16real valid-CF paired group/normalNMI cases remain byte/state/colour exact.

The bound negative stale WWF queue could overwrite native PRE restore; final source cancels only complete exact own queued commands through a bounded native-format parser before valid-last PRE-native restoration. Actual source full queues/foreign new leases and18palette vector cuts pass. Earlier fixture errors (palette mirror model and failing to begin a new foreground after the genuine PauseRoutine end) remain separate preserved negatives.

Real deepest cold/active Main probes found stack collisions that direct API fixtures did not cover. Final source reuses one cold save frame, sends native19 straight to genuine JnReset once, performs own transient reset at authenticated scene, and detaches the exact19-byte active context into its own21-byte C2DFC1..<DFD6 data frame during serial movement/graphics/draw. All33 live transport bytes are still verified. Cold SP147/actual lagNMI124; active SP151/NMI130; deepest legally unmasked nestedIRQ125. Forcedblank cold NMI naturally masks nested IRQ. No interrupt-disable shortcut is introduced.

Foreign scenes retire before the old Bw/S2/Qw/Ar/Fw chain. After restoring the19-byte context, only the proven genuine current SFC-worker return is dropped; original saved oldA/caller frame is reused.97native-scene pairs and216actual normal/lag/pausedNMI/legalIRQ cuts preserve full native results/maps/33bytes. All36WWF source service paths×64flags2304pairs preserve genuine callback outputs and ordered application writes. The21transport bytes are verified exactly against each actual saved caller frame; prior SFC operands can legitimately differ between direct and typed call origins, so only that explicitly verified workspace is excluded from source-state equivalence. All other cache/code/cookie/native data remains exact.576native/CF-invalid/Samus complete DrawAll pairs preserve once-only callback order; ordinary route+2CPU, native-freeze extra156CPU, CF-invalid extra106CPU, with transport costs recorded rather than treated as an unlock veto.

No WWF audio engine is built: A1 is inactive zero data. Other wrestlers, advanced grapples/endurance, ring/campaign progression, all powerups/two-player and full1-1 are unqualified. The external snapshot epoch Notify contract remains explicit; the admitted basic punch path is serial before native enemy updates and rechecks identity before defeat. Root must review/compose current source and run its exact native packet before any publication.

Source-only ZIP is a bounded replayable delta: actual assembly, explicit hook patch/bytes, guarded main/union/link recipes, original body/metadata/cookie inputs, finite tools/receipts and retained negatives. Existing native/source dependencies are hash-pinned rather than duplicated. No ROM/object/24KiB image forest is archived. Replay the builder only into a NEW private output root, validating all output paths before compilation.
''',encoding='utf-8')
 tools=set(R/'tools/audit'/n for n in ['prepare_wwf_hogan_natural_source_v15.py','wwf_hogan_owner_rebind_v1.py','wwf_hogan_natural_controls_v9.py','wwf_hogan_menu_source_controls_v5.py','wwf_hogan_typed_api_controls_v5.py','wwf_hogan_pose_contact_controls_v5.py','wwf_hogan_palette_closure_v6.py','wwf_hogan_live_vectors_v6.py','wwf_hogan_whole_main_stack_probe_v3.py','wwf_hogan_foreign_scene_controls_v1.py','wwf_hogan_foreign_draw_controls_v5.py','wwf_hogan_valid_cf_palette_rebind_v3.py'])|{Path(__file__)}
 refs={R/'tools/reference'/n for n in['wwf_hogan_runtime_v13.s','wwf_hogan_palette_v4.s','wwf_hogan_world_v2.s','wwf_first_hogan_owner_v2.s']}
 files=local_imports(tools)|tools|refs|{R/'build/wwf-hogan-basic-loop-qualified-v2/freeze-negative.json',R/'build/wwf-hogan-basic-loop-qualified-v1/freeze-negative.json',stage,*tests,*negatives,mask,R/'build/wwf-ready74-first-host-resource-v1/resource-contract.json'}
 files|={p for p in J.rglob('*')if p.is_file()and p.suffix in['.s','.inc','.cfg','.dep','.json']}
 files|={p for p in J.parent.glob('*.json')}
 files|={J/n for n in['hogan-metadata.bin','hogan-body.chr','cookie.bin']}
 files|={p for p in O.iterdir()if p.is_file()}
 # Actual source VM/recovery/host inputs are needed by the final builder.
 for root in[R/'build/wwf-c2-symbol-relocation-v3',R/'build/wwf-frame-recovery-v2',R/'build/wwf-native-proxy-lab-v1']:
  files|={p for p in root.glob('*.s')}
 files={p.resolve()for p in files};assert len(files)<420,len(files)
 bindings={str(p.resolve()):sha(p)for p in files|external|dependency_files|{J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl'}}
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:
  for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 for p,h in bindings.items():assert sha(p)==h,p
 handoff=dict(source=True,native=False,installed=False,root_admission_pending=True,status='FIRST_HOGAN_NATURAL_BASIC_LOOP_SOURCE_PROPOSAL_PASS',candidate=s['candidate'],parent=s['parent'],joint=str(J),source_stage=str(stage),bindings=bindings,members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)},archive_sha256=sha(O/'source-only.zip'),archive_bytes=(O/'source-only.zip').stat().st_size,resource_contract=s['resource_contract'],resident_bytes=resident,C2_bytes=c2,private_source_ready=75,current_parent_ready=74,actual_native_runs=0,limits=api['limits'])
 save(O/'handoff.json',handoff)
 for n in['handoff.json','source-only.zip','integration-api.json','physical-fit.json','hook-bytes.json','source-hooks.patch','verification-summary.json','README.txt']:(D/n).write_bytes((O/n).read_bytes())
 (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(tools|refs))+'\n'+D.relative_to(R).as_posix()+'/\n')
 print(json.dumps(dict(passed=True,handoff=str(D/'handoff.json'),sha256=sha(D/'handoff.json'),candidate=s['candidate'],bindings=len(bindings),members=len(files),archive_bytes=handoff['archive_bytes'],resident=resident,C2=c2)))
if __name__=='__main__':main()
