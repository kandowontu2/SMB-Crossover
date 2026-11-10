"""Stdout-only original32/native16 geometry qualification; no host admission."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_native_shape_contact_1110 as B
from verify_native_relocation import NesMPU

ROM=R/'build/complete-roster-native-1110/candidate.nes'
PIN='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
POINT_SOURCE_PIN='fc135d40cb35d115d4854db00b29943b57ee9a454b7cff58f65e2a2e6ddf8eff'
STOP=0x5b00
CANARY=bytes((i*73+41)&255 for i in range(65536))
STATE_CANARY=bytes((i*31+93)&255 for i in range(256))


def digest(data):return sha256(data).hexdigest()


class Memory(list):
    def __init__(self,program,attributes):
        super().__init__(CANARY);self.program=program;self.active=False
        self.writes=[];self.buffer_reads=[];self.attribute_reads=[];self.fixture_reads=[]
        self.minimum_SP=255;self.rawtags=(254,3,2,255)
        for pc,data in((0xa000,program['core']['image']),
                      (program['point']['entry'],program['point']['image']),
                      (program['code_half_open'][0],program['image']),
                      (0xef36,attributes)):
            list.__setitem__(self,slice(pc,pc+len(data)),data)
        list.__setitem__(self,slice(0x300,0x4a0),bytes(416))
        self.setup_domain(0)
    def __getitem__(self,at):
        if self.active and isinstance(at,int):
            if 0x300<=at<0x4a0:self.buffer_reads.append(at)
            elif 0xef36<=at<0xf036:self.attribute_reads.append(at)
            elif 0xc800<=at<0xd900:self.fixture_reads.append(at)
        return list.__getitem__(self,at)
    def __setitem__(self,at,value):
        assert isinstance(at,int)
        value&=255
        if self.active:
            assert 0xc000<=at<0xc116 or 0x17b<=at<=0x1e0 or at in self.program['core']['SMC_operands'],('Unowned shape write',hex(at),value)
            self.writes.append((at,value))
        list.__setitem__(self,at,value)
    def setup_domain(self,page):
        host=self.program['point']['host']
        cursor,left=(4095,4072)if page==255 else(page*16+24,page*16)
        values={'ColumnSets':255,'AreaParserTaskNum':1 if page==255 else 0,
                'CurrentPageLoc':cursor//16,'CurrentColumnPos':cursor&15,
                'BlockBufferColumnPos':cursor&31,'ScreenLeftPage':left//16,'ScreenLeftX':(left&15)*16}
        for name,value in values.items():self[host[name]]=value
    def reset(self,state):
        list.__setitem__(self,slice(0xc000,0xc100),state)
        list.__setitem__(self,slice(0xc100,0xc116),bytes([0x9d])*22)
        self.writes=[];self.buffer_reads=[];self.attribute_reads=[];self.fixture_reads=[]


def put24(state,at,value):state[at:at+3]=(value&0xffffff).to_bytes(3,'little')
def word(memory,at):return memory[at]|memory[at+1]<<8
def stateword(state,at):return state[at]|state[at+1]<<8
def point(state,axis):
    width,height=state[0x41:0x43]
    negative=bool(state[0x21 if axis==0 else 0x61]&128)
    edge=0 if negative else(width if axis==0 else height)
    x=stateword(state,0x71)+(edge if axis==0 else width//2)
    y=stateword(state,0x74)+(height//2 if axis==0 else edge)
    return x,y,negative,edge


def invoke(memory,pc,*,p=0x21,trace=False):
    c=NesMPU(memory=memory,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,73,109,p,224
    memory.active=True
    try:
        c.stPushWord(STOP-1);low=c.sp
        for _ in range(1800):
            if c.pc==STOP:break
            assert 0xa000<=c.pc<0xbc00,('Escaped private code',hex(c.pc))
            assert memory[c.pc],('Shape BRK',hex(c.pc))
            low=min(low,c.sp)
            if trace and 0xa5e1<=c.pc<0xa6ed:
                if c.pc in(0xa5fa,0xa603,0xa684,0xa68c):assert c.y in(0,3)
                if c.pc in(0xa6d2,0xa6d8,0xa6db,0xa6e1,0xa6e4,0xa6ea):assert c.x in(0,64)
            c.step()
        else:raise AssertionError('Shape execution bound')
    finally:memory.active=False
    assert c.sp==224 and not memory.fixture_reads,'Retired fixture world/flags were read'
    memory.minimum_SP=min(memory.minimum_SP,low)
    return dict(regs=(c.a,c.x,c.y,c.p&0xef,c.sp),cycles=c.processorCycles,minimum_SP=low)


def base_state(*,mode=1,height=32,x=64<<8,y=96<<8,vx=0x181,vy=0x181,flags=0xc4):
    state=bytearray(STATE_CANARY)
    for at,value in((0x70,x),(0x73,y),(0x20,vx),(0x60,vy)):put24(state,at,value)
    state[0x41],state[0x42],state[0x30]=24,height,flags
    state[0xb4]=mode
    return state


def fill_point(memory,state,axis,tile):
    x,y,_,_=point(state,axis)
    if 0<=x<65536 and 32<=y<240:
        at=(0x3d0 if x//256&1 else 0x300)+((y&0xf0)-32)+(x>>4&15)
        memory[at]=tile
        return at
    return None


def oracle(memory,state,axis):
    ctx=memory.program['context'];mode=state[0xb4]
    if mode!=1:return 8,None
    if state[0x41]!=24 or state[0x42]not in(24,32):return 11,None
    mid,high=state[(0x21 if axis==0 else 0x61)],state[(0x22 if axis==0 else 0x62)]
    if high!=(255 if mid&128 else 0):return 9,None
    x,y,negative,edge=point(state,axis)
    if x>=65536 or y>=65536:return 10,None
    if not 32<=y<240:return 1,None
    host=memory.program['point']['host'];phase=memory[host['AreaParserTaskNum']]
    if memory[host['ColumnSets']]!=255:return 2,None
    if phase>=8:return 3,None
    col=memory[host['CurrentColumnPos']];page=memory[host['CurrentPageLoc']]
    if col>=16 or memory[host['BlockBufferColumnPos']]!=(page&1)*16+col:return 4,None
    first=memory[host['ScreenLeftPage']]*16+(memory[host['ScreenLeftX']]>>4)
    end=page*16+col+int(phase in(1,2,3,5,6,7))
    if not 1<=end-first<=32:return 5,None
    if not first<=x//16<end:return 6,None
    pointer=(0x3d0 if x//256&1 else 0x300)+((y&0xf0)-32)+(x>>4&15)
    tile=memory[pointer];attributes=memory[0xef36+tile]
    if attributes&2 or attributes&1 and(tile in(0x5f,0x60,0x67,0x68)or axis==0 and tile in(0x1c,0x6b)):return 7,None
    solid=bool(attributes&1)and tile not in(0x23,0xc2,0xc3)
    # Independent world-cell arithmetic, rather than the adapter's phase
    # formula: choose the exact near/far16px boundary in world coordinates.
    leading=x if axis==0 else y
    cell=leading//16*16
    boundary=cell+(16 if negative else 0)
    shape=boundary-(leading//32*32)if solid else 128
    out=bytearray(state);out[0x80:0x83]=bytes((shape,edge,0))
    out[0x30]&=0xbf if axis==0 else 0x7f
    return 0,dict(state=out,solid=solid,shape=shape,edge=edge,boundary=boundary,
                  negative=negative,kind=axis*2+int(negative)+1 if solid else 0,
                  point=(x,y),pointer=pointer,tile=tile,attributes=attributes)


def native_case(actual,reference,state,axis,*,p=0x21):
    program=actual.program;wanted,expected=oracle(actual,state,axis)
    actual.reset(state)
    out=invoke(actual,program['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'],p=p,trace=True)
    assert actual[program['context']['Status']]==wanted,(wanted,actual[program['context']['Status']],axis,list(state[0x20:0x23]),point(state,axis))
    assert bool(out['regs'][3]&1)==(wanted==0)
    if wanted:
        assert bytes(actual[0xc000:0xc0b4])==bytes(state[:0xb4]),('Unavailable mutated original state',wanted,axis)
        assert actual[program['context']['Kind']]==0
        assert out['regs'][0]==wanted
        if wanted!=7:assert not actual.buffer_reads and not actual.attribute_reads
        else:assert len(actual.buffer_reads)==len(actual.attribute_reads)==1
        return wanted,out['cycles'],None
    reference.reset(expected['state'])
    invoke(reference,program['core']['symbols']['HorizontalContact'if axis==0 else'VerticalContact'],p=p,trace=True)
    assert bytes(actual[0xc000:0xc0b4])==bytes(reference[0xc000:0xc0b4]),('Original contact result',axis,expected)
    assert actual[program['context']['Kind']]==expected['kind']and out['regs'][0]==0
    assert actual.buffer_reads==[expected['pointer']]and actual.attribute_reads==[0xef36+expected['tile']]
    assert actual[0xc080]==expected['shape']and actual[0xc081]==expected['edge']and actual[0xc082]==0
    for frac in(0x70,0x73):assert actual[0xc000+frac]==state[frac],'Source fraction was changed'
    flags=state[0x30]&(0xbf if axis==0 else 0x7f)
    if expected['solid']:
        at=0x71 if axis==0 else 0x74
        assert word(actual,0xc000+at)==(expected['boundary']-expected['edge'])&65535
        vel=0x20 if axis==0 else 0x60
        assert bytes(actual[0xc000+vel:0xc003+vel])==bytes(3),'Contact did not stop exact24-bit velocity'
        other=0x60 if axis==0 else 0x20
        assert bytes(actual[0xc000+other:0xc003+other])==bytes(state[other:other+3]),'Flat contact changed orthogonal velocity'
        if axis==0:flags|=0x40
        elif not expected['negative']:flags|=0x80
    else:
        for lo,hi in((0x20,0x23),(0x60,0x63),(0x70,0x76)):
            assert bytes(actual[0xc000+lo:0xc000+hi])==bytes(state[lo:hi])
    assert actual[0xc030]==flags,('Ground/wall/ceiling flags',axis,expected,actual[0xc030],flags)
    return wanted,out['cycles'],expected


def original32(program,attributes):
    old,new=Memory(program,attributes),Memory(program,attributes);count=0;cost=[]
    for axis in(0,1):
        print('Original32 mode exhaustive axis',axis,flush=True)
        for flag in range(64):
            for orthogonal in range(32):
                for leading_phase in range(32):
                    for negative in(0,1):
                        height=24 if(flag+leading_phase+negative)&1 else 32
                        edge=0 if negative else(24 if axis==0 else height)
                        leading=0x1e0+leading_phase
                        x=leading-edge if axis==0 else 128+orthogonal-12
                        y=128+orthogonal-height//2 if axis==0 else leading-edge
                        fraction=(0,1,127,255)[(orthogonal+leading_phase)&3]
                        state=base_state(mode=0,height=height,x=(x<<8)|fraction,y=(y<<8)|(fraction^255),
                                         vx=-0x181 if negative and axis==0 else 0x181,
                                         vy=-0x181 if negative and axis==1 else 0x181,
                                         flags=(0,0x89,0xc4,255)[(orthogonal+flag)&3])
                        state[0x82]=flag|(((orthogonal+leading_phase)&3)<<6)
                        old.reset(state);new.reset(state)
                        before=invoke(old,program['core']['symbols']['HorizontalTerrain'if axis==0 else'VerticalTerrain'],p=(0x21,0x60,0xad)[flag%3],trace=True)
                        after=invoke(new,program['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'],p=(0x21,0x60,0xad)[flag%3],trace=True)
                        assert before['regs']==after['regs']and bytes(old[0xc000:0xc100])==bytes(new[0xc000:0xc100]),('Original32 mismatch',axis,flag,orthogonal,leading_phase,negative)
                        assert [old[i]for i in program['core']['SMC_operands']]==[new[i]for i in program['core']['SMC_operands']]
                        assert not old.buffer_reads and not new.buffer_reads
                        cost.append(after['cycles']-before['cycles']);count+=1
    return dict(cases=count,full_state_and_AXYP_SP_exact=True,all64_classes_and_all256_flag_bytes=True,
                shape_ordinate_and_contact_phase_each32=True,cycle_delta=[min(cost),max(cost)],
                minimum_SP=min(old.minimum_SP,new.minimum_SP))


def geometric_state(axis,negative,height,page,phase,along,across,fraction):
    cellx=page*256+64+phase*16
    if axis==0:
        x=cellx+along-(0 if negative else 24)
        y=128+across-height//2
    else:
        x=page*256+64+across-12
        y=96+phase*16+along-(0 if negative else height)
    vx=(-0x181 if negative else 0x181)if axis==0 else -0x100
    vy=(-0x181 if negative else 0x181)if axis==1 else 0x7f
    return base_state(height=height,x=(x<<8)|fraction,y=(y<<8)|(fraction^255),vx=vx,vy=vy,
                      flags=(0,0x89,0xc4,255)[(along+across)&3])


def native16(program,attributes):
    actual,reference=Memory(program,attributes),Memory(program,attributes)
    assert attributes[0x54]&3==1
    counts=Counter();cycles=[];shapes=set();kinds=Counter()
    for page in(0,1,255):
        print('Native16 geometry exhaustive page',page,flush=True)
        actual.setup_domain(page)
        for axis in(0,1):
            for negative in(0,1):
                for height in(24,32):
                    for phase in(0,1):
                        for along in range(16):
                            for across in range(16):
                                for fraction in(0,1,127,255):
                                    state=geometric_state(axis,negative,height,page,phase,along,across,fraction)
                                    pointer=fill_point(actual,state,axis,0x54)
                                    status,cost,expected=native_case(actual,reference,state,axis,p=(0x21,0x60,0xad)[fraction%3])
                                    assert not status;shapes.add(expected['shape']);kinds[expected['kind']]+=1
                                    cycles.append(cost);counts['full16_geometry_fractional_cases']+=1
                                    actual[pointer]=0
    actual.setup_domain(1)
    print('Native exact256 metatile classifications',flush=True)
    for tile in range(256):
        for axis in(0,1):
            for negative in(0,1):
                for height in(24,32):
                    for phase in(0,1):
                        state=geometric_state(axis,negative,height,1,phase,7,9,tile)
                        pointer=fill_point(actual,state,axis,tile)
                        status,_,_=native_case(actual,reference,state,axis)
                        counts['metatile_classification_cases']+=1
                        counts['classification_'+('unsupported'if status else'available')]+=1
                        actual[pointer]=0
    for axis in(0,1):
        for velocity in(0,1,127,255,0x100,0x1000,-1,-127,-255,-0x100,-0x1000):
            negative=velocity<0
            state=geometric_state(axis,negative,32,1,1,3,5,255)
            put24(state,0x20 if axis==0 else 0x60,velocity)
            pointer=fill_point(actual,state,axis,0x54)
            assert native_case(actual,reference,state,axis)[0]==0
            counts['zero_subpixel_and_cap_velocity_cases']+=1;actual[pointer]=0
    # A naive SOLID-bit classifier incorrectly makes collectible coins and
    # the transient blank block placeholder into physical walls/floors.
    wrong=Memory(program,attributes)
    for tile in(0x23,0xc2,0xc3):
        for axis in(0,1):
            for negative in(0,1):
                for height in(24,32):
                    state=geometric_state(axis,negative,height,1,1,7,9,255)
                    pointer=fill_point(actual,state,axis,tile)
                    status,_,expected=native_case(actual,reference,state,axis)
                    assert not status and not expected['solid']and attributes[tile]&1
                    fake=bytearray(expected['state'])
                    x,y,_,edge=point(state,axis);leading=x if axis==0 else y
                    boundary=leading//16*16+(16 if negative else 0)
                    fake[0x80]=boundary-leading//32*32
                    wrong.reset(fake)
                    invoke(wrong,program['core']['symbols']['HorizontalContact'if axis==0 else'VerticalContact'])
                    assert bytes(actual[0xc000:0xc0b4])!=bytes(wrong[0xc000:0xc0b4])
                    counts['naive_SOLID_bit_negative_controls']+=1;actual[pointer]=0
    assert shapes=={0,16,32}and set(kinds)=={1,2,3,4}
    return dict(counts=dict(counts),adapted_offsets=sorted(shapes),contact_kinds=dict(kinds),
                valid_cycles=[min(cycles),max(cycles)],minimum_SP=actual.minimum_SP,
                exact_integer_cell_boundary=True,original_fraction_preserved=True,
                original24bit_contact_stop_and_flags=True)


def unavailable(program,attributes):
    actual,reference=Memory(program,attributes),Memory(program,attributes);counts=Counter()
    host=program['point']['host'];cases=[]
    for axis in(0,1):
        for y in(0,15,16,31,240,255,256,65535):
            state=base_state(x=64<<8,y=y<<8,vx=0x181,vy=-0x181)
            if axis==0:put24(state,0x73,max(0,y-state[0x42]//2)<<8)
            cases.append((state,axis,{},'vertical_bounds'))
        for x in(512,1024,0xff00):cases.append((base_state(x=x<<8),axis,{},'distant_page_alias'))
        for name,value in(('ColumnSets',0),('AreaParserTaskNum',8),('AreaParserTaskNum',255),
                           ('CurrentColumnPos',16),('BlockBufferColumnPos',255),('ScreenLeftPage',8)):
            cases.append((base_state(),axis,{host[name]:value},'parser_unavailable'))
        for width,height in((0,0),(16,16),(24,0),(24,31),(255,32)):
            state=base_state();state[0x41:0x43]=bytes((width,height));cases.append((state,axis,{},'unsupported_body'))
        for high,mid in((1,0),(0,255),(255,0),(128,128)):
            state=base_state();state[0x22 if axis==0 else 0x62]=high;state[0x21 if axis==0 else 0x61]=mid
            cases.append((state,axis,{},'malformed_velocity'))
        state=base_state(x=65530<<8,y=96<<8);cases.append((state,axis,{},'world_coordinate_overflow'))
        state=base_state(y=65530<<8);cases.append((state,axis,{},'vertical_coordinate_overflow'))
        for mode in(2,3,255):cases.append((base_state(mode=mode),axis,{},'unsupported_mode'))
    for state,axis,changes,label in cases:
        actual.setup_domain(0)
        for at,value in changes.items():actual[at]=value
        wanted,_,_=native_case(actual,reference,state,axis)
        assert wanted,(label,axis,point(state,axis))
        counts[label]+=1
    return dict(cases=len(cases),counts=dict(counts),original_actor_and_core_scratch_unchanged=True,
                explicit_failure_not_empty=True)


def corners(program,attributes):
    count=0;negative_controls=0;outcomes=Counter()
    for page in(0,1):
        for height in(24,32):
            for left in(0,1):
                for up in(0,1):
                    for fraction in(0,255):
                        ordered=Memory(program,attributes);wrong=Memory(program,attributes)
                        for m in(ordered,wrong):m.setup_domain(page)
                        x=page*256+(82 if left else 70);y=108 if up or height==24 else 100
                        state=base_state(height=height,x=(x<<8)|fraction,y=(y<<8)|(fraction^255),
                                         vx=-0x181 if left else 0x181,vy=-0x181 if up else 0x181,flags=0)
                        clippedx=page*256+(96 if left else 56)
                        targetx=clippedx+12;targety=y if up else y+height
                        targettop=targety//16*16
                        for m in(ordered,wrong):
                            fill_point(m,state,0,0x54)
                            pointer=(0x3d0 if targetx//256&1 else 0x300)+(targettop-32)+(targetx>>4&15)
                            m[pointer]=0x54;m.reset(state)
                        for axis in(0,1):
                            out=invoke(ordered,program['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'])
                            assert out['regs'][3]&1
                        for axis in(1,0):
                            out=invoke(wrong,program['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'])
                            assert out['regs'][3]&1
                        assert word(ordered,0xc071)==clippedx
                        expectedy=targettop+16 if up else targettop-height
                        assert word(ordered,0xc074)==expectedy,(page,height,left,up,expectedy,word(ordered,0xc074))
                        assert ordered[0xc030]==(0x40 if up else 0xc0)
                        assert ordered[0xc070]==fraction and ordered[0xc073]==fraction^255
                        assert word(wrong,0xc074)!=word(ordered,0xc074),'Swapped contact order was not detected'
                        negative_controls+=1;count+=1;outcomes['ceiling'if up else'floor']+=1
    return dict(cases=count,recomputed_vertical_probe_after_X=True,swapped_XY_negative_controls=negative_controls,
                outcomes=dict(outcomes),scope='Two contact passes on a post-integration state; not an OrdinaryFrame/native hook')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--only',choices=('all','legacy','native','corners'),default='all')
    args=parser.parse_args();assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    raw=ROM.read_bytes();assert digest(raw)==PIN
    def exact(bank,pc,value):
        data=bytes.fromhex(value);at=16+bank*8192+(pc&8191)
        assert raw[at:at+len(data)]==data,(bank,hex(pc))
    exact(126,0x9d83,'c9c2f006c9c3f0021860') # coins are dispatched before BG clipping
    exact(126,0x9eca,'c95ff002c96060') # invisible blocks need native head behavior
    exact(126,0x9eea,'c967f005c96818d0013860') # native spring transaction
    exact(126,0x9c77,'c88c0601a5bdc920901dc9e4b0302097e4f014c91cf010c96bf00ca8b936')
    exact(9,0xbf21,'9db805209fbfa405a9239109a9108d8107') # struck-block blank23 producer
    assert digest((R/'tools/reference/sonic_sms_native_point_read_1110.py').read_bytes())==POINT_SOURCE_PIN
    program=B.build();attributes=raw[16+127*8192+0xf36:16+127*8192+0xf36+256]
    for name in('ContactXSlide','ContactYSlide','ContactMagnet'):
        assert program['core']['image'][program['core']['symbols'][name]-0xa000]==0
    report=dict(passed=True,source_only=True,files_written=0,ROM_written=False,current_SHA256=PIN,
                adapter_bytes=len(program['image']),adapter_SHA256=digest(program['image']),
                proposed_code_half_open=program['code_half_open'],proposed_context_half_open=program['context_half_open'],
                census=program['census'],frozen_core_SHA256=digest(program['core']['image']),
                frozen_PointRead_SHA256=digest(program['point']['image']),
                no_host_admission_ordinary_frame_constructor_renderer_or_RAM_lease=True)
    if args.only in('all','legacy'):report['original32']=original32(program,attributes)
    if args.only in('all','native'):
        report['native16']=native16(program,attributes);report['unavailable']=unavailable(program,attributes)
    if args.only in('all','corners'):report['corners']=corners(program,attributes)
    assert not args.output.exists()
    print(json.dumps(report,sort_keys=True),flush=True)


if __name__=='__main__':main()
