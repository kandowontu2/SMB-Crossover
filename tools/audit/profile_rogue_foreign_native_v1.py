"""Passive native attribution of Rogue hooks on the exact Bill comparison."""
from pathlib import Path
import json
import os
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import rogue_current_native_v1 as base
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=R/'build/rogue-current-menu-v6/native/bill-profile-v1'
P=R/'build/character-host-union-profile-v3'
V=R/'build/character-host-union-v11'


def main():
    assert not O.exists()
    rom=R/'build/rogue-current-menu-v6/candidate.nes'
    b=scoped_load(rom)
    names=sorted(n for n,s in b['syms'].items()if n.startswith('Rd')and'::'not in n
                 and'seg'in s and int(s.get('size','0'))>0 and address(b,n)>=0x8000)
    source=(V/'native_cold.lua').read_text()
    observer=(P/'observer.lua').read_text()
    at=observer.index('local watch={')
    end=observer.index('\nfor _,name',at)
    observer=observer[:at]+'local watch='+base.lua(names+['GameRoutines','ResetPalStar','NrUi','DrawAllMetasprites'])+observer[end:]
    patches=[("emu.addMemoryCallback(function()\n if active()and bank(L.GameLoop)",observer+"\nemu.addMemoryCallback(function()\n if active()and bank(L.GameLoop)"),
             ("main={start=s['cpu.cycleCount'],interrupt=0,sp=s['cpu.sp']}\n", "main={start=s['cpu.cycleCount'],interrupt=0,sp=s['cpu.sp']}\n  hotspot_begin()\n"),
             ("  main=nil\n", "  hotspot_end()\n  main=nil\n"),
             ("done=true;shot('endpoint');csv:close();cycles:close()", "done=true;shot('endpoint');csv:close();cycles:close();hotspot_close()")]
    source=source.replace('local main,isrs=nil,{}','local main,isrs=nil,{}\nlocal hotspot_close')
    for old,new in patches:
        assert source.count(old)==1
        source=source.replace(old,new,1)
    inverse=source
    for old,new in reversed(patches):
        inverse=inverse.replace(new,old,1)
    inverse=inverse.replace('local main,isrs=nil,{}\nlocal hotspot_close','local main,isrs=nil,{}',1)
    assert inverse==(V/'native_cold.lua').read_text()
    O.mkdir(parents=True)
    observed=O/'controller-observed.lua'
    observed.write_text(source,newline='\n')
    wrapper=O/'controller.lua'
    ret=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    digest=base.sha(rom)
    wrapper.write_text('COLD_ARGS={raw=3,slot=3,variant=0,sha256="'+digest+'",main_return='+str(ret)+'}\n'+
        'dofile([=['+observed.as_posix()+']=])\n',newline='\n')
    inputs={str(p):base.sha(p)for p in [Path(__file__).resolve(),V/'native_cold.lua',P/'observer.lua',observed,wrapper,rom]}
    os.environ['SMB_RUN_OUTPUT']=str(O)
    result=base.run(wrapper,rom,timeout=120,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false',
        '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    for p,h in inputs.items():assert base.sha(p)==h,p
    exact=[]
    if result==0:
        for name in ['result.json','trace.csv','main-cycles.csv']:
            assert(O/name).read_bytes()==(O.parent/'bill-candidate-v1'/name).read_bytes(),name
            exact.append(name)
    (O/'binding.json').write_text(json.dumps(dict(ROM_sha256=digest,exit_code=result,
        passive_only=True,inverse_controller_exact=True,byte_identical_native_outputs=exact,inputs=inputs),indent=2)+'\n')
    raise SystemExit(result)


if __name__=='__main__':main()
