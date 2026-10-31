"""Bounded files-only source checkpoint; no Git/native/Download operations."""
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-scroll-publisher-1031-v2'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-scroll-source-v1'
H=R/'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
N=R/'build/contra-force-11-native-1031-v5/burns'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
def check(p,passed=True):
 q=json.loads(p.read_text())
 if passed:assert q['passed']
 for f,h in q.get('bindings',{}).items():assert sha(f)==h,('Changed frozen dependency',f)
 return q
def main():
 assert not O.exists();O.mkdir()
 parent=check(H);stage=check(P/'source-stage.json')
 positive=[R/'build'/n/'controls.json'for n in[
   'contra-force-scroll-negative-controls-1031-v3','contra-force-scroll-positive-controls-1031-v3',
   'contra-force-scroll-seam-controls-1031-v1','contra-force-scroll-paused-normal-controls-1031-v1','contra-force-scroll-menu-controls-1031-v1']]
 for p in positive:check(p)
 negative=[R/'build'/n/f for n,f in[
   ('contra-force-scroll-publisher-1031-v1','negative.json'),
   ('contra-force-scroll-negative-controls-1031-v1','controls.json'),
   ('contra-force-scroll-negative-controls-1031-v2','controls.json'),
   ('contra-force-scroll-positive-controls-1031-v1','controls.json'),
   ('contra-force-scroll-combat-negative-1031-v1','controls.json'),
   ('contra-force-scroll-combat-pulse-controls-1031-v1','controls.json')]]
 for p in negative:check(p,False)
 result=json.loads((N/'capture/result.json').read_text());assert not result['passed']and result['maximum_x']==239 and result['kills']==0
 raw=(N/'capture/endpoint.png').read_bytes();derived=(N/'capture/endpoint-decoded-review.png').read_bytes()
 assert raw.replace(b'\r\n',b'\n')==derived
 assert hashlib.sha256(derived).hexdigest()=='b91b620b4543ba55cc03eec126742c9c1243c4b78d7a5fced141a357bb70dcc1'
 Image.open(N/'capture/endpoint-decoded-review.png').verify()
 (O/'negative-endpoint-original.png').write_bytes(raw);(O/'negative-endpoint-derived-review.png').write_bytes(derived)
 review=dict(original=str(N/'capture/endpoint.png'),original_sha256=hashlib.sha256(raw).hexdigest(),
   derivative=str(N/'capture/endpoint-decoded-review.png'),derivative_sha256=hashlib.sha256(derived).hexdigest(),
   transformation='One byte-stream replacement CRLF→LF, reversing Windows text-output translation; never applied twice. Original remains unchanged.',
   original_signature=raw[:12].hex(),derived_signature=derived[:8].hex(),PIL_verified=True,gameplay_outcome_changed=False,
   screenshot_fix_for_future='Every new PNG is opened wb. Original corrupt capture remains negative evidence.')
 save(O/'native-negative-review.json',review)
 coverage=dict(passed=True,source=True,native=False,installed=False,candidate=stage['candidate'],parent=stage['parent'],
   source_ready74=True,menu_profiles=86,
   cause='CF graphics bypassed native PlayerOffscreenChk, so native Player_Pos_ForScroll stayed0 after real AllZeros power-on. Native ScrollHandler correctly refused scrolling, clamped atX239, and never advanced terrain/enemy parser.',
   change='Same-PC five-byte CfHostGraphics prefix becomes JSR+2NOP to own12B BFBA..<BFC6 helper. Helper copies genuine native LDA Player_Rel_XPos / STA Player_Pos_ForScroll then original LDA0 / STA ObjectMetasprite / RTS.',
   original_native_scroll_parser_source_unchanged=True,original_CF_motion_jump_weapons_art_unchanged=True,
   actual_source_controls=dict(zero_field_old_X239_camera0_no_spawns=True,classes=4,positive_X=[369]*4,positive_camera=[257]*4,
      actual_native_terrain_and_Goomba_spawn=True,jump_avoidance_no_enemy_or_guest_seed=True,
      graphics1_3_all64flags_pairs=512,normal_lag_and_lagpaused_NMI_IRQ_cuts=216,additional_normalpaused_NMI_IRQ_cuts=72,
      all_AXYP_live_page1_33SMC_maps_exact=True,foreign_menu_pairs=86,ready_counts=[74,74],Start_flag_cases=10240),
   fixture_coverage_correction='Earlier finite cold helper inherited native Player_Pos_ForScroll96, masking missing publication; those finite body/jump/palette observations remain valid but did not prove actual AllZeros camera/spawn. New source probe changes ONLY this additional native initial byte96→0 before real menu/Start; after cold entry only controller fields and normalNMI fixture boundary change. Full hardware power-on remains root native scope.',
   actual_native_negative=dict(frames=result['frames'],Main=result['Main'],maximum_x=239,gameplay_frames=7000,kills=0,collections=0,source_unchanged=True),
   combat_hold='Separate heldDown+B and settledDown4 + freshB2on/6off probes still die. Starting source projectileY193/startup or189/settled; original body settledanchorY192. Actual GoombaY184/control9 bbox[3,14,13,20] givesY198..204; current contact adapter pointY misses. No projectile-Y/physics/art/contact source changed; no conclusion that only edge timing causes failure.',
   remaining=['Root advancing-scroll native smoke/visual review; no new native or install claim.',
     'Ground enemy shooting/contact alignment remains a separate retained blocker before a successful full1-1 route.',
     'No1-1 clear/allpowerups/60Hz/crowding improvement claim.'])
 save(O/'scope-and-coverage-correction.json',coverage)
 (O/'README.md').write_text('''# Contra Force native scrolling publication

The original bounded controller run reached X239 with camera0 and no new terrain or enemies. CF bypassed the native graphics tail that normally publishes Player_Rel_XPos to Player_Pos_ForScroll. The native scroll and parser routines themselves were behaving correctly.

This source child preserves all prior native and private entry PCs. A five-byte CF graphics prefix now calls a12-byte helper in its already-owned unused A3 tail; the helper copies the two genuine native publisher instructions, then the overwritten original CF prefix. The original movement/jump/weapons/art and every non-CF ROM byte are unchanged. The real carrier and full cookie are regenerated (version3).

The inherited source fixture started the native scroll-position field at96. That counterexample is retained and explicitly narrows earlier cold-source coverage. New cohorts start this field at its real AllZeros0 before the genuine menu/Start/parser; no CF cache/state, camera, terrain or enemy is seeded. All four reach X369/camera257 with genuine new terrain and a native Goomba using ordinary jump avoidance.512 full-flag graphics pairs and288 actual native ISR cuts pass;86 menu pairs and10240 Start masks are unchanged.

The separate crouch-fire probes remain failed combat evidence, including a settled duck and fresh B pulses. They are not relabeled as successful shooting or rolled into scrolling success. Root must run a bounded advancing-camera smoke before another full route. No native launch, Download change, staging or commit was performed here.
''',encoding='utf-8')
 toolnames=['prepare_contra_force_scroll_publisher_1031_v1.py','prepare_contra_force_scroll_publisher_1031_v2.py',
   'contra_force_scroll_probe_1031_v1.py','contra_force_scroll_probe_1031_v2.py','contra_force_scroll_probe_1031_v3.py','contra_force_scroll_probe_1031_v4.py','contra_force_scroll_probe_1031_v5.py','contra_force_scroll_probe_1031_v6.py',
   'contra_force_scroll_seam_controls_1031_v1.py','contra_force_scroll_paused_normal_controls_1031_v1.py','contra_force_scroll_foreign_menu_1031_v1.py',
   'contra_force_scroll_combat_diagnostic_1031_v1.py','contra_force_scroll_combat_diagnostic_1031_v2.py',Path(__file__).name]
 tools=[R/'tools/audit'/n for n in toolnames]
 native=[N/n for n in('ready.json','controller.lua','run.py')]+[N/'capture'/n for n in('binding.json','inputs.csv','trace.csv','events.jsonl','result.json','candidate-controller.log','capture-budget.json')]
 files=set(positive+negative+tools+native+[P/'source-stage.json',O/'scope-and-coverage-correction.json',O/'native-negative-review.json',O/'README.md'])
 files.update(p for p in P.iterdir()if p.is_file()and p.suffix=='.json')
 files.update(p for d in(P/'kernel',P/'joint')for p in d.iterdir()if p.is_file()and p.suffix in('.s','.cfg','.dep'))
 members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}
 save(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:
  assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in members.items())
 bindings=dict(parent['bindings']);bindings.update(stage['bindings'])
 for p in positive+negative:bindings.update(json.loads(p.read_text()).get('bindings',{}))
 refs=files|{H,O/'source-only.zip',O/'source-members.json',N/'capture/endpoint.png',N/'capture/endpoint-decoded-review.png',O/'negative-endpoint-original.png',O/'negative-endpoint-derived-review.png'}
 bindings.update({str(p.resolve()):sha(p)for p in refs})
 handoff=dict(**coverage,actual_link_recipe=str(P/'final-link.json'),actual_kernel_recipe=str(P/'kernel-link.json'),actual_config=str(P/'joint/candidate.cfg'),
   inherited_parent_handoff=str(H),inherited_parent_handoffSHA=sha(H),archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,bindings=bindings)
 save(O/'handoff.json',handoff)
 owned=tools+[O/n for n in('scope-and-coverage-correction.json','README.md','native-negative-review.json','negative-endpoint-original.png','negative-endpoint-derived-review.png','source-members.json','source-only.zip','handoff.json','owned-files.json')]
 save(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in owned],agent_stage_or_commit=False))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=stage['candidate'],bindings=len(bindings),members=len(members),bytes=handoff['archive_bytes'])),flush=True)
if __name__=='__main__':main()
