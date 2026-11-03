"""Four actual owner cold/readback/transition proofs for combined101 only."""
import json
from pathlib import Path
import measure_dkjr_prince_owner_1103_v101 as P
import check_prince_strike_cold_1103_v131 as C
import prepare_dkjr_anchored_owner_1103_v90 as DK

A,R,O,N=P.A,P.R,P.O,C.N


def main():
    b,q=P.image();seeds={};cold=[];payload=(O/'native-payload-v90.bin').read_bytes()
    for owner in [37,38,39,40]:
        m,z=C.cold(b,owner);seeds[owner]=N.fork(m)
        for bank in [2,3]:assert bytes(m.ram[bank][0x1fe0:0x1ff0])==bytes(m.ram[2][0x1fe0:0x1ff0])
        if owner==40:
            code=bytearray(payload[:8192]);code[0x1fe0:0x1ff0]=bytes.fromhex(q['DK_cookie'])
            assert bytes(m.ram[3])==bytes(code)
            assert bytes(m.ram[2][0x1000:0x1800])==payload[9216:11264]
            assert bytes(m.ram[2][:0x900])==bytes(2304)
        if owner==38:
            live=(P.PR.O/'native-live-v149.bin').read_bytes()
            assert bytes(m.ram[3][0x1fa3:0x1fd8])==live
            assert bytes(m.ram[2][0x200:0x235])==bytes(53)
            assert bytes(m.ram[2][0x766:0x77f])==(P.PR.O/'native-installer-v153.bin').read_bytes()
        cold.append(dict(owner=owner,CPU=z['CPU'],minimum_SP=z['minSP'],cookie=bytes(m.ram[2][0x1fe0:0x1ff0]).hex(),Prince_live_install_checked=owner==38,DK_code_meta_zero_checked=owner==40))
        print('DKcombined cold owner',owner,'PASS',flush=True)
    transitions=[]
    for before in [37,38,39,40]:
        for after in [37,38,39,40]:
            m=N.fork(seeds[before]);C.fields(m,after)
            z=C.I.invoke(m,193,0xae00,(83,71,109,0x21));assert z['regs'][3]&1,(before,after,z['regs'])
            for bank in [2,3]:assert bytes(m.ram[bank])==bytes(seeds[after].ram[bank]),(before,after,bank)
            transitions.append(dict(old=before,new=after,CPU=z['CPU'],minimum_SP=z['minSP']))
        print('DKcombined transitions from',before,'PASS',flush=True)
    rejected=0
    for owner in [37,38,39,40]:
        for bank in [2,3]:
            for index in range(16):
                m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1;initial=[bytes(v)for v in m.ram]
                z=C.I.invoke(m,193,0xb08c,(83,71,109,0x21))
                assert not z['regs'][3]&1 and z['regs'][:3]==[83,71,109]
                assert initial==[bytes(v)for v in m.ram]
                rejected+=1
    # Direct all-foreign data comparison to159 is deliberately limited to
    # untouched payload/state, not resident temporary stack snapshots/cycles.
    old,_=P.PR.image();foreign=[]
    for owner in [37,38,39]:
        m,z=C.cold(old,owner);actual=seeds[owner]
        assert [bytes(m.ram[k])for k in [2,3]]==[bytes(actual.ram[k])for k in [2,3]],owner
        assert m.rawtags==actual.rawtags,owner
        foreign.append(owner)
    own=N.fork(seeds[40]);N.invoke(own,'HuFresh',a=83,x=0,y=109,p=0x21)
    assert own.ram[2][0x8fe]==1 and own.ram[2][0x6b]==1 and own.ram[2][0x65]==36
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),cold=cold,ordered_transitions=transitions,
        bad_header_bytes_rejected=rejected,unchanged_foreign_payload_state_and_maps=foreign,
        DK_Fresh=dict(Ready=1,source_state=1,original_defeat_counter=36),
        scope='Actual101 complete sharedcold worker/scatterbuffer/readback/authenticated four-owner retirement/typed originalboot and twoheaderpublication. All4owners/16transitions/128poisons. Prince53B BFA3 live leaf exact, stagedC200 cleared and realC766installer retained; DK8192code exceptintentional16headerbytes+2048meta+2304zero exactly90payload. Foreign37/38/39 cold completeprivate images/maps match canonical159. No wholeforeignnativeABI/SMC/ISR/lifecycle/native/menu approval.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(C.__file__),O/'native-combined-owner-v101-measurement.json',O/'native-payload-v90.bin',P.PR.O/'native-live-v149.bin',P.PR.O/'native-installer-v153.bin']})
    (O/'native-combined-cold-v102-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','memory_only_SHA256','bad_header_bytes_rejected','unchanged_foreign_payload_state_and_maps','DK_Fresh']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-combined-cold-v102-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
