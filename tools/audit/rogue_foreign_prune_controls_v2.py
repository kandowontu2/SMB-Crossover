"""Check genuine owner and foreign callers after pruning redundant checks."""
from pathlib import Path
import importlib.util
import json
import sys
import subprocess

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import rogue_current_menu_controls_v1 as existing
import rogue_dawn_scheduler_controls_v1 as cpu
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address
from sunny_integrated_controls_v1 import app,registers

O=R/'build/rogue-current-menu-v8'


def snapshot(arena,cpu_result,low):
    # Preserve all native page1 application bytes below the actual stack.
    b=arena.b
    smc=set(range(0x15a,0x17b))
    return(registers(cpu_result),app(arena),tuple(arena.m.banks),
           bytes(arena.m[i]for i in range(0x100,0x101+low)if i not in smc))


def main():
    existing.O=O
    if not(O/'controls.json').exists():
        command=[sys.executable,'-c',"import sys;sys.path[:0]=['tools/audit','tools'];import rogue_current_menu_controls_v1 as c;from pathlib import Path;c.O=Path('build/rogue-current-menu-v8').resolve();c.main()"]
        result=subprocess.run(command,cwd=R,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
    complete=json.loads((O/'controls.json').read_text())
    assert complete['passed']and complete['ROM_sha256']==existing.sha(O/'candidate.nes')
    for path,digest in complete['source_bindings'].items():assert existing.sha(path)==digest,path
    out=O/'prune-controls.json'
    assert not out.exists()
    old=scoped_load(R/'build/rogue-current-menu-v6/candidate.nes')
    new=scoped_load(O/'candidate.nes')
    differences=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    assert len(differences)==3,differences
    from check_tmnt_render_oa import location
    start=location(old,'RdUiEarly')
    assert all(start<=i<start+int(old['syms']['RdUiEarly']['size'])for i in differences)
    assert all(address(new,n)==address(old,n)for n in old['syms'])
    spec=importlib.util.spec_from_file_location('prune_menu_adapter',O/'menu-controls-adapter.py')
    menu=importlib.util.module_from_spec(spec);spec.loader.exec_module(menu);menu.ROOT=R
    ui=[]
    for slot,count in enumerate(menu.COUNTS):
        for variant in range(count):
            for flags in [0x30,0x71]:
                pair=[]
                for b in [old,new]:
                    a=menu.fresh(b,slot)
                    a.invoke('MenuResolveCharacter');a.invoke('QueueSelection')
                    for _ in range(variant):menu.button(a,32)
                    c,_=a.invoke('FmPending')
                    if c.p&1:break
                    a.put(OperMode=1,CrossoverMenuState=0,NmiDisable=255,DisableScreenFlag=0,
                          VRAM_Buffer1_Offset=0,RdAnimFrame=8,GameEngineSubroutine=8)
                    c,z=cpu.invoke(a.m,'RdUiEarly',a=0x36,x=0x57,y=0x98,p=flags)
                    pair.append((a,c,z))
                if not pair:continue
                assert len(pair)==2
                lo=min(z['minimum_SP']for a,c,z in pair)
                assert snapshot(*pair[0][:2],lo)==snapshot(*pair[1][:2],lo),(slot,variant,flags)
                # Mapper-shadow transactions differ because one entire nested
                # foreign farcall is removed. Application writes stay ordered.
                def writes(a):
                    omit={address(a.b,'CurrentBank'),address(a.b,'CurrentBankC')}|set(range(0x15a,0x17b))
                    return[(i,v)for i,v in a.m.writes if not 0x100<=i<0x200 and not 0x5114<=i<=0x5117 and i not in omit]
                assert writes(pair[0][0])==writes(pair[1][0]),(slot,variant,flags,'ordered writes')
                saved=pair[0][2]['CPU']-pair[1][2]['CPU']
                assert saved==(0 if(slot,variant)==(2,1)else 122 if slot==2 else 114),(slot,variant,flags,saved,pair[0][2]['CPU'],pair[1][2]['CPU'])
                smc=[]
                normal_operands={address(old,n)+i for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC','SafereturnA_SMC']for i in ([1,2]if n=='FarcallJmpTarget_SMC'else[1])}
                for at in range(0x15a,0x17b):
                    x,y=pair[0][0].m[at],pair[1][0].m[at]
                    if x!=y:
                        assert at in normal_operands,(slot,variant,flags,at)
                        smc.append(dict(address=at,old=x,new=y))
                ui.append(dict(slot=slot,variant=variant,flags=flags,saved_CPU=saved,dead_farcall_operand_differences=smc))
    assert len(ui)==96
    report=dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=existing.sha(O/'candidate.nes'),
        changed_ROM_offsets=differences,all_existing_symbol_addresses_exact=True,
        UI_cases=ui,source_bindings={str(p):existing.sha(p)for p in [Path(__file__).resolve(),
            O/'build-proof.json',O/'controls.json',O/'candidate.nes',R/'build/rogue-current-menu-v6/candidate.nes']},
        limits=['Finite isolated real6502 helper/owner ABI checks and menu controls. Actual Bill timing/native route remains separate.'])
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,changed_ROM_bytes=3,UI_cases=len(ui))))


if __name__=='__main__':main()
