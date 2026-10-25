"""Frozen-v1 native controls/timing plus actual NMI return for overrun attribution."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--event',default='0x21');p.add_argument('--profile',default='basic');p.add_argument('--run',action='store_true');a=p.parse_args();out=a.output.resolve()
 cmd=[sys.executable,str(ROOT/'tools/audit/cv3_remaining_sfx_native_v7.py'),'--rom',str(a.rom),'--output',str(out),'--mode',str(a.mode),'--event',a.event,'--profile',a.profile]
 subprocess.run(cmd,cwd=ROOT,check=True);original=(out/'run.lua').read_bytes();(out/'original-v7-script.lua').write_bytes(original);cfg=json.loads((out/'configuration.json').read_text());b=load(a.rom);q=qualified(a.rom)
 for name,pc in [('GameLoop',address(b,'GameLoop')),('NoLagSoDraw',q[('NoLagSoDraw',)]),('SkipDrawingCauseLagged',q[('SkipDrawingCauseLagged',)])]:
  offset=location(b,'GameLoop')if name=='GameLoop'else location(b,'GameCoreRoutine')+pc-address(b,'GameCoreRoutine');cfg['hooks'][name]=dict(address=pc,physical_bank=(offset-16)//8192,bytes=list(b['raw'][offset:offset+3]))
 for name in ['NmiDisable','NmiSkipped','ShouldSkipDrawSprites','FramesSinceLastSpriteDraw']:cfg['ram'][name]=address(b,name)
 for name in ['Cv3FxResidentDispatch','Cv3FxResidentNoise']:
  if name in b['syms']:
   offset=location(b,name);cfg['hooks'][name]=dict(address=address(b,name),physical_bank=(offset-16)//8192,bytes=list(b['raw'][offset:offset+3]));cfg['perf_names'].append(name)
 offset=location(b,'IrqScrollSplit')+67;assert b['raw'][offset]==0x40
 cfg['hooks']['IrqReturn']=dict(address=address(b,'IrqScrollSplit')+67,physical_bank=(offset-16)//8192,bytes=[0x40])
 text=original.decode().split('\n',1)[1];timing=r'''
local timing=assert(io.open(OUTPUT..'deadline-timing.csv','w'))
timing:write('kind,wall,age,audioEpoch,cpuCycle,ppuFrame,scanline,dot,pc,bank,sp,interruptedPC,stackP,nmiDisable,nmiSkipped,skipDraw,framesSinceDraw,newValue,interruptedBank\n')
local function deadlineStamp(kind,interrupted,stackP,newValue)
 if not entered or done then return end
 local s=emu.getState();local pc=s['cpu.pc']
 timing:write(table.concat({kind,wall,age,audioEpoch,s['cpu.cycleCount'],s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],pc,bank(pc),s['cpu.sp'],interrupted or -1,stackP or -1,r('NmiDisable'),r('NmiSkipped'),r('ShouldSkipDrawSprites'),r('FramesSinceLastSpriteDraw'),newValue or -1,interrupted and bank(interrupted)or -1},',')..'\n');timing:flush()
end
emu.addMemoryCallback(function()
 if not entered or done or not valid('NonMaskableInterrupt')then return end
 local sp=emu.getState()['cpu.sp']
 -- Real hardware NMI stack at the entry before the first handler PHA:
 -- [SP+1]=P, [SP+2]=return-PC low, [SP+3]=return-PC high.
 local lo=emu.read(0x100|((sp+2)&255),emu.memType.nesDebug)
 local hi=emu.read(0x100|((sp+3)&255),emu.memType.nesDebug)
 local p=emu.read(0x100|((sp+1)&255),emu.memType.nesDebug)
 deadlineStamp('NMI-entry',lo|hi<<8,p)
end,emu.callbackType.exec,C.hooks.NonMaskableInterrupt.address)
for _,name in ipairs({'GameLoop','PauseSkip','NoLagSoDraw','SkipDrawingCauseLagged','NmiReturn','IrqScrollSplit','IrqReturn'})do
 local n=name
 emu.addMemoryCallback(function()if valid(n)then deadlineStamp(n)end end,emu.callbackType.exec,C.hooks[n].address)
end
emu.addMemoryCallback(function(_,value)
 if not entered or done then return end
 local pc=emu.getState()['cpu.pc'];local p=C.hooks.PauseSkip
 if value==0 and bank(pc)==p.physical_bank and pc>=p.address+2 and pc<=p.address+5 then deadlineStamp('publication-write',nil,nil,value)end
end,emu.callbackType.write,C.ram.NmiDisable)
'''
 assert text.count('local perf=assert')==1;text=text.replace('local perf=assert',timing+'\nlocal perf=assert',1)
 script=out/'run.lua';script.write_bytes(('CV3_REMAINING_NATIVE_CONFIG='+lua(cfg)+'\n'+text).encode());assert 'True'not in script.read_text().splitlines()[0]and'False'not in script.read_text().splitlines()[0]
 (out/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n');(out/'original-v7-bindings.json').write_bytes((out/'bindings.json').read_bytes());bindings=json.loads((out/'bindings.json').read_text());bindings.update(script_sha256=sha(script),original_v7_script_sha256=sha(out/'original-v7-script.lua'),additional_timing_tool_sha256=sha(__file__),deadline_timing_scope='NMI entry before PHA actual hardware stack PC/P, real publication write and actual draw branch. Instrumentation only; no game-memory writes or mode overrides.')
 shutil.copyfile(__file__,out/'frozen'/Path(__file__).name);(out/'bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
 if not a.run:print(json.dumps(dict(prepared=True,executed=False,ROM_sha256=sha(a.rom),script_sha256=sha(script),output=str(out)),indent=2));return
 cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/mesen2/Mesen.exe',str(script),str(a.rom.resolve()),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False);proof.update(ROM_sha256=sha(a.rom),bindings_sha256=sha(out/'bindings.json'),profile=a.profile,event=int(a.event,0),mode=a.mode,emulator_exit=r.returncode,passed=not r.returncode and proof.get('passed',False),accepted=False,scope='Unchanged v7 real-controller source/control/strict DMA fixtures plus actual deadline entry/publication/draw timestamps. No waveform or complete campaign certification.');(out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=r.returncode,output=str(out))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
