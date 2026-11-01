"""Differential source model for funded HUD cleanup and the unchanged loader."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_loader_funding_1101_v6 as F
from prepare_karnov_hud_funding_1101_v9 import transform_sources
from check_tmnt_render_oa import address
O=R/'build/karnov-hud-funding-1101-v9';B=R/'build/karnov-host-resource-base-1101-v1'
PIN='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    assert sha(B/'candidate.nes')==PIN
    old=F.P.H.C.qualified(B/'candidate.nes')
    q=dict(passed=False,source_model=True,owning_link=False,native=False,installed=False,parent_ROM_sha256=PIN)
    try:
        graft=transform_sources(resident=(B/'kr-resident.inc').read_text(),carrier_helper=(B/'kr-loader-carrier-v6.inc').read_text())
        F.O=O;inputs=set();new,assembly=F.assemble(old,'resident-v9',graft['resident'],graft['fragments'],inputs)
        new,rebound=F.model_link(old,new)
        # Genuine loader source and kernel payload, with no executable overlay.
        q['loader'],_=F.loader_checks(old,new,carrier=False)
        q['negative_loader']=F.negative_checks(old,new)
        q['headers']=F.header_checks(old,new)
        rows=[]
        for owner,corrupt,flags in itertools.product([0,1,0xe9,0xea],[None,(2,0),(3,15)],[0,63]):
            states=[]
            for b in [old,new]:
                m=F.P.cold(b);F.H.put(m,InvHudActive=owner,ReloadCHRBank=0)
                if corrupt:m.ram[corrupt[0]][0x1fe0+corrupt[1]]^=1
                before=[bytes(z)for z in m.ram];c,low=F.call(m,'KrRetire',a=85,x=7,y=91,p=F.L.flags(flags))
                assert [bytes(z)for z in m.ram][0:2]==before[0:2]
                states.append((m,c,low))
            a,z=states
            if owner==0xe9:
                assert F.H.get(z[0],'InvHudActive')==0 and F.H.get(z[0],'ReloadCHRBank')==1
                # Exclude only the deliberately changed native font lease.
                F.H.put(a[0],InvHudActive=0,ReloadCHRBank=1)
            assert F.state(a[0],a[1])==F.state(z[0],z[1]),('Retirement ABI/state',owner,corrupt,flags)
            rows.append(dict(owner=owner,corrupt=corrupt,flags=flags,minimum_SP=z[2]))
        q.update(passed=True,assembly=assembly,model_relocations=rebound,retirement_cases=rows,
                 scope='Source-model-only full cold/warm/failure loader differential and both cache headers; no real owner build/native claim. Only ownE9 retirement clears native HUD+requests publication; foreign owners/AXYP/other RAM and maps retain exact behavior. Hot dispatcher instruction stream is unchanged except source relocation.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),R/'tools/audit/prepare_karnov_hud_funding_1101_v9.py',Path(F.__file__),B/'candidate.nes',B/'candidate.dbg',B/'kr-resident.inc',B/'kr-loader-carrier-v6.inc']}
    (O/'funding-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],error=q.get('error'),resident=q.get('assembly',{}).get('resident_bytes'),retirement_cases=len(q.get('retirement_cases',[])))))
    assert q['passed'],q.get('error','Funding controls')


if __name__=='__main__':main()
