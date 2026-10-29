"""Freeze bounded body unit with actual C/ASM consumption and exact hooks."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import rogue_dawn_host_body_controls_v1 as cpu
O=R/'build/rogue-dawn-host-body-v1'
REPORT=R/'docs/qa/rogue-dawn-host-body-f56a-source-2026-10-28.json'
sha=lambda p:ref.digest(Path(p).read_bytes())

def dependencies(path):
 t=path.read_text().split(':\t',1)[1].split('\n\n',1)[0].replace('\\\n',' ').strip()
 out=[]
 for s in re.split(r'(?<!\\)\s+',t):
  if not s:continue
  p=Path(s.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),str(p)
  if p not in out:out.append(p)
 return out

def main():
 assert not(O/'handoff.json').exists(),'Frozen unit'
 b=json.loads((O/'build.json').read_text());assert b['passed']
 for x in b['bindings']:assert ref.binding(x['path'])==x,x['path']
 checks={n:json.loads((O/n).read_text())for n in['body-controls.json','body-edge-controls.json','ordinary-controls.json']}
 for n,d in checks.items():
  assert d['passed'],n
  for x in d['bindings']:assert ref.binding(x['path'])==x,x['path']
 # Actual C preprocessing/compile dependencies are separate from ca65's
 # last-produced ASM list. Same real flags; no changed ROM/object relink.
 cmd=[str(R/'tools/Windows/cc65/bin/cc65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-T','-I',str(R),'--create-full-dep',str(O/'c-full.dep'),'-o',str(O/'c-closure.s')]
 original=b['commands'][0]
 for i,v in enumerate(original):
  if v=='-D':cmd+=['-D',original[i+1]]
 cmd += [str(O/'main.c')]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'c-closure.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 cdeps=dependencies(O/'c-full.dep');adeps=dependencies(O/'assembler-full.dep');assert len(adeps)==490
 paths=list(dict.fromkeys(adeps+cdeps));allinput=[ref.binding(p)for p in paths]
 # Genuine parent preimages and candidate instruction bytes for every old
 # hook extent. New allocations have explicit prior fill proof in build.json.
 old=scoped_load(cpu.P);new=scoped_load(O/'candidate.nes');hooks=[]
 for q in b['old_hook_extents']:
  x,y=q['start'],q['end'];aa=bytes(old['raw'][x:y]);bb=bytes(new['raw'][x:y]);bank=(x-16)//8192
  hooks.append(dict(name=q['name'],file_offset=x,physical_bank=bank,CPU_address=hex((0xc000 if bank==94 else 0xa000)+(x-16)%8192),bytes=y-x,parent_hex=aa.hex(),candidate_hex=bb.hex(),changed=sum(a!=c for a,c in zip(aa,bb))))
 delta={}
 for i,(x,y)in enumerate(zip(old['raw'],new['raw'])):
  if x!=y:
   key=('PRG'+str((i-16)//8192))if i<16+1048576 else'CHR';delta[key]=delta.get(key,0)+1
 # Actual current service costs, never old/new semantic equivalence or FPS.
 costs=[]
 for request,offset in[(0,0),(1,0),(1,78)]:
  m=cpu.pipe.base(new);m[0x5c7c]=request;cpu.put(m,VRAM_Buffer1_Offset=offset)
  c,low,tr=cpu.d.call(m,'RdBodyGraphics',sp=224)
  costs.append(dict(body_color_request=request,VRAM_offset=offset,CPU=c.processorCycles,minimum_SP=low))
 primary=checks['body-controls.json']['checks'];edges=checks['body-edge-controls.json']['checks']
 summary=dict(status='PRIVATE bounded body/geometry/render source unit qualified; NOT playable admission',native_run=False,ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(cpu.P),previous_motion=ref.binding(R/'build/rogue-dawn-host-pipeline-v2/candidate.nes'),layout=dict(A95_host_start='A600',literal_motion_prefix_end='B5D2',body_start='B5D2',body_end='B803',new_body_bytes=561,remaining_bytes=0xc000-0xb803,B1_BG_gate='B958..B96F exact frozen24B',B1_selector='B970..B97E15B; B97F EA; DoneB980 RTS',bank4_owner='BF5A..BF8544B; fast world CPY/BNE/JMP precedes A95 call',post_BG='71:ABC738B; inline exact gate24B+14EA',new_RAM=0),authenticity=dict(source_ROM_sha256=ref.EXPECTED,original_CORE4090_AUX508_ART3150_bridge175_literal=True,source_original_8x8_to_host_8x16_pose_pixels='180 direct real renderer cells and120 complete DrawAll cells, all admitted30poses/bothfacings; exact indices/priority/palette. No hardware visibility claim.',source_radius='authentic radiusX/radiusY unchanged',native_contact_adaptation='SMB bottom is source center+radiusY+1 leading-foot plane, matching frozen support/native platform consumer. Morph landing top−25; stand top−32.',context_B='Previously approved virtual original8x8 cursor0, actual decoder return perpose/facing/F7; not host cursor/constant36; feeds RdAcceleration.'),counts={k:len(v)if isinstance(v,list)else v for k,v in primary.items()if k!='inline_postBG_exact_foreign'},extra_counts={k:len(v)if isinstance(v,list)else v for k,v in edges.items()if k!='foreign_Proto_catchup_unqualified_baseline_countercheck'},costs=dict(foreign_fullMain_vs_f56a_CPU=sorted(set(x['CPU_delta']for x in primary['all_foreign_complete_Main'])),foreign_fullDraw_CPU=sorted(set(x['CPU_delta']for x in primary['all_foreign_complete_DrawMetasprite_DrawAll'])),foreign_post_BG_CPU=primary['inline_postBG_exact_foreign']['CPU_delta'],foreign_platform_CPU=sorted(set(x['CPU_delta']for x in edges['foreign_complete_platform_callers'])),world_fast_path_added_CPU=0,body_graphics_absolute=costs,no_deadline_FPS_or_performance_win_claim=True),actual_minimum_SP=checks['body-controls.json']['minimum_SP'],CHR_palette=dict(body_window=0,preserved_window_shadows='1..11 and modes exact',body_palette='$3F11..13 only, original suit/missile source colors',preserved_palettes='universal backdrop and palettes1..3 unchanged by producer',busy_queue='>=78 retains existing RdColorRequest; no newRAM/cache',source_effect_windows='Frozen full publisher is deliberately not used; source weapons/effects need a separately qualified lease.'),visibility_OPEN=dict(reason='GuestPlayerVisible runs before Rogue body graphics and still consults legacy GuestHurt/Injury/MMdeath state.',full_Main_precondition='GuestHurtKind=InjuryTimer=MmDeathFlag=GuestPowerupActive0',direct_hurt_scope='110 declared source-hurt→F7/pose→genuine draw cases; NOT admission from real native actor damage.',next_required='Separate exact-owner native lifecycle/injury/visibility gate; no return-PC multiplexing added.'),lifecycle_OPEN=dict(implemented_but_not_hooked=['RdBodyNewSession','RdBodyNewLife','RdBodyEnterScene'],fresh='clear all6 persistent bytes; sourceBCD99',life='retain gear/tanks/max/currentmissiles, refill tank-capacityBCDhealth',scene='active/action only; no AreaPointer identity detection',pause='Future actual caller must freeze clocks/actions/animation. This unit adds no automatic pause/lifecycle owner.'),retained_negatives=dict(immediate_inside_ControlStep192=ref.binding(R/'build/rogue-dawn-host-transactions-v3/control-SP192-negative.json'),standalone_preserved_flush192=ref.binding(R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json'),separate_foreign_catchup=edges['foreign_Proto_catchup_unqualified_baseline_countercheck'],ordinary_first_source_negative='First expanded prototype lacked two flagoff conditionals; expandedROMunchanged after correction. No ordinary candidate admitted before fresh f4ffd/d444 rebuild.',test_setup_corrections='CPU reviewer fixed16bit carry expectation, exact even OAM tile encoding and real PlayerOAMReservation predecessor; no product/guard waiver.'),remaining=['Native displayed pixel/physical OAM/CHR/PPUMASK deadline check','Typed native lifecycle/injury/death/visibility admission','Mature world item contacts/unique authentic emergence art/announcements','Source weapon/typed actor HP/Ice/boss consumers','Actual Rogue audio driver/data bridge','Menu/playable admission'],input_closure=dict(actual_ASM_incbin_inputs=len(adeps),actual_C_preprocessor_inputs=len(cdeps),unique_consumed_files=len(paths),ASM_command=b['commands'][0],C_dependency_command=cmd,scope='Actual ca65/cc65 full dependencies, plus explicit linker cfg/tool/library and postprocessor inputs in handoff; no handwritten-list closure claim.',no_full_source_tree_copy=True),per_bank_changed_byte_counts=delta,exact_hook_preimages=hooks)
 REPORT.write_text(json.dumps(summary,indent=2)+'\n')
 extras=[Path(__file__),REPORT,O/'build.json',O/'body-controls.json',O/'body-edge-controls.json',O/'ordinary-controls.json',O/'c-full.dep',O/'c-closure.s',O/'c-closure.log',O/'main.c',R/'tools/Windows/cc65/bin/cc65.exe',R/'tools/Windows/cc65/lib/nes.lib',R/'tools/prepare_cv3_dmc_mirror.py',R/'audio/cv3/primary72.dmc',R/'audio/cv3/sypha75.dmc',O/'candidate.cv3-mirror.json']
 extras += [R/'tools'/n for n in ['prepare_rogue_dawn_host_body_v1.py','rogue_dawn_host_body_controls_v1.py','rogue_dawn_host_body_edges_v1.py','rogue_dawn_host_body_ordinary_v1.py']]
 # Include every direct true linker/debug/config artifact and sparse source,
 # while references to old frozen source packets remain their own scopes.
 extras += [Path(x['path'])for x in b['bindings']]
 bindings=[ref.binding(p)for p in dict.fromkeys(paths+extras)]
 owned=[R/'src/rogue_dawn_host_body.s',REPORT,*[R/'tools'/n for n in ['prepare_rogue_dawn_host_body_v1.py','rogue_dawn_host_body_controls_v1.py','rogue_dawn_host_body_edges_v1.py','rogue_dawn_host_body_ordinary_v1.py','prepare_rogue_dawn_host_body_handoff_v1.py']]]
 owned += [O/n for n in ['build-private.py','entrypoint.s','player.s','luigi_native.s','megaman_weapons.s','object.s','new_roster_dispatch.s','zelda2_link_platform.s','legacy-player-prg.s','control-include.s','services-include.s','art-include.inc','bridge-include.s','movement-flush.s','private.cfg','source.patch','assembler-full.dep','c-full.dep','build.json','body-controls.json','body-edge-controls.json','ordinary-controls.json','candidate.cv3-mirror.json','c-closure.s','c-closure.log']]
 packet=dict(passed=True,source_only=True,native_run=False,playable_admission=False,ROM_sha256=b['ROM_sha256'],report=ref.binding(REPORT),bindings=bindings,owned_publication_files=[ref.binding(p)for p in owned],runtime_artifacts_no_public_copies=[ref.binding(O/('candidate'+s))for s in['.nes','.dbg','.lbl','.map']],unqualified_foreign_catchup_retained=True)
 (O/'handoff.json').write_text(json.dumps(packet,indent=2)+'\n')
 print(json.dumps(dict(ROM_sha256=b['ROM_sha256'],report_sha256=sha(REPORT),handoff_sha256=sha(O/'handoff.json'),bindings=len(bindings),owned=len(owned),ASM_inputs=len(adeps),C_inputs=len(cdeps))))
if __name__=='__main__':main()
