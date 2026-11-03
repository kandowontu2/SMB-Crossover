"""Current shared cold/readback/header rejection for final private callbacks."""
import json
from pathlib import Path
import compose_bub_tail_gateways_1102_v66 as G
import check_bubble_bobble_common_cold_1102_v4 as C
from prepare_selected_native_packet_v1 import R,sha
Q,N=G.G.G.Q,G.G.G.Q.N
O=R/'build/bub-upgrades-root-cold-1102-v71'

def main():
    O.mkdir(exist_ok=True);old,b,route,q=G.bundles();labels=C.P.P.labels(R/'build/bubble-bobble-source-1101-v1/common-owner.lbl')
    image=(G.U.O/'private-image.bin').read_bytes();cookie=bytes.fromhex(q['new_cookie']);rows=[];poisons=0
    for case,fault in [('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('protected','locked')]:
        m=C.ready(b);N.put(m,SelectedCharacter=39)
        if fault=='locked':m.protection=[0,0]
        elif fault:m.corrupt_at=fault
        scratch=bytes(m[3:11]);maps=m.rawtags[:];r=C.call(m,labels['CoCold'])
        assert bytes(m[3:11])==scratch and m.rawtags==maps
        if fault:assert not r['P']&1 and m.ram[2][0x1fe0]!=0xa7
        else:
            assert r['P']&1 and bytes(m.ram[3][:0x1fe0])==image[:0x1fe0]
            for bank in [2,3]:assert bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie
            before=m.ppu_reads;writes=len(m.ram_writes);warm=C.call(m,labels['CoCold'])
            assert warm['P']&1 and before==m.ppu_reads and writes==len(m.ram_writes)
            for bank in [2,3]:
                for i in range(16):
                    z=N.fork(m);z.ram[bank][0x1fe0+i]^=1;state=[bytes(v) for v in z.ram];p=C.call(z,labels['CoCheckCode'])
                    assert not p['P']&1 and state==[bytes(v) for v in z.ram];poisons+=1
        rows.append(dict(case=case,cold_return_C=bool(r['P']&1),minimum_SP=r['min_SP']))
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],cases=rows,full_header_poison_rejections=poisons,scope='Actual current shared owner/cold decoder with final8carrier branch-relaxed body, helper441 and full newcookie. Exact code readback, all32header bytes required, warm noPPUread/noRAMwrite, physical code/helper corruption and WRAMprotection reject without publishingready. No cold-IRQ sweep/emulator/native gameplay claim.',bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),G.O/'proposal.json',G.U.O/'proposal.json',G.U.O/'private-image.bin']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
