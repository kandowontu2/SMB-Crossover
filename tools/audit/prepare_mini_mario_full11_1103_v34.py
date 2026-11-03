"""Observer-only first-scroll CHR diagnostic; controls and ROM unchanged."""
from pathlib import Path
import argparse,json,re,sys
import prepare_mini_mario_native_smoke_1103_v25 as S
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/mini-mario-full11-packet-1103-v34'
SOURCE=R/'build/mini-mario-full11-packet-1103-v33/full11/controller.lua'

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    ready=json.loads(SOURCE.with_name('ready.json').read_text());assert ready['ROM_sha256']==a.sha and sha(SOURCE)==ready['bindings'][str(SOURCE)]
    text=SOURCE.read_text();G=S.labels(S.GLOBALS)
    names=['CurrentCHRBank','ReloadCHRBank','X5WideChrActive','SsChrActive','CurrentBank','CurrentBankC','FrameCounter']
    prefix='for k,v in pairs('+lua({n:G[n]for n in names})+')do L[k]=v end\nL.X5ChrMode=0x73e0\n'
    anchor='-- Controller inputs only.';assert text.count(anchor)==1;text=text.replace(anchor,prefix+anchor)
    text=text.replace('local checks,dmas,boxes,draws,minSP=0,0,0,0,255','local checks,dmas,boxes,draws,minSP=0,0,0,0,255\nlocal chr_failure=nil')
    text=text.replace('script_RAM_writes=false,controller_only=true','chr_failure=chr_failure,script_RAM_writes=false,controller_only=true')
    old="check(emu.getState()['mapper.chrBanks4']==C.expected_chr4,'Published original Mini CHR4=968')"
    new="""local actual=emu.getState()['mapper.chrBanks4']
 if actual~=C.expected_chr4 then
  local map={};for k,v in pairs(emu.getState())do if k:match('^mapper%.')or k:match('^ppu%.')then
   if type(v)=='number'or type(v)=='boolean'then map[k]=v end
  end end
  local desired,modes={},{};for i=0,7 do desired[#desired+1]=read(L.CurrentCHRBank+i);modes[#modes+1]=read(L.X5ChrMode+i)end
  chr_failure={actual=actual,expected=C.expected_chr4,mappings=map,CurrentCHRBank=desired,X5ChrMode=modes,
   ReloadCHRBank=r('ReloadCHRBank'),X5WideChrActive=r('X5WideChrActive'),SsChrActive=r('SsChrActive'),
   bankA=r('CurrentBank'),bankC=r('CurrentBankC'),epoch=r('FrameCounter'),ready=ram(0xc300),
   nativeX=r('Player_X_Position')+256*r('Player_PageLoc'),nativeY=r('Player_Y_Position'),
   sourceX16=word(0xc250),sourceY16=word(0xc252),DMApage=page,held=ram(0xc248)}
  if shots<2 then shot('mini-chr-failure')end
 end
 check(actual==C.expected_chr4,'Published original Mini CHR4 actual'..tostring(actual)..' expected'..C.expected_chr4)"""
    assert text.count(old)==1;text=text.replace(old,new)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    # Bind only the live source graph already proven by33, not its capture tree.
    deps=[Path(x)for x in ready['bindings']if Path(x)not in [SOURCE,SOURCE.with_name('run.py')]]
    prepare(O/'full11',a.rom,text,[*deps,Path(__file__),SOURCE,*a.ref],expected=a.sha,timeout=240,allow_interactive=True,
        scope='Observer-only successor33, same exactcandidate and controls. Retain CHR968 assertion; on first failure record actualspritebank/MMC5+PPUscalars, desiredCurrentCHRBank/modes/reload/wide, source/native/ready/input and secondPNG. No ROM/physics/controlstatewrites; menu+failure atmost2PNG; previousnegative preserved.')

if __name__=='__main__':main()
