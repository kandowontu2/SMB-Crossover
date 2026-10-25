"""All 1,024 pool occupancy masks and original-handler differential checks.

Legal component input states, not natural controller reachability evidence.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address


def setup(b,mask,face=1,up=0,ammo=15,active=0):
    q=Arena(b,11)
    q.put(InvFresh=32,PlayerFacingDir=face,SavedJoypadBits=32|up,SavedJoypad1Bits=32|up)
    q.set('InvOwnedLo',3,11);q.set('InvSelected',1,11);q.set('InvAmmo',ammo,177)
    occupied=[i for i in range(10) if mask&(1<<i)]
    for n,i in enumerate(occupied):
        typ=44 if n<active else 45 if n<4 else 6
        q.set('RgShotType',typ,i);q.set('RgShotImpact',10 if typ==6 else 0,i)
        q.set('RgShotX',144,i);q.set('RgShotPage',1,i)
        q.set('RgShotY',176,i);q.set('RgShotYHigh',1,i)
        q.set('RgShotDir',face,i)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=scoped_load(a.baseline),scoped_load(a.rom)
    rows=[];negative=0;exact=0
    for mask in range(1024):
        q=setup(new,mask);_,trace=q.invoke('RemainingWeapons::SophiaInput')
        free=10-mask.bit_count(); count=sum(q.get('RgShotType',i)==44 for i in range(10))
        spent=15-q.get('InvAmmo',177)
        assert (count,spent)==((3,3) if free>=3 else (0,0)),(mask,free,count,spent)
        rows.append(dict(mask=mask,free=free,created=count,spent=spent))
    # Every occupied standard-missile slot, both facings, aiming directions and
    # low/full ammo: the existing one-volley rule always rejects another volley.
    for occupied_slot,face,up,ammo in itertools.product(range(10),[1,2],[0,8],[0,2,3,15]):
        mask=1<<occupied_slot
        q=setup(new,mask,face,up,ammo,active=1)
        before=list(q.m[:0x8000]);q.invoke('RemainingWeapons::SophiaInput')
        assert q.get('InvAmmo',177)==ammo
        assert sum(q.get('RgShotType',i)==44 for i in range(10))==1
        negative+=1
    excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for g in new['segs'].values():
        if g.get('name')=='"SMCCODE"':excluded.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
    for n in ['safecall_a','SafecallA']:
        if n in new['syms']:excluded.add(address(new,n))
    # Same full handler on both binaries; enough room (including low-ammo
    # refusals) must leave all application RAM and bank shadows identical.
    for mask,face,up,ammo in itertools.product([0,1,0x155,0x2aa,0x3f8],[1,2],[0,8],[0,2,3,15]):
        assert 10-mask.bit_count()>=3
        q1,q2=(setup(b,mask,face,up,ammo) for b in [old,new])
        q1.invoke('RemainingWeapons::SophiaInput');q2.invoke('RemainingWeapons::SophiaInput')
        diff=[i for i in range(0x8000) if i not in excluded and q1.m[i]!=q2.m[i]]
        assert not diff,[(hex(i),q1.m[i],q2.m[i]) for i in diff[:12]]
        assert q1.m.banks==q2.m.banks
        exact+=1
    proof=dict(passed=True,baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
        ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        occupancy_masks=len(rows),existing_standard_missile_refusals=negative,
        original_handler_exact_application_RAM_and_banks=exact,
        scope=__doc__,excluded_state='Hardware stack, five mapper windows and original SMC/call bookkeeping only. No application-state exclusions.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    (a.output/'masks.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
