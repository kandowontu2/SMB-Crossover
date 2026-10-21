"""Retain the first exhaustive-arena failure without altering its inputs."""
from pathlib import Path
import hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'build/verification/ryu49o2-head-components-d'
OUT=ROOT/'build/verification/root49o2-head-b2-foot-stack-diagnostic-a.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists();sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('foot_d',HERE/'check.py')
    d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    old=d.Image(ROOT/'build/checkpoints/roster-audit-v49-provisional-o2/smb-crossover-mmc3.nes')
    new=d.Image(ROOT/'build/verification/root49o2-head-private-build-b2/source/build/smb-crossover-mmc3.nes')
    ram,registers,banks=d.seed(old,0,0,0,0,0,0,0)
    cls=d.loadcpu().NesMPU;results=[]
    for image in (old,new):
        memory=d.Bus(image,ram,banks);cpu=cls(memory=memory)
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=registers
        cpu.pc=image.hook('GuestFootContactSide')['address'];history=[];error=None
        try:
            while cpu.pc!=d.RET:
                memory.pc=cpu.pc;memory.op=memory.data[cpu.pc]
                history.append({'pc':cpu.pc,'opcode':memory.op,'A':cpu.a,'X':cpu.x,'Y':cpu.y,'P':cpu.p,'SP':cpu.sp,
                                'SMC_tail':list(memory.data[0x180:0x18b])})
                assert len(history)<500
                cpu.step()
        except Exception as e:error=repr(e)
        results.append({'ROM_sha256':sha(image.path),'error':error,'final_pc':cpu.pc,
                        'instructions':history,'ordered_writes':memory.trace,
                        'SMC_0185_before':ram[0x185],'SMC_0185_after':memory.data[0x185]})
    assert results[0]['error']is None and results[1]['error']is not None
    smc=next(s for s in new.segs.values()if s['name']=='SMCCODE')
    stores=[w for w in results[1]['ordered_writes']if w[3]==0x185]
    assert stores and ram[0x185]==0x60 and stores[0][1]==0x20
    report={'status':'ACTUAL_COMPILED_COMPONENT_NEGATIVE_ADDITIONAL_STACK_OVERWRITES_SMC_RTS',
            'script_sha256':sha(Path(__file__)),'checker_sha256':sha(HERE/'check.py'),
            'old_ROM':str(old.path),'candidate_ROM':str(new.path),'seed_ordinal':0,
            'input_registers':registers,'banks':banks,'SMCCODE':smc,'write_to_0185':stores,
            'results':results,'limits':['Seeded SP0x89 arena; no ordinary-game stack-depth reachability demonstrated',
                                       'Existing main Pit-wings P ROM contains no private head/foot relocation',
                                       'Do not silently remove this arena; reduce stack usage or establish actual reachability/invariant with evidence']}
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'report_sha256':sha(OUT),'SMC_0185_write':stores}))


if __name__=='__main__':main()
