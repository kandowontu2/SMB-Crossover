"""Join source-verified normal/rolling X and Y paths with disjoint fixture RAM."""
import json,re,random,subprocess
from pathlib import Path
import port_sonic_rolling_motor_1102_v12 as H
import port_sonic_rolling_jump_1102_v13 as J
import port_sonic_y_velocity_1102_v4 as Y
R=H.R;sha=H.sha;NesMPU=H.NesMPU
O=R/'build/sonic-sms-motion-1102-v14'

def remap(text, addresses):
    return re.sub(r'\$([0-9a-f]{2})(?![0-9a-f])',lambda m:'$'+addresses.get(m[1],m[1]),text)

# Only zero-page operands move; immediates such as #$80 must remain literal.
def operands(text, addresses):
    return '\n'.join(remap(line,addresses)if '#'not in line else line for line in text.splitlines())+'\n'

ASM=H.ASM+'\nJumpComponent:\n'+operands(J.ASM.split('.segment "CODE"',1)[1],{f'{i:02x}':f'{i+64:02x}'for i in range(16,32)})
ASM+='\nVerticalCommit:\n'+operands(Y.ASM.split('.segment "CODE"',1)[1],dict(zip(['10','11','12','13','14','15','23','24','25','26','27','28'],['50','51','53','52','54','55','60','61','62','63','64','65'])))
ASM+='''
MotionStep:
 lda $30
 and #1
 beq MotionNormalX
 jsr RollingBody
 jmp MotionY
MotionNormalX:
 jsr HorizontalBody
MotionY:
 lda $60
 sta $50
 lda $61
 sta $51
 lda $62
 sta $52
 lda #0
 sta $53
 sta $54
 sta $55
 lda $30
 sta $56
 lda $40
 sta $57
 lda OldV
 sta $5f
 lda $30
 and #1
 beq MotionNormalY
 jsr RollingJump
 jmp MotionFinishY
MotionNormalY:
 jsr JumpComponent
MotionFinishY:
 lda $56
 sta $30
 lda $5f
 sta OldV
 jsr VerticalCommit
 rts
'''
ASM+='\n.export MotionStep\n'

def main():
    O.mkdir(exist_ok=True);donor=R/'build/sonic-sms-original-1102-v2/out/s1.sms';rom=donor.read_bytes()
    assert sha(donor)=='6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
    (O/'component.s').write_text(ASM);(O/'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$1000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg','-Ln',O/'labels.txt','-o',O/'component.bin',O/'component.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    entry=int(next(line.split()[1]for line in (O/'labels.txt').read_text().splitlines()if line.endswith('.MotionStep')),16)
    code=(O/'component.bin').read_bytes();rng=random.Random(110214);rolling=J.oracle();cycles=[]
    original_coast=H.P.P.oracle();original_left=H.P.P.P.oracle();original_right=H.P.P.P.P.right
    fixtures=[]
    for inp in range(256):
        for flags in [0,1,128,129,137,255]:
            fixtures.append(([rng.randrange(256),2,0],32,65532,inp,flags,5,0,0))
    fixtures.extend(([rng.randrange(256)for _ in range(3)],rng.randrange(256),rng.randrange(65536),rng.randrange(256),rng.randrange(256),rng.randrange(256),rng.randrange(65536),rng.randrange(256))for _ in range(4096))
    for old,height,y,inp,flags,anim,vy,timer in fixtures:
        if flags&1:
            values,ef,ea,width,eh,ey,ec,commit=H.original(rom,old,height,y,inp,flags,anim,48,768,0)
            if commit:_,stored,_=H.P.P.P.P.X.original(rom,values,old)
            else:stored=old[:]
        else:
            pc,values,width,eh,ey=H.P.entry(rom,old,height,y,inp)
            fn={0x4f01:original_right,0x4f5c:original_left,0x4aba:original_coast}[pc]
            values,ef,ea=fn(rom,values,flags,anim,16,8 if pc==0x4aba else 48,768,2)
            _,stored,_=H.P.P.P.P.X.original(rom,values,old);ec=0
        ys=[vy&255,vy>>8,255 if vy&32768 else 0,0,0,0,ef,inp,timer,0x80,0xfc,0x38,0,8,0,stored[0]]
        js=rolling(rom,ys)if ef&1 else J.P.original(rom,ys)
        vv=[js[0],js[1],js[3],js[2],js[4],js[5]]
        _,vertical,_=Y.original(rom,vv);stored[0]=js[15]
        m=[0]*65536;m[0x8000:0x8000+len(code)]=code;m[0x20:0x23]=old
        m[0x30:0x39]=[flags,anim,16,0,48,0,0,3,2]
        m[0x40:0x4a]=[inp,99,height,y&255,y>>8,8,0,0,0,0]
        m[0x58:0x5f]=[timer,0x80,0xfc,0x38,0,8,0];m[0x60:0x63]=[vy&255,vy>>8,255 if vy&32768 else 0]
        cpu=NesMPU(memory=m,pc=entry);cpu.sp=224;cpu.p=0x30;cpu.stPushWord(0x5aff)
        for _ in range(420):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError('Motion step bound')
        assert m[0x20:0x23]==stored and m[0x30:0x32]==[js[6],ea] and m[0x60:0x66]==vertical,(flags,inp,stored,m[0x20:0x23],vertical,m[0x60:0x66])
        assert m[0x41:0x45]==[width,eh,ey&255,ey>>8] and m[0x47:0x49]==[ec&255,ec>>8]
        assert m[0x58:0x5f]==js[8:15] and cpu.sp==224
        cycles.append(cpu.processorCycles)
    q=dict(passed=True,private=True,installed=False,cases=len(fixtures),bytes_6502=len(code),cycles=[min(cycles),max(cycles)],original_ROM_SHA256=sha(donor),scope='Composed normal/rolling horizontal caller, post-X rolling flag dispatch, exact jump input and Yvelocity/bounce commit. All256 inputs. Source terrain/landing callbacks, world position, full Main/render/audio/native RAM integration remain excluded.',bindings={str(p):sha(p)for p in [Path(__file__),Path(H.__file__),Path(J.__file__),Path(Y.__file__),O/'component.s',O/'component.bin']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
