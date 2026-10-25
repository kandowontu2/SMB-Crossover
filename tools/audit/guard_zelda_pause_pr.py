"""Pause transitions with the existing real NMI bank/SMC guard and PPU images."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--script',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--camera',type=int,default=0)
    p.add_argument('--exercise-status',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    text=a.script.read_text();entry=(ROOT/'tests/full-roster-entry.lua').read_text()
    start=entry.index("emu.addMemoryCallback(function()\n assert(not ctx,'NMI nesting')")
    end=entry.index('emu.addEventCallback(function()',start)
    guard='''local ctx,smc
local nmis,irqs,publicationWindows=0,0,0
local minimumNmiSP=255
local function actual(a)return emu.convertAddress(a).address//8192 end
local function shared()local t={}for a=L.__SMCCODE_RUN__,L.__SMCCODE_RUN__+32 do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end
'''+entry[start:end].replace("local st=emu.getState();ctx=", "local st=emu.getState();minimumNmiSP=math.min(minimumNmiSP,st['cpu.sp']);ctx=")
    marker='emu.addMemoryCallback(function()\n if emu.convertAddress(L.Z2PanelTick)'
    assert text.count(marker)==1;text=text.replace(marker,guard+marker)
    marker='  if t==10 then\n'
    assert text.count(marker)==1
    camera=a.camera;world=camera+40
    setup={"ScreenLeft_X_Pos":camera%256,"ScreenLeft_PageLoc":camera//256,
        "ScreenRight_X_Pos":(camera+255)%256,"ScreenRight_PageLoc":(camera+255)//256,
        "HorizontalScroll":camera%256,"Player_X_Position":world%256,"Player_PageLoc":world//256}
    text=text.replace(marker,marker+''.join("   w("+json.dumps(n)+','+str(v)+')\n' for n,v in setup.items()))
    text=text.replace(marker,marker+"   w('Mirror_PPUCTRL',(r('Mirror_PPUCTRL')&0xfe)|"+str((camera//256)&1)+") -- native ScrollScreen nametable parity\n")
    if camera>=256:
        # Camera teleporting does not run the normal area parser. Authenticate
        # the initial native ground and populate just the four matching foot
        # cells at the target, so an unloaded column cannot kill the UI actor.
        seed="""   local foundation=r('Block_Buffer_1',176+2)
   assert(foundation==0x54,'Authenticate native1-1 ground before camera fixture')
"""
        for x in [world+2,world+13]:
            for row in [11,12]:
                index=(x//256)%2*208+row*16+(x%256)//16
                seed+="   w('Block_Buffer_1',foundation,"+str(index)+")\n"
        text=text.replace(marker,marker+seed)
    if a.exercise_status:
        text=text.replace(marker,marker+"   emu.write(0x5ff6,42,emu.memType.nesDebug) -- current player score/coins/timer; title top-score is not a gameplay field\n")
    text=text.replace('  if t==32 then','  if t==18 then image(\'before\')end\n  if t==32 then')
    text+='''
local guardedStop=emu.stop
emu.stop=function(code)
 if code==0 then
  assert(not ctx and nmis>400 and irqs>100 and minimumNmiSP>=122,'Observed NMI/IRQ/stack guard')
  local f=assert(io.open(OUTPUT..'interrupt-proof.json','w'))
  f:write(string.format('{"passed":true,"NMIs":%d,"IRQs":%d,"observed_minimum_NMI_SP":%d,"decoded_publication_windows":%d}\\n',nmis,irqs,minimumNmiSP,publicationWindows));f:close()
 end
 guardedStop(code)
end
'''
    script=a.output/'run.lua';script.write_text(text)
    q=dict(ROM_sha256=sha(a.rom),source_script_sha256=sha(a.script),guard_source_sha256=sha(ROOT/'tests/full-roster-entry.lua'),
        generated_script_sha256=sha(script),seeded_camera=camera,seeded_deferred_status=a.exercise_status,
        seeded_native_foundation=camera>=256,native_nametable_parity=(camera//256)&1)
    (a.output/'binding.json').write_text(json.dumps(q,indent=2)+'\n')
    args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','90',
        '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(a.output/'host.log').write_text(z.stdout+z.stderr)
    print((z.stdout+z.stderr)[-1000:]);return z.returncode
if __name__=='__main__':raise SystemExit(main())
