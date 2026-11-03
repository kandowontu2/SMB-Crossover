"""Measure exact existing rare/bbox operand extensions for Mini raw41."""
from pathlib import Path
import hashlib
import itertools
import json
from py65.devices.mpu6502 import MPU
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-native-gates-1103-v23'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
sha=lambda b:hashlib.sha256(b).hexdigest()


def memory(raw,bank):
    m=[0]*65536;m[0xa000:0xc000]=raw[16+bank*8192:16+(bank+1)*8192]
    return m


def run(m,pc,stops,a,x,y,p):
    cpu=MPU(memory=m,pc=pc);cpu.a,cpu.x,cpu.y,cpu.p=a,x,y,p;cpu.sp=224
    for _ in range(65):
        if cpu.pc in stops:break
        assert m[cpu.pc]!=0,('BRK',hex(cpu.pc))
        cpu.step()
    else:raise AssertionError(('finite gate',hex(cpu.pc)))
    return(cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)


def main():
    G.preflight(private_root=O,reserved_bytes=10000,reserved_files=1,fresh=True)
    O.mkdir(exist_ok=False);raw=ROM.read_bytes();assert sha(raw)==PIN
    patches=[];after=bytearray(raw)
    for bank,pc,old,new,role in [
        (124,0xa7cb,41,42,'Existing GmOnlyHigh rare bound admits41 alongside prior0..40'),
        (65,0xade3,2,3,'Existing source-funded FullBox gate admits36 or39..41')]:
        at=16+bank*8192+pc-0xa000;assert raw[at]==old
        after[at]=new;patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+1],
            file_offset=at,old_hex=bytes([old]).hex(),new_hex=bytes([new]).hex(),role=role))
    before_rare,new_rare=memory(raw,124),memory(after,124)
    foreign=own=0
    for selected,alt,subtype,y,a,p in itertools.product(
            range(256),[0,32,64,68],[0,1],range(16),[0,255],[0x20,0xe1]):
        rows=[]
        for m in [before_rare,new_rare]:
            m[0x6002],m[0x5fe5],m[0x5fee]=selected,alt,subtype
            rows.append(run(m,0xa22a,{0xa179,0xa24e,0xa252},a,197,y,p))
        if selected==41:
            assert rows[0][0]==0xa24e and rows[1][0]==0xa179,rows
            own+=1
        else:assert rows[0]==rows[1],(selected,rows);foreign+=1
    before_box,new_box=memory(raw,65),memory(after,65)
    assert bytes(before_box[0xadd8:0xaddf])==bytes.fromhex('08ad0260c924f0')
    box_foreign=box_own=0
    for selected,a,p in itertools.product(range(256),[0,255],[0x20,0x61,0xe0,0xa1]):
        rows=[]
        for m in [before_box,new_box]:
            m[0x6002]=selected
            rows.append(run(m,0xadd8,{0x9f4e,0x15a},a,71,109,p))
        if selected==41:
            assert rows[0][0]==0x9f4e and rows[1][0]==0x15a,rows
            box_own+=1
        else:assert rows[0]==rows[1],(selected,rows);box_foreign+=1
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,granted=False,
        native_admitted=False,parent_ROM_SHA256=PIN,patches=patches,
        rare_exact_foreign_cases=foreign,rare_intended41_cases=own,
        bbox_exact_foreign_cases=box_foreign,bbox_intended41_cases=box_own,
        scope='Only two existing immediate operands. All256 selector values and native rare alternate/subtype/policy/A/P contexts preserve non41 gate targetAXYP/SP. Bbox gate keeps its source37B body/ADFD RTS and nativeFarCall ABI. No payload/header bypass.',
        limits='Mini full payload/header/selector/scene/caller/IRQ and actual native movement/bbox/contact/item qualification remain required. These CPU gate cuts stop at named authority/fallback entries, not after private callbacks.',
        bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in [Path(__file__),ROM,
            R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
