"""Independent donor save/restore oracle; no host game-state or ROM writes."""
from hashlib import sha256
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as Original
from verify_native_relocation import NesMPU


def check():
    raw = Original.donor()
    save = raw[16+4*16384+0x2f57:16+4*16384+0x2f57+12]
    restore = raw[16+7*16384+0x1afa:16+7*16384+0x1afa+12]
    assert save == bytes.fromhex('ad0f068ddb04ad10068ddc04')
    assert restore == bytes.fromhex('addb048d0f06addc048d1006')
    # The source host relocates original $0000..$07FF to RAM2 C000..C7FF.
    translated = bytearray(save)
    for at in (2,5,8,11):
        translated[at] |= 0xc0
    assert translated == bytes.fromhex('ad0fc68ddbc4ad10c68ddcc4')
    reference,host = bytearray(65536),bytearray(65536)
    reference[0xa000:0xa00c] = save
    reference[0xa020:0xa02c] = restore
    host[0xa000:0xa00c] = translated
    before = [bytes(reference),bytes(host)]
    a,b = NesMPU(memory=reference,pc=0xa000),NesMPU(memory=host,pc=0xa000)
    examples=[]
    for value in range(65536):
        lo,hi = value&255,value>>8
        flags=(lo^hi)&255
        for cpu,base in ((a,0),(b,0xc000)):
            mem=cpu.memory
            mem[base+0x60f],mem[base+0x610]=lo,hi
            mem[base+0x4db],mem[base+0x4dc]=lo^255,hi^255
            cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc=85,lo,hi,flags,224,0xa000
            for _ in range(4):cpu.step()
            assert cpu.pc==0xa00c
            assert mem[base+0x4db:base+0x4dd]==value.to_bytes(2,'little')
            assert (cpu.x,cpu.y,cpu.sp)==(lo,hi,224)
            assert cpu.p&~130 == flags&~130
        assert (a.a,a.x,a.y,a.p,a.sp)==(b.a,b.x,b.y,b.p,b.sp)
        # The actual original restore must recover the saved value, rather
        # than the deliberately changed current coordinate.
        reference[0x60f],reference[0x610]=lo^255,hi^255
        a.pc=0xa020
        for _ in range(4):a.step()
        assert a.pc==0xa02c and reference[0x60f:0x611]==value.to_bytes(2,'little')
        if value in (0,255,256,1463,32768,65535):
            examples.append(dict(source_x=value,saved_x=int.from_bytes(host[0xc4db:0xc4dd],'little'),
                restored_x=int.from_bytes(reference[0x60f:0x611],'little')))
    # No instruction may affect any byte outside the explicitly declared
    # original source coordinate/cache and their existing host relocation.
    for mem,old,base in ((reference,before[0],0),(host,before[1],0xc000)):
        changed={i for i,(x,y) in enumerate(zip(mem,old)) if x!=y}
        assert changed <= {base+0x60f,base+0x610,base+0x4db,base+0x4dc}
    return dict(passed=True,donor_SHA256=sha256(raw).hexdigest(),
        actual_original_save=save.hex(),actual_original_restore=restore.hex(),
        exact_host_translation=translated.hex(),all_16bit_coordinate_cases=65536,
        reference_and_translation_registers_flags_stack_equal=True,
        original_restore_recovers_saved_coordinate=True,examples=examples,
        host_gameplay_state_writes=0,ROM_changes=0,outputs=0,Mesen_run=False,
        scope='Four actual donor save instructions and four actual donor restore instructions in a flat CPU oracle. This qualifies the proposed12-byte relocated save semantics, not placement, Main scheduling, interrupts or gameplay.')


if __name__=='__main__':
    print(json.dumps(check(),sort_keys=True),flush=True)
