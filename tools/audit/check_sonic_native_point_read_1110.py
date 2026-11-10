"""Stdout-only qualification of the proposed isolated native PointRead leaf.

Uses actual current parser/attribute bytes and native buffer addressing.
No image, ROM, RAM lease, native routing or ordinary-frame proof is emitted.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_native_point_read_1110 as B
import check_remaining_roster_starts_1110 as C
import check_getsu_fuma_owner_1110 as O
from check_tmnt_render_oa import address,location

ROM=R/'build/complete-roster-native-1110/candidate.nes'
PIN='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
ATTR_PIN='02ca3678ee8114a3eb336262b9472ee9929237a31f39d5b6886886dc252b8470'
N=O.N
STOP=0x5b00


def digest(data):return sha256(data).hexdigest()
def raw_at(raw,bank,pc,n):
    start=16+bank*8192+(pc&8191);return raw[start:start+n]


class PointBus(O.ControllerBus):
    point_active=False
    point_program=None
    point_reads=None
    def __getitem__(self,at):
        if self.point_active and isinstance(at,int):
            if 0x300<=at<0x4a0:self.point_reads['buffers'].append(at)
            if 0xef36<=at<0xf036:self.point_reads['attributes'].append(at)
        return super().__getitem__(at)
    def __setitem__(self,at,value):
        if self.point_active and isinstance(at,int):
            lo,hi=self.point_program['scratch_half_open']
            assert lo+4<=at<hi or at in(0x1df,0x1e0),('Unowned PointRead write',hex(at),value)
        return super().__setitem__(at,value)


def install(m,program):
    m.__class__=PointBus;m.point_program=program;m.point_active=False
    lo,hi=program['code_half_open'];m.ram[3][lo-0xa000:hi-0xa000]=program['image']
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2)
    m.ram[2][0x1fd0:0x1ff0]=bytes((i*19+37)&255 for i in range(32))
    m.ram[3][0x1fe0:0x1ff0]=bytes((i*23+71)&255 for i in range(16))
    return m


def word(m,at):return m[at]|m[at+1]<<8
def putword(m,at,value):m[at]=value&255;m[at+1]=value>>8
def native_cursor(m):return m[B.HOST['CurrentPageLoc']]*16+m[B.HOST['CurrentColumnPos']]
def screen_column(m):return m[B.HOST['ScreenLeftPage']]*16+(m[B.HOST['ScreenLeftX']]>>4)


def expected(m,x,y):
    # Geometric interval definition, independently checked against the real
    # native writer/phase sequence below. This never assumes32 valid slots.
    if not 32<=y<240:return 1,None
    if m[B.HOST['ColumnSets']]!=255:return 2,None
    phase=m[B.HOST['AreaParserTaskNum']]
    if phase>=8:return 3,None
    page,col=m[B.HOST['CurrentPageLoc']],m[B.HOST['CurrentColumnPos']]
    if col>=16 or m[B.HOST['BlockBufferColumnPos']]!=(page&1)*16+col:return 4,None
    end=page*16+col+(phase in(1,2,3,5,6,7))
    start=screen_column(m)
    if not 1<=end-start<=32:return 5,None
    if not start<=x//16<end:return 6,None
    index=((y//16)-2)*16+(x//16&15)
    pointer=(0x300 if x//256%2==0 else 0x3d0)+index
    tile=m[pointer];attribute=m[0xef36+tile]
    return 0,dict(tile=tile,attribute=attribute,index=index,pointer=pointer,buffer=x//256&1,
                  originx=x//16*16,originy=y//16*16,start=start,end=end)


def call(m,program,x,y,*,p=0x21):
    fields=program['fields'];putword(m,fields['WorldXLo'],x);putword(m,fields['ScreenYLo'],y)
    wanted,oracle=expected(m,x,y)
    O.clear_logs(m);m.point_reads={'buffers':[],'attributes':[]}
    maps=(tuple(m.rawtags),tuple(m.chr_latches),m.upper,m.lastset,m.ppu_reads)
    headers=O.headers(m);mailbox=bytes(m.ram[2][0x1fd0:0x1fd3])
    c=O.NesMPU(memory=m,pc=program['entry']);c.a,c.x,c.y,c.p,c.sp=83,71,109,p,224
    m.point_active=True
    try:
        c.stPushWord(STOP-1)
        for _ in range(1024):
            if c.pc==STOP:break
            assert m[c.pc],('PointRead BRK',hex(c.pc))
            c.step()
        else:raise AssertionError('PointRead execution bound')
    finally:m.point_active=False
    assert c.sp==224 and m[fields['Status']]==wanted,(x,y,wanted,m[fields['Status']],hex(c.pc))
    assert word(m,fields['WorldXLo'])==x and word(m,fields['ScreenYLo'])==y
    assert maps==(tuple(m.rawtags),tuple(m.chr_latches),m.upper,m.lastset,m.ppu_reads)
    assert headers==O.headers(m)and mailbox==bytes(m.ram[2][0x1fd0:0x1fd3])
    assert not m.blocked and all(bank==2 and 0x104<=at<0x116 for bank,at,_ in m.ram_writes)
    if wanted:
        assert(c.a,c.x,c.y,c.p&1)==(0,0,0,0),(x,y,wanted)
        assert m.point_reads==dict(buffers=[],attributes=[]),'Invalid point read stale native storage'
        for name in('Tile','Attributes','CellXLo','CellXHi','CellYLo','CellYHi','BufferIndex','BufferPage'):
            assert m[fields[name]]==0,(name,x,y,wanted)
    else:
        assert(c.a,c.x,c.y,c.p&1)==(oracle['tile'],oracle['attribute'],oracle['index'],1),(x,y,oracle,c.a,c.x,c.y)
        assert m[fields['Tile']]==oracle['tile']and m[fields['Attributes']]==oracle['attribute']
        assert word(m,fields['CellXLo'])==oracle['originx']and word(m,fields['CellYLo'])==oracle['originy']
        assert m[fields['BufferIndex']]==oracle['index']and m[fields['BufferPage']]==oracle['buffer']
        assert word(m,fields['StartColumnLo'])==oracle['start']and word(m,fields['EndColumnLo'])==oracle['end']
        assert m.point_reads==dict(buffers=[oracle['pointer']],attributes=[0xef36+oracle['tile']])
    return wanted,c.processorCycles


def domain(m,*,cursor,phase=0,left=None,pixel=0,ready=255):
    assert 0<=cursor<4096 and 0<=phase<256
    end=cursor+int(phase in(1,2,3,5,6,7))
    if left is None:left=end-24
    assert 0<=left<4096
    page,col=divmod(cursor,16)
    for name,value in(dict(CurrentPageLoc=page,CurrentColumnPos=col,BlockBufferColumnPos=cursor&31,
                            AreaParserTaskNum=phase,ColumnSets=ready,
                            ScreenLeftPage=left>>4,ScreenLeftX=(left&15)*16+pixel)).items():m[B.HOST[name]]=value


def source_bindings(raw,bundle):
    def exact(bank,pc,hexbytes):
        wanted=bytes.fromhex(hexbytes)
        assert raw_at(raw,bank,pc,len(wanted))==wanted,(bank,hex(pc))
    for name,at in B.HOST.items():
        actual_name={'ScreenLeftPage':'ScreenLeft_PageLoc','ScreenLeftX':'ScreenLeft_X_Pos',
                     'BlockBuffer1':'Block_Buffer_1','BlockBuffer2':'Block_Buffer_2'}.get(name,name)
        assert address(bundle,actual_name)==at,(actual_name,hex(at))
    table=raw_at(raw,127,0xef36,256);assert digest(table)==ATTR_PIN
    assert all(raw_at(raw,bank,0xef36,256)==table for bank in(119,120,125,127))
    # The actual task table is traversed backwards from7 to0. Native writes
    # happen before the task counter is decremented to7 or3.
    exact(2,0xa09b,'ac2207d005a0088c2207889820c1a0ce2207d0eb')
    exact(2,0xa0c1,'20098ae6a0d4a0d4a007a2e6a0d4a0d4a007a2')
    exact(2,0xa0e6,'ee2907ad2907290fd0068d2907ee2807eea004ada004291f8da0046000306093')
    exact(126,0x95d8,'00d00303484a4a4a4aa8b9da95850a68290f1879d895850960')
    init=location(bundle,'InitializeArea');init_bytes=raw[init:init+250]
    assert bytes.fromhex('a90b8d2107')in init_bytes,'Actual initial12-column-set count'
    control=location(bundle,'AreaParserTaskControl')
    assert bytes.fromhex('ce2107')in raw[control:control+60]
    return dict(attribute_SHA256=ATTR_PIN,actual_attribute_values=sorted(set(table)),
                parser_phase_add=B.PHASE_ADD,initial_columns=24,
                native_buffer_bases=[0x300,0x3d0],rows=13,columns_per_page=16)


def native_pointer_oracle(m):
    for column in range(32):
        c=O.NesMPU(memory=m,pc=0x95dc);c.a,c.x,c.y,c.p,c.sp=column,71,109,0x21,224
        c.stPushWord(STOP-1)
        for _ in range(80):
            if c.pc==STOP:break
            c.step()
        else:raise AssertionError('Actual native buffer-address leaf bound')
        assert c.sp==224 and word(m,9)==(0x300+column if column<16 else 0x3d0+column-16)
    return 32


def actual_parser(bundle,program):
    receipts=[];cases=0
    for initial_page in(0,1):
        print('Actual native parser initial24 / phase proof page',initial_page,flush=True)
        m=N.fresh(bundle);N.put(m,AreaPointer=0x25,SelectedCharacter=0)
        N.invoke(m,'GetAreaDataAddrs')
        N.put(m,CurrentPageLoc=initial_page,CurrentColumnPos=0,BlockBufferColumnPos=(initial_page&1)*16,
              ScreenLeft_PageLoc=initial_page,ScreenLeft_X_Pos=0,ColumnSets=11,AreaParserTaskNum=0,
              CurrentNTAddr_High=0x24 if initial_page&1 else 0x20,CurrentNTAddr_Low=0x80,
              BackloadingFlag=initial_page,NmiDisable=255)
        written=set()
        for initial_set in range(12):
            O.clear_logs(m);N.put(m,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=0)
            before=native_cursor(m);N.invoke(m,'AreaParserTaskControl')
            positions={at for at,_ in m.writes if 0x300<=at<0x4a0}
            expected_positions={base+row*16+(col&15)for col in(before,before+1)
                                for row in range(13)for base in(0x300 if col//16%2==0 else 0x3d0,)}
            assert positions==expected_positions,(initial_set,positions^expected_positions)
            written.update((before,before+1))
            assert native_cursor(m)==before+2 and m[B.HOST['ColumnSets']]==(10-initial_set)&255
            assert m[B.HOST['AreaParserTaskNum']]==0
        assert written==set(range(initial_page*16,initial_page*16+24))
        m=install(m,program)
        # Initial first24 are complete; the next same-parity page slot is not.
        for col in range(initial_page*16,initial_page*16+32):
            wanted,_=call(m,program,col*16,32);assert(wanted==0)==(col in written);cases+=1
        phases=Counter()
        for column_set in range(8):
            left=initial_page*16+(column_set+1)*2
            m[B.HOST['ScreenLeftPage']],m[B.HOST['ScreenLeftX']]=left>>4,(left&15)*16
            for step in range(8):
                before=native_cursor(m);old_phase=m[B.HOST['AreaParserTaskNum']]
                O.clear_logs(m);N.put(m,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=0)
                N.invoke(m,'AreaParserTaskHandler')
                positions={at for at,_ in m.writes if 0x300<=at<0x4a0}
                should_write=old_phase in(0,4)
                expected_positions={(0x300 if before//16%2==0 else 0x3d0)+row*16+(before&15)for row in range(13)}if should_write else set()
                assert positions==expected_positions,(initial_page,column_set,old_phase,positions^expected_positions)
                if should_write:written.add(before)
                phase=m[B.HOST['AreaParserTaskNum']];phases[phase]+=1
                end=native_cursor(m)+B.PHASE_ADD[phase]
                assert end==max(written)+1,(old_phase,phase,end,max(written))
                assert m[B.HOST['BlockBufferColumnPos']]==native_cursor(m)&31
                for col in range(left,end):
                    for y in(32,239):assert call(m,program,col*16+15,y)[0]==0;cases+=1
                for col in(left-1,end,left+32,left+64):
                    assert call(m,program,col*16,32)[0]==6;cases+=1
        assert phases==Counter({i:8 for i in range(8)})
        receipts.append(dict(start_page=initial_page,initial24_exact=True,actual_phase_counts=dict(phases),
                             final_parser_cursor=native_cursor(m),actual_written_columns=len(written)))
    return dict(cases=cases,episodes=receipts)


def finite(bundle,program):
    m=install(N.fresh(bundle),program);counts=Counter();cycles=[]
    pointers=native_pointer_oracle(m)
    for at in range(0x300,0x4a0):m[at]=(at*37+19)&255
    for page in(0,1):
        print('All256 metatiles / actual buffer page',page,flush=True)
        domain(m,cursor=page*16+24,left=page*16)
        for row in range(13):
            for column in range(16):
                at=(0x300 if page==0 else 0x3d0)+row*16+column
                for tile in range(256):
                    m[at]=tile
                    status,cost=call(m,program,page*256+column*16+(tile&15),32+row*16+(tile>>4),p=(0x21,0x20,0x6c,0xad)[tile&3])
                    assert status==0;counts['all_metatiles_both_buffers_every_cell']+=1;cycles.append(cost)
    domain(m,cursor=24,left=0)
    print('All65536 vertical coordinates',flush=True)
    for y in range(65536):
        assert(call(m,program,17,y)[0]==0)==(32<=y<240)
        counts['all_16bit_vertical_coordinates']+=1
    print('Parser frontier / seam / distant-alias sweep',flush=True)
    for page in(0,1,2,15,127,254,255):
        for column in range(16):
            cursor=page*16+column
            if cursor<24:continue
            for phase in range(8):
                end=cursor+B.PHASE_ADD[phase];left=end-24
                domain(m,cursor=cursor,phase=phase,left=left,pixel=phase*2)
                tests={left*16+d for d in(-1024,-513,-512,-511,-17,-16,-1,0,1,15,16,31,255,383,384,385,511,512,513,1024)}
                tests|={end*16+d for d in(-17,-16,-1,0,1,15,16,511,512,1024)}
                for x in sorted(t for t in tests if 0<=t<65536):
                    for y in(31,32,47,48,223,224,239,240):
                        call(m,program,x,y);counts['phase_interval_pixel_seams']+=1
    # End4096 is an actual mathematical frontier, not a wrapped page0 alias.
    domain(m,cursor=4095,phase=1,left=4072)
    for x in(0,15,511,4072*16-1,4072*16,65519,65520,65535):
        assert(call(m,program,x,239)[0]==0)==(x>=4072*16);counts['world16_end_boundary']+=1
    for phase in range(8,256):
        domain(m,cursor=48,phase=phase,left=24)
        assert call(m,program,400,64)[0]==3;counts['unstable_phase_rejects']+=1
    for ready in range(255):
        domain(m,cursor=24,left=0,ready=ready)
        assert call(m,program,32,64)[0]==2;counts['initial_incomplete_rejects']+=1
    for column in range(16,256):
        domain(m,cursor=48,left=24);m[B.HOST['CurrentColumnPos']]=column
        assert call(m,program,400,64)[0]==4;counts['noncanonical_column_rejects']+=1
    for ring in range(256):
        if ring==16:continue
        domain(m,cursor=48,left=24);m[B.HOST['BlockBufferColumnPos']]=ring
        assert call(m,program,400,64)[0]==4;counts['inconsistent_ring_rejects']+=1
    for length in(0,33,34,255,256,257,-1,-16,-256):
        domain(m,cursor=512,left=512-length)
        assert call(m,program,(512-length)*16,64)[0]==5;counts['invalid_capacity_rejects']+=1
    for length in range(1,33):
        domain(m,cursor=512,left=512-length)
        assert call(m,program,(512-length)*16,64)[0]==0
        assert call(m,program,512*16,64)[0]==6;counts['exact_capacity_edges']+=2
    assert bytes(m.ram[3][B.CODE-0xa000:B.CODE-0xa000+len(program['image'])])==program['image']
    return dict(counts=dict(counts),native_GetBlockBufferAddr_cases=pointers,
                valid_cycles=[min(cycles),max(cycles)],minimum_SP=222,
                all_writes_confined_to_declared_private_outputs_and_return_stack=True,
                no_ZP_mapper_SMC_header_mailbox_native_buffer_writes=True,
                invalid_points_read_no_buffer_or_attribute_byte=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--only',choices=('all','parser','finite'),default='all')
    args=parser.parse_args();assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    raw=ROM.read_bytes();assert digest(raw)==PIN
    bundle=C.W.bundle(raw);program=B.build();bindings=source_bindings(raw,bundle)
    report=dict(passed=True,current_SHA256=PIN,files_written=0,ROM_written=False,
                leaf_bytes=len(program['image']),leaf_SHA256=digest(program['image']),
                proposed_code_half_open=program['code_half_open'],proposed_scratch_half_open=program['scratch_half_open'],
                scratch_signature=program['fields'],status=program['status'],source_bindings=bindings,
                domain='Stable foreground after initial24 columns: [floor(actual screen-left/16), committed parser end). Behind-camera retained cells excluded; not a full32-slot residency claim.',
                no_new_RAM_lease_native_admission_shape_or_ordinary_frame_claim=True)
    if args.only in('all','parser'):report['actual_parser']=actual_parser(bundle,program)
    if args.only in('all','finite'):report['finite']=finite(bundle,program)
    assert not args.output.exists()
    print(json.dumps(report,sort_keys=True),flush=True)


if __name__=='__main__':main()
