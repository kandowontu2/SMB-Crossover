"""Actual7c0f cold/new-span faults/headers/retire; no historical image execution."""
from hashlib import sha256
import json

import compose_dkjr_forced_entry_current_1116 as C
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_carry_camera_lifecycle_1116 as Existing
import check_dkjr_footer_lifecycle_1116 as Header

N,W,L=Existing.Retire.N,Existing.Retire.W,Existing.Retire.L
H=lambda value:sha256(value).hexdigest()


def cold(seed,raw):
    packet=C.Camera.payload(raw);cookie=raw[534485:534501];rows=[]
    for fault in(None,(3,0x865),(3,0x87f),(3,0xb14),(3,0xdcb),(3,0x1fc1),(2,0x165e)):
        m=Existing.Retire.manager(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        N.put(m,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,
            DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        Base=type(m)
        dormant_before=bytes(m.ram[2][0x900:0xd00])
        class Fault(Base):
            def __getitem__(self,at):
                value=Base.__getitem__(self,at)
                if isinstance(at,int)and at>=0x8000:
                    bank=self.rawtags[(at-0x8000)//8192]
                    if bank==2 and 0x900<=at&8191<0xd00:self.dormant_reads+=1
                    if not bank&128 and(bank&3,at&8191)==self.read_fault:
                        self.fault_reads+=1;return value^1
                return value
        m.__class__=Fault;m.read_fault=fault;m.fault_reads=0;m.dormant_reads=0
        reads=m.ppu_reads;result=N.invoke(m,'CoCold',p=0x21)
        copied=m.ppu_reads-reads
        assert bool(result['P']&1)==(fault is None)
        if fault is not None:
            assert m.fault_reads and all(m.ram[b][0x1fe0]!=167 for b in(2,3))
            executed=[]
            def watch(memory,c):
                if c.pc>=0x8000 and memory.rawtags[(c.pc-0x8000)//8192]in(2,3):executed.append(c.pc)
            L.call(m,'HuMovement',p=0x21,observe=watch)
            assert not executed
            m.read_fault=None;assert N.invoke(m,'CoCold',p=0x21)['P']&1
        assert bytes(m.ram[3][:0x1fe0])==packet[:0x1fe0]
        # Current public cold admits8 R3 pages +2 R2D000..D7FF pages.
        # Payload page8 is retained dormant metadata, not a C900 source lease.
        assert m.dormant_reads==0 and bytes(m.ram[2][0x900:0xd00])==dormant_before
        assert bytes(m.ram[2][0x1000:0x1800])==packet[9216:]
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        warm=m.ppu_reads;assert N.invoke(m,'CoCold',p=0x21)['P']&1
        assert m.ppu_reads==warm
        rows.append(dict(fault=fault,initial_carry=bool(result['P']&1),fault_reads=m.fault_reads,
            first_PPU_reads=copied,all10_admitted_pages_and_cookies_exact_before_constructor=True,
            dormant_page8_C900_reads=m.dormant_reads,dormant_C900_untouched=True,warm_no_copy=True))
    return rows


if __name__=='__main__':
    raw,composition=C.current_proposal(C.BT.ROM.read_bytes());opening,seed=Route.cold(raw)
    reads=cold(seed,raw)
    # These established parameterized APIs execute their candidate argument.
    # Their payload reader is generic; no old owning image/API normalization occurs.
    assert Existing.Route.C.payload(raw)==C.Camera.payload(raw)
    retired=Existing.retire_cases(seed,raw)
    headers=Header.header_contact(seed)
    report=dict(passed=True,candidate_SHA256=H(raw),cold_new_span_faults=reads,retirement=retired,
        all32_header_bytes_native_contact_gate=headers,actual_current_source_execution=True,
        old_tests_reexecuted_with_owning_candidate_argument=True,outputs=0,
        scope='Actual shared cold/foreign-retire/Fresh and every native-contact header byte. Foreign full gameplay/entry-ABI/IRQ are separate gates.')
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_LIFECYCLE '+text,flush=True)
    print('DKJR_ENTRY_LIFECYCLE_SHA256 '+H(text.encode()),flush=True)
