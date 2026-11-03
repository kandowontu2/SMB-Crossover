"""Execute all current owner cold/readback/retirement on the DK proposal."""
import json
from pathlib import Path
import prepare_dkjr_current_owner_1103_v79 as P

A,R,O,N,C=P.A,P.R,P.O,P.C.N,P.C


def main():
    base,manifest=P.image();payload=(O/'native-payload-v79.bin').read_bytes()
    seeds={};cold=[]
    for owner in [37,38,39,40]:
        m,z=C.cold(base,owner)
        seeds[owner]=N.fork(m)
        if owner==40:
            assert bytes(m.ram[3])==payload[:8192]
            assert bytes(m.ram[2][0x1000:0x1800])==payload[9216:11264]
            assert bytes(m.ram[2][:0x900])==bytes(0x900)
            assert bytes(m.ram[2][0x1fe0:0x1ff0]).hex()==manifest['cookie']
        cold.append(dict(owner=owner,CPU=z['CPU'],minimum_SP=z['minSP'],
            complete_header=bytes(m.ram[2][0x1fe0:0x1ff0]).hex()))
    transitions=[]
    for old in [37,38,39,40]:
        for new in [37,38,39,40]:
            m=N.fork(seeds[old]);C.fields(m,new)
            z=C.I.invoke(m,193,0xae00,(83,71,109,0x21))
            assert z['regs'][3]&1,(old,new,z['regs'])
            for k in [2,3]:
                assert bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(seeds[new].ram[k][0x1fe0:0x1ff0])
            transitions.append(dict(old=old,new=new,CPU=z['CPU'],minimum_SP=z['minSP']))
    # The new image must not authenticate arbitrary matching header bytes.
    rejected=0
    for owner in [37,38,39,40]:
        for bank in [2,3]:
            for index in range(16):
                m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1
                before=[bytes(z)for z in m.ram]
                z=C.I.invoke(m,193,0xb08c,(83,71,109,0x21))
                assert not z['regs'][3]&1 and before==[bytes(z)for z in m.ram]
                assert z['regs'][:3]==[83,71,109]
                rejected+=1
    own=N.fork(seeds[40]);C.fields(own,40)
    fresh=N.invoke(own,'HuFresh',a=83,x=71,y=109,p=0x21)
    assert fresh['P']&1 and own.ram[2][0x8fe]==1 and own.ram[2][0x6b]==1
    assert own.ram[2][0x65]==36
    source_constructor=dict(ready=own.ram[2][0x8fe],state=own.ram[2][0x6b],
        original_defeat_counter=own.ram[2][0x65],actual_Fresh_CPU=fresh['CPU'])
    out=dict(passed=True,qualified=False,ROM_written=False,installed=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(base['raw']),cold=cold,all_ordered_transitions=transitions,
        bad_header_bytes_rejected=rejected,DK_constructor=source_constructor,
        actual_DK_all8192_code_and2048_metadata_exact=True,
        scope='Actual complete current proposed manager/common worker and DK119B bootstrap execute against real reserved physical payload pages. All4 owners,16 ordered transitions,128 bad-header byte rejects, complete headers and source constructor. Native scene/menu admission, populated retirement, full foreign/public ABI/IRQ/audio and root native gameplay remain unqualified; no shared or ROM mutation.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),
            O/'native-owner-proposal-v79.json',O/'native-payload-v79.bin',O/'native-owner-v79.bin',
            O/'native-owner-extra-v79.bin',O/'native-selector-v79.bin']})
    (O/'native-current-cold-v80-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','memory_only_SHA256','cold','bad_header_bytes_rejected','DK_constructor']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-current-cold-v80-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
