"""Zero-output CPU qualification of the mounted Steve armor packet."""

import json
import argparse
from unittest.mock import patch

import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet
from check_steve_armor_transport_1112 import call


def check(raw, *, interrupts=False, reverse=False,fast_order=False,faults=False):
    if fast_order:
        with patch.object(Live,'order_blocks',lambda rows:rows):
            candidate, info = Live.proposal(raw)
    else:
        candidate, info = Live.proposal(raw)
    if reverse:
        assert Live.reverse(candidate) == raw
    cuts = set()
    cold_labels = info['program']['symbols']
    cold_points = {cold_labels[name] for name in ('StevePacketCold', 'DecodePass', 'ReadByte',
                                                'WriteByte', 'NextBlock', 'CommitRaw1', 'ColdReturn')}

    def cold_interrupt(memory, cpu):
        if not interrupts or memory.rawtags[1] != 1 or cpu.pc not in cold_points:
            return
        key = ('cold',cpu.pc,memory[cold_labels['ComparePass']],
               memory[7] if cpu.pc == cold_labels['ReadByte'] else None)
        if key in cuts:
            return
        cuts.add(key)
        _, branch = Packet.Cold.C.Vector.clone(memory,cpu)
        Packet.Cold.C.ColdVector.interrupt(branch,'FF')

    memory, steps = Packet.load(candidate, info, observe=cold_interrupt)
    C, N, W = Packet.Cold.C, Packet.Cold.N, Packet.Cold.W
    rejected_faults = []
    if faults:
        for fault in ((1,0),(1,len(info['runtime']['images']['STEVE_ARMOR_RUNTIME'])-1),
                      (2,0x1ee),(2,0x3fa),(3,0x1f1f)):
            broken = C.Common.blank(Packet.Host.C.Start.W.bundle(candidate))
            C.Common.scene(broken,16)
            broken[0x730b] = 0x40
            broken.corrupt_at = fault
            Packet.load(candidate,info,broken,allow_failure=True)
            assert not any(broken.ram[bank][0x1fe0] for bank in (1,2,3)), fault
            broken.corrupt_at = None
            Packet.load(candidate,info,broken)
            rejected_faults.append(fault)
    original = Packet.original_resident(raw)
    assert bytes(memory.ram[3][:0xb00]) == original[3][:0xb00]
    expected = bytearray(original[3])
    for address,before,after in info['wave_hooks']:
        offset = address-0xa000
        assert expected[offset:offset+len(before)] == before
        expected[offset:offset+len(after)] = after
    assert bytes(memory.ram[3][0x1000:0x1fe0]) == expected[0x1000:0x1fe0]
    memory.raw_page(2,2)
    memory[0xc033] = 0xa5
    reads = memory.ppu_reads
    Packet.load(candidate,info,memory)
    assert memory.ppu_reads == reads and memory[0xc033] == 0
    memory.ram[1][0x1fef] ^= 1
    Packet.load(candidate,info,memory)
    recovery_reads = memory.ppu_reads-reads
    assert recovery_reads > 0
    memory[0xc033] = 0xa5
    N.put(memory,FamilyMainCommit=0)
    reads = memory.ppu_reads
    Packet.load(candidate,info,memory)
    assert memory.ppu_reads == reads and memory[0xc033] == 0xa5
    N.put(memory,FamilyMainCommit=1)
    Packet.load(candidate,info,memory)
    N.put(memory, GamePauseStatus=0, PlayerFacingDir=1, Player_X_Position=64,
          Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1,
          Player_State=0, SavedJoypadBits=0, GameEngineSubroutine=8,
          Player_Rel_XPos=64, Player_Rel_YPos=176)
    memory.raw_page(1, 3)
    memory.raw_page(2, 2)
    N.put(memory, CurrentBank=3, CurrentBankC=2)
    memory[0xc1f0:0xc200] = bytes(16)
    memory[0xc1f6], memory[0xc1f1] = 1, 0x15
    cpu = N.NesMPU(memory=memory)
    states = []
    for age in range(1, 180):
        N.put(memory, FrameCounter=age&255)
        call(cpu, 0xca00)
        if age in (80,81,128,159,179):
            states.append((age, memory[0xc1f4], memory[0xc1f3], memory[0xc1f9], memory[0xc1f2]))
        if age == 159:
            assert (memory[0xc1f4], memory[0xc1f9], memory[0xc1f2]) == (0,3,127)
    assert states[:3] == [(80,13,48,127,0), (81,13,47,123,0), (128,13,0,123,0)], states
    pose_cases = 0
    for face in (1, 2):
        N.put(memory, PlayerFacingDir=face)
        for pose, (page, right, left) in info['records'].items():
            memory[0x5c80], memory[0x5c83] = 1, pose
            C.Vector.call(memory, 'JnSetPose', x=0)
            C.Vector.call(memory, 'X5PublishChr')
            record = right if face == 1 else left
            expected = bytearray(record)
            for at in range(1, len(expected), 4):
                expected[at+2] = (expected[at+2]+16)&255
                expected[at+3] = (expected[at+3]+8)&255
            assert bytes(memory[0xc8c0:0xc8c0+len(expected)]) == expected, (face, hex(pose))
            assert N.get(memory, 'SmPosePtr') | N.get(memory, 'SmPosePtr', 1)<<8 == 0xc8c0
            assert memory.chr_latches[0] == page, (face, hex(pose), page, memory.chr_latches)
            pose_cases += 1
    memory.raw_page(1, 3)
    N.put(memory, CurrentBank=3, FrameCounter=16)
    memory[0xc1f2] = 2
    call(cpu, 0xca00)
    assert (memory[0xc1f4], memory[0xc1f2], memory[0xc97c]) == (16,0,16)
    for exit_age in range(1, 300):
        N.put(memory, FrameCounter=(16+exit_age)&255)
        call(cpu, 0xca00)
        if not memory[0xc1f4]:
            break
    else:
        raise AssertionError('Mounted original exit did not finish')
    assert memory[0xc1f2] == 0 and memory[0xc1f6] == 1 and memory[0xc1f7] == 16
    assert memory[0xc1fd] == 255
    injury_cases = 0

    def injury_interrupt(m, cpu):
        if not interrupts or cpu.pc < 0x8000:
            return
        bank = m.rawtags[(cpu.pc-0x8000)//8192]
        owned = ((bank == 0x85 and 0xbfdf <= cpu.pc < 0xc000) or
                 (bank == 0x88 and 0xbfe6 <= cpu.pc < 0xc000) or
                 (bank == 1 and 0xa000 <= cpu.pc < 0xa800) or
                 (bank == 2 and (0xc3bf <= cpu.pc < 0xc400 or 0xcd00 <= cpu.pc < 0xcd88)))
        key = ('injury',bank,cpu.pc)
        if not owned or key in cuts:
            return
        cuts.add(key)
        for kind in ('FF','IRQ'):
            _, branch = C.Vector.clone(m,cpu)
            C.ColdVector.interrupt(branch,kind)
    for c_map in (2, 3, 0xe1):
        for slot in (0, 1, 5, 127, 255):
            memory.raw_page(2, 2)
            memory[0xc1f2], memory[0xc97e], memory[0x5c85] = 127, 32, 127
            N.put(memory, JnHealth=6, JnHurt=0, CurrentBankC=c_map)
            memory.raw_page(2, c_map)
            current = C.Vector.call(memory, 'JnInjury', x=slot, y=109,
                                    observe=injury_interrupt if slot == 5 and c_map == 0xe1 else None)
            assert N.get(memory, 'JnHealth') == 6 and N.get(memory, 'JnHurt') == 0
            assert memory.ram[2][0x1f2] == 119 and memory.ram[2][0x97e] == 0
            assert (current.x, current.y, current.sp, current.p&1) == (slot, 109, 224, 1)
            assert memory.rawtags[2] == N.get(memory, 'CurrentBankC') == c_map
            injury_cases += 1
    memory.raw_page(2, 2)
    N.put(memory, CurrentBankC=2, JnHealth=1)
    assert C.Vector.call(memory, 'JnInjuryStatus').a == 1 and N.get(memory, 'JnHealth') == 1
    for bank in (1, 2, 3):
        saved = bytes(memory.ram[bank][0x1fe0:0x1ff0])
        memory.ram[bank][0x1fef] ^= 1
        memory.ram[2][0x1f2], memory.ram[2][0x97e] = 127, 32
        N.put(memory, JnHealth=6, JnHurt=0)
        current = C.Vector.call(memory, 'JnInjury', x=5, y=109)
        assert N.get(memory, 'JnHealth') == 4 and N.get(memory, 'JnHurt') == 60, bank
        assert memory.ram[2][0x1f2] == 127, bank
        assert (current.x, current.y, current.sp, current.p&1) == (5,109,224,1)
        for owner in (1,2,3):
            memory.ram[owner][0x1fe0:0x1ff0] = info['cookie']
    return dict(parent=Packet.Entry.digest(raw), candidate=Packet.Entry.digest(candidate),
                cold_steps=steps, packed_bytes=info['packed_bytes'], spare=info['spare'],
                matching_pattern_and_robot_fixture=True, entry_updates=159,
                source_timing_states=states, native_pose_calls=pose_cases,
                source_exit_updates=exit_age, native_injury_hook_mounted=True,
                native_injury_cases=injury_cases, corrupted_owner_headers_rejected=3,
                warm_extra_reads=0,raw1_header_recovery_reads=recovery_reads,
                rejected_phase_unchanged=True,
                interrupt_cut_points=len(cuts), exact_reverse=reverse,
                write_readback_faults_rejected_and_recovered=rejected_faults,
                packet_order_optimized=not fast_order,
                original_jay_preserved=True, release_qualified=False, output_files=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interrupts',action='store_true')
    parser.add_argument('--reverse',action='store_true')
    parser.add_argument('--fast-order',action='store_true')
    parser.add_argument('--faults',action='store_true')
    parser.add_argument('--before-quick',action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(Packet.qualification_parent(before_quick=args.before_quick), interrupts=args.interrupts,
                           reverse=args.reverse,fast_order=args.fast_order,faults=args.faults),
                     sort_keys=True), flush=True)
