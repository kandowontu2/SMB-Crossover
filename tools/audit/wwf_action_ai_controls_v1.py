"""Genuine controller-selector AI tail entry, not a replacement AI policy."""
from pathlib import Path
import json
import sys
import traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_action_source_controls_v2 as T
O=R/'build/wwf-action-ai-controls-v1'

def main():
    assert not O.exists();O.mkdir();proof=json.loads((T.L/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert T.sha(p)==h,p
    prg=T.W.W.raw();snapshot=(T.W.N/'capture/ram-match-entry.bin').read_bytes();chars=T.W.W.tables(prg)
    report=dict(passed=False,source_CPU_lab=True,native_host=False,cases=0,AI_tail_calls=0,limits=['Explicit CPU AI-selector entry fixtures; native AI is an environment callback, not part of the assembled component or an SMB AI implementation.'])
    deltas=[]
    try:
        for actor in [0,1]:
            for ch in chars:
                for raw_flags in range(64):
                    flags=0x30|(raw_flags&15)|((raw_flags&48)<<2)
                    buses=[T.LabBus(prg,snapshot,proof,v)for v in [None,'native','relocated']]
                    for b in buses:
                        b.ram[0x2a+int(actor==0)],b.ram[0x2b-int(actor==0)]=ch['id'],(ch['id']+1)%6
                        T.call(b,'WfInitDescriptors')
                        b.ram[0xcb+actor]=0
                    starts=[(len(b.writes),len(b.callbacks))for b in buses]
                    cpus=[T.call(b,'WfSelectAction',a=0x53,x=actor,y=255,flags=flags)for b in buses]
                    deltas.append(T.compare(buses,cpus,starts,(actor,ch['id'],flags)))
                    assert len(buses[2].callbacks[starts[2][1]:])==1 and buses[2].callbacks[-1]['name']=='WfCbAI'
                    report['cases']+=1;report['AI_tail_calls']+=1
        report.update(passed=True,relocated_cycle_delta=[min(deltas),max(deltas)])
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        report['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),Path(T.__file__),T.W.W.ROM,T.W.N/'capture/ram-match-entry.bin',T.L/'build-proof.json',T.L/'native.bin',T.L/'relocated.bin']}
        T.save(O/'controls.json',report);print(json.dumps({k:report.get(k)for k in ['passed','cases','AI_tail_calls','relocated_cycle_delta','error']}))
if __name__=='__main__':main()
