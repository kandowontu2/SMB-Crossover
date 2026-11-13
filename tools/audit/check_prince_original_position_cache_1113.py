"""Independent donor save/restore oracle; no host game-state or ROM writes."""
from hashlib import sha256
import argparse
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


def split_check():
    import prince_draw_cache_1113 as Fix
    parent=(R.parent.parent.parent/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(parent).hexdigest()==Fix.PARENT
    candidate,info=Fix.proposal(parent)
    assert sha256(candidate).hexdigest()=='209abc2fd6144d59720e54352ed6f9f7384e2fa9ede0fbb1fb37f9e02d385008'
    assert Fix.reverse(candidate)==parent
    _,before,_=Fix.Packet.extract(parent)
    _,after,_=Fix.Packet.extract(candidate)
    assert tuple(map(len,before))==tuple(map(len,after))
    assert before[1:]==after[1:]
    allowed={pc-0xa000+i for pc,old,new in Fix.EDITS for i in range(len(old))}
    assert len(allowed)==24
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(before[0],after[0])))
    memory=bytearray(65536)
    memory[0xa000:0xa000+len(after[0])]=after[0]
    cpu=NesMPU(memory=memory,pc=0xb396)
    maximum_steps=0
    for value in range(65536):
        lo,hi=value&255,value>>8
        flags=(lo^hi)&255
        memory[0xc60f:0xc611]=value.to_bytes(2,'little')
        memory[0xc4db:0xc4dd]=(value^65535).to_bytes(2,'little')
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc=85,lo,hi,flags,224,0xb396
        for steps in range(12):
            if cpu.pc==0xac3f:break
            cpu.step()
        else:raise AssertionError(('Split cache did not reach original AdvanceActor',value,hex(cpu.pc)))
        maximum_steps=max(maximum_steps,steps)
        assert memory[0xc4db:0xc4dd]==value.to_bytes(2,'little')
        expected_flags=(flags&~130)|(128 if hi&128 else 0)|(2 if hi==0 else 0)
        assert (cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)==(hi,lo,hi,expected_flags,222)
        assert memory[0x1df:0x1e1]==bytes.fromhex('98b3')
    ordinary=0
    for flags in range(256):
        state=bytes(memory[0xc000:0xc800])
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc=85,71,109,flags,224,0xa4c1
        cpu.step()
        assert (cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)==(0xa4cd,85,71,109,flags,224)
        assert bytes(memory[0xc000:0xc800])==state
        ordinary+=1
    return dict(passed=True,parent_SHA256=sha256(parent).hexdigest(),
        candidate_SHA256=sha256(candidate).hexdigest(),exact_inverse=True,
        decoded_runtime_edit_envelope=24,other_decoded_streams_exact=True,
        all_16bit_split_entry_cases=65536,maximum_split_instructions=maximum_steps,
        phase0_JSR_return_address_and_stack_retained=True,
        ordinary_material_bypass_flag_cases=ordinary,ordinary_bypass_state_exact=True,
        packed_runtime_bytes=info['packed_bytes'][0],staging_spare=6528-info['packed_bytes'][0],
        aggregate_packed_spare=info['spare'],ROM_files_written=0,host_gameplay_state_writes=0,
        Mesen_run=False,scope='Actual proposed decoded instructions in declared flat reference CPU fixtures, stopping at original AdvanceActor. Not a full Main, cold, interrupt or physical gameplay qualification.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split-candidate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(split_check() if args.split_candidate else check(),sort_keys=True),flush=True)
