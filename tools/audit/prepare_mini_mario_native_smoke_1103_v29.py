"""Distinct smoke for native32px-envelope/source6x7 Mini anchor repair."""
from pathlib import Path
import argparse,sys
import prepare_mini_mario_native_smoke_1103_v25 as S
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-native-smoke-1103-v29'

def build(rom,expected,kernel,labels,refs):
    built={};old=S.prepare
    def capture(output,rom,text,deps,**kw):built.update(text=text,deps=deps)
    try:
        S.prepare=capture;S.prepare_packet(rom,expected,kernel=kernel,kernel_labels=labels,refs=refs,output=O/'unused')
    finally:S.prepare=old
    text=built['text']
    for before,after in [('((p.y+9)&255)','((p.y+25)&255)'),('((p.y+15)&255)','((p.y+31)&255)')]:
        assert text.count(before)==1;text=text.replace(before,after)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    return text,[*built['deps'],Path(__file__)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--sha',required=True)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--labels',type=Path,required=True)
    p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args();O.mkdir(exist_ok=True)
    text,refs=build(a.rom,a.sha,a.kernel,a.labels,a.ref)
    prepare(O/'smoke',a.rom,text,refs,expected=a.sha,timeout=180,allow_interactive=True,
        scope='Distinct controller-only Mini anchor-repair smoke: nativeY=sourceYinteger-24, actualoriginal6x7bboxnativeY+25..31; renderedcanvas sourceYinteger-8 unchanged. Cold Select/Start, sourceidle20/right16/strictreversal/A20/apex/supportedlanding, sourcepixels/CHR968/normalDMA. Prior25idle-driftnegative retained. TwoPNG/noRAMwrites/fullstageclaim.')

if __name__=='__main__':main()
