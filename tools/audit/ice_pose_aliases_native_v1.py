"""Controller-only Ice aliases A/B test with one bounded lossless PNG stream."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

R=Path(__file__).resolve().parents[2]
O=R/'build/ice-pose-aliases-v2'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from parodius_chr_compact_native_v1 import replace_once
from run_mesen import run


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--variant',type=int,choices=[0,1],required=True)
    ap.add_argument('--parent',action='store_true')
    a=ap.parse_args()
    template=R/'build/character-host-union-v7/native_cold.lua'
    code=template.read_text()
    code=replace_once(code,"local csv=assert(io.open(OUTPUT..'trace.csv','w'))",
        "local screens=assert(io.open(OUTPUT..'screens.bin','wb'));local screenCount=0\n"
        "local csv=assert(io.open(OUTPUT..'trace.csv','w'))")
    code=replace_once(code,"done=true;shot('endpoint');csv:close();cycles:close()",
        "done=true;shot('endpoint');csv:close();cycles:close();screens:close()")
    code=replace_once(code,"gameplay_frames=activeFrames,main_updates=updates,timing=timing,",
        "gameplay_frames=activeFrames,main_updates=updates,timing=timing,captured_screens=screenCount,")
    code=replace_once(code,"if P.raw==3 or P.raw==24 then if age>=25 and age<90 then b.b=true end end",
        "if age==150 or age==180 or age==210 or age==240 then b.b=true end")
    code=replace_once(code,"frame=frame+1;age=age+1",
        "frame=frame+1;age=age+1\n if frame>=100 then local png=emu.takeScreenshot();"
        "assert(#png<1048576,'Screenshot bound');screenCount=screenCount+1;"
        "screens:write(string.pack('<I4I4',frame,#png));screens:write(png) end")
    code=replace_once(code,"assert(r('SelectedCharacter')==P.raw,'Actual ready raw owner');",
        "assert(r('SelectedCharacter')==P.raw,'Actual ready raw owner');"
        "assert(r('IcVariant')==P.variant,'Actual Ice alternate');")
    code=code.replace('no1-1 clear or60Hz claim.',
        'Actual Popo/Nana menu entry, walking/jump/hammer and all screens streamed. No1-1 clear or60Hz claim.')
    tag=('parent'if a.parent else'aliased')+'-jump-then-hammer-v'+str(a.variant)
    out=O/'native'/tag
    assert not out.exists(),out
    out.mkdir(parents=True)
    bp=json.loads((O/'build-proof.json').read_text())
    rom=R/'build/parodius-chr-compact-v1/candidate.nes'if a.parent else O/'candidate.nes'
    expected=bp['parent_ROM_sha256'if a.parent else'ROM_sha256'];assert sha(rom)==expected
    b=scoped_load(rom);ret=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    controller=out/'controller.lua'
    controller.write_text('COLD_ARGS={'+f'raw=20,slot=19,variant={a.variant},sha256="{expected}",main_return={ret}'+'}\n'+code,newline='\n')
    os.environ['SMB_RUN_OUTPUT']=str(out)
    result=run(controller,rom,timeout=120,
        emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false',
                          '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    assert sha(rom)==expected
    (out/'binding.json').write_text(json.dumps(dict(ROM_sha256=expected,exit_code=result,
        controller_sha256=sha(controller),template_sha256=sha(template),driver_sha256=sha(__file__),
        no_native_RAM_writes=True,normal_sprite_limit=True),indent=2)+'\n')
    print(json.dumps(dict(run=tag,exit_code=result)))
    raise SystemExit(result)


if __name__=='__main__':main()
