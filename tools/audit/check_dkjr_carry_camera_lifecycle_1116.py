"""Actual owning CoRetire/CoCold reentry over the frozen carry-camera image."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_retire_lease_1113 as Retire

H=lambda value:sha256(value).hexdigest()


def cold_cases(seed,candidate):
    N,W,L=Retire.N,Retire.W,Retire.L
    body=Route.C.payload(candidate);cookie=candidate[534485:534501];rows=[]
    for fault in(None,(3,0x16a5),(3,0x1770),(3,0x1fde),(2,0x1000),(2,0x17ff)):
        m=Retire.manager(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        N.put(m,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,
            DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        Base=type(m)
        class Fault(Base):
            def __getitem__(self,at):
                value=Base.__getitem__(self,at)
                if isinstance(at,int) and at>=0x8000:
                    bank=self.rawtags[(at-0x8000)//8192]
                    if not bank&128 and (bank&3,at&8191)==self.read_fault:
                        self.fault_reads+=1;return value^1
                return value
        m.__class__=Fault;m.read_fault=fault;m.fault_reads=0
        before=m.ppu_reads;W.clear_logs(m);result=N.invoke(m,'CoCold',p=0x21)
        reads=m.ppu_reads-before
        assert bool(result['P']&1)==(fault is None)
        if fault is not None:
            assert m.fault_reads and all(m.ram[b][0x1fe0]!=167 for b in(2,3))
            seen=[]
            def watch(memory,cpu):
                if cpu.pc>=0x8000 and memory.rawtags[(cpu.pc-0x8000)//8192]in(2,3):seen.append(cpu.pc)
            L.call(m,'HuMovement',p=0x21,observe=watch);assert not seen
            m.read_fault=None;assert N.invoke(m,'CoCold',p=0x21)['P']&1
        assert bytes(m.ram[3][:0x1fe0])==body[:0x1fe0]
        assert bytes(m.ram[2][0x1000:0x1800])==body[9*1024:]
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        warm_before=m.ppu_reads;assert N.invoke(m,'CoCold',p=0x21)['P']&1
        assert m.ppu_reads==warm_before
        rows.append(dict(read_fault=fault,initial_C=bool(result['P']&1),
            initial_PPU_reads=reads,read_faults=m.fault_reads,ready_after_retry=True,warm_no_copy=True))
    return rows


def retire_cases(seed,candidate):
    N,L=Retire.N,Retire.L
    body=Route.C.payload(candidate);cookie=candidate[534485:534501];rows=[]
    for owner in(9,37,38,39,41):
        m=Retire.manager(seed);status=N.get(m,'PlayerStatus')
        N.put(m,SelectedCharacter=owner,OperMode=1,FamilyMainCommit=1,
            DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        N.invoke(m,'CoRetire',p=0x21)
        assert all(m.ram[b][0x1fe0]!=167 for b in(2,3))
        seen=[]
        def watch(memory,cpu):
            if cpu.pc>=0x8000 and memory.rawtags[(cpu.pc-0x8000)//8192]in(2,3):seen.append(cpu.pc)
        L.call(m,'HuMovement',a=0,x=5,y=3,p=0x61,observe=watch);assert not seen
        # Explicit inactive foreign-guest fixture, not foreign constructor/UI.
        m.ram[3][:0x1fe0]=bytes((i*29+owner)&255 for i in range(0x1fe0))
        m.ram[2][0x1000:0x1800]=bytes((i*17+owner)&255 for i in range(0x800))
        N.put(m,SelectedCharacter=40)
        assert N.invoke(m,'CoCold',p=0x21)['P']&1
        assert bytes(m.ram[3][:0x1fe0])==body[:0x1fe0]
        assert bytes(m.ram[2][0x1000:0x1800])==body[9*1024:]
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
        assert m.ram[2][0x8fe]==0
        assert N.invoke(m,'HuFresh',p=0x21)['P']&1
        assert m.ram[2][0x8fe]==1 and m.ram[2][0x6b]==1 and m.ram[2][0x4a]==1
        assert N.get(m,'PlayerStatus')==status
        rows.append(dict(outgoing_owner=owner,both_headers_invalidated=True,
            foreign_callback_rejected=True,owning_code_metadata_recopied=True,fresh_ready1=True))
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,composition=Route.C.proposal(parent)
    assert Route.C.inverse(candidate)==parent
    opening,seed=Route.cold(candidate)
    info=dict(cookie=candidate[534485:534501].hex())
    # These existing tests execute actual shared manager instructions, using
    # the owning image/cookie and explicitly declared foreign-page contents.
    # They do not run the historical producer, composer or source recipe.
    assert Retire.P.T.payload(candidate)==Route.C.payload(candidate)
    print('DKJR_CAMERA_LIFECYCLE_PHASE cold-fault-retry',flush=True)
    cold=cold_cases(seed,candidate)
    print('DKJR_CAMERA_LIFECYCLE_PHASE retirement',flush=True)
    retire=retire_cases(seed,candidate)
    report=dict(passed=True,composition=composition,opening=opening,
        cold_fault_retry=cold,retirement=retire,
        historical_fixture_negative='First attempted historical C900-added-page cold fixture expected22550 PPU reads; actual public10-page loader reads20500. No added C900 lease or page is claimed here.',
        CPU_execution_input=Route.C.CANDIDATE,
        scope='Actual shared retirement/cold/Fresh reentry; declared foreign-page and read-fault fixtures, no complete foreign-game UI or native claim',
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_LIFECYCLE '+encoded,flush=True)
    print('DKJR_CAMERA_LIFECYCLE_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
