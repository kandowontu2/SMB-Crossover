"""Serial controller-only PN baseline/dense comparison, one bounded PNG stream."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

R=Path(__file__).resolve().parents[2]
O=R/'build/parodius-chr-compact-v1'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from run_mesen import run


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--variant',type=int,choices=[1,2,3],required=True)
    ap.add_argument('--parent',action='store_true')
    a=ap.parse_args()
    source=R/'build/character-host-union-v7/native_cold.lua'
    control=source.read_text()
    control=replace_once(control,"local csv=assert(io.open(OUTPUT..'trace.csv','w'))",
        "local screens=assert(io.open(OUTPUT..'screens.bin','wb'));local screenCount=0\n"
        "local csv=assert(io.open(OUTPUT..'trace.csv','w'))")
    control=replace_once(control,"done=true;shot('endpoint');csv:close();cycles:close()",
        "done=true;shot('endpoint');csv:close();cycles:close();screens:close()")
    control=replace_once(control,"gameplay_frames=activeFrames,main_updates=updates,timing=timing,",
        "gameplay_frames=activeFrames,main_updates=updates,timing=timing,captured_screens=screenCount,")
    control=replace_once(control,"if age>=45 and age<63 then b.a=true end",
        "if age>=45 and age<63 then b.up=true end\n  if age>=100 and age<118 then b.down=true end")
    control=replace_once(control,"if P.raw==3 or P.raw==24 then if age>=25 and age<90 then b.b=true end end",
        "if age>=25 and age<140 then b.b=true end")
    control=replace_once(control,"frame=frame+1;age=age+1",
        "frame=frame+1;age=age+1\n if frame>=100 then local png=emu.takeScreenshot();"
        "assert(#png<1048576,'Screenshot bound');screenCount=screenCount+1;"
        "screens:write(string.pack('<I4I4',frame,#png));screens:write(png) end")
    control=replace_once(control,"assert(r('SelectedCharacter')==P.raw,'Actual ready raw owner');",
        "assert(r('SelectedCharacter')==P.raw,'Actual ready raw owner');"
        "assert(r('VvVariant')==P.variant,'Actual Parodius alternate');")
    control=replace_once(control,
        "updates>=100 and maxX-startX>=24 and jumped and landed and clockErrors==0",
        "updates>=100 and maxX-startX>=24 and startY-apex>=8 and clockErrors==0")
    control=control.replace("no1-1 clear or60Hz claim.",
        "Parodius up/down/shoot adaptation; all screens streamed to one bounded file. No1-1 clear or60Hz claim.")
    tag=('parent'if a.parent else'dense')+'-v'+str(a.variant)
    out=O/'native'/tag
    assert not out.exists(),out
    out.mkdir(parents=True)
    rom=R/'build/character-host-union-v5/candidate.nes'if a.parent else O/'candidate.nes'
    expected=json.loads((O/'build-proof.json').read_text())['parent_sha256'if a.parent else'candidate_sha256']
    assert sha(rom)==expected
    b=scoped_load(rom)
    ret=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    controller=out/'controller.lua'
    controller.write_text('COLD_ARGS={'+f'raw=18,slot=17,variant={a.variant},sha256="{expected}",main_return={ret}'+'}\n'+control,newline='\n')
    os.environ['SMB_RUN_OUTPUT']=str(out)
    result=run(controller,rom,timeout=120,
        emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    assert sha(rom)==expected
    binding=dict(ROM_sha256=expected,controller_sha256=sha(controller),
                 template_sha256=sha(source),driver_sha256=sha(__file__),exit_code=result,
                 no_RAM_writes=True,no_physics_or_palette_changes=True,
                 scope='Actual controller Start/Select/Ready/free movement/shooting; exact A/B screen comparison follows separately.')
    (out/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    print(json.dumps(dict(run=tag,exit_code=result)))
    raise SystemExit(result)


if __name__=='__main__':main()
