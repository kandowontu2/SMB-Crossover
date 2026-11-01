"""Move the real driver's scratch into its owned RAM bank and reprove all themes."""
from pathlib import Path
import hashlib,json,re,struct,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import port_wwf_audio_source_bounded_v1 as V
from private_build_outputs_v1 import validate
P=R/'build/wwf-audio-source-1101-v1';O=R/'build/wwf-audio-private-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')


class HostBus(V.V.Bus):
    def __init__(self,code,scratch):
        super().__init__(bytes(32768));self.m[0xa000:0xa000+len(code)]=code;self.scratch=scratch
        self.m[3:5]=[165,90]
    def __setitem__(self,a,v):
        assert isinstance(a,int)and(a<0x8000 or 0xc500<=a<0xc5c0 or self.scratch<=a<self.scratch+10),('Private audio ownership',hex(a))
        self.writes.add(a);self.m[a]=v
        if 0x4000<=a<=0x4017:self.apu.append((a,v))


def main():
    assert not(O/'source-controls.json').exists();O.mkdir(exist_ok=True)
    q=json.loads((P/'source-controls.json').read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    old=R/'tools/reference/wwf_audio_virtual_read_v1.s';helper=R/'tools/reference/wwf_audio_virtual_read_v2.s'
    text=(P/'audio.s').read_text();assert text.count(old.read_text())==1
    text=text.replace(old.read_text(),helper.read_text(),1)
    text=text.replace('WfAudioReadByte=$dfdb','R0=$03\nR1=$04\n.macpack longbranch',1)
    raw=V.V.raw();bank=raw[65536:98304];decoder=V.MPU();lines=[];converted=0
    for line in text.splitlines():
        match=re.search(r'; original([0-9A-F]{4})$',line)
        if match:
            pc=int(match[1],16);op=bank[pc-0x8000];name,mode=decoder.disassemble[op]
            value=bank[pc+1-0x8000]
            if mode in['zpg','zpx','zpy','inx']:
                assert value<=8,(hex(pc),value)
                assert mode!='inx','No unhandled indexed source stream pointer'
                line=' '+name.lower()+' WfAudioScratch+$%x'%value+(',x'if mode=='zpx'else',y'if mode=='zpy'else'')+' ; original%04X'%pc;converted+=1
            elif mode=='ind':
                assert value==7;line=' jmp (WfAudioScratch+7) ; original%04X'%pc
        lines.append(line)
    lines+=['WfAudioScratch:','.export WfAudioScratch',' .res 10,0']
    (O/'audio.cfg').write_text((P/'audio.cfg').read_text())
    attempts=[]
    for attempt in range(8):
        (O/'audio.s').write_text('\n'.join(lines)+'\n')
        cmd=list(map(str,[R/'tools/Windows/cc65/bin/ca65.exe',O/'audio.s','-o',O/'audio.o','-l',O/'audio.lst']))
        guard=validate(cmd,O,cwd=R);result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        attempts.append(dict(returncode=result.returncode,stderr=result.stderr))
        save(O/'assemble.json',dict(command=cmd,guard=guard,attempts=attempts))
        if result.returncode==0:break
        failing=[int(n)-1 for n in re.findall(r'audio\.s:(\d+): Error: Range error',result.stderr)]
        assert failing,result.stderr
        for i in failing:
            match=re.match(r' (b(?:cc|cs|eq|mi|ne|pl|vc|vs)) (.*)',lines[i]);assert match,lines[i]
            lines[i]=' j'+match[1][1:]+' '+match[2].replace('+$0','')
    else:raise AssertionError('Bounded audio branch repair attempts')
    cmd=list(map(str,[R/'tools/Windows/cc65/bin/ld65.exe','-C',O/'audio.cfg',O/'audio.o','-o',O/'audio.bin','-Ln',O/'audio.lbl']))
    guard=validate(cmd,O,cwd=R);result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    save(O/'link.json',dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    blob=(O/'audio.bin').read_bytes();assert len(blob)<=8192
    labels={name:int(value,16)for value,name in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'audio.lbl').read_text())}
    scratch=labels['WfAudioScratch'];rows=[]
    assert scratch&255<=246,'The indirect command pointer must not straddle a6502 page'
    for char in V.V.tables(raw):
        src=V.V.Bus(bank);host=HostBus(blob,scratch)
        for entry in[0xe22e,0xe249]:
            if entry==0xe249:src.m[1]=host.m[scratch+1]=char['theme']
            src.apu=[];host.apu=[];V.invoke(src,entry,original=True);V.invoke(host,labels['WfAudio_%04X'%entry]);assert src.apu==host.apu
            assert src.m[0x500:0x5c0]==host.m[0xc500:0xc5c0]and host.m[3:5]==[165,90]
        costs=[];old_costs=[];writes=0;digest=hashlib.sha256()
        for frame in range(2400):
            src.apu=[];host.apu=[];a,_=V.invoke(src,0xe4de,original=True);z,_=V.invoke(host,labels['WfAudio_E4DE'])
            assert src.apu==host.apu,('APU',char['name'],frame)
            assert src.m[0x500:0x5c0]==host.m[0xc500:0xc5c0],('Channel state',char['name'],frame)
            assert src.m[:7]==host.m[scratch:scratch+7],('Private scratch',char['name'],frame)
            assert host.m[3:5]==[165,90],('Borrowed host pointer',char['name'],frame)
            assert(a.a,a.x,a.y,a.p)==(z.a,z.x,z.y,z.p),('Return registers',char['name'],frame)
            costs.append(z.processorCycles);old_costs.append(a.processorCycles);writes+=len(host.apu)
            for reg,value in host.apu:digest.update(struct.pack('<IHB',frame,reg,value))
        assert not any(0x2000<=a<0x4000 for a in host.writes)
        rows.append(dict(id=char['id'],name=char['name'],theme=char['theme'],ticks=2400,APU_writes=writes,APU_trace_sha256=digest.hexdigest(),original_cycles=[min(old_costs),max(old_costs)],private_cycles=[min(costs),max(costs)]))
    report=dict(passed=True,source_CPU=True,native=False,installed=False,driver_and_scratch_bytes=len(blob),capacity=8192,spare_bytes=8192-len(blob),private_scratch_address=scratch,private_scratch_bytes=10,source_ZP_instructions_rebased=converted,branch_repairs=len(attempts)-1,rows=rows,
                scope='All six original themes,2400ticks each. Exact ordered APU writes, channel state, private scratch0..6 and returnAXYP; nativeR0/R1 restored after every read. No extra C2 read temporary or host0..2 scratch. No native NMI/track playback/mixed-SFX qualification yet.',
                bindings={str(p.resolve()):sha(p)for p in[Path(__file__),helper,old,P/'audio.s',P/'source-controls.json',*[p for p in O.iterdir()if p.is_file()]]})
    save(O/'source-controls.json',report);print(json.dumps({k:v for k,v in report.items()if k not in['bindings','rows']}))


if __name__=='__main__':main()
