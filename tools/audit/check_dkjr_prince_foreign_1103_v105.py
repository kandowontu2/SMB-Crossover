"""Positive actual foreign source services and fail-closed raw-ID parity101."""
import itertools
import json
from pathlib import Path
import measure_dkjr_prince_owner_1103_v101 as P
import check_prince_strike_cold_1103_v131 as C
import check_dkjr_current_foreign_1103_v82 as V

A,R,O,N,W=P.A,P.R,P.O,C.N,P.A.W


def loaded(base,owner):
    if owner==36:
        N.Bus=C.C.C.C.V.ControllerBus;m=N.fresh(base)
        for bank in [2,3]:m.ram[bank][:]=bytes([0x9d])*8192;m.ram[bank][0x1fe0:0x1ff0]=bytes(16)
        C.fields(m,owner);out=C.I.invoke(m,193,0xa87f,(83,71,109,0x21));assert out['regs'][3]&1
    else:m,out=C.cold(base,owner)
    z=N.invoke(m,'HuFresh',a=83,x=0,y=109,p=0x21);assert z['P']&1,owner
    C.clear(m);return m


def main():
    old,_=P.PR.image();new,q=P.image();count=0;owners=[]
    for owner in [36,37,38,39]:
        pair=[loaded(base,owner)for base in [old,new]]
        assert V.view(pair[0])==V.view(pair[1]),('foreigncold/Fresh',owner)
        for window,row,flags in itertools.product([2,201],range(38),[0x21,0x60,0xa1,0xe1]):
            instances=[N.fork(m)for m in pair];results=[]
            for m in instances:
                C.clear(m);m.raw_page(2,window);N.put(m,CurrentBankC=window,FrameCounter=1)
                y=6 if row==10 else 9 if row==14 else 109
                target=0xb029 if row==37 else 0xb08c+3*row
                results.append(C.I.invoke(m,193,target,(83,0,y,flags)))
            assert results[0]['regs']==results[1]['regs']and V.view(instances[0])==V.view(instances[1]),('foreign public',owner,window,row,flags,results[0]['regs'],results[1]['regs'])
            count+=1
        owners.append(owner);print('DKcombined foreign positive',owner,'38rowsPASS',flush=True)
    # Invalid/nonmatching owners cannot gain private movement/body/event or
    # contact access. UI26/30's deliberate native forwarding is outside this
    # reject cohort and above has positive current-owner service coverage.
    rejects=0
    for owner,row,flags in itertools.product([x for x in range(256)if x not in [36,37,38,39,40]],[0,11,16,27,37],[0x21,0x60,0xa1,0xe1]):
        instances=[];results=[]
        for base in [old,new]:
            m=N.fresh(base);C.fields(m,owner);C.clear(m)
            target=0xb029 if row==37 else 0xb08c+3*row
            results.append(C.I.invoke(m,193,target,(83,71,109,flags)));instances.append(m)
        assert results[0]['regs']==results[1]['regs']and V.view(instances[0])==V.view(instances[1]),('foreign reject',owner,row,flags)
        assert not results[1]['regs'][3]&1
        rejects+=1
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        parent_memory_SHA256=A.sha(old['raw']),memory_only_SHA256=A.sha(new['raw']),
        actual_foreign_owners=owners,positive_source_service_pairs=count,nonmatching_raw_reject_pairs=rejects,
        rows_per_positive_owner=38,virtual_contact37=0xb029,real_B0FB_unchanged=True,
        full_private_native_ZP_SMC_liveStack_maps_PPU_AXYP_SP_exact=True,
        scope='Canonical159 versus combined101. Sh36 genuineA87Floader, otherthree actualfullcold; all actualHuFresh at forcedblank. Every37legacy publishedrows+virtual37, four publicflags,twoCwindows preserve complete original/private/native/ZP/liveSMC/liveStack/maps/PPU/AXYP/SP. All251otherraws fiveinert movement/body/fullbox/bounce/contactrows failclosed with exactforeign parity. RealB0FBMenuDone never executed as virtual37. Scene40 andnewcold/headerIRQ/finalPrincecanonical rebind remain outside this test.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(C.__file__),Path(V.__file__),O/'native-combined-owner-v101-measurement.json',O/'native-combined-cold-v104-CPU.json',R/'build/shinobi-bbox-design-1101-v29/resident-design.bin']})
    (O/'native-combined-foreign-v105-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','actual_foreign_owners','positive_source_service_pairs','nonmatching_raw_reject_pairs']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-combined-foreign-v105-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
