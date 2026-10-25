"""Read-only PPU/map evidence around a suspicious scrolling-edge column."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'mario-edge-observer-v1';out.mkdir(exist_ok=False)
route=D/'known-routes-v3/discover-mario-easy';rom=D/'food-candidate-v3/candidate.nes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
observer=out/'observer.lua';observer.write_text('EDGE_OUT='+json.dumps(out.as_posix()+'/')+'\n'+r'''
local frame=0
local raw=assert(io.open(EDGE_OUT..'snapshots.bin','wb'))
local log=assert(io.open(EDGE_OUT..'state.csv','w'))
local writes=assert(io.open(EDGE_OUT..'ppu-writes.csv','w'))
local fields={'ScreenLeft_PageLoc','ScreenLeft_X_Pos','Player_PageLoc','Player_X_Position','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','AreaParserTaskNum','CurrentColumnPos','ColumnSets','ScrollThirtyTwo','HorizontalScroll','Mirror_PPUCTRL_REG1','Mirror_PPUMASK','DisableScreenFlag','ShouldSkipDrawSprites'}
log:write('frame,ppuFrame,cpuCycle,'..table.concat(fields,',')..'\n')
writes:write('frame,address,value,pc,physicalAddress,scanline,cpuCycle\n')
local stop=emu.stop
emu.stop=function(code)raw:close();log:close();writes:close();stop(code)end
local function r(n)if not L or not L[n]then return -1 end;return emu.read(L[n],emu.memType.nesDebug)end
emu.addMemoryCallback(function(addr,value)
 if frame<1449 or frame>1950 then return end
 local s=emu.getState();local pc=s['cpu.pc'];local p=emu.convertAddress(pc)
 writes:write(table.concat({frame+1,addr,value,pc,p and p.address or -1,s['ppu.scanline'],s['cpu.cycleCount']},',')..'\n')
end,emu.callbackType.write,0x2000,0x2007)
emu.addEventCallback(function()
 frame=frame+1
 if frame<1450 or frame>1950 then return end
 local s=emu.getState();assert(s['ppu.frameCount']==frame)
 local row={frame,s['ppu.frameCount'],s['cpu.cycleCount']}
 for _,n in ipairs(fields)do row[#row+1]=r(n)end
 log:write(table.concat(row,',')..'\n')
 local data={}
 for a=0x2000,0x27ff do data[#data+1]=string.char(emu.read(a,emu.memType.nesPpuDebug))end
 for i=0,415 do data[#data+1]=string.char(emu.read(L.Block_Buffer_1+i,emu.memType.nesDebug))end
 raw:write(string.pack('<I4',frame)..table.concat(data))
end,emu.eventType.endFrame)
''')
t=(route/'run.lua').read_text();old='out='+json.dumps(route.as_posix()+'/');assert t.count(old)==1;t=t.replace(old,'out='+json.dumps(out.as_posix()+'/'));assert t.count('replay=nil')==1;t=t.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix()));assert t.count('capture=12,')==1;t=t.replace('capture=12,','capture=0,');at=t.index('dofile(');t=t[:at]+'dofile('+json.dumps(observer.as_posix())+')\n'+t[at:];script=out/'run.lua';script.write_text(t)
cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','120','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
with(out/'host.log').open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0
for name in ['inputs.csv','trace.csv']:assert(out/name).read_bytes()==(route/name).read_bytes()
assert json.loads((out/'result.json').read_text())==json.loads((route/'result.json').read_text())
q=dict(passed=True,goal_complete=False,ROM_sha256=sha(rom),observer_sha256=sha(observer),driver_sha256=sha(Path(__file__)),original_manifest_sha256=sha(route/'manifest.json'),fixed_inputs_and_trace_exact=True,snapshot_frames=501,raw_sha256=sha(out/'snapshots.bin'),writes_sha256=sha(out/'ppu-writes.csv'),scope='Read-only actual PPU nametable and native logical-map snapshots,1450..1950 inclusive, plus native register writes. Exact original controller inputs/state/CPU-cycle trace and endpoint retained. This establishes evidence only; whether the right-edge column is an engine defect remains to be analyzed.')
(out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
