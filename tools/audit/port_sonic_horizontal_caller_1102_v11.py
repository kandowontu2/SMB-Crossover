"""Compose normal-body setup and active-low inputs with all three X paths."""
import json,random,subprocess
from pathlib import Path
import port_sonic_coasting_1102_v10 as P
R=P.R;sha=P.sha;NesMPU=P.NesMPU
O=R/'build/sonic-sms-horizontal-1102-v11'
head,tail=P.ASM.split('CoastMotor:',1)
# Keep braking and passive friction distinct when both run in one component.
ASM=head+'CoastMotor:'+tail.replace('lda $34','lda $45').replace('lda $35','lda $46')+'''
HorizontalBody:
 lda $42
 cmp #32
 beq BodyHeightReady
 sec
 lda $43
 sbc #8
 sta $43
 lda $44
 sbc #0
 sta $44
BodyHeightReady:
 lda #24
 sta $41
 lda #32
 sta $42
 lda OldV
 sta VL
 lda OldV+1
 sta VH
 lda OldV+2
 sta VB
 lda #0
 sta VC
 sta VE
 sta VD
 lda $40
 and #8
 bne NotRight
 jmp RightMotor
NotRight:
 lda $40
 and #4
 bne NotLeft
 jmp LeftMotor
NotLeft:
 jmp CoastMotor
'''

def entry(rom,old,height,y,input_byte):
    pc=0x4a89;a=l=h=b=c=d=e=0;z=carry=False;out={};width=0
    for _ in range(50):
        if pc in [0x4f01,0x4f5c,0x4aba]:return pc,[l,h,c,b,e,d],width,height,y
        op=rom[pc];pc+=1
        if op==0xdd:
            sub,offset=rom[pc:pc+2];pc+=2
            if sub==0x7e:assert offset==14;a=height
            elif sub==0x46:assert offset==9;b=old[2]
            elif sub==0x36:
                v=rom[pc];pc+=1
                if offset==13:width=v
                elif offset==14:height=v
                else:raise AssertionError(offset)
            else:raise AssertionError(sub)
        elif op==0xfe:z=a==rom[pc];carry=a<rom[pc];pc+=1
        elif op==0x28:
            offset=rom[pc];pc+=1
            if z:pc+=offset
        elif op==0x2a:
            at=rom[pc]|rom[pc+1]<<8;pc+=2
            assert at in [0xd401,0xd403];v=y if at==0xd401 else old[0]|old[1]<<8;l=v&255;h=v>>8
        elif op==0x11:e,d=rom[pc:pc+2];pc+=2
        elif op==0x19:v=(h<<8|l)+(d<<8|e);l=v&255;h=v>>8&255;carry=v>65535
        elif op==0x22:assert rom[pc:pc+2]==bytes([1,212]);pc+=2;y=h<<8|l
        elif op==0x0e:c=rom[pc];pc+=1
        elif op==0x59:e=c
        elif op==0x51:d=c
        elif op==0xfd:
            assert rom[pc:pc+2]==bytes([0xcb,3]);sub=rom[pc+2];pc+=3
            assert sub in [0x5e,0x56];z=not(input_byte&(8 if sub==0x5e else 4))
        elif op==0xca:
            target=rom[pc]|rom[pc+1]<<8;pc+=2
            if z:pc=target
        else:raise AssertionError((hex(pc-1),hex(op)))
    raise AssertionError('Original entry bound')

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-o',O/'component.bin',O/'component.o']]:
        z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    code=(O/'component.bin').read_bytes();assert code[:322]==(R/'build/sonic-sms-leftmotor-1102-v9/component.bin').read_bytes()
    original_coast=P.oracle();original_left=P.P.oracle();original_right=P.P.P.right
    rng=random.Random(110211);cycles=[];paths={}
    fixtures=[]
    for inp in range(256):
        for height in [16,32]:
            for v in [0,767,768,65535]:fixtures.append(([v&255,v>>8,255 if v&32768 else 0],height,5,inp))
    fixtures.extend(([rng.randrange(256)for _ in range(3)],rng.randrange(256),rng.randrange(65536),rng.randrange(256))for _ in range(2048))
    for old,height,y,inp in fixtures:
        flags=rng.randrange(256);anim=rng.randrange(256);acc,brake,friction,cap=16,48,8,768
        pc,values,width,eh,ey=entry(rom,old,height,y,inp);paths[pc]=paths.get(pc,0)+1
        select={0x4f01:original_right,0x4f5c:original_left,0x4aba:original_coast}[pc]
        selected,ef,ea=select(rom,values,flags,anim,acc,friction if pc==0x4aba else brake,cap,2)
        expected,stored,a=P.P.P.X.original(rom,selected,old)
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x20:0x23]=old
        m[0x30:0x39]=[flags,anim,acc,0,brake,0,cap&255,cap>>8,2]
        m[0x40:0x47]=[inp,99,height,y&255,y>>8,friction,0]
        cpu=NesMPU(memory=m,pc=0x8000+419);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(180):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('6502 bound')
        assert m[0x10:0x16]==expected and m[0x20:0x23]==stored and m[0x30:0x32]==[ef,ea]
        assert m[0x41:0x45]==[width,eh,ey&255,ey>>8] and cpu.a==a and cpu.sp==224
        assert m[0x34:0x36]==[brake,0] and m[0x45:0x47]==[friction,0]
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),cycles=[min(cycles),max(cycles)],paths={hex(k):v for k,v in paths.items()},scope='Executed original normal-body caller plus original right/left/coast and commit versus unified6502. All256 active-low inputs including right priority, bodyheight correction, independent brake/friction parameters. Full Main/rolling/terrain/host ABI and native play remain unimplemented.',bindings={str(p):sha(p)for p in [Path(__file__),Path(P.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
