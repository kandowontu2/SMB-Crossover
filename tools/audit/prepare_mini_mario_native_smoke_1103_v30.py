"""Preserve29 pixel-negative; add exact MMC5 debug/art failure diagnostics."""
from pathlib import Path
import argparse,sys
import prepare_mini_mario_native_smoke_1103_v29 as S
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-native-smoke-1103-v30'

def build(rom,expected,kernel,labels,refs):
    text,deps=S.build(rom,expected,kernel,labels,refs)
    text=text.replace('local checks,dmas,boxes,draws,minSP=0,0,0,0,255','local checks,dmas,boxes,draws,minSP=0,0,0,0,255\nlocal pixel_failure=nil')
    text=text.replace('script_RAM_writes=false,controller_only=true','pixel_failure=pixel_failure,script_RAM_writes=false,controller_only=true')
    old="for i=0,31 do check(emu.read(0x1000+(tile&254)*16+i,emu.memType.nesPpuDebug)==C.art[(tile&254)*16+i+1],'Actual PPU source2bpp pixels')end"
    new="""for i=0,31 do
    local offset=(tile&254)*16+i;local addr=0x1000+offset
    local actual=emu.read(addr,emu.memType.nesPpuDebug);local expected=C.art[offset+1]
    if actual~=expected then
     local map={};for k,v in pairs(emu.getState())do if k:match('^mapper%.')or k:match('^ppu%.')then
      if type(v)=='number'or type(v)=='boolean'then map[k]=v end
     end end
     pixel_failure={PPU_address=addr,actual=actual,expected=expected,pose=p.pose,tile=tile,
      pair_offset=offset,physical_CHR_address=C.expected_chr4*1024+offset,
      physical_CHR_actual=emu.read(C.expected_chr4*1024+offset,emu.memType.nesChrRom),
      mappings=map,source_X=p.x,source_Y=p.y,normal_DMA_page=page,normal_DMA_slot=p.slot}
     if shots<2 then shot('mini-pixel-failure')end
    end
    check(actual==expected,'Actual PPU source2bpp pixels address'..addr..' actual'..actual..' expected'..expected)
   end"""
    assert text.count(old)==1;text=text.replace(old,new)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    return text,[*deps,Path(__file__)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    text,deps=build(a.rom,a.sha,a.kernel,a.labels,a.ref)
    prepare(O/'smoke',a.rom,text,deps,expected=a.sha,timeout=180,allow_interactive=True,
        scope='Observer-only successor29: original exactPPUpixelassertion retained; on first failure record actual/expectedPPUbyte, physicalCHRbyte, MMC5/PPU mapping scalars and nativePNG. No ROM/control/physics/input-state change; atmost2PNGtotal. Preserve25idle and29pixel negatives.')

if __name__=='__main__':main()
