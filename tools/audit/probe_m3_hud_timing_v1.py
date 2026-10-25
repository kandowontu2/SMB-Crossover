"""Read-only fixed-controller replay of the actual MMC5 SMB3 HUD font deadline.

Keeps a failed graphic assertion as evidence; does not change game state or ROM.
"""
from pathlib import Path
import argparse, csv, hashlib, json, subprocess, sys
import numpy as np
from PIL import Image
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
OBSERVER = r'''
local C=HUD_PROBE
local f=assert(io.open(C.out..'hud-events.csv','w'))
f:write('frame,scanline,dot,cpuCycle,kind,value,pc,bank,active,font,disable\n')
local upper,wall,checks=0,0,0
local bad,saved={},nil
local function r(n)return emu.read(C.ram[n],emu.memType.nesDebug)end
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or -1 end
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function window(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
local function event(kind,v)
 local s=emu.getState();local pc=s['cpu.pc']
 f:write(table.concat({s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.cycleCount'],kind,v or -1,pc,bank(pc),r('InvHudActive'),r('InvHudPhysical')+256*r('X5HudChrUpper'),r('DisableScreenFlag')},',')..'\n')
end
emu.addMemoryCallback(function(_,v)upper=v&3;event('5130',v)end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)event('5128',v+256*upper)end,emu.callbackType.write,0x5128)
emu.addMemoryCallback(function(_,v)event('mask',v)end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)event('active-write',v)end,emu.callbackType.write,C.ram.InvHudActive)
emu.addMemoryCallback(function(_,v)event('reload-write',v)end,emu.callbackType.write,C.ram.ReloadCHRBank)
for n,h in pairs(C.hooks)do
 emu.addMemoryCallback(function()
  if bank(h.address)~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound hook '..n)end
  event(n)
  if n=='nmi' then
   local s=emu.getState();local sp=s['cpu.sp']
   local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
   saved={a=bank(0xa000),c=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,fields={},sp=sp,cpu_a=s['cpu.a']}
   saved.wa=saved.a~=saved.sa and window(pc,0x5115,C.ram.CurrentBank)
   saved.wc=saved.c~=saved.sc and window(pc,0x5116,C.ram.CurrentBankC)
   for _,a in ipairs(C.smc)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end
  elseif n=='nmi_return' and saved then
   assert(bank(0xa000)==(saved.wa and saved.sa or saved.a)and bank(0xc000)==(saved.wc and saved.sc or saved.c),'NMI A/C restoration')
   assert(r('CurrentBank')&127==saved.sa and r('CurrentBankC')&127==saved.sc,'NMI shadow restoration')
   assert(emu.getState()['cpu.sp']==saved.sp and emu.getState()['cpu.a']==saved.cpu_a,'NMI SP/A restoration')
   for i,a in ipairs(C.smc)do assert(saved.fields[i]==emu.read(a,emu.memType.nesDebug),'NMI five SMC operands')end
   saved=nil
  end
 end,emu.callbackType.exec,h.address)
end
local function capture(frame,screen)
 local p=assert(io.open(C.out..string.format('frame-%06d.argb',frame),'wb'))
 for _,v in ipairs(screen)do p:write(string.pack('<I4',v))end
 p:close()
end
emu.addEventCallback(function()
 wall=wall+1
 local s=emu.getState();assert(s['ppu.frameCount']==wall,'Actual PPU frame identity')
 local bar=true
 for i=0,7 do
  local t=emu.read(0x202b+i,emu.memType.nesPpuDebug)
  if t<0x30 or t>0x35 then bar=false end
 end
 if r('SelectedCharacter')==17 and bar and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('DisableScreenFlag')==0 then
  checks=checks+1
  local screen=emu.getScreenBuffer();local bg=screen[8*256+1]&0xffffff
  local mismatch=0
  for tile=0,7 do
   local t=emu.read(0x202b+tile,emu.memType.nesPpuDebug)
   for y=0,7 do
    local at=545*1024+t*16+y
    local bits=emu.read(at,emu.memType.nesChrRom)|emu.read(at+8,emu.memType.nesChrRom)
    for x=0,7 do
     local want=(bits&(128>>x))~=0
     local actual=(screen[(8+y)*256+88+tile*8+x+1]&0xffffff)~=bg
     if want~=actual then mismatch=mismatch+1 end
    end
   end
  end
  if mismatch>0 then bad[#bad+1]={frame=wall,pixels=mismatch};event('pixel-mismatch',mismatch)end
  if mismatch>0 or(wall>=C.capture_first and wall<=C.capture_last)then capture(wall,screen)end
 end
 if wall>=C.limit then
  f:close()
  local p=assert(io.open(C.out..'native.json','w'))
  p:write(string.format('{"passed":%s,"frames":%d,"pixel_frames":%d,"bad":[',#bad==0 and'true'or'false',wall,checks))
  for i,q in ipairs(bad)do if i>1 then p:write(',')end;p:write(string.format('{"frame":%d,"pixels":%d}',q.frame,q.pixels))end
  p:write('],"game_state_writes":false}');p:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['rom','route','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--frames',type=int,default=1370)
    p.add_argument('--capture-first',type=int,default=1348)
    p.add_argument('--capture-last',type=int,default=1360)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    b=scoped_load(a.rom)
    names=['OperMode','OperMode_Task','GameEngineSubroutine','InvHudActive','InvHudPhysical','X5HudChrUpper','DisableScreenFlag','ReloadCHRBank','CurrentBank','CurrentBankC','SelectedCharacter']
    def hook(name,delta=0):
        at=location(b,name)+delta
        return dict(address=address(b,name)+delta,bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
    hooks={n:hook(s)for n,s in [('nmi','NonMaskableInterrupt'),('screen','UpdateScreen'),('early_gate','PnPaletteScreenUpdate'),('audio','RemainingAudioBegin')]}
    hooks['nmi_return']=hook('NonMaskableInterrupt',int(b['syms']['NonMaskableInterrupt']['size'],0)-1)
    config=dict(out=out.as_posix()+'/',limit=a.frames,capture_first=a.capture_first,capture_last=a.capture_last,
                ram={n:address(b,n)for n in names},hooks=hooks,
                smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    observer=out/'observer.lua';observer.write_text('HUD_PROBE='+lua(config)+'\n'+OBSERVER,encoding='utf-8')
    run=(a.route/'run.lua').read_text();old='out='+json.dumps(a.route.as_posix()+'/');assert run.count(old)==1
    run=run.replace(old,'out='+json.dumps(out.as_posix()+'/'))
    assert run.count('replay=nil')==1
    run=run.replace('replay=nil','replay='+json.dumps((a.route/'inputs.csv').as_posix()))
    run=run.replace('capture=12,','capture=0,');at=run.index('dofile(')
    script=out/'run.lua';script.write_text(run[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+run[at:])
    command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),'--timeout','90',
             '--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    with(out/'host.log').open('w')as log:result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    native=json.loads((out/'native.json').read_text())if(out/'native.json').exists()else{}
    captures=[]
    for raw in sorted(out.glob('frame-*.argb')):
        values=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256)
        rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
        png=raw.with_suffix('.png');Image.fromarray(rgb).save(png)
        with Image.open(png)as saved:assert np.array_equal(np.asarray(saved.convert('RGB')),rgb)
        captures.append(dict(frame=int(raw.stem.split('-')[1]),raw_sha256=sha(raw),png_sha256=sha(png),RGB_sha256=hashlib.sha256(rgb.tobytes()).hexdigest()))
    events=list(csv.DictReader((out/'hud-events.csv').open()))
    font_writes=[r for r in events if r['kind']=='5128'and r['value']=='545']
    late=[r for r in font_writes if 8<=int(r['scanline'])<240]
    proof=dict(passed=result.returncode==0 and native.get('passed')is True and not late,goal_complete=False,ROM_sha256=sha(a.rom),exit=result.returncode,native=native,
               font_publications=len(font_writes),late_font_publications=late,
               source_route_manifest_sha256=sha(a.route/'manifest.json'),source_inputs_sha256=sha(a.route/'inputs.csv'),
               tool_sha256=sha(Path(__file__)),observer_sha256=sha(observer),events_sha256=sha(out/'hud-events.csv'),captures=captures,
               scope='Read-only actual PPU eight SMB3 P-bar tile masks, original recorded menu/controller inputs replayed on explicit ROM. All font writes timestamped by actual PPU scanline/dot, actual bank-bound NMI/early screen/audio hooks, A/C and all five SMC operands guarded. A fixed prefix, not a campaign or sprite/scroll fidelity proof.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k]for k in ['passed','ROM_sha256','exit','native']}));return 0 if proof['passed']else 1


if __name__=='__main__':raise SystemExit(main())
