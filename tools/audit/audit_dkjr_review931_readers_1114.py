"""Authenticate live Bowser/BT cold readers of review-only FF carriers.

Runs current82 menu/native scheduled source CPU only; no historical producer,
ROM composition, carrier reassignment or emulator process is used.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import current_dkjr_review_input_1114 as Input
import check_bowser_natural_powerups_1113 as Bowser

W,N=Bowser.W,Bowser.N


def battletoads_cold(raw,identity):
    """Reach current BT solely through actual native menu/controller calls."""
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in (4,4,1,1,1,1,1,1,1):W.UI.key(m,bits)
    assert N.get(m,'CrossoverMenuIndex')==23 and N.get(m,'SelectedCharacter')==33
    if identity:W.UI.key(m,32)
    assert bool(N.get(m,'FmGroups')&32)==bool(identity)
    menu=W.UI.menu_name(m)[0];start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for epoch in range(700):
        assert N.get(m,'SelectedCharacter')==33 and N.get(m,'NumberofLives')==2
        if tuple(N.get(m,n)for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            ready=m.ram[3][W.address(b,'BtHostReady')&8191]
            assert ready==1
            return m,dict(menu=menu,epoch=epoch,actual_grid=[4,4,1,1,1,1,1,1,1],
                Select_presses=identity,ready=ready)
        m.controller_pad=0;Bowser.Frames.frame(m,cold=True)
    raise AssertionError('Actual current BT menu/constructor bound')


def battletoads_readers(raw,b,identity):
    expected=bytes.fromhex('a9038d3051a5044a4a69678d2b512c0220a90c8d0620a9008d0620ad0720a00060')
    at=W.location(b,'BtMapPage');assert raw[at:at+len(expected)]==expected
    points={((((W.location(b,name)-16)//8192)|128),W.address(b,name)):name
        for name in ('BtMapPage','BtCopy256','BtVerify256')}
    maps=[];reads=Counter();base=N.NesMPU
    class Probe(base):
        def step(self):
            memory=self.memory
            if self.pc>=0x8000:
                key=(memory.rawtags[(self.pc-0x8000)//8192],self.pc)
                name=points.get(key)
                if name=='BtMapPage':
                    destination=memory[4]<<8
                    assert 0xc000<=destination<0xe000 and destination%1024==0
                    maps.append(dict(destination=destination,physical_page=919+(destination-0xc000)//1024))
                elif name in ('BtCopy256','BtVerify256'):
                    reads[memory.chr_latches[11],name]+=1
            return base.step(self)
    with patch.object(N,'NesMPU',Probe):m,opening=battletoads_cold(raw,identity)
    assert maps==[dict(destination=0xc000+1024*i,physical_page=919+i)for i in range(8)for _ in range(2)],maps
    assert all(reads[page,name]==1024 for page in range(919,927)
        for name in ('BtCopy256','BtVerify256')),reads
    return dict(actual_controller_cold=opening,physical_pages_read=list(range(919,927)),
        review925_copy_reads=reads[925,'BtCopy256'],review925_echo_reads=reads[925,'BtVerify256'],
        authenticated_map_PC=W.address(b,'BtMapPage'),authenticated_map_raw_bank=((at-16)//8192)|128,
        authenticated_map_SHA256=sha256(expected).hexdigest(),map_calls=len(maps))


def main():
    raw=Input.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==Input.Reset.CANDIDATE
    b=dict(W.Symbols.bundle(),raw=raw)
    map_pc=W.address(b,'BwMapPage');map_at=W.location(b,'BwMapPage')
    expected=bytes.fromhex('a9038d3051a50438e9c04a4a18699f8d2b512c0220a90c8d0620a9008d0620ad0720a00060')
    assert raw[map_at:map_at+len(expected)]==expected
    points={}
    for name in ('BwMapPage','BwCopy256','BwVerify256'):
        points[(((W.location(b,name)-16)//8192)|128,W.address(b,name))]=name
    assert W.address(b,'R1')==4
    results=[];base=N.NesMPU
    for identity in (0,1):
        maps=[];reads=Counter()
        class Probe(base):
            def step(self):
                memory=self.memory
                if self.pc>=0x8000:
                    key=(memory.rawtags[(self.pc-0x8000)//8192],self.pc)
                    name=points.get(key)
                    if name=='BwMapPage':
                        destination=memory[4]<<8
                        assert 0xc000<=destination<0xe000 and destination%1024==0
                        maps.append(dict(destination=destination,physical_page=927+(destination-0xc000)//1024))
                    elif name in ('BwCopy256','BwVerify256'):
                        page=memory.chr_latches[11]
                        reads[page,name]+=1
                return base.step(self)
        with patch.object(N,'NesMPU',Probe):m,receipt=Bowser.cold(raw,identity)
        expected_maps=[dict(destination=0xc000+1024*i,physical_page=927+i)
            for i in range(8)for _ in range(2)]
        assert maps==expected_maps,maps
        assert all(reads[page,name]==1024 for page in range(927,935)
            for name in ('BwCopy256','BwVerify256')),reads
        results.append(dict(identity=identity,actual_controller_cold=receipt,
            physical_pages_read=sorted({page for page,_ in reads}),
            review931_copy_reads=reads[931,'BwCopy256'],
            review931_echo_reads=reads[931,'BwVerify256'],
            map_calls=len(maps),source_fields_ready=m.ram[3][0x1e26]))
    bt=[battletoads_readers(raw,b,identity)for identity in (0,1)]
    page=raw[1048592+931*1024:1048592+932*1024]
    print('DKJR_REVIEW931_READERS '+json.dumps(dict(passed=True,
        actual_current_SHA256=Input.Reset.CANDIDATE,review_target=931,allocated_to_DK=False,
        current_Bowser_map_PC=map_pc,current_Bowser_map_raw_bank=((map_at-16)//8192)|128,
        authenticated_map_SHA256=sha256(expected).hexdigest(),
        physical931_preimage_SHA256=sha256(page).hexdigest(),results=results,battletoads=bt,
        conclusion='Physical925 and931/932/933 are actively copied and echo-verified by their current owners. Their FF contents do not permit an unchanged-caller domain release.',
        outputs_written=0,ROM_composed=False,ROM_written=False,native_claim=False,
        scope='Current exact-source cold reader proof, not global page ownership closure or a resource grant.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
