"""Current-byte Main publication/auth lifetime census; no cache or ROM writes."""
import collections, hashlib, json, zipfile
from pathlib import Path
import measure_bub_landing_1102_v21 as L

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address
O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    _,b,layout,route=L.bundle()
    rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes()
    assert P.sha(b['raw'])==PIN
    raw=b['raw'];owner=P.P.labels(L.B/'native-event-v9-owner.lbl')
    routes=P.P.labels(L.B/'native-proxy-routes.lbl')
    protocol=address(b,'FamilyMainCommit');assert protocol==0x5fff
    # These are literal references, not an assertion that arbitrary ROM data
    # is executable. Each current candidate below has an instruction/context
    # binding. The existing dedicated-byte source grant covers the inherited
    # indexed/indirect constructor domains, not merely this literal search.
    literals=[]
    for bank in range(128):
        data=raw[16+bank*8192:16+(bank+1)*8192]
        for offset in range(8190):
            opcode=data[offset]
            if opcode not in [0xad,0xae,0xac,0xcd,0x2d,0x0d,0x8d,0x8e,0x8c,0xee,0xce]:continue
            if data[offset+1:offset+3]!=b'\xff\x5f':continue
            role='read' if opcode in [0xad,0xae,0xac,0xcd,0x2d,0x0d] else 'write'
            suffix=data[offset+3:offset+7]
            consumer=('mask_busy_1' if suffix[:2]==b'\x29\x01' else
                      'mask_Rogue_completed_6' if suffix[:2]==b'\x29\x06' else
                      'set_busy_OR_1' if suffix[:2]==b'\x09\x01' else
                      'nonzero_busy_guard' if bank==82 and offset==0x1e11 else 'writer')
            assert role=='write' or consumer!='writer',(bank,offset,data[offset:offset+12].hex())
            literals.append(dict(physical_PRG=bank,bank_offset=offset,role=role,
                opcode=opcode,consumer=consumer,context_half_open=[max(0,offset-5),offset+12],
                context=data[max(0,offset-5):offset+12].hex()))
    expected_writers={(63,0x1404),(63,0x1420),(63,0x1428),(63,0x1501),
        (63,0x1544),(63,0x15e1),(70,0x1c9a),(82,0x1df2),(95,0x18ae)}
    assert {(q['physical_PRG'],q['bank_offset']) for q in literals if q['role']=='write'}==expected_writers
    reader_counts=collections.Counter(q['consumer'] for q in literals if q['role']=='read')
    assert reader_counts=={
        'mask_busy_1':24,'mask_Rogue_completed_6':1,'set_busy_OR_1':1,'nonzero_busy_guard':1},reader_counts
    historical=R/'docs/qa/checkpoints/2026-10-30/joint-common-protocol-source/frozen-source-and-evidence.zip'
    member='build/character-host-union-rogue-v2/joint/rogue_dawn_audio_scheduler_hooks_v5.s'
    with zipfile.ZipFile(historical) as z:source=z.read(member)
    text=source.decode();assert 'RdsCommit=FamilyMainCommit' in text
    assert 'inc RdsCommit' in text and 'and #1\n sta RdsCommit' in text.replace('\r','')
    # Actual current Main gate's two public inputs remain exactly AFF begin
    # and A00 end. No source alias/old5FB6 byte is used for execution here.
    gate=address(b,'RdsMainGate');assert gate==0xb400
    gatefile=16+63*8192+0x1400
    assert raw[gatefile:gatefile+8]==bytes.fromhex('0848f017eeff5f68')
    assert raw[gatefile+0x26:gatefile+0x2b]==bytes.fromhex('a9008dff5f')
    native=N.NesMPU;cases=[]
    for identity in [0,1]:
        for keys in [0,1,129,64]:
            m=Q.fresh(b,route,identity);L.E.main_fields(m)
            N.put(m,FamilyMainCommit=0,NmiDisable=255,GamePauseStatus=0,
                FrameCounter=10,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
            events=[];headers=[];read_addresses=set();selected=set();row_counts=collections.Counter()
            class Trace(native):
                def step(self):
                    mem=self.memory;pc=self.pc
                    tag=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
                    before=(mem[protocol],tuple(bytes(mem.ram[k][0x1fe0:0x1ff0]) for k in [2,3]))
                    selected.add(N.get(mem,'SelectedCharacter'))
                    if tag==193 and pc==routes['ExDispatch']:
                        target=mem[address(b,'FarcallJmpTarget_SMC')+1]+256*mem[address(b,'FarcallJmpTarget_SMC')+2]
                        row=(target-0xb08c)//3;row_counts[row]+=1
                        events.append(dict(kind='service',row=row,Main_protocol=mem[protocol],SP=self.sp))
                    if tag==193 and pc==owner['CoCheckCode']:
                        events.append(dict(kind='full_auth',Main_protocol=mem[protocol],SP=self.sp))
                    z=native.step(self)
                    if mem[protocol]!=before[0]:events.append(dict(kind='protocol_write',physical_PRG=tag,PC=pc,old=before[0],new=mem[protocol]))
                    after=tuple(bytes(mem.ram[k][0x1fe0:0x1ff0]) for k in [2,3])
                    if after!=before[1]:headers.append(dict(physical_PRG=tag,PC=pc))
                    return z
            N.NesMPU=Trace
            try:
                begin=N.invoke(m,'PauseRoutine',a=255,x=7,y=91,p=0x31)
                assert N.get(m,'FamilyMainCommit')==1
                main=N.invoke(m,'GameCoreRoutine',x=0,y=0)
                assert N.get(m,'FamilyMainCommit')==1
                end=N.invoke(m,'RdsMainGate',a=0,x=7,y=91,p=0x31)
                assert N.get(m,'FamilyMainCommit')==0
            finally:N.NesMPU=native
            assert selected=={39} and not headers
            assert sum(q['kind']=='full_auth' for q in events)==sum(row_counts.values())
            cases.append(dict(identity=identity,held_keys=keys,begin=begin,Main=main,end=end,
                events=events,header_writes=headers,raw_owners=sorted(selected),service_rows=dict(sorted(row_counts.items()))))
    # A tentative high-bit lease is NOT implemented. These current-byte
    # controls establish that actual busy foreign NMI strips that bit while
    # preserving the real busy bit. Direct CoCheckCode always checks headers,
    # independent of the publication byte, including all32 byte poisons.
    nmis=[];poisons=0
    for identity in [0,1]:
        seed=Q.fresh(b,route,identity);L.E.main_fields(seed)
        for proposed_value in [0x81,0xc1,0xff]:
            m=N.fork(seed);N.put(m,FamilyMainCommit=proposed_value,NmiDisable=255)
            c=native(memory=m,pc=0x5b00);c.sp=224;c.p=0x31;c.a=17;c.x=53;c.y=71
            regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=list(m.rawtags)
            headers=[bytes(m.ram[k][0x1fe0:0x1ff0]) for k in [2,3]]
            smc=bytes(m[0x15a:0x17b]);scratch=bytes(m[3:11]);c.nmi()
            for _ in range(200000):
                if c.pc==regs[-1] and c.sp==regs[-2]:break
                assert m[c.pc]!=0,('Actual NMI BRK',hex(c.pc));c.step()
            else:raise AssertionError('Actual NMI return bound')
            assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc) and maps==m.rawtags
            assert smc==bytes(m[0x15a:0x17b]) and scratch==bytes(m[3:11])
            assert headers==[bytes(m.ram[k][0x1fe0:0x1ff0]) for k in [2,3]]
            assert N.get(m,'FamilyMainCommit')==1
            nmis.append(dict(identity=identity,declared_proposed_bits=proposed_value,
                actual_after_NMI=1,AXYP_SP_SMC_R0_7_maps_headers_exact=True,cycles=c.processorCycles))
        for protocol_value in [0,1,0x81]:
            for bank in [2,3]:
                for index in range(16):
                    m=N.fork(seed);N.put(m,FamilyMainCommit=protocol_value)
                    m.ram[bank][0x1fe0+index]^=1
                    before=[bytes(q) for q in m.ram];maps=list(m.rawtags);scratch=bytes(m[3:11])
                    result=L.E.C.call(m,owner['CoCheckCode'],flags=0x31)
                    assert not result['P']&1 and before==[bytes(q) for q in m.ram]
                    assert maps==m.rawtags and scratch==bytes(m[3:11])
                    assert N.get(m,'FamilyMainCommit')==protocol_value
                    poisons+=1
    out=dict(passed=True,ROM_written=False,source_mutated=False,cache_implemented=False,native=False,
        ROM_SHA256=PIN,publication_literal_census=literals,actual_Main_cases=cases,
        actual_busy_foreign_NMI_high_bit_invalidation=nmis,direct_full_auth_header_poison_cases=poisons,
        conclusions=[
            'FamilyMainCommit is a dedicated real odd/busy plus Rogue completed-count protocol, not an epoch counter.',
            'All27 literal readers mask1/mask6, setbusyOR1, or require nonzero busy. Existing foreign NMI AND1 clears any proposed high-bit lease; actual foreign Main-end stores0.',
            'Actual idle/walk/jump/shot GameCore calls retain raw39, busy1, both fullheaders and perform a full authentication for every dispatched service.',
            'No cache, selector bit, public ABI change, reduced header test, or new resource is implemented/allocated by this receipt.',
            'A possible scoped reuse still needs a complete current header/owner writer closure, genuine Main/direct-call ingress discrimination, pre-writer invalidation, source-funded byte fit and all actual IRQ/lagNMI cuts. These observed empty Main cases are not that complete closure.'
        ],
        inherited_dedicated_byte_evidence=dict(archive=str(historical.relative_to(R)),SHA256=P.sha(historical.read_bytes()),
            member=member,member_SHA256=P.sha(source),current_RdsMainGate_bytes=raw[gatefile:gatefile+49].hex()),
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes()) for p in [Path(__file__),rom,
            O/'combined-current-landing.json',O/'clock-bridge-profile-v46.json',
            L.B/'native-event-v9-owner.s',L.B/'native-proxy-routes.s',
            R/'docs/qa/checkpoints/2026-10-30/family-main-commit-private-allocation/root-review.json']})
    dst=O/'auth-lifetime-v48.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,Main_cases=len(cases),literal_readers=27,literal_writers=9,
        actual_busy_NMIs=len(nmis),direct_header_poison_cases=poisons,cache_implemented=False,receipt=str(dst.relative_to(R)))))


if __name__=='__main__':main()
