"""Freeze current two-platform source and ONE unlaunched controller-only pilot."""
from pathlib import Path
import argparse,configparser,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation
from celeste_platform_current_controls_v1 import *

def opening(bundle,mode):
 q=fresh(bundle,mode,camera=144)
 for j in range(3):q.set('AreaObjectLength',255,j)
 for _ in range(32):run(q,'AreaParserCore');run(q,'IncrementColumnPos')
 q.put(Player_PageLoc=0,Player_X_Position=240,Player_Y_Position=176,Player_State=0,CmState=0,Player_X_Speed=32,Player_XSpeedAbsolute=32,Player_MovingDir=1,PlayerFacingDir=1,CmPreviousAB=0,CmCoyote=0,CmJumpInterval=0,CmJumpBuffer=0,Player_CollisionBits=255,DisableCollisionDet=0,GameTimerDisplay=4,SavedJoypadBits=1,Left_Right_Buttons=1)
 jumped=False;at=None;IDs=set();item_updates=0
 for t in range(240):
  xx=q.get('Player_PageLoc')*256+q.get('Player_X_Position');a=False
  if not jumped and xx>=264 and q.get('Player_State')==0:
   jumped=True;at=q.get('CmClock');a=True
  if at is not None and q.get('Player_State')!=0 and((q.get('CmClock')-at)&255)<32:a=True
  q.put(SavedJoypadBits=1|(128 if a else 0),VRAM_Buffer1_Offset=0,VRAM_Buffer2_Offset=0);run(q,'GameLoop')
  for i in range(6):
   if q.get('Enemy_Flag',i)>0:
    IDs.add(q.get('Enemy_ID',i));item_updates+=int(q.get('Enemy_ID',i)==46)
  assert q.get('CmTier')==0 and q.get('PlayerStatus')==0 and q.get('GameEngineSubroutine')==8 and q.get('NumberofLives')==2
  xx=q.get('Player_PageLoc')*256+q.get('Player_X_Position')
  if xx>=420:return dict(passed=True,mode=mode,updates=t+1,last_X=xx,Tier=0,item_actor_updates=item_updates,actual_live_enemy_IDs=sorted(IDs),scope='Typed current-parser/source fullGameLoop opening predicate mirror, not native cold-menu/enemy timing or LuaVM execution.')
 raise AssertionError(('opening source predicate stalled',mode,xx))

def coyote(bundle,mode,start,delay=None,stride=1):
 q=fresh(bundle,mode,camera=start-96)
 for j in range(3):q.set('AreaObjectLength',255,j)
 for _ in range(64):run(q,'AreaParserCore');run(q,'IncrementColumnPos')
 q.put(Player_PageLoc=start>>8,Player_X_Position=start&255,Player_Y_Position=128,Player_Y_HighPos=1,Player_State=0,CmState=0,Player_X_Speed=32,Player_XSpeedAbsolute=32,Player_MovingDir=1,PlayerFacingDir=1,CrouchingFlag=0,CmPreviousAB=0,CmCoyote=0,CmJumpInterval=0,CmJumpBuffer=0,Player_CollisionBits=255,DisableCollisionDet=0,TimerControl=0,GameEngineSubroutine=8)
 pressed=False;press=None;rows=[]
 for t in range(90):
  xx=q.get('Player_PageLoc')*256+q.get('Player_X_Position')
  if delay is not None:pressed=t>=delay
  elif t%stride==0 and not pressed:
   # Exact new Lua walk-phase predicate; Python does not pretend to execute
   # a Lua VM. The ROM kernel/actual complete consumer execute below.
   pressed=640<=xx<=644 and q.get('CmCoyote')>0 and q.get('CmPreviousAB')&128==0 and q.get('CmJumpInterval')==0
  if pressed and press is None:press=dict(update=t,x=xx,y=q.get('Player_Y_Position'),coyote=q.get('CmCoyote'))
  q.put(SavedJoypadBits=1|(128 if pressed else 0));run(q,'PlayerCtrlRoutine')
  xx=q.get('Player_PageLoc')*256+q.get('Player_X_Position');yy=q.get('Player_Y_Position');rows.append([xx,yy,q.get('Player_State')])
  if xx>=736 and yy<=112:return dict(passed=True,start_X=start,delay=delay,poll_stride=stride,press=press,updates=t+1,face=[xx,yy],tier=q.get('CmTier'))
 return dict(passed=False,start_X=start,delay=delay,poll_stride=stride,press=press,updates=90,last=rows[-1])

def freeze():
 out=B/'celeste_platform_rcr_handoff_v1.json';assert not out.exists()
 rom=B/'celeste-platform-rcr-v1.nes';parent=B/'roster-shared-rcr-adopted-v8.nes';legacy=B/'celeste-platform-two-v3.nes'
 assert sha(rom)=='81cdc9be7366d943996ec1288371a0f2ea417a17de87f0d89358c0ea8cf2e2fa'
 assert sha(parent)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 b=scoped_load(rom);old=scoped_load(parent);prior=scoped_load(legacy)
 proof=B/'celeste_platform_rcr_controls_v1.json';p=json.loads(proof.read_text());assert p['passed']and not p['native_run']
 for f,h in p['bindings'].items():assert sha(f)==h
 start=16+26*8192+0x1140;end=start+577
 assert b['raw'][start:end]==prior['raw'][start:end]
 # Re-execute exact source-coyote632/Y128 after4..6 ordinary updates.
 local=[]
 for mode in[0,1]:
  for delay in[4,5,6]:
   row=coyote(b,mode,632,delay);assert row['passed'];local.append(dict(mode=mode,**row))
  for x in[632,633,634,635,636]:
   for stride in[1,2]:
    row=coyote(b,mode,x,stride=stride);assert row['passed'],row;local.append(dict(mode=mode,**row))
 # The controller may simply stay off A while original carry reaches capY112.
 elevator=[]
 for mode in[0,1]:
  for wall in[912,2240]:
   row=approach(b,mode,wall,999);assert row['reached']and any(r[4]for r in row['rows'])
   elevator.append(dict(mode=mode,wall=wall,updates=len(row['rows']),first_face=row['rows'][-1],actual_contact_updates=sum(bool(r[4])for r in row['rows']),A_pressed=False))
 ov=B/'celeste-platform-rcr-overlay';entry=ov/'src/entrypoint.s'
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_platform_rcr_current.d';obj=B/'celeste_platform_rcr_current.o'
 cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(ov/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(ov),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(entry)];result=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_platform_rcr_current.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 deps={}
 for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file();deps[str(f)]=sha(f)
 assert str((R/'src/river_city_core_host_v8.inc').resolve())in deps
 assert str((R/'src/river_city_shared_palette_host_v8.inc').resolve())in deps
 assert str((ov/'src/celeste_platform_two.s').resolve())in deps
 assert not any('celeste-platform-two-overlay' in f for f in deps)
 ordinary={m:sha(B/('celeste-platform-rcr-'+m+'.nes'))for m in['mmc3','mmc5']}
 assert ordinary=={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
 # Preserve the complete historical499-binding packet, not just its ROM.
 previous=B/'celeste_platform_two_handoff_v1.json';previous_data=json.loads(previous.read_text())
 for f,h in previous_data['bindings'].items():assert sha(f)==h,('old499 packet changed',f)
 policy=R/'tools/playthroughs/celeste_tier0_11_v1.lua';text=policy.read_text()
 assert text.isascii()and not re.search(r'\bemu\.|io\.open|addMemoryCallback|setInput',text)
 policy_sources=base.policy_dependencies(policy)
 bindings=dict(deps)
 extras=[Path(__file__),R/'tools/prepare_celeste_platform_current_v1.py',R/'tools/audit/celeste_platform_current_controls_v1.py',proof,previous,dep,ov/'smb1base-mmc5-expanded.cfg',B/'celeste_platform_rcr_v1.patch',R/'tools/build_mmc5_expanded.py',R/'build_options.ini']+list(policy_sources)+[z.with_suffix(s)for z in[rom,parent,legacy]for s in['.nes','.dbg','.lbl']]+[B/('celeste-platform-rcr-'+m+s)for m in['mmc3','mmc5']for s in['.nes','.build.json']]
 for f in extras:bindings[str(f.resolve())]=sha(f)
 hand=dict(passed=True,source_CPU_only=True,native_run=False,parent_ROM_sha256=sha(parent),ROM=str(rom),ROM_sha256=sha(rom),DBG_sha256=sha(rom.with_suffix('.dbg')),LBL_sha256=sha(rom.with_suffix('.lbl')),proof=str(proof),proof_sha256=sha(proof),actual_assembly_dependencies=len(deps),actual_dependency_command=cmd,layout=p['checks']['allocation'],ordinary=ordinary,coyote_current_actual_CPU=local,no_A_native_elevator_actual_CPU=elevator,source_opening_predicate=[opening(b,mode)for mode in[0,1]],prior499_bindings_preserved=True,prior_helper577_bytes_exact=True,Lua_VM_executed=False,policy_scope='New input-only discovery, not a native clear/controller-safety proof. Complete native guard remains unchanged.',finite_costs=p['checks']['actual_complete_owned_GameLoop_cost'],owned_publication_files=['tools/prepare_celeste_platform_current_v1.py','tools/audit/celeste_platform_current_controls_v1.py','tools/playthroughs/celeste_tier0_11_v1.lua','tools/audit/celeste_tier0_route_prepare_v1.py','docs/qa/celeste-platform-rcr-tier0-ready-2026-10-28.txt'],bindings=bindings)
 out.write_text(json.dumps(hand,indent=2)+'\n');return out,hand

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--mode',choices=['easy','hard'],default='easy');args=parser.parse_args()
 hand_path,hand=freeze()
 base.BASE['celeste']=(0,0,'MarioVariant',4);base.navigation=navigation
 a=argparse.Namespace(rom=Path(hand['ROM']),expected_sha256=hand['ROM_sha256'],output=args.output,identity='celeste',mode=args.mode,frames=8000,policy=R/'tools/playthroughs/celeste_tier0_11_v1.lua',replay=None)
 base.prepare(a)
 ready=args.output.resolve()/'ready.json';q=json.loads(ready.read_text());q['bindings'].update(hand['bindings']);q['bindings'][str(hand_path.resolve())]=sha(hand_path)
 for f in[Path(__file__).resolve(),R/'tools/audit/roster_expansion_native_prepare_v2.py',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll')]:q['bindings'][str(f.resolve())]=sha(f)
 q.update(source_handoff=str(hand_path),source_handoff_sha256=sha(hand_path),source_parent='4cbd RCR; not historical00597',tier0_controller='Natural skip Mushroom, require actual raw0/variant4+CmTier0; actual consumed-A readback, source-coyote takeoff640..644 after632 neighborhood, source-native actor25 boarding/carry at912/2240. No state writes/cheats.',native_grant=False,Lua_VM_executed=False,additional_callbacks=False,global_worker_owner='ROOT only',fidelity_limits=['No native run yet. Source local access does not prove controller safety through enemies/complete1-1.','Only2supports; broader145census/globaltier0traversal remain open.','Native platform warm fullcaller cost about4395 extraCPU, not a lag improvement.','SourceClock controls ordinary inputs; actual display publication/cadence still guarded/observed by unchanged native harness.'])
 q['human_GUI_settings_nonruntime_provenance']=dict(path='C:/Mesen2/settings.json',sha256=sha(Path('C:/Mesen2/settings.json')),informational_only=True,no_file_writes=True)
 ready.write_text(json.dumps(q,indent=2)+'\n')
 report=R/'docs/qa/celeste-platform-rcr-tier0-ready-2026-10-28.txt'
 report.write_text('Celeste two-platform RCR composition and unpowered controller -- SOURCE/READY ONLY\n\nROM '+hand['ROM_sha256']+'; actual4cbd parent. Same577-byte helper at26:B140..<B381 plus3genuine81targetbytes, every otherbank/CHR/oldruntimePC exact. No shared source/CFG/data/physics edits; no new global fields; Goku/Rogue/FF allocations untouched. Fresh sourcecontrols rerun all ABI/capacity/staleownership/carry/pickup/IRQ/lagNMI/foreign cases; ordinaryd444/f4ffd exact. Real native YMovingPlatform route selected via owners81/82, no sine helper. Historical21f19 and499bindings remain exact.\n\nFresh compiled coyote632/Y128 after4..6Right/noA updates then freshA reaches736 in bothmodes. Independent controller-predicate mirror tested startingX632..636 and pollingstride1/2; genuine liveCoyote plus consumedA and actualJumpInterval, takeoffX640..644. These Python checks execute complete real PlayerCtrlRoutine, not Lua VM. Native policy logs actual source clock/X/Y/grace; native observed elapsed from an overshot runupanchor is not silently called4..6. Both native25 elevators also reach cap with noA, genuine large-platform bbox/collision/carry, bothmodes.\n\nController is a new input-only discovery. One early opening jump avoids intentional Mushroom reveal/pursuit; actual CmTier/PlayerStatus0 asserted throughout. It aligns on real secondpipe, uses source-clock/readback coyote, waits for reciprocal actual native platform actor/contact+bodyY relation before treating boarding as seen, then rides/walks to cap. Finalstair landing and actualgrounded pole-base retry are inputs only. Full enemy/gap/landing safety is NOT source-proven; original zero-death/stationary8000/control1-2/strictE008/all256DMA/IRQ/NMI/5SMC/CHR guards remain literalunchanged. Firstfailure must stayFALSE; no retries are granted here.\n\nNative preparation '+str(ready)+'. Final ready hash is returned by the preparer after binding this report. One compact512MiB container; central2GB/64file budget, at most8selected wholeframe epochs, no perframe files. Root owns launch/lease. Lua_VM_executed=false; Mesen will perform actual parser/runtime admission. GUIsettings hash is informational provenance; runtime exe/core/CLI and existing isolated runner are strictbound. No settings writes.\n\nMaterial typed fullGameLoop CPU extras: distant156/powered-empty120/warm native platform4395/spawn5076..5082. No FPS/deadline/whole-route timing claim. No native, canonical install, Downloads, Git or sharedsource changes by this agent.\n',encoding='utf-8')
 # Add report after writing it; no self-hash cycle in the source handoff.
 q['bindings'][str(report.resolve())]=sha(report);ready.write_text(json.dumps(q,indent=2)+'\n')
 (args.output/'command.json').write_text(json.dumps(q['command'],indent=2)+'\n')
 print(json.dumps(dict(prepared=True,native_run=False,source_handoff=str(hand_path),source_handoff_sha256=sha(hand_path),source_bindings=len(hand['bindings']),ASM_dependencies=hand['actual_assembly_dependencies'],ready=str(ready),ready_sha256=sha(ready),bindings=len(q['bindings']),command=q['command']),indent=2))
if __name__=='__main__':main()
