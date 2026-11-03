"""Exact current cold authentication and init-only foreground equivalence."""
import hashlib,json
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
import check_bubble_bobble_common_cold_1102_v4 as C
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-current-cold-1103-v97'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'

def main():
    O.mkdir(exist_ok=True)
    _,parent,route,q,p,oldimage=H.bundle()
    manifest=R/'build/bub-initial-tier-1103-v87/proposal.json';init=json.loads(manifest.read_text())
    rom=R/init['candidate'];assert sha(rom)==PIN==init['ROM_SHA256']
    for f,h in init['bindings'].items():assert sha(R/f)==h,f
    current=dict(parent,raw=rom.read_bytes());image=(rom.parent/'private-image.bin').read_bytes();cookie=bytes.fromhex(init['cookie'])
    # Prove the entire cartridge delta, rather than assuming all other owners
    # or callbacks are unaffected by the new constructor.
    expected=bytearray(parent['raw']);changed=[]
    for i,page in enumerate(H.H.H.PAGES):
        at=1048592+page*1024;expected[at:at+1024]=image[i*1024:(i+1)*1024]
    expected[q['cookie_offset']:q['cookie_offset']+16]=cookie
    assert bytes(expected)==current['raw']
    for i,(a,b)in enumerate(zip(oldimage,image)):
        if a!=b:changed.append(0xa000+i)
    allowed=set(range(init['hook_CPU'],init['hook_CPU']+4))|set(range(init['leaf_CPU'],init['leaf_CPU']+10))
    assert set(changed)<=allowed and len(changed)==14
    assert image[init['hook_CPU']-0xa000:init['hook_CPU']-0xa000+4]==bytes.fromhex('4c20b3ea')
    assert image[init['leaf_CPU']-0xa000:init['leaf_CPU']-0xa000+10]==(rom.parent/'initial-tier.bin').read_bytes()
    labels=C.P.P.labels(R/'build/bubble-bobble-source-1101-v1/common-owner.lbl')
    cases=[];poisons=0
    for selected in[39]:
        for name,fault in [('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('protected','locked')]:
            m=C.ready(current);H.N.put(m,SelectedCharacter=selected)
            if fault=='locked':m.protection=[0,0]
            elif fault:m.corrupt_at=fault
            scratch=bytes(m[3:11]);maps=m.rawtags[:];r=C.call(m,labels['CoCold'])
            assert bytes(m[3:11])==scratch and m.rawtags==maps
            if fault:assert not r['P']&1 and m.ram[2][0x1fe0]!=167
            else:
                assert r['P']&1 and bytes(m.ram[3][:0x1fe0])==image[:0x1fe0]
                for bank in[2,3]:assert bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie
                reads=m.ppu_reads;writes=len(m.ram_writes);warm=C.call(m,labels['CoCold'])
                assert warm['P']&1 and reads==m.ppu_reads and writes==len(m.ram_writes)
                for bank in[2,3]:
                    for i in range(16):
                        z=H.N.fork(m);z.ram[bank][0x1fe0+i]^=1;before=[bytes(v)for v in z.ram]
                        rr=C.call(z,labels['CoCheckCode']);assert not rr['P']&1 and before==[bytes(v)for v in z.ram];poisons+=1
                H.N.put(m,SelectedCharacter=0);ret=C.call(m,labels['CoRetire'])
                assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
                before=[bytes(v)for v in m.ram];C.call(m,labels['CoRetire']);assert before==[bytes(v)for v in m.ram]
            cases.append(dict(case=name,carry=bool(r['P']&1),minimum_SP=r['min_SP']))
    # Parent proofs keep their own cc7 hash. This additional exact-candidate
    # comparison establishes the changed constructor does not alter their
    # initialized foreground state or any original instruction trace.
    actual=H.N.NesMPU;trace=[];paired=0;cost=[]
    class Trace(actual):
        def step(self):
            m=self.memory
            if m.rawtags[1]==3 and 0xa100<=self.pc<q['labels']['BbCodeEnd']:
                trace.append((self.pc,self.a,self.x,self.y,self.p,self.sp))
            return super().step()
    H.N.NesMPU=Trace
    try:
        for identity in[0,1]:
            for keys in[0,1,2,129,130]:
                pair=[H.Q.Q.fresh(b,route,identity)for b in[parent,current]]
                for m in pair:H.N.put(m,PlayerStatus=0);H.Q.L.E.main_fields(m)
                for epoch in range(25):
                    outs=[];traces=[]
                    for m in pair:
                        pad=(keys&3)|(128 if keys&128 and epoch==1 else 0)
                        H.N.put(m,FrameCounter=epoch,SavedJoypadBits=pad,SavedJoypad1Bits=pad,VRAM_Buffer1_Offset=0)
                        trace.clear();outs.append(H.N.invoke(m,'GameCoreRoutine',x=0,y=0));traces.append(tuple(trace))
                    a,z=pair
                    assert traces[0]==traces[1] and bytes(a.ram[2][:0x1000])==bytes(z.ram[2][:0x1000])
                    assert bytes(a[0x200:0x800])==bytes(z[0x200:0x800])
                    assert bytes(a[3:11])==bytes(z[3:11])and bytes(a[0x15a:0x17b])==bytes(z[0x15a:0x17b])and a.rawtags==z.rawtags
                    assert[outs[0][k]for k in['A','X','Y','P','minimum_SP']]==[outs[1][k]for k in['A','X','Y','P','minimum_SP']]
                    cost.append(outs[1]['CPU']-outs[0]['CPU']);paired+=1
    finally:H.N.NesMPU=actual
    assert set(cost)=={0}
    out=dict(passed=True,CPU_only=True,installed=False,ROM_SHA256=PIN,parent_ROM_SHA256=init['parent_ROM_SHA256'],exact_cartridge_delta_only_initialization_and_cookie=True,changed_private_bytes=len(changed),changed_private_CPU=changed,cold_cases=cases,header_poison_rejections=poisons,repeat_retire_unchanged=True,paired_Main_updates=paired,original_instruction_AXYP_SP_exact=True,full_source_native_scratch_SMC_maps_exact=True,CPU_delta_range=[min(cost),max(cost)],new_instruction_interrupts=init['new_instruction_IRQs'],scope='Exact cf7 cold/readback/warm/32byte-header-rejection/code+helperfault/protection/retire and250pairedMain updates. Parent cc7 head ISR receipts retain their own hash and scope; no claim those runs used cf7. New init-only instructions have their separately bound10IRQ/10genuineFF checks; candidate88 has actual two mushroom/two full1-1 runs. Flower route/performance/audio fidelity remain incomplete.',bindings={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),manifest,rom.parent/'private-image.bin',H.O/'head-projection-v55.json',R/'docs/qa/checkpoints/2026-11-03/bub-earned-native-v90/receipt.json']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['bindings','changed_private_CPU']}))

if __name__=='__main__':main()
