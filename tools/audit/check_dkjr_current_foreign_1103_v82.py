"""Actual current foreign cold/Fresh/all37 public rows versus the DK factor."""
import json
from pathlib import Path
import prepare_dkjr_current_owner_1103_v79 as P

A,R,O,C=P.A,P.R,P.O,P.C
N=C.N


def view(m):
    return ([bytes(z)for z in m.ram],bytes(m[:0x100]),bytes(m[0x200:0x800]),
        bytes(m[0x15a:0x17b]),bytes(m[0x1e0:0x200]),m.rawtags[:],list(m.ppu_log))


def main():
    old,_=C.image();new,manifest=P.image();rows=[];count=0
    for owner in [37,38,39]:
        pair=[];cold=[]
        for base in [old,new]:
            m,z=C.cold(base,owner)
            fresh=N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21)
            assert fresh['P']&1
            C.clear(m);pair.append(m);cold.append(z['CPU'])
        assert view(pair[0])==view(pair[1]),('actual complete foreign cold/Fresh',owner)
        for cwindow in [2,201]:
            for row in range(37):
                for flags in [0x21,0x60,0xa1,0xe1]:
                    instances=[N.fork(m)for m in pair];results=[]
                    for m in instances:
                        C.clear(m);m.raw_page(2,cwindow)
                        N.put(m,CurrentBankC=cwindow,FrameCounter=1)
                        y=6 if row==10 else 9 if row==14 else 109
                        results.append(C.I.invoke(m,193,0xb08c+3*row,(83,0,y,flags)))
                    assert results[0]['regs']==results[1]['regs']and view(instances[0])==view(instances[1]),('current foreign public',owner,cwindow,row,flags,results[0]['regs'],results[1]['regs'])
                    count+=1
        rows.append(dict(owner=owner,complete_cold_CPU=cold,published_rows=37,C_windows=[2,201],flag_states=4))
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        parent_memory_SHA256=A.sha(old['raw']),proposed_memory_SHA256=A.sha(new['raw']),
        actual_current_foreign_cold_Fresh_pairs=3,actual_current_foreign_public_pairs=count,owners=rows,
        full_private_native_ZP_SMC_liveStack_maps_PPU_AXYP_SP_exact=True,
        scope='Actual cf7+Prince130 versus exact proposed four-owner source factor, every foreign actor genuinely cold-loaded and constructed before every37-row comparison. All live source/private/native/ZP/SMC/active stack/maps/PPU and serviceAXYP/SP match. Sh legacy/raw-reject/virtual37 and populated retirement/IRQ remain separate, no shared/native admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),
            O/'native-owner-proposal-v79.json',O/'native-current-cold-v81-CPU.json',
            C.O/'strike-manifest-v130.json',C.O/'post-owner-v130.s',C.O/'post-selector-v130.s']})
    (O/'native-current-foreign-v82-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','actual_current_foreign_cold_Fresh_pairs','actual_current_foreign_public_pairs','owners']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-current-foreign-v82-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
