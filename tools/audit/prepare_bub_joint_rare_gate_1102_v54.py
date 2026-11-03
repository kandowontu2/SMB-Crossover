"""Joint Prince/Bub rare gate with exact foreign internal flags retained."""
import itertools,json,subprocess
from pathlib import Path
import check_bub_original_upgrades_1102_v49 as Q
import prepare_bub_original_upgrades_1102_v51 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-gate-1102-v54'
SOURCE=R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s'

def bundles():
    previous=Q.U;Q.U=U
    try:old,new,route,body=Q.bundles()
    finally:Q.U=previous
    q=json.loads((O/'proposal.json').read_text());raw=bytearray(new['raw'])
    for row in q['patches']:
        at=row['file_offset'];prior=bytes.fromhex(row['old']);data=bytes.fromhex(row['new']);assert raw[at:at+len(prior)]==prior;raw[at:at+len(data)]=data
    assert Q.L.P.sha(raw)==q['expected_memory_only_ROM_SHA256']
    return old,dict(new,raw=bytes(raw)),route,{**body,'expected_memory_only_ROM_SHA256':q['expected_memory_only_ROM_SHA256']}

def main():
    O.mkdir(exist_ok=True);prior=Q.U;Q.U=U
    try:old,new,route,body=Q.bundles()
    finally:Q.U=prior
    raw=new['raw'];source=SOURCE.read_text();assert ' jmp GmMatureGate\n .res 15,$ea\nOwn:'in source and ' jmp GmPickupGate\n .res 15,$ea\nIce:'in source
    off=lambda pc:16+124*8192+pc-0xa000
    assert raw[off(0xa2be):off(0xa2c5)]==bytes.fromhex('c925b08c4c79a1')
    assert raw[off(0xa7c7):off(0xa7d9)]==bytes.fromhex('4c5aa4')+bytes([234])*15
    assert raw[off(0xa81c):off(0xa82e)]==bytes.fromhex('4c65a4')+bytes([234])*15
    asm='''.setcpu "6502"
.export JointRare,JointRareEnd,RestoreNo,RestoreNoEnd
.segment "PRIMARY"
JointRare:
 cmp #40
 .byte $b0,$a81f-($a7ca+4) ; BCS RestoreNo across separately linked tails.
 cmp #37
 .byte $f0,$a81f-($a7ca+8) ; BEQ RestoreNo; exact fixed span bound below.
 jmp $a2c2
JointRareEnd:
.segment "RESTORE"
RestoreNo:
 cmp #37 ; Preserve exact original foreign internal NZ/C before old reject.
 jmp $a24e
RestoreNoEnd:
'''
    (O/'gate.s').write_text(asm);(O/'gate.cfg').write_text('MEMORY{P:start=$a7ca,size=$f,file=%O;R:start=$a81f,size=$f,file="'+(O/'restore.bin').as_posix()+'";}SEGMENTS{PRIMARY:load=P,type=ro;RESTORE:load=R,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for command in[[cc/'ca65.exe',O/'gate.s','-o',O/'gate.o'],[cc/'ld65.exe','-C',O/'gate.cfg',O/'gate.o','-o',O/'gate.bin','-Ln',O/'gate.lbl']]:
        p=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    primary=(O/'gate.bin').read_bytes();restore=(O/'restore.bin').read_bytes();assert len(primary)==11 and len(restore)==5
    changes=[(0xa2be,bytes.fromhex('4ccaa7ea')),(0xa7ca,primary),(0xa81f,restore)];post=bytearray(raw);patches=[]
    for pc,data in changes:
        at=off(pc);patches.append(dict(CPU_half_open=[pc,pc+len(data)],physical_PRG=124,file_offset=at,old=raw[at:at+len(data)].hex(),new=data.hex()));post[at:at+len(data)]=data
    memories=[]
    for image in[raw,bytes(post)]:
        mem=[0]*65536;mem[0xa000:0xc000]=image[16+124*8192:16+125*8192];memories.append(mem)
    foreign=changed=0
    for selected,alt,subtype,y,a,p in itertools.product(range(256),[0,32,64,68],[0,1],range(16),[0,255],[0x20,0xe1]):
        results=[]
        for mem in memories:
            mem[0x6002]=selected;mem[0x5fe5]=alt;mem[0x5fee]=subtype;c=Q.N.NesMPU(memory=mem,pc=0xa22a);c.a,c.x,c.y,c.p,c.sp=a,197,y,p,224
            for _ in range(65):
                if c.pc in[0xa179,0xa24e,0xa252]:break
                assert mem[c.pc]!=0;c.step()
            else:raise AssertionError('Classifier bound')
            results.append((c.pc,c.a,c.x,c.y,c.p,c.sp))
        if selected not in[38,39]:assert results[0]==results[1],(selected,alt,subtype,y,a,p,results);foreign+=1
        else:assert results[0][0]==0xa24e and results[1][0]==0xa179;changed+=1
    q=dict(passed=True,proposal_only=True,ROM_written=False,installed=False,parent_ROM_SHA256=U.PIN,prior_memory_SHA256=Q.L.P.sha(raw),expected_memory_only_ROM_SHA256=Q.L.P.sha(post),patches=patches,source_funding=dict(existing_Prince_primary_pad=[0xa7ca,0xa7d9],primary_used=11,new_NrPickup_source_pad=[0xa81f,0xa82e],secondary_used=5,original_gate_bytes=4),all_native_classifier_cases=foreign+changed,foreign_exact_AXYP_SP_and_target_cases=foreign,joint_38_39_intended_route_cases=changed,source_basis='Actual NrPickupCollision and NrPickup each end their foreign path with an unconditional JMP, followed by explicit15EA source padding and the real Own/Ice label. No normal fallthrough or published entry targets either tail. Existing exact central4B CMP37/BCS becomes JMP+NOP, all downstream addresses retained. RestoreNo repeats CMP37 for all rejected values, preserving original foreign internal NZ/C as well as AXY/SP.',scope='Memory-only joint38+39 rare classification proposal. Current native host skipped both HuMature and HuPickup for Bub39; corrected public pickup24 alone is insufficient. Includes existing approved Prince native-gate source funding plus5B of separate source-declared NrPickup tail; root source review required before ROM emission. Full PowerUpObjHandler, owner lifecycle, header/ISR and native gameplay are still required.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),SOURCE,U.O/'proposal.json',U.O/'private-image.bin',O/'gate.s',O/'gate.bin',O/'restore.bin']})
    (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['patches','bindings']}))

if __name__=='__main__':main()
