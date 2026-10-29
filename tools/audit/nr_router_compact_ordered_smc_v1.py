"""Explicit page1 SMC write accounting; genuine full callers, no stack mask."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
import nr_router_compact_controls_v1 as C
from sunny_integrated_controls_v1 import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    old,new=[scoped_load(p)for p in[C.OLD,C.NEW]];names=C.re.findall(r'^NrGate (\w+),',(C.R/'src/new_roster_dispatch.s').read_text(),C.re.M)
    files=[Path(__file__),Path(C.__file__)]+[p.with_suffix(e)for p in[C.OLD,C.NEW]for e in['.nes','.dbg','.lbl']]
    proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p.resolve()):sha(p)for p in files},checks={})
    try:
        smc=set(smc_at(old));assert smc==set(smc_at(new))and all(0x100<=n<0x200 for n in smc)
        count=0;rows=[]
        for name in names:
            stores=0
            for char,flags in itertools.product(range(256),[p for p in range(256)if p&0x30==0x30]):
                pair=[]
                for b in[old,new]:
                    q=C.setup(b,char,name);c,_,sp,_,_=C.actual(q,name,flags=flags)
                    seq=[(at,v)for at,v in q.m.writes if at in smc]
                    pair.append((registers(c),tuple(q.m.banks),bytes(q.m[n]for n in sorted(smc)),seq))
                assert pair[0]==pair[1],('actual ordered5SMC',name,char,flags,pair[0],pair[1])
                stores+=len(pair[1][3]);count+=1
            rows.append(dict(name=name,calls=16384,actual_SMC_stores_each_side=stores));print(name,count,flush=True)
        proof['checks']['ordered_page1_SMC_full_callers']=dict(passed=True,cases=count,all256raw_all64flags_all11complete_callers=True,explicit_SMC_addresses=sorted(smc),ordered_address_value_sequence_and_final_values_AXYP_SP_banks_exact=True,rows=rows)
        assert all(sha(p)==h for p,h in proof['bindings'].items());proof['passed']=True
    except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'))));assert proof['passed']

if __name__=='__main__':main()
