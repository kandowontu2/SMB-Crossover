"""Zero-output actual6502 witness/preflight check; no native collision claim."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from py65.devices.mpu6502 import MPU

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
import sonic_sms_native_sweep_witness_1110 as B

STOP = 0x5b00
CANARY = bytes((i*73+41)&255 for i in range(65536))
FROZEN = {
    'tools/reference/sonic_sms_relocated_core_1110.py':'f031aad8dfac2b9586df81f303a6b9464db6941095321af23e791a579562b10d',
    'tools/reference/sonic_sms_native_point_read_1110.py':'fc135d40cb35d115d4854db00b29943b57ee9a454b7cff58f65e2a2e6ddf8eff',
    'tools/reference/sonic_sms_native_shape_contact_1110.py':'ceea5507300f07bbe1da0339a109af90067ac1b37c8a0f92d6b2488c8ec9c602',
}


class Memory(list):
    def __init__(self, program):
        super().__init__(CANARY)
        self.program, self.active, self.writes = program, False, []
        self.phase, self.forbidden_reads = '', []
        for pc, data in ((0xa000, program['shape']['core']['image']),
                         (B.CODE, program['image'])):
            list.__setitem__(self, slice(pc, pc+len(data)), data)

    def __getitem__(self, at):
        if self.active and isinstance(at, int) and (at<0x100 or 0x300<=at<0x4a1 or 0xc800<=at<0xd900):
            self.forbidden_reads.append(at)
        return list.__getitem__(self, at)

    def __setitem__(self, at, value):
        if self.active:
            assert isinstance(at, int)
            own = B.CONTEXT<=at<B.CONTEXT+len(B.FIELDS)
            original = self.phase=='PositionStep' and 0xc070<=at<0xc076
            assert own or original or 0x1df<=at<=0x1e0, ('Unowned write', self.phase, hex(at))
            self.writes.append((at,value&255))
        list.__setitem__(self, at, value&255)


def put24(m, at, value):
    for i in range(3):m[at+i]=(value>>(8*i))&255


def get24(m, at):return m[at]|m[at+1]<<8|m[at+2]<<16
def word(m, at):return m[at]|m[at+1]<<8


def invoke(m, label):
    program=m.program
    pc=(program['shape']['core']['symbols'][label] if label=='PositionStep'
        else program['symbols'][label])
    cpu=MPU(memory=m,pc=pc);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=85,73,109,0x21,224
    m.phase=label;m.active=True
    try:
        cpu.stPushWord(STOP-1);minimum=cpu.sp
        for _ in range(400):
            if cpu.pc==STOP:break
            assert (0xa000<=cpu.pc<0xb596 or B.CODE<=cpu.pc<program['code_half_open'][1]),hex(cpu.pc)
            minimum=min(minimum,cpu.sp);cpu.step()
        else:raise AssertionError(('Execution bound',label,hex(cpu.pc)))
    finally:m.active=False
    assert cpu.sp==224 and not m.forbidden_reads
    return cpu.a,bool(cpu.p&1),cpu.processorCycles,minimum


def setup(m,axis,old,velocity,height=32):
    list.__setitem__(m,slice(0xc000,0xc100),bytes((i*31+93)&255 for i in range(256)))
    m[0xc041],m[0xc042],m[0xc0b4]=24,height,1
    put24(m,0xc070,old if axis==0 else 80<<8)
    put24(m,0xc073,old if axis==1 else 96<<8)
    put24(m,0xc020,velocity if axis==0 else 0)
    put24(m,0xc060,velocity if axis==1 else 0)
    m.writes=[];m.forbidden_reads=[]


def sequence(m,axis):
    before=bytes(m[0xc000:0xc0b4])
    captured=invoke(m,'SonicSweepCapture')
    assert bytes(m[0xc000:0xc0b4])==before
    old=bytes(m[0xc070:0xc076])
    assert bytes(m[B.CONTEXT:B.CONTEXT+6])==old
    moved=invoke(m,'PositionStep')
    actor=bytes(m[0xc000:0xc0b4])
    out=invoke(m,'SonicSweepPreflightHorizontal' if axis==0 else 'SonicSweepPreflightVertical')
    assert bytes(m[0xc000:0xc0b4])==actor,'Preflight changed original state'
    assert bytes(m[B.CONTEXT:B.CONTEXT+6])==old,'Preflight changed old witness'
    return out,captured,moved


def finite(m):
    fields=m.program['fields'];count=0;spans=Counter();cycles=[];minimum=255
    for axis in (0,1):
        for negative in (False,True):
            for fraction in range(256):
                for velocity_fraction in range(256):
                    phase=(fraction+5*velocity_fraction)&31
                    old_word=0xe0+phase+(((fraction^velocity_fraction)&1)<<8)
                    old=(old_word<<8)|fraction
                    velocity=(0xfff000 if negative else 0x1000)|velocity_fraction
                    height=24 if (fraction^velocity_fraction)&1 else 32
                    setup(m,axis,old,velocity,height)
                    out,capture,move=sequence(m,axis)
                    assert out[:2]==(0,True),(axis,negative,fraction,velocity_fraction,out)
                    new=(old+velocity)&0xffffff
                    assert get24(m,0xc070+3*axis)==new,'Original24-bit position result'
                    edge=0 if negative else (24 if axis==0 else height)
                    a,b=old_word+edge,(new>>8)+edge
                    start,end=a&0xfff0,b&0xfff0
                    span=abs(end-start)//16+1
                    assert 1<=span<=(2 if negative else 3)
                    assert word(m,fields['OldLeadingLo'])==a
                    assert word(m,fields['NewLeadingLo'])==b
                    assert word(m,fields['StartCellLo'])==start
                    assert word(m,fields['EndCellLo'])==end
                    assert m[fields['CellCount']]==span and m[fields['Negative']]==int(negative)
                    assert m[fields['Status']]==0
                    spans[axis,negative,span]+=1;count+=1
                    cycles.append(out[2]);minimum=min(minimum,out[3],capture[3],move[3])
            print(json.dumps(dict(phase='cap_fraction_matrix',axis=axis,negative=negative,cases=count)),flush=True)
    assert any(k[2]==3 and n>0 for k,n in spans.items()),'Missing actual17px/three-cell witness'
    return dict(cases=count,spans={str(k):v for k,v in spans.items()},
                preflight_cycles=[min(cycles),max(cycles)],minimum_SP=minimum)


def negatives(m):
    counts=Counter();f=m.program['fields']
    for axis in (0,1):
        for kind in ('mode','missing','width','height','positive_cap','negative_cap',
                     'positive_high','negative_high','fraction','integer','witness','world_wrap','edge_overflow'):
            setup(m,axis,96<<8|255,0x10ff)
            invoke(m,'SonicSweepCapture');invoke(m,'PositionStep')
            vel=0xc020+64*axis;pos=0xc070+3*axis
            if kind=='mode':m[0xc0b4]=0;expected=8
            elif kind=='missing':m[f['Ready']]=0;expected=12
            elif kind=='width':m[0xc041]=16;expected=11
            elif kind=='height':m[0xc042]=23;expected=11
            elif kind=='positive_cap':m[vel+1]=17;expected=14
            elif kind=='negative_cap':m[vel+1],m[vel+2]=0xef,255;expected=14
            elif kind=='positive_high':m[vel+2]=1;expected=9
            elif kind=='negative_high':m[vel+1],m[vel+2]=0xff,0;expected=9
            elif kind=='fraction':m[pos]^=1;expected=13
            elif kind=='integer':m[pos+1]^=1;expected=13
            elif kind=='witness':m[B.CONTEXT+3*axis]^=1;expected=13
            elif kind=='world_wrap':
                setup(m,axis,0,0xfff000);invoke(m,'SonicSweepCapture');invoke(m,'PositionStep');expected=14
            elif kind=='edge_overflow':
                setup(m,axis,65520<<8,0);invoke(m,'SonicSweepCapture');invoke(m,'PositionStep');expected=10
            actor=bytes(m[0xc000:0xc0b4]);old=bytes(m[B.CONTEXT:B.CONTEXT+6])
            out=invoke(m,'SonicSweepPreflightHorizontal' if axis==0 else 'SonicSweepPreflightVertical')
            assert out[:2]==(expected,False),(axis,kind,out,expected)
            assert m[f['Status']]==expected and m[f['CellCount']]==0
            assert bytes(m[0xc000:0xc0b4])==actor and bytes(m[B.CONTEXT:B.CONTEXT+6])==old
            counts[kind]+=1
    return dict(cases=sum(counts.values()),kinds=dict(counts))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();assert args.output.resolve().is_relative_to(R/'build') and not args.output.exists()
    for path,digest in FROZEN.items():assert sha256((R/path).read_bytes()).hexdigest()==digest,path
    program=B.build();m=Memory(program)
    proof=finite(m);bad=negatives(m)
    # Whole-memory canaries: setup touches only the proposed/existing source
    # state page. Executed writes are checked individually by Memory above.
    for at,value in enumerate(m):
        if 0xc000<=at<0xc100 or 0x1df<=at<=0x1e0 or 0xa000<=at<0xb596 or B.CODE<=at<program['code_half_open'][1]:continue
        assert value==CANARY[at],hex(at)
    for path,digest in FROZEN.items():assert sha256((R/path).read_bytes()).hexdigest()==digest,path
    print(json.dumps(dict(passed=True,outputs_written=0,ROM_written=False,
        image_bytes=len(program['image']),image_SHA256=sha256(program['image']).hexdigest(),
        source_SHA256=sha256(Path(B.__file__).read_bytes()).hexdigest(),
        code=program['code_half_open'],context=program['context_half_open'],
        finite=proof,negatives=bad,source_census=program['source_census'],
        frozen_sources=FROZEN,
        scope='Actual6502 capture/originalPositionStep/preflight only. No swept PointRead/contact, native frame/lifecycle, RAM/code grant, ROM/Mesen or gameplay.'),sort_keys=True))
    assert not args.output.exists()


if __name__=='__main__':main()
