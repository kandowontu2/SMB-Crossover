"""Relocate the real WWF music driver, preserving virtual source stream words."""
from pathlib import Path
import hashlib,json,re,struct,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from py65.devices.mpu6502 import MPU
import wwf_roster_source_review_v1 as V
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
P=R/'build/wwf-roster-package-1101-v1';O=R/'build/wwf-audio-source-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
START,END=0xe22e,0xe84e
ENTRIES=[0xe22e,0xe249,0xe4de,0xe297,0xe2a7,0xe2ac,0xe2b1]


class HostBus(V.Bus):
    def __init__(self,code):
        super().__init__(bytes(32768));self.m[0xa000:0xa000+len(code)]=code
    def __setitem__(self,a,v):
        assert isinstance(a,int)and(a<0x8000 or 0xc000<=a<0xc800 or a==0xdfdb),('Port wrote outside audio ownership',hex(a))
        self.writes.add(a);self.m[a]=v
        if 0x4000<=a<=0x4017:self.apu.append((a,v))


def invoke(bus,pc,*,original=False,limit=100000):
    c=NesMPU(memory=bus,pc=pc);c.sp=224;c.stPushWord(0x5aff)
    virtual=[]
    for _ in range(limit):
        if c.pc==0x5b00:break
        op=bus.m[c.pc]
        if original and op==0xb1:
            p=bus.m[c.pc+1];target=((bus.m[p]|bus.m[(p+1)&255]<<8)+c.y)&65535
            assert p in[4,7]and(0x8018<=target<0x88d7 or 0xe84e<=target<0xf83c),('Indirect source data outside mapped spans',hex(c.pc),hex(target))
            virtual.append(target)
        assert op!=0,('Audio BRK',hex(c.pc));c.step()
    else:raise AssertionError(('Audio CPU bound',hex(c.pc)))
    assert c.sp==224
    return c,virtual


def main():
    assert not(O/'source-controls.json').exists();O.mkdir(exist_ok=True)
    q=json.loads((P/'source-package.json').read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    raw=V.raw();bank=raw[65536:98304];decoder=MPU()
    byte=lambda a:bank[a-0x8000]
    word=lambda a:byte(a)|(byte(a+1)<<8)
    op_table=range(0xe5e9,0xe609,2);targets=[word(a)for a in op_table]
    pending=[*ENTRIES,*targets];code={}
    branches={'BCC','BCS','BEQ','BMI','BNE','BPL','BVC','BVS'}
    while pending:
        pc=pending.pop()
        while pc not in code:
            assert START<=pc<END,('Audio control flow outside driver',hex(pc))
            op=byte(pc);name,mode=decoder.disassemble[op]
            assert name not in['???','BRK']and mode!='???',(hex(pc),hex(op),name,mode)
            n={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}[mode]
            code[pc]=(name,mode,n)
            if name in branches:
                delta=byte(pc+1);pending.append(pc+2+(delta if delta<128 else delta-256))
            elif name=='JSR':pending.append(word(pc+1))
            elif name=='JMP':
                if mode=='abs':pending.append(word(pc+1))
                else:assert pc==0xe5e6 and word(pc+1)==7
                break
            elif name in['RTS','RTI']:break
            pc+=n
    occupied={a:pc for pc,(_,_,n)in code.items()for a in range(pc,pc+n)}
    assert not any(a in occupied for p in op_table for a in[p,p+1])
    helper=R/'tools/reference/wwf_audio_virtual_read_v1.s'
    def lab(a):
        if 0x8018<=a<0x88d7:return 'WfAudioLowData+$%x'%(a-0x8018)
        if 0xe84e<=a<0xf83c:return 'WfAudioHighData+$%x'%(a-0xe84e)
        if 0xe222<=a<0xe22e:return 'WfAudioTempo+$%x'%(a-0xe222)
        assert START<=a<END,hex(a)
        if 0xe5e9<=a<0xe609:
            base=0xe5e9+2*((a-0xe5e9)//2)
            return 'WfAudio_%04X+$%x'%(base,a-base)
        if a in occupied:return 'WfAudio_%04X+$%x'%(occupied[a],a-occupied[a])
        return 'WfAudio_%04X'%a
    lines=['.setcpu "6502"','.segment "WF_AUDIO"','WfAudioReadByte=$dfdb']
    for a in ENTRIES:lines.append('.export WfAudio_%04X'%a)
    pc=START;indirect_sites=[]
    while pc<END:
        lines.append('WfAudio_%04X:'%pc)
        if pc in op_table:
            lines.append(' .word '+lab(word(pc)));pc+=2;continue
        if pc not in code:
            lines.append(' .byte $%02x'%byte(pc));pc+=1;continue
        name,mode,n=code[pc];op=byte(pc)
        if mode=='iny':
            assert name=='LDA'and byte(pc+1)in[4,7]
            indirect_sites.append(pc);text='jsr WfAudioRead%d'%byte(pc+1)
        elif mode in['imp','acc']:text=name.lower()
        elif mode=='imm':text=name.lower()+' #$%02x'%byte(pc+1)
        elif mode=='rel':
            delta=byte(pc+1);text=name.lower()+' '+lab(pc+2+(delta if delta<128 else delta-256))
        elif mode in['zpg','zpx','zpy','inx']:
            value=byte(pc+1)
            text=name.lower()+(' ($%02x,x)'%value if mode=='inx'else' $%02x'%value+(',x'if mode=='zpx'else',y'if mode=='zpy'else''))
        elif mode=='ind':text=name.lower()+' ($%04x)'%word(pc+1)
        else:
            value=word(pc+1)
            operand=lab(value)if value>=0x8000 else'$%04x'%(value+0xc000 if 0x400<=value<0x800 else value)
            text=name.lower()+' '+operand+(',x'if mode=='abx'else',y'if mode=='aby'else'')
        lines.append(' '+text+' ; original%04X'%pc);pc+=n
    lines+=[helper.read_text(),'WfAudioTempo:', ' .byte '+','.join('$%02x'%b for b in bank[0x6222:0x622e]),'WfAudioHighData:']
    for a in range(0xe84e,0xf83c,32):lines.append(' .byte '+','.join('$%02x'%byte(i)for i in range(a,min(a+32,0xf83c))))
    lines.append('WfAudioLowData:')
    for a in range(0x8018,0x88d7,32):lines.append(' .byte '+','.join('$%02x'%byte(i)for i in range(a,min(a+32,0x88d7))))
    (O/'audio.s').write_text('\n'.join(lines)+'\n')
    (O/'audio.cfg').write_text('MEMORY { AUDIO:start=$a000,size=$2000,type=ro,file=%O; }\nSEGMENTS { WF_AUDIO:load=AUDIO,type=ro; }\n')
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    run('assemble',[R/'tools/Windows/cc65/bin/ca65.exe',O/'audio.s','-o',O/'audio.o','-l',O/'audio.lst'])
    run('link',[R/'tools/Windows/cc65/bin/ld65.exe','-C',O/'audio.cfg',O/'audio.o','-o',O/'audio.bin','-Ln',O/'audio.lbl'])
    blob=(O/'audio.bin').read_bytes();assert len(blob)<=8192
    labels={name:int(value,16)for value,name in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'audio.lbl').read_text())}
    results=[]
    for char in V.tables(raw):
        src=V.Bus(bank);host=HostBus(blob)
        for entry in[0xe22e,0xe249]:
            if entry==0xe249:src.m[1]=host.m[1]=char['theme']
            src.apu=[];host.apu=[];a,_=invoke(src,entry,original=True);z,_=invoke(host,labels['WfAudio_%04X'%entry]);assert src.apu==host.apu
            assert src.m[0x500:0x5c0]==host.m[0xc500:0xc5c0]
        digest=hashlib.sha256();costs=[];original_costs=[];reads=set();writes=0
        for frame in range(2400):
            src.apu=[];host.apu=[]
            a,seen=invoke(src,0xe4de,original=True);z,_=invoke(host,labels['WfAudio_E4DE'])
            assert src.apu==host.apu,('APU trace',char['name'],frame)
            assert src.m[0x500:0x5c0]==host.m[0xc500:0xc5c0],('Source channel state',char['name'],frame)
            assert(a.a,a.x,a.y,a.p)==(z.a,z.x,z.y,z.p),('Source return registers',char['name'],frame)
            reads.update(seen);costs.append(z.processorCycles);original_costs.append(a.processorCycles);writes+=len(host.apu)
            for reg,value in host.apu:digest.update(struct.pack('<IHB',frame,reg,value))
        assert not any(0x2000<=a<0x4000 for a in host.writes),'No PPU register writes from the original music paths'
        results.append(dict(id=char['id'],name=char['name'],theme=char['theme'],ticks=2400,APU_writes=writes,trace_sha256=digest.hexdigest(),original_cycles=[min(original_costs),max(original_costs)],relocated_cycles=[min(costs),max(costs)],virtual_ROM_read_range=[min(reads),max(reads)]))
    result=dict(passed=True,source_CPU=True,native=False,installed=False,driver_bytes=len(blob),audio_bank_capacity=8192,static_source_instructions=len(code),indirect_sites=[hex(a)for a in indirect_sites],rows=results,
                ownership='Original0..8 scratch still requires a native save/restore adapter; original audio RAM500..5BF is relocated into donor-ownedC500..C5BF; temporary read byteDFDB must be allocated after the69-byte pose-buffer layout.',
                scope='All six original themes:2400ticks each, exact ordered per-tick APU writes, original channel state and return registers/flags. Static control-flow recovery includes all16 source command handlers. No NMI integration, audible native/music/SFX mixing or playback-deadline claim.',
                bindings={str(p.resolve()):sha(p)for p in[Path(__file__),helper,V.ROM,P/'source-package.json',*[p for p in O.iterdir()if p.is_file()]]})
    save(O/'source-controls.json',result);print(json.dumps({k:v for k,v in result.items()if k not in['bindings','rows']}))


if __name__=='__main__':main()
