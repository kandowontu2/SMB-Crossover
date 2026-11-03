"""Bounded active-Mini CHR publication writer history; no emulated writes."""
from pathlib import Path
import argparse,json,sys
import prepare_mini_mario_native_smoke_1103_v25 as S
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/mini-mario-chr-writers-1103-v38'
SOURCE=R/'build/mini-mario-native-packets-1103-v36/full36/controller.lua'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    ready=json.loads(SOURCE.with_name('ready.json').read_text());assert ready['ROM_sha256']==a.sha and sha(SOURCE)==ready['bindings'][str(SOURCE)]
    text=SOURCE.read_text();G=S.labels(S.GLOBALS)
    names=['CurrentCHRBank','ReloadCHRBank','X5WideChrActive','SsChrActive','AreaType','AreaChrBank','CurrentBank','CurrentBankC']
    prefix='for k,v in pairs('+lua({n:G[n]for n in names})+')do L[k]=v end\nL.X5ChrMode=0x73e0\nC.max_frames=850\n'
    anchor='-- Controller inputs only.';assert text.count(anchor)==1;text=text.replace(anchor,prefix+anchor)
    text=text.replace('local checks,dmas,boxes,draws,minSP=0,0,0,0,255','local checks,dmas,boxes,draws,minSP=0,0,0,0,255\nlocal writerRing={}')
    text=text.replace('script_RAM_writes=false,controller_only=true','CHR_writer_ring=writerRing,script_RAM_writes=false,controller_only=true')
    old='if not ok then result(false,tostring(e))'
    new="if not ok then if shots<2 then local f=io.open(OUTPUT..'mini-writer-failure.png','wb');if f then f:write(emu.takeScreenshot());f:close();shots=shots+1 end end;result(false,tostring(e))"
    assert text.count(old)==1;text=text.replace(old,new)
    anchor='local function transition(p)';assert text.count(anchor)==1
    observer="""local function writer(a,v)
 if not active()then return end
 local s=emu.getState();local pc=s['cpu.pc'];local m=emu.convertAddress(pc);local stack={}
 for i=1,16 do stack[#stack+1]=read(256+((s['cpu.sp']+i)&255))end
 local desired,modes,area={}, {}, {};for i=0,11 do desired[#desired+1]=read(L.CurrentCHRBank+i);modes[#modes+1]=read(L.X5ChrMode+i)end
 for i=0,11 do area[#area+1]=read(L.AreaChrBank+i)end
 local q={pc=pc,physical=m and m.address,memory=m and tostring(m.memType),address=a,
  old=a==0x5124 and s['mapper.chrBanks4']or read(a),new=v,frame=frame,Main=mains,source=updates,
  sp=s['cpu.sp'],stack=stack,AreaType=r('AreaType'),AreaChrBank=area,CurrentCHRBank=desired,X5ChrMode=modes,
  OPTask=r('OperMode_Task'),Selected=r('SelectedCharacter'),chr4=s['mapper.chrBanks4'],
  lastChrReg=s['mapper.lastChrReg'],prevChrA=s['mapper.prevChrA'],
  Reload=r('ReloadCHRBank'),Wide=r('X5WideChrActive'),Ss=r('SsChrActive'),bankA=r('CurrentBank'),bankC=r('CurrentBankC')}
 if #writerRing>=32 then table.remove(writerRing,1)end;writerRing[#writerRing+1]=q
end
emu.addMemoryCallback(guard(writer),emu.callbackType.write,L.CurrentCHRBank,L.CurrentCHRBank+11)
emu.addMemoryCallback(guard(writer),emu.callbackType.write,L.X5ChrMode,L.X5ChrMode+11)
for _,a in ipairs({L.ReloadCHRBank,L.X5WideChrActive,L.SsChrActive,0x5124})do emu.addMemoryCallback(guard(writer),emu.callbackType.write,a)end
"""
    text=text.replace(anchor,observer+anchor)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    deps=[Path(x)for x in ready['bindings']if Path(x)not in [SOURCE,SOURCE.with_name('run.py')]]
    prepare(O/'diagnostic',a.rom,text,[*deps,Path(__file__),SOURCE,*a.ref],expected=a.sha,timeout=120,allow_interactive=True,
        scope='Read-only Mini-active CHRwriter diagnostic, exact36controls/ROM.850physicalframe cap, last32DesiredCHR/Mode/Reload/Wide/Ss/5124writes withphysicalPC/16stackbytes/nativeArea/context+desiredstate. ExistingCHRguard/failure retained; menu+failure2PNGmaximum. No RAM/mapper/ability/physics writes.')

if __name__=='__main__':main()
