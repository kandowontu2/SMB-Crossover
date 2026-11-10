"""Stdout-only actual-CPU qualification of compact six-owner cold descriptors.

No ROM/artifact is emitted and no seventh identity is registered.  Current
source bytes are reproduced before in-memory worker/linkage proposals run.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as B
import check_remaining_roster_starts_1110 as Current
import check_getsu_fuma_owner_1110 as O
from check_mini_funded_actor_1108_v3 import slim_fork

ROM=R/'build/complete-roster-native-1110/candidate.nes'
PIN='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
N=O.N
DESCRIPTORS={37:(123,0xafd5,20),38:(123,0xbf93,8),39:(123,0xafe9,22),
             40:(65,0xa7dc,8),41:(123,0xb9f9,6),42:(123,0xafcd,8)}


def digest(data):return sha256(data).hexdigest()
def off(bank,pc):return 16+bank*8192+(pc&8191)


def proposal(raw,program):
    assert digest(raw)==PIN
    candidate=bytearray(raw);patches=[]
    def put(bank,pc,old,new,role):
        at=off(bank,pc);assert raw[at:at+len(old)]==old and len(new)==len(old),(role,bank,hex(pc))
        candidate[at:at+len(new)]=new
        patches.append(dict(bank=bank,pc=pc,bytes=len(new),old_hex=old.hex(),new_hex=new.hex(),role=role))
    for name,(pc,size)in B.LAYOUT.items():
        old=program['old']['images'][name].ljust(size,b'\xff')
        new=program['new']['images'][name].ljust(size,b'\xff')
        put(123,pc,old,new,'Source-exact compact common worker '+name)
    old=program['old_typed']['images']['TYPED'];new=program['new_typed']['images']['TYPED']
    put(91,0xb1ba,old,new.ljust(len(old),b'\xea'),'Bounded raw37..43 typed filter; no seventh registry')
    assert raw[off(91,0xb1fc):off(91,0xb20b)]==bytes.fromhex('a9208d6c01a9b78d6d01a9cf4c5a01')
    assert candidate[off(91,0xb1fc):off(91,0xb20b)]==raw[off(91,0xb1fc):off(91,0xb20b)]
    for owner in (38,40):
        bank,pc,size=DESCRIPTORS[owner];old=raw[off(bank,pc):off(bank,pc)+size]
        assert old[3]==0xd0 and size==8
        put(bank,pc,old,(old[:3]+old[4:]).ljust(size,b'\xff'),f'Owner{owner} compact descriptor; original extent retained')
    put(65,0xabc7,bytes.fromhex('a007b9dca799e0df8810f760ea'),
        bytes.fromhex('a006b9dca799e0df8810f760ea'),'DK copies seven descriptor bytes, not padding')
    old=bytes.fromhex('d593e9e0f9cdafbfafdfb9af')
    low=bytes((program['new']['symbols']['BbColdExDescriptor']&255,0x93,
               program['new']['symbols']['BbColdBBDescriptor']&255,0xe0,0xf9,
               program['new']['symbols']['GfColdDescriptor']&255))
    put(65,0xab91,old,low+old[6:],'Existing six-owner descriptor pointer linkage fixture')
    old_rows={}
    for owner,(bank,pc,size)in DESCRIPTORS.items():
        descriptor=raw[off(bank,pc):off(bank,pc)+size]
        assert descriptor[0]*2+4==size and descriptor[3]==0xd0,(owner,descriptor.hex())
        old_rows[owner]=dict(rows=descriptor[0],code_rows=descriptor[1],zero_pages=descriptor[2],
                             pages=[int.from_bytes(descriptor[i:i+2],'little')for i in range(4,size,2)])
    return bytes(candidate),patches,old_rows


def invoke(m,target=O.COLD,*,program=None,reads=None,bank=O.CO):
    m[0x16a],m[0x16c],m[0x16d]=83,target&255,target>>8
    c=O.NesMPU(memory=m,pc=0x15a)
    c.a,c.x,c.y,c.p,c.sp=bank,71,109,0x21,224;c.stPushWord(0x5aff)
    low=224;sites={i['pc']for i in program['instructions']if i['mode']=='iny'and i['operand']==6}if program else set()
    for _ in range(4_000_000):
        if c.pc==0x5b00:break
        low=min(low,c.sp)
        assert m[c.pc],('BRK',hex(c.pc),m.rawtags,m[0x6002])
        if reads is not None and c.pc in sites and m.rawtags[1]==251:reads[c.y]+=1
        c.step()
    else:raise AssertionError(('Cold call bound',hex(c.pc),m.rawtags))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p&0xef,CPU=c.processorCycles,minimum_SP=low)


def cold(m,owner,program,*,expect_success=True):
    O.scene(m,owner);O.clear_logs(m);before=m.ppu_reads;reads=Counter()
    out=invoke(m,program=program,reads=reads)
    assert(out['A'],out['X'],out['Y'],out['P'])==(83,71,109,0x21 if expect_success else 0x20),(owner,out)
    assert m.rawtags[2]==m[O.CURRENT]==2 and m.ppuctrl==160
    out['PPU_reads']=m.ppu_reads-before;out['descriptor_offsets']=sorted(reads)
    return out


def parity(old,new,a,b,*,fault=False,dk_failed_descriptor=False):
    left,right=old.ram,new.ram
    if dk_failed_descriptor:
        assert O.headers(old)==(bytes.fromhex('000009d0c003c103')+b'\0'*8,b'\0'*16),[x.hex()for x in O.headers(old)]
        assert O.headers(new)==(bytes.fromhex('000009c003c10300')+b'\0'*8,b'\0'*16),[x.hex()for x in O.headers(new)]
        # Existing DK scratch lease transiently aliases the invalid header.
        # Its five dead format bytes differ, while both commit markers stay0.
        left=[bytearray(row)for row in old.ram];right=[bytearray(row)for row in new.ram]
        left[2][0x1fe3:0x1fe8]=right[2][0x1fe3:0x1fe8]=b'\0'*5
    assert left==right,('Full eight-bank RAM result differs',
        [(bank,hex(at),x,y)for bank,(left,right)in enumerate(zip(old.ram,new.ram))
         for at,(x,y)in enumerate(zip(left,right))if x!=y][:24])
    assert old.rawtags==new.rawtags and old.chr_latches==new.chr_latches,'Map/latch restore differs'
    assert old.ppu_log==new.ppu_log and a['PPU_reads']==b['PPU_reads'],'PPU traffic differs'
    assert bytes(old[0:256])==bytes(new[0:256]),'Host ZP restore differs'
    assert [old[i]for i in O.SMC]==[new[i]for i in O.SMC],'Host SMC restore differs'
    assert bytes(old[0x0139:0x0148])==bytes(new[0x0139:0x0148]),'NMI/CHR mailbox restore differs'
    assert not old.blocked and not new.blocked if not fault else True
    assert {k:a[k]for k in('A','X','Y','P','minimum_SP')}=={k:b[k]for k in('A','X','Y','P','minimum_SP')}
    if not dk_failed_descriptor:assert O.headers(old)==O.headers(new)


def actual_six(base,trial,program,rows):
    seeds={};receipts={};counts=Counter()
    for owner in range(37,43):
        print('Actual cold descriptor comparison owner',owner,flush=True)
        old,new=O.blank(base),O.blank(trial)
        before=cold(old,owner,program['old']);after=cold(new,owner,program['new'])
        parity(old,new,before,after)
        assert 3 not in before['descriptor_offsets'],'Retired metadataHi was read'
        expected_old={0,1,2}|set(range(4,4+rows[owner]['rows']*2))
        expected_new={0,1,2}|set(range(3,3+rows[owner]['rows']*2))
        assert set(before['descriptor_offsets'])==expected_old,(owner,before)
        assert set(after['descriptor_offsets'])==expected_new,(owner,after)
        O.clear_logs(old);O.clear_logs(new);seeds[owner]=(old,new)
        receipts[owner]=dict(before=before,after=after)
        warm_old,warm_new=slim_fork(old),slim_fork(new)
        a=cold(warm_old,owner,program['old']);b=cold(warm_new,owner,program['new'])
        parity(warm_old,warm_new,a,b);assert a['PPU_reads']==b['PPU_reads']==0
        assert warm_old.ram==old.ram and warm_new.ram==new.ram
        counts['cold_pairs']+=1;counts['warm_pairs']+=1
        # Authentication must reject all one-byte cookie poisons unchanged.
        for bank in (2,3):
            for index in range(16):
                a,b=slim_fork(old),slim_fork(new)
                a.ram[bank][0x1fe0+index]^=1;b.ram[bank][0x1fe0+index]^=1
                x,y=invoke(a,O.AUTH),invoke(b,O.AUTH)
                assert not x['P']&1 and not y['P']&1 and not a.ram_writes and not b.ram_writes
                counts['poisoned_header_pairs']+=1
        for fault in('write-protection',(2,0),(3,0)if rows[owner]['code_rows']else(2,0x1000)):
            a,b=O.blank(base),O.blank(trial)
            if fault=='write-protection':a.protection=b.protection=[0,0]
            else:a.corrupt_at=b.corrupt_at=fault
            x=cold(a,owner,program['old'],expect_success=False)
            y=cold(b,owner,program['new'],expect_success=False)
            dk_staged=owner==40 and O.headers(a)!=(b'\0'*16,b'\0'*16)
            parity(a,b,x,y,fault=True,dk_failed_descriptor=dk_staged)
            if owner==40:
                assert not invoke(a,O.AUTH)['P']&1 and not invoke(b,O.AUTH)['P']&1
                counts['invalid_DK_staged_header_pairs']+=1
            else:assert O.headers(a)==O.headers(b)==(b'\0'*16,b'\0'*16)
            counts['readback_failure_pairs']+=1
        del warm_old,warm_new
    for source in range(37,43):
        dest=37+(source-36)%6
        print('Actual foreign retirement comparison',source,'->',dest,flush=True)
        old,new=(slim_fork(m)for m in seeds[source])
        a=cold(old,dest,program['old']);b=cold(new,dest,program['new'])
        parity(old,new,a,b);assert O.headers(new)==O.headers(seeds[dest][1])
        counts['foreign_retirement_pairs']+=1
    for owner in range(37,43):
        for name,fields in(('foreign',dict(SelectedCharacter=43)),('title',dict(OperMode=0)),
                            ('uncommitted',dict(FamilyMainCommit=0)),('visible',dict(DisableScreenFlag=0)),
                            ('mask',dict(Mirror_PPUMASK=24)),('NMIzero',dict(NmiDisable=0))):
            old,new=O.blank(base),O.blank(trial)
            for m in(old,new):O.scene(m,owner);N.put(m,**fields);O.clear_logs(m)
            before=[bytes(m.ram[k])for m in(old,new)for k in range(len(m.ram))]
            a,b=invoke(old),invoke(new)
            assert not a['P']&1 and not b['P']&1
            assert before==[bytes(m.ram[k])for m in(old,new)for k in range(len(m.ram))]
            assert not old.ram_writes and not new.ram_writes
            counts['cold_guard_pairs']+=1
    for owner,(old,new)in seeds.items():
        old,new=slim_fork(old),slim_fork(new)
        for m in(old,new):N.put(m,SelectedCharacter=0)
        a,b=invoke(old,O.RETIRE),invoke(new,O.RETIRE)
        assert old.ram==new.ram and old.ram[2][0x1fe0]==old.ram[3][0x1fe0]==0
        assert not invoke(old,O.AUTH)['P']&1 and not invoke(new,O.AUTH)['P']&1
        counts['foreign_selector_retire_pairs']+=1
    return dict(counts=dict(counts),owners=receipts)


def proposed_single_row(trial,program):
    """Test worker contract only, with no raw43 or authenticated outer frame."""
    m=O.blank(trial);O.scene(m,37)
    m[6],m[7]=0xfa,0xaf
    before=[bytes(row)for row in m.ram];O.clear_logs(m);reads=Counter();ppureads=m.ppu_reads
    out=invoke(m,0xaf40,program=program['new'],reads=reads,bank=251)
    assert out['P']&1
    assert bytes(m.ram[2][:0x900])==b'\0'*0x900
    assert bytes(m.ram[2][0x900:0x1000])==before[2][0x900:0x1000]
    assert bytes(m.ram[2][0x1000:0x1400])==trial['raw'][1048592+328*1024:1048592+329*1024]
    assert bytes(m.ram[2][0x1400:])==before[2][0x1400:]
    assert bytes(m.ram[3])==before[3] and O.headers(m)==(b'\0'*16,b'\0'*16)
    assert m.ppu_reads-ppureads==2050 and set(reads)=={0,1,2,3,4}
    return dict(worker_only=True,rows=1,code_rows=0,zero_pages=9,metadata_page=328,
                descriptor=program['new']['symbols']['ProposedSonicColdDescriptor'],
                destination=[0xd000,0xd400],PPU_reads=2050,CPU=out['CPU'],headers_uncommitted=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--static-only',action='store_true')
    args=parser.parse_args();output=args.output.resolve()
    assert output.is_relative_to(R/'build')and not output.exists(),'No output files or directory are permitted'
    raw=ROM.read_bytes();program=B.build();image,patches,rows=proposal(raw,program)
    old=program['old'];new=program['new']
    fixed=[i for i in old['instructions']if i['mode']=='iny'and i['operand']==6]
    assert len(fixed)==6 # zero count, code count twice, total rows and two mapper bytes.
    assert not any(i['op']=='LDY'and i['mode']=='imm'and i['operand']==3 for i in old['instructions'])
    assert new['symbols']['BbColdMainEnd']-old['symbols']['BbColdMainEnd']==-2
    report=dict(passed=True,source_only=True,current_SHA256=PIN,proposal_memory_SHA256=digest(image),
                fixed_meta_D0=True,metadataHi_byte3_unused=True,current_descriptor_rows=rows,
                static_funding=dict(core_saved=2,resident_descriptors_saved=3,new_descriptor_bytes=5,
                                    main_used=191,main_reserved=192,map_used=40,map_reserved=42,
                                    new_descriptor_start=0xaffa,new_descriptor_hex='0100094801',
                                    typed_old=66,typed_new=66,live_Getsu_name_tail_retained=True),
                patches=patches,no_raw43_registry_cookie_RAM_or_native_claim=True,outputs_written=0)
    if not args.static_only:
        base=Current.W.bundle(raw);trial=dict(base,raw=image)
        report['actual_CPU']=actual_six(base,trial,program,rows)
        report['proposed_one_row_contract']=proposed_single_row(trial,program)
    assert not output.exists()
    print(json.dumps(report,sort_keys=True),flush=True)


if __name__=='__main__':main()
