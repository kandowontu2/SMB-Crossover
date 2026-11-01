"""Read the original Karnov hardware palette and player CHR latch at cold start."""
from pathlib import Path
import hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from run_mesen import run
from mesen_session_guard_v1 import require_free_workspace
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-palette-native-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
LUA='''local frame,updates=0,0
emu.addEventCallback(function()local p={};if emu.read(0x10,emu.memType.nesDebug)~=11 then p.start=frame>=120 and frame%60<3 end;emu.setInput(p,0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()if emu.read(0x10,emu.memType.nesDebug)==11 then updates=updates+1 end end,emu.callbackType.exec,0xf297)
emu.addEventCallback(function()
 frame=frame+1
 if updates>=40 then
  local pal={};for i=0,31 do pal[#pal+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
  local page=emu.read(0x15,emu.memType.nesDebug);local match=true
  for i=0,1023 do if emu.read(0x1000+i,emu.memType.nesPpuDebug)~=emu.read(page*1024+i,emu.memType.nesChrRom)then match=false end end
  assert(match,'Original player CHR page matches native PPU window4')
  local f=assert(io.open(OUTPUT..'palette.json','w'));f:write('{"passed":true,"frame":'..frame..',"updates":'..updates..',"CHR_page":'..page..',"palette":['..table.concat(pal,',')..']}\\n');f:close()
  f=assert(io.open(OUTPUT..'standing.png','wb'));f:write(emu.takeScreenshot());f:close();print('KARNOV_PALETTE_PASS');emu.stop(0)
 elseif frame>=700 then assert(false,'700 frame bound')end
end,emu.eventType.endFrame)
'''


def main():
    assert sha(ROM)==EXPECTED;O.mkdir(exist_ok=True);assert not(O/'capture').exists();(O/'capture').mkdir();controller=O/'controller.lua';controller.write_text(LUA,encoding='utf-8')
    require_free_workspace(R,ROM);os.environ['SMB_RUN_OUTPUT']=str(O/'capture')
    code=run(controller,ROM,timeout=120,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false']);assert code==0
    q=json.loads((O/'capture/palette.json').read_text());assert q['passed']
    (O/'controls.json').write_text(json.dumps(dict(passed=True,native_original=True,native_port=False,installed=False,donor_sha256=EXPECTED,body_palette=q['palette'][16:20],hardware=q,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),ROM,controller,O/'capture/palette.json',R/'tools/run_mesen.py']}),indent=2)+'\n',encoding='utf-8');print(json.dumps(q))


if __name__=='__main__':main()
