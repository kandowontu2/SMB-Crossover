"""Correct MMC5 sprite-art observer; retain29/30 BG-debug-view negatives."""
from pathlib import Path
import argparse,json,sys
import prepare_mini_mario_native_smoke_1103_v29 as S
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/mini-mario-native-smoke-1103-v31'

def build(rom,expected,kernel,labels,refs):
    text,deps=S.build(rom,expected,kernel,labels,refs)
    old="for i=0,31 do check(emu.read(0x1000+(tile&254)*16+i,emu.memType.nesPpuDebug)==C.art[(tile&254)*16+i+1],'Actual PPU source2bpp pixels')end"
    new="for i=0,31 do check(emu.read(C.expected_chr4*1024+(tile&254)*16+i,emu.memType.nesChrRom)==C.art[(tile&254)*16+i+1],'Actual mapped sprite physicalCHR source2bpp pixels')end"
    assert text.count(old)==1;text=text.replace(old,new)
    old="check(emu.getState()['mapper.chrBanks4']==C.expected_chr4,'Published original Mini CHR4=968')"
    new=old+"\n check(emu.getState()['mapper.chrMode']==3 and emu.getState()['ppu.control.largeSprites']==true,'Actual MMC5 1KB spritebank/8x16 mode')"
    assert text.count(old)==1;text=text.replace(old,new)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    return text,[*deps,Path(__file__)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True);p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    diagnosis=R/'build/mini-mario-native-smoke-1103-v30/smoke/capture/result.json';d=json.loads(diagnosis.read_text())['pixel_failure']
    assert d['actual']==56 and d['expected']==d['physical_CHR_actual']==0
    assert d['mappings']['mapper.chrBanks4']==968 and d['mappings']['mapper.chrMode']==3
    assert d['mappings']['mapper.prevChrA']==False and d['mappings']['mapper.lastChrReg']==0x512b
    q=dict(resolved_observer_mismatch=True,ROM_changed=False,negative30_SHA256=sha(diagnosis),
        diagnostic=dict(PPU_address=d['PPU_address'],BG_debug_actual=d['actual'],source_expected=d['expected'],physical_CHR_actual=d['physical_CHR_actual'],
                        mapper_chr4=968,chr_mode=3,last_CHR_register=0x512b,prev_ChrA=False),
        conclusion='Vblank nesPpuDebug follows last MMC5 BG mapping. Sprite witness is actual1KB mode+8x16/odd tile+spritebank4=968+normalDMA tuple+exact physicalCHRpair+opaqueP0. Root visually inspects finalnativePNG.29/30 retain negative observer results; no corruptsprite inference.')
    evidence=O/'observer-resolution.json';evidence.write_text(json.dumps(q,indent=2)+'\n')
    text,deps=build(a.rom,a.sha,a.kernel,a.labels,[*a.ref,evidence])
    prepare(O/'smoke',a.rom,text,deps,expected=a.sha,timeout=180,allow_interactive=True,
        scope='Observer-corrected Mini smoke: trueMMC5sprite1KB/8x16 mapping, oddsourcepose/nativeDMA tuple, exactphysicalCHR968sourcepixels andopaqueP0; vblankBGdebug patternviewexcluded by actual30diagnostic. Original idle20/right16/reversal/A20/apex/floor/bbox/stablezero unchanged. TwoPNG/rootvisualwitness; noROM/RAM/physicschanges/fullstageclaim.')

if __name__=='__main__':main()
