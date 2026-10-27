"""Three actually earned Kirby copies, strict live HUD/green-shell palette witnesses."""
from pathlib import Path
import argparse,hashlib,json,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2];B=R/'build';SHA='3d597ffaf0409ff7b611c968e31818d276eda5e01ae647a3ba6234b9f88d1130';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
OBSERVER='''-- Startup-static actual KbDrawShots::Draw caller/return and committed OAM witness.
local paletteScope
hook('IconDrawEntry',function(s)
 if not entered or not rec or done then return end
 assert(not paletteScope,'No stale or nested Kirby icon draw scope')
 local ptr=r('R0')+256*r('R1');local chosen
 for family,icon in pairs(C.palette_icons)do if ptr==icon.pc and bank(ptr)==icon.bank then chosen=icon end end
 if not chosen then return end
 local sp=s['cpu.sp'];local ret=emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1
 local kind=ret==C.draw_returns.hud and'hud'or ret==C.draw_returns.shot and'shell'or nil
 assert(kind and bank(ret-3)==C.draw_returns.bank,'Genuine icon HUD/shot caller PC and physical bank')
 local task=C.plan[index];assert(task.kind=='copy'and r('KbCopy')==task.family and chosen.family==task.family,'Actually swallowed matching source family')
 if kind=='shell'then local i=r('KbSavedSlot');assert(task.family==2 and i<3 and r('KbShotType',i)==3 and r('KbShotKind',i)==2,'Actual green shell source actor and pool owner')end
 for i,v in ipairs(chosen.bytes)do assert(emu.read(ptr+i-1,emu.memType.nesDebug)==v,'Actual corrected icon record bytes')end
 paletteScope={sp=sp,kind=kind,icon=chosen,offset=r('CurrentOAMOffset'),rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0,x=r('R4'),xh=r('R5'),y=r('R6'),update=updates,wall=wall}
end)
hook('IconDrawReturn',function(s)
 local o=paletteScope;paletteScope=nil;if not o then return end
 assert(s['cpu.sp']==o.sp,'Same genuine icon Draw return SP')
 local length=o.icon.bytes[1];local after=r('CurrentOAMOffset')
 if o.offset+length>255 then assert(after==o.offset,'Original full-OAM rejection');return end
 assert(after==o.offset+length,'Original icon OAM span retained')
 local parts={}
 for j=0,length//4-1 do
  local source=length//4-1-j;local at=2+source*4;local xoff=o.icon.bytes[at+3];local yoff=o.icon.bytes[at+2]
  if xoff>=128 then xoff=xoff-256 end;if yoff>=128 then yoff=yoff-256 end
  local x,y=o.x+xoff,o.y+yoff;assert(o.xh==0 and x>=0 and x<256 and y>=0 and y<240,'This source icon is inside real visible coordinate bounds')
  local slot=(o.offset+o.rotation+j*4)&255;local want={y,o.icon.bytes[at],o.icon.bytes[at+1]&0xf3,x}
  assert(want[3]&3==1,'Original world palette1 chosen; high flip/priority retained')
  for k,v in ipairs(want)do assert(emu.read(512+slot+k-1,emu.memType.nesDebug)==v,'Actual renderer emitted exact original tile/position/flip plus corrected palette')end
  parts[#parts+1]={slot=slot,bytes=want}
 end
 rec.palette_draws=rec.palette_draws or{};rec.palette_draws[o.kind]={parts=parts,update=updates,wall=wall,record=o.icon.pc,family=o.icon.family}
 if not rec['palette_first_'..o.kind]then rec['palette_first_'..o.kind]=true;event('actual-world-palette1-'..o.kind,o.icon.family)end
end)
hook('IconDmaComplete',function()
 if not pending or not rec or not rec.palette_draws then return end
 for kind,o in pairs(rec.palette_draws)do
  local match=true
  for _,p in ipairs(o.parts)do for k,v in ipairs(p.bytes)do if k==3 then v=v&0xe3 end;if emu.read(p.slot+k-1,emu.memType.nesSpriteRam)~=v then match=false end end end
  if match then
   local palette={};local want=C.palette_by_area[r('AreaType')+1]
   for i=1,3 do palette[i]=emu.read(0x3f14+i,emu.memType.nesPpuDebug);assert(palette[i]==want[i],'Actual original area sprite palette1, not Kirby pink palette0')end
   local key='palette_'..kind..'_commits';rec[key]=(rec[key]or 0)+1
   if rec[key]<=2 then rec['palette_committed_'..kind]={parts=o.parts,source_update=o.update,DMA=dmas+1,update=updates,wall=wall,palette=palette};event('actual-committed-palette1-'..kind,rec[key])end
  end
 end
end)
'''
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert not out.exists();rom=B/'kirby_world_icon_palette.nes';assert sha(rom)==SHA;b=scoped_load(rom)
 controls=B/'kirby_world_icon_palette_controls.json';proof=json.loads(controls.read_text());assert proof['passed']and proof['candidate_sha256']==SHA;source=proof['acquired_three_families'];assert source['passed']and len(source['plan'])==3
 old=B/'current-bdf9-kirby-hard-copies-low-v2';cfg=json.loads((old/'config.json').read_text());cfg.update(ROM_sha256=SHA,unit='world-icon-palettes-three',plan=source['plan'])
 fixture=R/'tools/audit/current_kirby_meta_earned_v1.lua';text=fixture.read_text();changes=[]
 def replace(before,after):
  nonlocal text
  assert text.count(before)==1,before;text=text.replace(before,after);changes.append(dict(before=before,after=after))
 replace("local function target(task)\n if rec.target then return end", "local function target(task)\n if rec.target then return end\n if task.kind=='copy'and task.family==2 and not rec.sample then return end -- Keep real shell visible through two committedDMAs before target.")
 replace("local function finishCase()\n assert(pool()", "local function finishCase()\n local task=C.plan[index];assert(task.kind=='copy'and rec.sample and(rec.palette_hud_commits or 0)>=2,'Actual corrected HUD icon through two complete realDMAs');if task.family==2 then assert((rec.palette_shell_commits or 0)>=2,'Actual green shell projectile through two complete realDMAs')end\n assert(pool()")
 oldsample="then rec.sample=true;screenshot=task.name..'.png'end";assert text.count(oldsample)==1;replace(oldsample,"then rec.palette_capture_requested=true end")
 marker='-- All callback registration is startup-static.';assert text.count(marker)==1;replace(marker,OBSERVER+marker)
 replace(" if screenshot then\n  assert(images<8", " if rec and rec.palette_capture_requested and not rec.sample and phase=='use'and r('KbAction')==4 and(rec.palette_hud_commits or 0)>=2 and(C.plan[index].family~=2 or(rec.palette_shell_commits or 0)>=2 and pool()>0)then rec.sample=true;screenshot=C.plan[index].name..'.png'end\n if screenshot then\n  assert(images<8")
 begin=marker;end="emu.addEventCallback(function()\n if not entered";original=fixture.read_text();assert text[text.index(begin):text.index(end)]==original[original.index(begin):original.index(end)]and len(text[text.index(begin):text.index(end)].encode())==4058
 assert text.count('emu.write(')==2 and text.count('emu.takeScreenshot(')==1 and'removeMemoryCallback'not in text
 def hook(name,d=0,size=3):
  at=location(b,name)+d;k=(at-16)//8192;bs=list(b['raw'][at:at+size]);banks=[k]
  if k==127:assert b['raw'][16+125*8192+(at-16)%8192:16+125*8192+(at-16)%8192+size]==bytes(bs);banks=[125,127]
  return dict(pc=address(b,name)+d,banks=banks,bytes=bs,source_symbol=name,source_delta=d)
 for key,h in list(cfg['hooks'].items()):
  fresh=hook(h['source_symbol'],h.get('source_delta',0),len(h['bytes']));assert fresh==h;cfg['hooks'][key]=fresh
 cfg['hooks']['IconDrawEntry']=hook('KbDrawShots::Draw');size=int(b['syms']['KbDrawShots']['size'],0);start=location(b,'KbDrawShots');ret_delta=address(b,'KbDrawShots')+size-1-address(b,'KbDrawShots::Draw');assert b['raw'][start+size-1]==96;cfg['hooks']['IconDrawReturn']=hook('KbDrawShots::Draw',ret_delta,1);cfg['hooks']['IconDmaComplete']=cfg['hooks']['DmaComplete']
 draw=address(b,'KbDrawShots::Draw');jsr=bytes([32,draw&255,draw>>8]);body=b['raw'][start:start+size];calls=[address(b,'KbDrawShots')+i+3 for i in range(size-2)if body[i:i+3]==jsr];assert len(calls)==4
 cfg['draw_returns']=dict(shot=calls[0],hud=calls[3],bank=(start-16)//8192)
 cfg['palette_icons']={}
 for family,icon in[(2,1),(7,6),(9,8)]:
  name='KbIcon'+str(icon);at=location(b,name);length=b['raw'][at];data=list(b['raw'][at:at+length+1]);assert all(data[2+i*4]&3==1 for i in range(length//4));cfg['palette_icons'][family]=dict(family=family,pc=address(b,name),bank=(at-16)//8192,bytes=data)
 cfg['palette_by_area']=[x['sprite_palette1']for x in proof['original_SMB']['area_palettes']]
 for n in'R0 R1 R3 R4 R5 R6 R7 CurrentOAMOffset GuestOamRotationActive RgOamRotation AreaType KbSavedSlot KbShotKind'.split():cfg['ram'][n]=address(b,n)
 for n,value in cfg['ram'].items():assert address(b,n)==value
 for d in source['cases']:
  for hit in d['defeats']:assert any(q['pc']==hit['return_PC']and q['bank']==hit['callerA']for q in cfg['defeat_returns'])
 emitted=lua(cfg);pre='local C=assert(CURRENT_KIRBY_META_EARNED);assert(C.variant==0 and C.mode==1 and #C.plan==3)\n'
 for family in[2,7,9]:assert f'[{family}]='in emitted and f'["{family}"]='not in emitted;pre+=f'assert(type(C.palette_icons[{family}])=="table" and C.palette_icons[{family}].family=={family})\n'
 for name,value in sorted(cfg['ram'].items()):pre+=f'assert(C.ram.{name}=={value},"actual RAM {name}")\n'
 assert b['raw'][location(b,'X5MenuCharacters')+12]==13
 out.mkdir(parents=True);put(out/'config.json',cfg);put(out/'source-controls.json',source);fp=out/'fixture.lua';fp.write_text(text,encoding='utf-8',newline='\n');(out/'run.lua').write_text('CURRENT_KIRBY_META_EARNED='+emitted+'\n'+pre+'dofile([=['+fp.as_posix()+']=])\n',encoding='utf-8',newline='\n')
 layout=dict(passed=True,native_run=False,old_helper_byte_exact=True,old_helper_sha256=sha(fixture),owned_generated_fixture_changes=changes,mechanics_inputs_and_guard_caps_unchanged_except_target_wait_for_real_two_DMA_sample=True,source_scope='Fresh exact-candidate original complete Main acquire/Down/use/discard for three affected families; CPU render controls cover214 cases,74 foreign/ordinary Main calls and160 actualIRQ sites. Native-specific committed-DMA delay and callback ownership need actual execution; not simulated Lua proof.',actual_draw_JSR_returns=calls,new_draw_hooks={n:cfg['hooks'][n]for n in['IconDrawEntry','IconDrawReturn','IconDmaComplete']},live_observer='Startup-static actual helper/returnPC/SP/physical bank/record bytes, exact emitted OAM attributes preserving flips, actual256DMA-backed physical record match twice and actual area palette1. Extra source hooks read-only; no callback registrations at runtime. Same source and hardware guards retained; new palette assertions are additional, never replacement.',acquisition='Real warmed inhale enemy0/10/14 -> Down swallow families2/7/9, actual ability action/target contact/cleanup/Select discard. No copy/HP/form/shot or resource outcomes written.',limits='Prepared only. Three facing-right ground Hard components, not underwater whole scene/all14copy families/full route/music/blanket graphics. Native target delay only green shell so image can precede real target contact; no source/game action changes.')
 put(out/'source-layout.json',layout)
 argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'];put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,requires_existing_ROOT_capture_gate=True,argv=argv))
 paths=[Path(__file__),fixture,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),controls,B/'kirby_world_icon_palette_build.json',B/'kirby_world_icon_palette_icons.inc',B/'kirby_world_icon_palette_implementation.patch',old/'config.json',R/'tools/audit/current_kirby_meta_earned_cpu_v1.py',R/'tools/audit/kirby_icon_palette_controls_v1.py',R/'tools/audit/kirby_icon_palette_build_v1.py',R/'tools/audit/observe_chip_committed_write.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',R/'tools/run_mesen.py']
 paths +=[R/'src'/n for n in['kirby_copy_icons.inc','kirby_draw.s','kirby_core.s','kirby_weapons.s','kirby_state.inc','metasprite_engine.s','sprite_render.s','reset.s']]
 paths +=[out/n for n in['config.json','fixture.lua','run.lua','source-controls.json','source-layout.json','command.json']]
 ready=dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=SHA,identity='kirby',mode=1,unit='world-icon-palettes-three',source_GameLoops=source['GameLoop_calls'],source_passed=True,caps=dict(wall_frames=8000,updates=3000,host_seconds=1200,bytes=2000000000,files=64,PNGs=8,containers=0),actual_source_menu_index=12,actual_raw_character=13,precise_palette_scope=[2,7,9],scope=layout['acquisition'],limits=layout['limits'],bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths]);put(out/'prepared-not-run.json',ready);print(json.dumps(dict(prepared=True,native_run=False,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths))))
if __name__=='__main__':main()
