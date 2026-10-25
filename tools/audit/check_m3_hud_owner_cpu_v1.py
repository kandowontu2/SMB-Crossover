"""Execute the old/new inventory leaf; exact outputs except intentional M3 ownership."""
from pathlib import Path
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def execute(b,char,active,hurt,kind,prev,joy,dirty):
    q=Arena(b,char);q.put(InvHudActive=active,ReloadCHRBank=2,InvDirty=dirty,GuestHurtTicks=hurt,GuestHurtKind=kind,InvPrevious=prev,SavedJoypad1Bits=joy)
    c,trace=q.invoke('X5NativeInventoryUiLeaf',a=0x91,x=0x57,y=0x2d)
    writes=[(r['address'],r['value'])for r in trace if not 0x100<=r['address']<0x200]
    return dict(cpu=(c.a,c.x,c.y,c.p&0xcf,c.sp),writes=writes,
                values={n:q.get(n)for n in ['InvHudActive','ReloadCHRBank','InvDirty','InvPrevious','InvFresh']},cycles=c.processorCycles)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=scoped_load(a.baseline),scoped_load(a.candidate);rows=[];failures=[]
    for char,active,hurt,prev,joy,dirty in itertools.product([13,14,16,17,19],[0,1],[0,1],[0,32,128,255],[0,32,65,255],[0,255]):
        for kind in([0]if not hurt else[0,4,5,8]):
            o=execute(old,char,active,hurt,kind,prev,joy,dirty);n=execute(new,char,active,hurt,kind,prev,joy,dirty)
            intentional=char==17 and active and not hurt
            expected=dict(o['values'])
            if intentional:expected.update(InvHudActive=active,ReloadCHRBank=2,InvDirty=dirty)
            exclude={address(old,k)for k in ['InvHudActive','ReloadCHRBank','InvDirty']}if intentional else set()
            equal=n['cpu']==o['cpu']and n['values']==expected and[(x,v)for x,v in o['writes']if x not in exclude]==[(x,v)for x,v in n['writes']if x not in exclude]
            r=dict(char=char,active=active,hurt=hurt,kind=kind,prev=prev,joy=joy,dirty=dirty,cycles_delta=n['cycles']-o['cycles'],intentional=bool(intentional),passed=equal)
            rows.append(r)
            if not equal and len(failures)<8:failures.append(r|dict(old=o,new=n))
    proof=dict(passed=all(r['passed']for r in rows),goal_complete=False,native_passed=False,baseline_sha256=sha(a.baseline),candidate_sha256=sha(a.candidate),
               cases=len(rows),cycles_delta=sorted({r['cycles_delta']for r in rows}),failures=failures,checks=rows,tool_sha256=sha(Path(__file__)),
               scope='Actual assembled leaf including its actual private helper, registers/flags/stack/RAM/ordered nonstack writes. Legal five admitted character IDs, native disable-input branches, button edge histories and dirty wrap. Only intended SMB3 font ownership/dirty/reload retention differs. Explicit CPU states; no native timing proof.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k]for k in ['passed','cases','cycles_delta','failures']}));return 0 if proof['passed']else 1


if __name__=='__main__':raise SystemExit(main())
