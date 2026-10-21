"""Reexecute actual whole head callers, with every RAM byte/write/register."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-head-axis-c'
G=V/'ryu49-head-status-bridge-g'
sys.path.insert(0,str(G))
spec=importlib.util.spec_from_file_location('head_native_bus_e',G/'check.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=D/'native-head-review-e.json';assert not out.exists()
    report=dict(status='RUNNING',script_sha256=sha(__file__),maps=[],main_changed=False,goal_complete=False)
    try:
        for mapper in ['mmc3','mmc5']:
            d=json.loads((D/f'native-head-e-{mapper}.json').read_text())
            im=g.Image(D/f'source/build/smb-crossover-{mapper}.nes')
            old=g.Image(V/f'root49-combined-working-c/source/build/smb-crossover-{mapper}.nes')
            assert sha(im.path)==d['ROM']['rom']['sha256'] and im.ram==old.ram
            p=R/f'build/roster-through-2-2/root49-sophia-head-call-e-11-v0-{mapper}'
            actual=[dict(zip(d['columns'],json.loads(z)))for z in(p/'head-calls-e.jsonl').read_text().splitlines()]
            raw=(p/'head-calls-e.ram').read_bytes()
            writes={}
            for z in csv.DictReader((p/'head-writes-e.csv').open()):
                writes.setdefault(int(z['id']),[]).append((int(z['address']),int(z['value'])))
            by={}
            for z in actual:by.setdefault(z['id'],{})[z['event']]=z
            assert len(by)>=30
            cases=[];gaps=[]
            for cid,pair in by.items():
                a,b=pair['entry'],pair['return']
                if b['interrupts']:
                    gaps.append(dict(id=cid,frame=a['frame'],actual_interrupts=b['interrupts'],reason='Captured but not reexecuted by the foreground-only bus; retained explicit gap.'))
                    continue
                before=raw[a['RAMoffset']:a['RAMoffset']+10240]
                after=raw[b['RAMoffset']:b['RAMoffset']+10240]
                assert len(before)==len(after)==10240
                regs=[a[k]for k in ['A','X','Y','P','SP']]
                assert regs[3]&0x30==0 and b['P']&0x30==0
                banks={addr:a[k]for addr,k in zip([0x8000,0xa000,0xc000,0xe000],['bank8000','bankA000','bankC000','bankE000'])}
                z=g.execute(im,CPU,before,regs,banks,a['PC'],b['PC'],native_status=True)
                expected=[b[k]for k in ['A','X','Y','P','SP','PC']]
                assert z['regs']==expected,('All AXYP/SP/PC',mapper,cid,z['regs'],expected)
                assert z['ram']==after,('All10240 RAM',mapper,cid,[(i,x,y)for i,(x,y)in enumerate(zip(z['ram'],after))if x!=y][:12])
                assert [(a,v)for pc,op,a,physical,v in z['trace']]==writes.get(cid,[]),('Every ordered write',mapper,cid)
                assert z['banks']==banks,('Restored native caller banks',mapper,cid)
                elapsed=b['cycles']-a['cycles']
                # DMA can stall an instruction while leaving the entire caller
                # state/write result exact; retain rather than mask cycle data.
                cases.append(dict(id=cid,frame=a['frame'],cycles_compiled=z['cycles'],cycles_native=elapsed,
                                  cycle_delta=elapsed-z['cycles'],writes=len(z['trace']),all_registers_RAM_writes_exact=True))
            assert len(cases)>=25
            # Same actual entry RAM as a controlled foreign dispatch, for every
            # other character and Lance. This is component/ABI evidence only.
            a=by[1]['entry'];before=raw[a['RAMoffset']:a['RAMoffset']+10240]
            regs=[a[k]for k in ['A','X','Y','P','SP']]
            banks={addr:a[k]for addr,k in zip([0x8000,0xa000,0xc000,0xe000],['bank8000','bankA000','bankC000','bankE000'])}
            foreign=[]
            for char,variant in [(c,0)for c in range(13)if c!=11]+[(3,1)]:
                seed=bytearray(before)
                seed[g.at(im.ram['SelectedCharacter'])]=char
                seed[g.at(im.ram['BillVariant'])]=variant
                aa=g.execute(old,CPU,seed,regs,banks,a['PC'],by[1]['return']['PC'],native_status=True)
                bb=g.execute(im,CPU,seed,regs,banks,a['PC'],by[1]['return']['PC'],native_status=True)
                assert aa==bb,('Foreign full caller literal',mapper,char,variant)
                foreign.append(dict(character=char,variant=variant,all_registers_RAM_ordered_writes_cycles_exact=True))
            report['maps'].append(dict(mapper=mapper,actual_calls=len(by),strict_reexecutions=cases,
                                       actual_interrupt_gaps=gaps,foreign_component_cases=foreign,
                                       receipts={n:sha(p/n)for n in ['head-calls-e.jsonl','head-calls-e.ram','head-writes-e.csv','manifest.json']}))
        report.update(status='PASS_ACTUAL_SOPHIA_WHOLE_RESIDENT_HEAD_CALLERS_WITH_EXPLICIT_INTERRUPT_GAPS',
                      qualifications=['Actual ordinary-input full head caller snapshots, no emulated writes or state loads.',
                                      'Interrupted actual callers are retained as explicit gaps; no blanket interrupt equivalence claim.',
                                      'Foreign tests change only seeded component identity; they are not route/acquisition evidence.',
                                      'Frame-limited1200 runs intentionally stop before a complete stage clear; final route/media audit still required.'])
    except Exception as e:
        report.update(status='FAIL_RETAINED',error=str(e));raise
    finally:out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],strict_calls=sum(len(z['strict_reexecutions'])for z in report['maps']),gaps=sum(len(z['actual_interrupt_gaps'])for z in report['maps']))))


if __name__=='__main__':main()
