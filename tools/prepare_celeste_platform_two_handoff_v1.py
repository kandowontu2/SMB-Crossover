"""Freeze the bounded private00597 two-support component, not a native release."""
from pathlib import Path
import configparser,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from celeste_platform_two_controls_v1 import *

def main():
 out=B/'celeste_platform_two_handoff_v1.json';assert not out.exists()
 proof=B/'celeste_platform_two_controls_v3.json';p=json.loads(proof.read_text());assert p['passed']and not p['native_run']
 for f,h in p['bindings'].items():assert sha(f)==h,('frozen proof input changed',f)
 rom=B/'celeste-platform-two-v3.nes';b=scoped_load(rom);assert sha(rom)=='21f19c13bb0a098c1ec245ab32234e422ca89d73f2db35982c7c39128cb6af7b'
 # Bounded simultaneous-cache control. The camera jump is an explicit typed
 # ownership stress, not an asserted naturally reachable displayed frame.
 rows=[]
 for mode in[0,1]:
  q=fresh(b,mode,camera=768);run(q,'CmPlatformWeapons');first=actors(q)[0][0]
  q.put(Player_PageLoc=3,Player_X_Position=96,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_CollisionBits=255,SavedJoypadBits=0,Left_Right_Buttons=0)
  run(q,'PlayerCtrlRoutine');q.put(ObjectOffset=first);run(q,'RunLargePlatform',x=first)
  assert q.get('PlatformCollisionFlag',first)==first
  # Preserve an unused third cell canary; never create an authored HpCount.
  for n in['HpActorSlot','HpXLo','HpXHi','HpY','HpPhaseLo','HpPhaseMid','HpPhaseHi']:q.set(n,197,2)
  q.put(ScreenLeft_PageLoc=8,ScreenLeft_X_Pos=48);run(q,'CmPlatformWeapons')
  aa=actors(q);assert len(aa)==2 and sorted(o for i,o in aa)==[129,130]and len({i for i,o in aa})==2
  assert q.get('HpCount')==0 and q.get('HpActorSlot',0)==first+1
  assert all(q.get(n,2)==197 for n in['HpActorSlot','HpXLo','HpXHi','HpY','HpPhaseLo','HpPhaseMid','HpPhaseHi'])
  target=next(i for i,o in aa if o==130);q.put(ObjectOffset=target)
  c,hits=execute(q,'HpNativePlatformDispatch',observe=['YMovingPlatform','HpMoveNativeHelper'],x=target)
  assert len(hits['YMovingPlatform'])==1 and not hits['HpMoveNativeHelper']
  rows.append(dict(mode=mode,actors=aa,first_real_collision_flag=first,third_cache_cell_unchanged=True,actual_YMovingPlatform_calls=1,helper_sine_calls=0,CPU=c.processorCycles))
 # Actual source closure, including the pre-RCR sparse leaves/assets. The
 # current shared RCR source is deliberately not claimed to be the parent.
 ov=B/'celeste-platform-two-overlay';entry=ov/'src/entrypoint.s'
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_platform_two_current.d';obj=B/'celeste_platform_two_current.o'
 cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(ov/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(ov),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(entry)];result=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_platform_two_current.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
 deps={}
 for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file();deps[str(f)]=sha(f)
 assert str((ov/'src/celeste_platform_two.s').resolve())in deps
 for name in['river_city.s','mac_roster.s','roster_expansion_menu.inc','zelda2_link_terrain.s']:
  assert str((ov/'src'/name).resolve())in deps and str((R/'src'/name).resolve())not in deps
 for asset in['chr/characters/packed-mmc5-roster-expanded.chr','chr/raw/roster-expansion-menu.bin']:
  assert str((ov/asset).resolve())in deps and str((R/asset).resolve())not in deps
 ordinary={m:sha(B/('celeste-platform-two-'+m+'.nes'))for m in['mmc3','mmc5']};assert ordinary=={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
 frozen={
  'docs/qa/celeste-unpowered-traversal-2026-10-28.json':'027da20ea9f13a612d4aa8dd9cf32bec628679ecd62b0a44138a7d2bab264936',
  'build/celeste_platform_stream_model_v1.json':'204cdf37e09f9a6a043299399d1d877d5b29be36501f7789520646bb511e34a0',
  'build/celeste_mac_union_controls_v1.json':'1c3d203d750771741077795a42402fab7f3370e70454a60dfe3ac5f6ddcbef89',
  'build/celeste_mac_union_handoff_v1.json':'468f90d324b6c1badcffafad52b4dd66007a9aed29e8c33defb8d92261851f83'}
 for name,h in frozen.items():assert sha(R/name)==h
 owned=['tools/prepare_celeste_platform_two_v1.py','tools/audit/celeste_platform_two_controls_v1.py','tools/prepare_celeste_platform_two_handoff_v1.py','docs/qa/celeste-platform-two-private-2026-10-28.txt']
 report=R/owned[-1];ck=p['checks'];cost=ck['actual_complete_owned_GameLoop_cost']['rows']
 report.write_text('''Celeste tier0 -- TWO PRIVATE native1-1 supports, SOURCE/CPU only

Parent00597 Celeste/Mac union; this is not the later RCR4cbd composition. No shared source/CFG/data adoption, Mesen, canonical/Downloads/settings/Git changes by this agent. Frozen145-candidate census, platform model and00597 controls remain unchanged. Only the locally proved912 tall-pipe and2240 first stair face are implemented; other candidates remain proposals. Thirdpipe736 is not automatically mandatory.

Exact private21f19c13bb0a098c1ec245ab32234e422ca89d73f2db35982c7c39128cb6af7b.577B emitted physical26:B140..<B381 within approved1216B B140..<B600;576 formerlyFF bytes differ, plus3 genuine existing farcall target bytes in81. Existing12B B134..B13F alignment staysFF. All old runtime labels/RAM/CHR/otherbanks and34 authored helper records exact; assembler-only _FARCALL_COUNT is a count, not a runtime alias. No CFG reservation is changed. Cels98/81 tails are not consumed.

Exact raw0/variant4, world0/level0, stable loaded scene25 only. Spawn only tier0 with original HpValid/key/scene/character/mode cache and HpCount0; an authored/nonzero cache declines. Existing HpSupport (previously only declared/whole-slab-cleared) marksCE, existing actor slots0/1 have reciprocal81/82 owners. Source owner tags1..3 stay distinct. No new persistent/global fields. No global preservation claim for helper SRAM; real area initialization clears native actors before HpConfigure clears all91 helper bytes. Sound-test HpValid0 prevents updates until the real new area reset. Identity changes require the existing real new-game lifecycle.

Two actual native25 actors: centers888/2216, left edges872/2200,32px width, initialY208, bbox5, genuine8px helper top and original girder art. Real InitEnemyObject/YMovingPlatform/large-platform bbox/collision/carry/draw/OffscreenBoundsCheck remain authoritative. Tags81/82 intentionally select the original native movement branch, not the authored sine record table.384 actual native updates in each mode/cell measuredY76..213. No simulated movement or painted terrain. An empty/full native enemy pool may defer spawn; no active native actor is replaced. Camera detach/re-entry uses real erase/init and restarts native phase, not a preserved detached sine-phase claim.

Spawning uses the existing exact Easy strict(-56,+296)/Hard inclusive[-48,+288] source margin. Coarse pages2/3/7/8 only avoid unnecessary empty-cache work. A real supporting collision flag pins a live platform across power pickup and camera movement; after the engine reports no support, powered actors retire and never respawn. Pause/timer/cutscene entries defer manager work. Native actor erasure/offscreen rules are not overridden. Original partial source paths and NMI are unchanged.

Finite controls:384 full weapon-tail returns covering64 architectural flags/both modes/spawn/warm/distant preserve AXYP/SP/R0..R7/ObjectOffset/banks.14 capacity cases plus24 strict stale-owner release cases;8 actual NrPickup→retention/retirement chains.16 parser-map arenas run complete PlayerCtrlRoutine/BG/bbox then genuine RunLargePlatform and reach each face atY<=112, with observed real contacts, both modes and four fresh-A delays. These are typed LOCAL access arenas, not a native complete route or an automatic controller. Correct clear-floor origins864/2224; the rejected2192 origin was inside the preceding staircase.

498 enabled new-code IRQ visits (236 unique physicalPCs) and8 real IRQ/lagNMI entry/init seams preserve all6 actual CPU flags/AXY/PC/SP/banks/5SMC/R0..R7/live stack/helper91B/Celeste active overlay. B/U status bits are stack encoding; no C/Z/I/D/V/N is excluded.92 other-profile complete GameLoops match full returned state/application RAM/orderedOAM/nonbank hardware/CPU exactly. Fresh ordinaryMMC3d444/MMC5f4ffd unchanged.

Whole typed fullGameLoop costs, including actual added actor collision/motion/drawing:
'''+json.dumps(cost,indent=2)+'''

Material warm native-platform cost is about4395 extra CPU in these local arenas; spawn5076/5082, distant156, powered-empty120. This is an accessibility accommodation, not a lag reduction. Native PPU/deadline/DMC/cadence/visibility/full1-1/tier0global traversal remain unqualified and may reject it. Zero additional NMI work; foreign profile CPU0 in the tested full callers.

Retained negatives: first ca65 relocation-size/branch failures and initial OR81 owner alias were corrected before qualification; invalid nonarchitectural P encodings and direct-call bank-map comparison were oracle errors. ProvisionalY176 gave a later native80..144 cycle inaccessible to a fresh floor jump. The earlier2240 first-jump failure used the invalid2192 origin and is explicitly withdrawn as placement evidence; Y208 and valid2224 were tested separately. No native failures have been hidden or retagged.

Reconstruction/integration: frozen sparse overlay is build/celeste-platform-two-overlay. Existing host leaf differs only by changing CmHostDashTail's first18B farcall target from CmWeapons to CmPlatformWeapons; add the new source include after original helper sources. It appends to existing CROSSOVER_HELPERS, asserts exact oldB134 end and approvedB600 cap. Saved11-path preimageZIP is82922B, not a source clone; ca65's CWD-first incbin precedence is handled by exact absolute staged asset paths. Standard build_mmc5_expanded.py --source-overlay build/celeste-platform-two-overlay --output NEW_PRIVATE_PATH.nes can rebuild this frozen parent; do not rerun builders over frozen triples. ROOT must compose/requalify against current4cbd before any native/adoption.
''',encoding='utf-8')
 bindings=dict(deps)
 extras=[Path(__file__),proof,dep,ov/'smb1base-mmc5-expanded.cfg',B/'celeste_platform_two_00597_preimages.zip',B/'celeste_platform_two_initial_negative.json',B/'celeste_platform_two_y176_access_negative.json',B/'celeste_platform_two_y208_working_note.json',B/'celeste_platform_two_v3.patch',R/'tools/build_mmc5_expanded.py',R/'build_options.ini']+[R/n for n in owned]+[rom.with_suffix(s)for s in['.nes','.dbg','.lbl','.map','.build.json']]+[B/('celeste-platform-two-'+m+s)for m in['mmc3','mmc5']for s in['.nes','.build.json']]
 for f in extras:bindings[str(f.resolve())]=sha(f)
 for name,h in frozen.items():bindings[str((R/name).resolve())]=h
 hand=dict(passed=True,source_CPU_only=True,native_run=False,parent_ROM_sha256='00597cddbff069acbd6fad1571b7b734c5c5f72bc67da49e672565e6c2c4e94d',ROM=str(rom),ROM_sha256=sha(rom),DBG_sha256=sha(rom.with_suffix('.dbg')),LBL_sha256=sha(rom.with_suffix('.lbl')),proof=str(proof),proof_sha256=sha(proof),actual_assembly_dependencies=len(deps),actual_dependency_command=cmd,layout=ck['allocation'],ordinary=ordinary,simultaneous_cache_source_controls=rows,whole_GameLoop_costs=cost,owned_publication_files=owned,private_source_overlay=str(ov),bindings=bindings,limits=['No native/deadline/FPS/fullroute/globaltier0traversal claim.','Only912/2240 supports;145 census remains proposals.','Foreign all-profile source equality follows untouched caller bytes; finite92 fullGameLoops additionally checked.','NewRCR4cbd composition requires fresh binding/qualification.'])
 out.write_text(json.dumps(hand,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(bindings),ASM_dependencies=len(deps),bytes=rom.stat().st_size)))
if __name__=='__main__':main()
