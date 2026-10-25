"""Read-only exact-input prefix: find why an actual HUD IRQ fired on line54."""
from pathlib import Path
import argparse,csv,gzip,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
OBSERVER=r'''local frame=0
local log=assert(io.open(IRQ_OUT..'timing.csv','w'))
log:write('frame,ppuFrame,scanline,dot,cycle,event,pc,p,disable,nmiDisable,mask,pause,ui,pending,ctrl,offset,value\n')
local dump=assert(io.open(IRQ_OUT..'vram.csv','w'));dump:write('frame,scanline,event,control,offset,bytes\n')
local overflow=assert(io.open(IRQ_OUT..'status-overflow.csv','w'));overflow:write('frame,ppuFrame,scanline,pc,address,value,x,y,offset,control,bank\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function emit(kind,value)
 if frame<IRQ_START or frame>IRQ_END then return end
 local s=emu.getState()
 local row={frame,s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle']or s['ppu.dot']or-1,s['cpu.cycleCount'],kind,s['cpu.pc'],s['cpu.ps']or s['cpu.p']or-1,r('DisableScreenFlag'),r('NmiDisable'),r('Mirror_PPUMASK'),r('GamePauseStatus'),r('Z2UiState'),r('Z2PanelPending'),r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer1_Offset'),value or-1}
 log:write(table.concat(row,',')..'\n');log:flush()
end
for _,name in ipairs({'NonMaskableInterrupt','NonMaskableInterrupt_RTI','IrqScrollSplit','AudioUpdate','SamusFreezeUpdateScreen'})do
 local at=L[name]
 if at then emu.addMemoryCallback(function()
  if name~='NonMaskableInterrupt_RTI' and B[name]and emu.convertAddress(at).address//8192~=B[name]then return end
  emit(name)
  if (name=='NonMaskableInterrupt' or name=='SamusFreezeUpdateScreen')and frame>=IRQ_START and frame<=IRQ_END then
   for _,buffer in ipairs({'VRAM_Buffer1','VRAM_Buffer2','SmFreezePalettePacket'})do
    local b={}for i=0,(buffer=='SmFreezePalettePacket'and 6 or 90)do b[#b+1]=string.format('%02x',emu.read(L[buffer]+i,emu.memType.nesDebug))end
    local s=emu.getState();dump:write(table.concat({frame,s['ppu.scanline'],name..'-'..buffer..'-ptr'..r('NmiR0')..'x'..r('NmiR1')..'-freeze'..r('SmFreezePalettePending'),r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer1_Offset'),table.concat(b,' ')},',')..'\n');dump:flush()
   end
  end
 end,emu.callbackType.exec,at)end
end
emu.addMemoryCallback(function(at,value)emit(string.format('write-%04x',at),value)end,emu.callbackType.write,0x5203,0x5204)
emu.addMemoryCallback(function(at,value)emit(string.format('write-%04x',at),value)end,emu.callbackType.write,0x2000,0x2001)
emu.addMemoryCallback(function(at,value)
 local s=emu.getState();local pc=s['cpu.pc']
 overflow:write(table.concat({frame,s['ppu.frameCount'],s['ppu.scanline'],pc,at,value,s['cpu.x'],s['cpu.y'],r('VRAM_Buffer1_Offset'),r('VRAM_Buffer_AddrCtrl'),emu.convertAddress(pc).address//8192},',')..'\n');overflow:flush()
end,emu.callbackType.write,L.VRAM_Buffer2_Offset,L.VRAM_Buffer2+33)
emu.addEventCallback(function()
 frame=frame+1
 if frame==IRQ_END then log:close();dump:close();overflow:close();emu.stop(0)end
end,emu.eventType.endFrame)
'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--start',type=int,default=1965);p.add_argument('--end',type=int,default=1985)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);digest=sha(a.rom)
    source=json.loads((a.route/'manifest.json').read_text());assert source['ROM_sha256']==digest
    symbols={};status_size=None
    for line in a.rom.with_suffix('.dbg').read_text().splitlines():
        if line.startswith('sym\t'):
            z=dict(v.split('=',1)for v in line[4:].split(',')if '=' in v)
            if 'val'in z:symbols[z['name'].strip('"')]=int(z['val'],0)
            if z.get('name')=='"NativeRarePrintStatusBarNumbersCore"':status_size=int(z['size'],0)
    aliases=''.join('L['+json.dumps(n)+']='+str(symbols[n])+'\n'for n in ['Z2UiState','Z2PanelPending'])
    assert status_size
    from check_tmnt_render_oa import load,location
    bank=(location(load(a.rom),'NativeRarePrintStatusBarNumbersCore')-16)//8192
    observer=a.output/'observer.lua';observer.write_text(aliases+'IRQ_OUT='+json.dumps(a.output.resolve().as_posix()+'/')+'\nIRQ_START='+str(a.start)+'\nIRQ_END='+str(a.end)+'\nIRQ_STATUS_BANK='+str(bank)+'\nIRQ_STATUS_START='+str(symbols['NativeRarePrintStatusBarNumbersCore'])+'\nIRQ_STATUS_END='+str(symbols['NativeRarePrintStatusBarNumbersCore']+status_size)+'\n'+OBSERVER)
    run=(a.route/'run.lua').read_text();old='out='+json.dumps(a.route.resolve().as_posix()+'/')
    assert run.count(old)==run.count('replay=nil')==1
    run=run.replace(old,'out='+json.dumps(a.output.resolve().as_posix()+'/')).replace('replay=nil','replay='+json.dumps((a.route.resolve()/'inputs.csv').as_posix())).replace('capture=12,','capture=0,')
    at=run.index('dofile(');run=run[:at]+'dofile('+json.dumps(observer.resolve().as_posix())+')\n'+run[at:]
    script=a.output/'run.lua';script.write_text(run)
    while True:
        z=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-CimInstance Win32_Process -Filter \"Name='Mesen.exe'\").Count"],capture_output=True,text=True)
        assert z.returncode==0,z.stderr
        if int(z.stdout.strip())<2:break
        time.sleep(2)
    args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','90',
        '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(a.output/'host.log').write_text(z.stdout+z.stderr)
    assert z.returncode==0,(z.stdout+z.stderr)[-1200:]
    for name in ['inputs.csv','trace.csv']:
        old=list(csv.reader((a.route/name).open()));new=list(csv.reader((a.output/name).open()))
        assert new==old[:len(new)],name
    (a.output/'binding.json').write_text(json.dumps(dict(read_only=True,ROM_sha256=digest,
        route_manifest_sha256=sha(a.route/'manifest.json'),observer_sha256=sha(observer),exact_prefix=True,
        physical_frame_window=[a.start,a.end]),indent=2)+'\n')
    print('PASS exact unchanged prefix; timing trace retained',flush=True)
if __name__=='__main__':main()
