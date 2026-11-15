"""Granted BT camera candidate gates: genuine cold/current CPU, zero files."""
from hashlib import sha256
from functools import lru_cache
import argparse,json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_camera_handoff_1114 as C
import replay_battletoads_camera_full11_1114 as F
import check_battletoads_full11_current_1114 as Previous
import check_smb1_alts_full11_1114 as Runner
import check_battletoads_camera_handoff_1114 as Research

W,N=F.W,F.N


def strict(raw):
    parent=C.inverse(raw);assert C.proposal(parent)[0]==raw
    rejects=[]
    for name,image,method in(('oldcf7_inverse',parent,C.inverse),('new_forward',raw,C.proposal),
            ('truncated',raw[:-1],C.inverse),('old1daca_forward',C.Parent.inverse(parent),C.proposal)):
        try:method(image)
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Wrong candidate accepted',name))
    for name,at in(('cookie',765868),('import',1993448),('export',1993646),('tail',1995254),
            ('unowned',90000),('Gimmick',622194),('DK',105706),('common',1034868)):
        changed=bytearray(raw);changed[at]^=1
        try:C.inverse(bytes(changed))
        except AssertionError:rejects.append(name)
        else:raise AssertionError(('Dirty candidate accepted',name))
    original=Path.read_bytes
    def forbid_read(path):
        assert path.resolve()!=F.ROM.resolve(),'Mutable Downloads read beyond initial input boundary'
        return original(path)
    with patch.object(Path,'read_bytes',forbid_read):
        assert C.inverse(raw)==parent and C.proposal(parent)[0]==raw
        for key in F.IDENTITIES:F.controller(raw,key)
    boundary=[]
    for name,image in(('parentcf7',parent),('postdeliveryf11a',raw)):
        reads=[]
        def reader(path):
            if path.resolve()==F.ROM.resolve():reads.append(1);assert len(reads)==1;return image
            return forbid_read(path)
        with patch.object(Path,'read_bytes',reader):assert C.load_current_image()==raw
        assert len(reads)==1;boundary.append(name)
    return dict(C.proposal(parent)[1],rejections=rejects,portable_inverse_roundtrip=True,
        mutable_Downloads_rereads=0,explicit_single_read_loader_cases=boundary)


def cold(raw,key):
    with patch.object(Previous,'Factory',F):return Previous.cold(raw,key)


@lru_cache(maxsize=1)
def bundle(raw):return dict(W.Symbols.bundle(),raw=raw)


def make(raw,**extra):
    b=bundle(raw);m=N.Bus(b)
    N.put(m,CurrentBank=m.rawtags[1],CurrentBankC=m.rawtags[2],SelectedCharacter=33,
        OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=168,NmiDisable=255,
        FamilyMainCommit=1,NumberofLives=2,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,
        HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=1,X5WideChrActive=0,
        X5SpecialChrUpper=0,X5HudChrUpper=0,**extra)
    m.ppuctrl=168;W.clear_logs(m)
    return m


def loader(raw):
    info=strict(raw);expected=bytearray(raw[C.BASE:C.BASE+8192]);expected[0x1fe0:0x1ff0]=raw[765863:765879]
    cold_rows=[];seed=None
    for wide,reload,ctrl in((0,0,168),(0,1,172),(1,0,172),(1,1,168)):
        m=make(raw);N.put(m,X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl);m.ppuctrl=ctrl
        private=tuple(map(bytes,m.ram[:3]));nreads=m.ppu_reads
        out=N.invoke(m,'BtLoad');assert out['P']&1 and(out['A'],out['X'],out['Y'])==(85,7,91)
        assert m.ram[3]==expected and tuple(map(bytes,m.ram[:3]))==private
        assert m.ram_writes[0]==(3,0x1fe0,0)and m.ram_writes[-1]==(3,0x1fe0,167)
        assert m.ppu_reads-nreads==16400
        assert m.ppuctrl==ctrl and N.get(m,'ReloadCHRBank')==reload and m.protection==[2,1]
        nreads=m.ppu_reads;nwrites=len(m.ram_writes);warm=N.invoke(m,'BtLoad')
        assert warm['P']&1 and m.ppu_reads==nreads and len(m.ram_writes)==nwrites
        cold_rows.append(dict(wide=wide,reload=reload,ctrl=ctrl,cold_CPU=out['CPU'],warm_CPU=warm['CPU'],minimum_SP=out['minimum_SP']))
        if seed is None:seed=N.fork(m)
    check_cases=0
    for bad in range(-1,16):
        m=N.fork(seed)
        if bad>=0:m.ram[3][0x1fe0+bad]^=1
        for p in(0x20,0x21,0x2c,0x6d,0xe0,0xed):
            z=N.fork(m);before=bytes(z.ram[3]);out=N.invoke(z,'BtCheck',p=p)
            assert bool(out['P']&1)==(bad<0)and bytes(z.ram[3])==before
            check_cases+=1
    old=N.fork(seed);old.ram[3][:]=C.inverse(raw)[C.BASE:C.BASE+8192]
    old.ram[3][0x1fe0:0x1ff0]=C.inverse(raw)[765863:765879]
    out=N.invoke(old,'BtCheck');assert not out['P']&1
    N.put(old,DisableScreenFlag=0,Mirror_PPUMASK=30);W.clear_logs(old);before=bytes(old.ram[3]);reads=old.ppu_reads
    out=N.invoke(old,'BtLoad');assert not out['P']&1 and bytes(old.ram[3])==before and old.ppu_reads==reads
    N.put(old,DisableScreenFlag=1,Mirror_PPUMASK=0);out=N.invoke(old,'BtLoad');assert out['P']&1 and old.ram[3]==expected
    foreign=0
    for owner in range(256):
        if owner==33:continue
        m=make(raw);N.put(m,SelectedCharacter=owner);before=tuple(map(bytes,m.ram));out=N.invoke(m,'BtLoad')
        assert not out['P']&1 and tuple(map(bytes,m.ram))==before and m.ppu_reads==0;foreign+=1
    faults=[]
    for name,locked,corrupt in(('locked',True,None),('readback',False,(3,17))):
        m=make(raw);m.protection=[0,0]if locked else[2,1];m.corrupt_at=corrupt
        out=N.invoke(m,'BtLoad');assert not out['P']&1 and m.ram[3][0x1fe0]!=167;faults.append(name)
    retires=[]
    for family in(0,9,22,26,28,32,33,39,43):
        m=N.fork(seed);m.ram[3][0x1fe1]=family;before=tuple(map(bytes,m.ram));N.invoke(m,'BtRetire')
        expected3=bytearray(before[3]);expected3[0x1fe0]=0 if family==33 else 167
        assert tuple(map(bytes,m.ram[:3]))==before[:3]and m.ram[3]==expected3;retires.append(family)
    return dict(composition=info,cold_and_warm_cases=cold_rows,all8192_bytes_readback_exact=True,
        invalid_first_valid_last=True,buffered_copy_verify_reads=16400,cookie_byte_flags_checks=check_cases,
        old_cookie_reject_active_and_forcedblank_reload=True,foreign_owner_rejects=foreign,
        fault_rejects=faults,retirement_families=retires,outputs=0,Mesen_run=False)


def stage(raw,key):
    info=strict(raw);copies=[];base=W.ControllerBus
    expected=bytearray(raw[C.BASE:C.BASE+8192]);expected[0x1fe0:0x1ff0]=raw[765863:765879]
    class Bus(base):
        def __setitem__(self,at,value):
            watched=isinstance(at,int)and at>=0x8000 and(self.rawtags[(at-0x8000)//8192]&3)==3 and not self.rawtags[(at-0x8000)//8192]&128 and at&8191==0x1fe0 and value==167
            result=super().__setitem__(at,value)
            if watched and self.ram[3][0x1fe1]==33:
                assert self.ram[3]==expected,'Actual cold loader complete8192 readback/new header'
                copies.append(dict(bytes=8192,header=bytes(self.ram[3][0x1fe0:0x1ff0]).hex()))
            return result
    with patch.object(Previous,'Factory',F),patch.object(Runner,'Factory',F),patch.object(Runner,'cold',cold),patch.object(W,'ControllerBus',Bus):
        q=Runner.run(raw,key,6500)
    assert q['passed']and copies,q
    return dict(composition=info,actual_cold_copies=copies,route=q,outputs=0,Mesen_run=False)


def interrupts(raw):
    info=strict(raw)
    def recipe(image):
        assert image==raw;b=dict(W.Symbols.bundle(),raw=image)
        return b,image[C.BASE:C.BASE+8192],tuple((pc,code)for pc,(_,_,code)in zip((0xaed8,0xaf9e,0xb5e6),C.spans()[:3],strict=True)),info
    def no_placement(m,spans):
        assert all(bytes(m.ram[3][pc&8191:(pc&8191)+len(code)])==code for pc,code in spans),'Actual new cold code already present'
    with patch.object(Previous,'Factory',F),patch.object(Research,'recipe',recipe),patch.object(Research,'install_ram',no_placement):
        q=Research.interrupts(raw)
    q.update(source_RAM_research_only=False,actual_candidate_cold=True,after_cold_code_placement=False)
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--loader',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--interrupts',action='store_true');p.add_argument('--identity',choices=F.IDENTITIES,default='rash');a=p.parse_args()
    raw=C.load_current_image()
    def forbid(*args,**kwargs):raise RuntimeError('BT candidate source attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=interrupts(raw)if a.interrupts else stage(raw,a.identity)if a.stage else loader(raw)if a.loader else strict(raw)
    q['file_and_Mesen_traps']=True;print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
