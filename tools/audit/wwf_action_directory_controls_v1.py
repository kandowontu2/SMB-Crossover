"""Bounded authentic action-entry oracle cases, separate from controller reachability."""
from pathlib import Path
import collections
import hashlib
import json
import sys
import traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_action_source_controls_v2 as T
O=R/'build/wwf-action-directory-controls-v1'

def main():
    assert not O.exists();O.mkdir()
    proof=json.loads((T.L/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert T.sha(p)==h,p
    prg=T.W.W.raw();snapshot=(T.W.N/'capture/ram-match-entry.bin').read_bytes();chars=T.W.W.tables(prg)
    table_ends={a:b for a,b in zip(sorted(c['script_table']for c in chars),sorted(c['script_table']for c in chars)[1:]+[0xf140])}
    report=dict(passed=False,source_CPU_lab=True,installed=False,native_host=False,
        scope='Each genuine directory action entry,64 updates, both actor slots, separated/near-opponent native-field contexts. These entry fixtures do not prove controller eligibility or SMB contacts.',
        cases=[],callback_counts=collections.Counter(),handler_counts=collections.Counter())
    stats=dict(read=set(),write=set(),callback_read=set(),callback_write=set(),pc=set(),min_sp=255,cycles=[])
    calls=0
    try:
        for context in ['native-separated','near-opponent']:
            for actor in [0,1]:
                for ch in chars:
                    count=(table_ends[ch['script_table']]-ch['script_table'])//2
                    for action in range(1,count):
                        buses=[T.LabBus(prg,snapshot,proof,v) for v in [None,'native','relocated']]
                        def group(name,**kwargs):
                            nonlocal calls
                            starts=[(len(b.writes),len(b.callbacks))for b in buses]
                            cpus=[T.call(b,name,**kwargs)for b in buses]
                            stats['cycles'].append(T.compare(buses,cpus,starts,(context,actor,ch['id'],action,name,calls)));calls+=1
                        for b in buses:b.ram[0x2a+int(actor==0)],b.ram[0x2b-int(actor==0)]=ch['id'],(ch['id']+1)%6
                        group('WfInitDescriptors')
                        for b in buses:
                            for at in [0x3c,0x3d,0x3e,0x3f,0x40,0x41,0x8b,0x8c,0xa2,0xa3,0xa4,0xa5,0xcb,0xcc,0xc0,0xc1]:b.ram[at]=0
                            # Explicit authored-action entry fixture; no prerecorded timeline.
                            b.ram[0x3c+actor]=action
                            if context=='near-opponent':
                                b.ram[0x2c],b.ram[0x2d]=128,142
                                b.ram[0x2e]=b.ram[0x2f]=180
                        for tick in range(64):
                            for b in buses:
                                b.ram[0x71]=(tick*2+actor)%6
                                b.ram[0x8d]=(snapshot[0x8d]+tick*2+actor)&255
                            group('WfVmTick')
                        b=buses[2]
                        report['cases'].append(dict(context=context,actor=actor,character=ch['id'],action=action,script_pointer=prg[ch['script_table']+2*action-0x8000]+256*prg[ch['script_table']+2*action+1-0x8000],final_actions=list(b.ram[0x3c:0x3e]),final_health=list(b.ram[0x42:0x44]),callbacks=dict(collections.Counter(q['name']for q in b.callbacks))))
                        report['callback_counts'].update(q['name']for q in b.callbacks);report['handler_counts'].update(b.handler_hits)
                        for k,s in [('read',b.reads_by_context['component']),('write',b.writes_by_context['component']),('callback_read',b.reads_by_context['callback']),('callback_write',b.writes_by_context['callback']),('pc',b.pc_by_context['component'])]:stats[k].update(s)
                        stats['min_sp']=min(stats['min_sp'],b.min_sp)
            print(json.dumps(dict(context=context,cases=len(report['cases']),API_triplets=calls)),flush=True)
        report.update(passed=True,API_triplets=calls,VM_tick_pairs=len(report['cases'])*64,relocated_cycle_delta=[min(stats['cycles']),max(stats['cycles'])])
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        report['observed']={k:sorted(v)if isinstance(v,set)else v for k,v in stats.items()if k!='cycles'}
        report['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),Path(T.__file__),Path(T.W.__file__),T.W.W.ROM,T.W.N/'capture/ram-match-entry.bin',T.L/'build-proof.json',T.L/'native.bin',T.L/'relocated.bin']}
        T.save(O/'controls.json',report)
        print(json.dumps({k:report.get(k)for k in ['passed','API_triplets','VM_tick_pairs','relocated_cycle_delta','error']}),flush=True)
if __name__=='__main__':main()
