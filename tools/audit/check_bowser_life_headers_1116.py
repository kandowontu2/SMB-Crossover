"""Actual6a3 full16-cookie faults, warm transport and foreign rejection."""
from pathlib import Path
from unittest.mock import patch
import json
import bowser_life_source_components_1116 as T

C,N,W=T.C,T.N,T.W
def run(parent):
    raw,composition=C.proposal(parent);m,opening=T.Current.cold(raw,'smb3',report=True);cases=0
    expected_cookie=bytes.fromhex(C.lease()['cookie_views']['new_hex']);assert bytes(m.ram[3][0x1fe0:0x1ff0])==expected_cookie
    for byte in(-1,*range(16)):
        for f in range(64):
            q=T.fork(m)
            if byte>=0:q.ram[3][0x1fe0+byte]^=1
            prior=[bytes(row)for row in q.ram];c,r=T.call(q,'BwCheck',p=T.flags(f))
            assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert c.p&0xcf==(T.flags(f)&0x4c)|(int(byte<0))
            assert not q.ram_writes and[bytes(row)for row in q.ram]==prior
            cases+=1
    rom_faults=[]
    for byte in range(16):
        q=T.fork(m);bad=bytearray(raw);bad[693672+byte]^=1;q.bundle=dict(q.bundle,raw=bytes(bad))
        for slot,tag in enumerate(q.rawtags):
            if tag&128:q.raw_page(slot,tag)
        T.clear(q);prior=[bytes(row)for row in q.ram];c,_=T.call(q,'BwCheck')
        assert not c.p&1 and not q.ram_writes and[bytes(row)for row in q.ram]==prior
        rom_faults.append(byte)
    live=T.fork(m);nr=live.ppu_reads;private=[bytes(row)for row in live.ram];c,r=T.call(live,'BwLoad')
    assert not c.p&1 and live.ppu_reads==nr and not live.ram_writes and[bytes(row)for row in live.ram]==private,'Visible gameplay is not a legal loader window'
    warm=T.fork(m);N.put(warm,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1)
    T.clear(warm);nr=warm.ppu_reads;private=[bytes(row)for row in warm.ram];c,r=T.call(warm,'BwLoad')
    assert c.p&1 and warm.ppu_reads==nr and not warm.ram_writes and[bytes(row)for row in warm.ram]==private
    foreigners=[]
    for owner in(0,22,33,39):
        q=T.fork(m);N.put(q,SelectedCharacter=owner);prior=[bytes(row)for row in q.ram]
        for name in('BwCheck','BwLoad'):
            T.clear(q);nr=q.ppu_reads;c,_=T.call(q,name)
            assert not c.p&1 and not q.ram_writes and q.ppu_reads==nr and[bytes(row)for row in q.ram]==prior
        foreigners.append(owner)
    q=dict(passed=True,composition=composition,opening=opening,full16_RAM_cookie_flags_cases=cases,
        ROM_expected_cookie_fault_bytes=rom_faults,foreign_owners_rejected=foreigners,forced_blank_warm_no_copy_or_write=True,visible_loader_rejected_without_writes=True,
        exact_AXY_SP_carry_and_flag_contract=True,scope='Actual candidate callback/header fault components; faults are diagnostic only, not gameplay seeds',outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Header source component attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
