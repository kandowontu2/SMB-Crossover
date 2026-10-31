"""Private lab cold/phase adapter around the frozen symbolic WWF VM.

No host ROM resources or callbacks are installed. The original cold producer is
assembled as source, rather than using a snapshot as the constructor.
"""
from pathlib import Path
import json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import wwf_c2_relocation_model_v2 as M
T=M.T;L=M.L;O=R/'build/wwf-isolated-host-phase-v3'

def main():
    assert not O.exists();O.mkdir();logs=[]
    try:
        h=R/'docs/qa/checkpoints/2026-10-31/wwf-c2-source-component-v1/handoff.json';q=json.loads(h.read_text())
        for p,v in q['bindings'].items():assert T.sha(p)==v,p
        raw=T.W.W.raw();mem=bytearray(65536);mem[0x8000:]=raw[:32768];cpu=MPU(memory=mem);dis=Disassembler(cpu)
        blocks=[(0x8044,0x80de),(0xc8e2,0xc91d)];instructions={}
        for lo,hi in blocks:
            pc=lo
            while pc<hi:
                n,text=dis.instruction_at(pc);mn,mode=cpu.disassemble[mem[pc]];v=int.from_bytes(mem[pc+1:pc+n],'little')
                instructions[pc]=dict(size=n,mn=mn,mode=mode,value=v,text=text);pc+=n
            assert pc==hi
        lines=['.setcpu "6502"\n.macpack longbranch\n.import WfState,WfInitDescriptors,WfSelectActionCore,WfAdoptRequestsCore,WfVmTickCore,WfCbRandom\n.importzp '+','.join('WfR'+str(i)for i in range(8))+'\n.segment "WF_HOST_CONTEXT"\n.export WfHostContext\nWfHostContext:.res 16\n.segment "WF_HOST_CODE"\n']
        # Same scoped public ABI as the VM; distinct private phase context.
        def scope(name,target):
            s=f'.export {name}\n{name}:\n sta WfHostContext+12\n php\n pla\n sta WfHostContext+13\n'
            s+=''.join(f' lda WfR{i}\n pha\n'for i in range(8))
            s+=' lda WfHostContext+13\n pha\n lda WfHostContext+12\n plp\n'
            s+=f' jsr {target}\n sta WfHostContext+12\n php\n pla\n sta WfHostContext+13\n'
            s+=''.join(f' pla\n sta WfR{i}\n'for i in reversed(range(8)))
            return s+' lda WfHostContext+13\n pha\n lda WfHostContext+12\n plp\n rts\n'
        lines+=[scope('WfHostCold','WfHostColdCore'),scope('WfHostFrame','WfHostFrameCore')]
        lines+=['''; A=actor0 identity, X=actor1 identity, Y=host seed; all IDs0..5.
WfHostColdCore:
 cmp #6
 jcs WfHostColdBad
 cpx #6
 jcs WfHostColdBad
 sta WfHostContext
 stx WfHostContext+1
 sty WfHostContext+2
 ldx #0
 lda #0
WfClear:
''']
        lines+=[''.join(f' sta WfState+${page:03x},x\n'for page in range(0,0x800,0x100))]
        lines+=[''' inx
 bne WfClear
 lda WfHostContext
 sta WfState+$2b
 lda WfHostContext+1
 sta WfState+$2a
 lda WfHostContext+2
 sta WfState+$82
 lda #1
 sta WfState+$100
 lda #$ff
 sta WfState+$12b
 jsr WfInitDescriptors
 .export WfHostNativeCold
WfHostNativeCold:
''']
        # All actual native match-state producer operands are source symbols.
        # Its final JMP C8E2 targets the genuinely compiled OAM/HUD producer.
        for pc,v in instructions.items():
            lines.append(f'.export WfColdN_{pc:04X}\nWfColdN_{pc:04X}: ; original {v["text"]}\n')
            mn,mode,a=v['mn'].lower(),v['mode'],v['value']
            if mode=='rel':
                target=(pc+2+(a if a<128 else a-256))&65535;assert target in instructions;operand=f'WfColdN_{target:04X}'
            elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
                if mn in ['jmp','jsr']:
                    assert a in instructions or a==0xce17;operand='WfCbRandom'if a==0xce17 else f'WfColdN_{a:04X}'
                elif a<0x2000:operand=f'WfState+${a&2047:03x}'
                elif 0xca55<=a<0xcab1:operand=f'WfColdData+${a-0xca55:02x}'
                else:raise AssertionError(('Cold unclassified operand',hex(pc),hex(a)))
                operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
            elif mode=='imm':operand=f'#${a:02x}'
            elif mode=='imp':operand=''
            elif mode=='acc':operand='a'
            else:raise AssertionError((pc,mode))
            lines.append(' '+mn+(' '+operand if operand else'')+'\n')
        lines+=['''WfHostColdBad:
 clc
 rts
; One accepted original video frame, A=held, X=fresh, Y=pause.
; Only actor0 is driven. Opponent callbacks remain explicit lab boundaries.
WfHostFrameCore:
 sta WfHostContext+3
 stx WfHostContext+4
 cpy #0
 bne WfHostFrameVideoEnd
 sta WfState+$0d
 stx WfState+$0e
 ldx #0
 ldy #0
 jsr WfSelectActionCore
 jsr WfAdoptRequestsCore
 lda WfState+$71
 and #1
 bne WfHostFrameAdvance
 jsr WfVmTickCore
WfHostFrameAdvance:
 inc WfState+$71
 lda WfState+$71
 cmp #6
 bcc WfHostFrameVideoEnd
 lda #0
 sta WfState+$71
WfHostFrameVideoEnd:
 inc WfState+$8d
 rts
.export WfHostCodeEnd
WfHostCodeEnd:
.assert *<=$dfd0,lderror,"Isolated host code collides with frozen phase context"
WfColdData:
''']
        lines+=['.byte '+','.join(str(v)for v in mem[0xca55:0xcab1])+'\n.export WfHostDataEnd\nWfHostDataEnd:\n.assert *<=$dfd0,lderror,"Isolated host data limit"\n']
        (O/'host.s').write_text(''.join(lines))
        cfg=(L/'private.cfg').read_text().replace(L.as_posix(),O.as_posix())
        cfg=cfg.replace('MEMORY {','MEMORY { HOSTCTX:start=$c800,size=$10,type=rw,file="";')
        cfg=cfg.replace('SEGMENTS {','SEGMENTS { WF_HOST_CONTEXT:load=HOSTCTX,type=bss;')
        cfg=cfg.replace('WF_HELPERS:load=C2,type=ro,start=$d400;','WF_HELPERS:load=C2,type=ro,start=$d400; WF_HOST_CODE:load=C2,type=ro,start=$d900;')
        (O/'private.cfg').write_text(cfg)
        def run(name,cmd):
            guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(name+'.json');T.save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(name,z.stderr)
        ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
        run('host-build',[str(ca),'-g',str(O/'host.s'),'-o',str(O/'host.o'),'-l',str(O/'host.lst'),'--create-dep',str(O/'host.dep')])
        objects=[L/(name+'.o')for name in ['vm','data','helpers','aliases','environment','irq']]+[O/'host.o']
        run('link',[str(ld),'-C',str(O/'private.cfg'),'-o',str(O/'lab.out'),'-Ln',str(O/'lab.lbl'),'-m',str(O/'lab.map'),'--dbgfile',str(O/'lab.dbg'),*map(str,objects)])
        labels={}
        for line in (O/'lab.lbl').read_text().splitlines():
            m=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
            if m:labels[m[2]]=int(m[1],16)
        assert (O/'vm.bin').read_bytes()==(L/'vm.bin').read_bytes()
        for n,v in M.P['labels'].items():assert labels[n]==v,n
        old=(L/'c2.bin').read_bytes();new=(O/'c2.bin').read_bytes();end=labels['WfHostDataEnd'];assert all(a==b or 0xd900<=0xc000+i<end for i,(a,b)in enumerate(zip(old,new)))
        footprint=dict(host_code=labels['WfHostCodeEnd']-0xd900,host_constant_data=92,host_total=end-0xd900,host_context=16,range=[0xd900,end],original_native_cold_instruction_count=len(instructions))
        proof=dict(source=True,isolated_lab=True,no_host_allocation=True,native_host=False,installed=False,parent_component=T.sha(h),labels=labels,footprint=footprint,instructions=instructions,limits=['This is an isolated accepted-video-frame API, not a physical hostNMI/lag mailbox implementation.','Original ring/contact/audio callbacks are still dynamic donor oracles. Host terrain/contact bodies are not installed.','Cold starts from cleared selected state and executes original descriptor+match producer; it no longer imports the initialized native snapshot.','The explicit single-hero phase adapter suppresses passive actor1 VM updates; it does not claim original full two-wrestler game behavior.'])
        proof['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),h,L/'build-proof.json',*objects,O/'host.s',O/'private.cfg',O/'lab.lbl',O/'lab.dbg',O/'vm.bin',O/'c2.bin',*logs]}
        T.save(O/'build-proof.json',proof);print(json.dumps(dict(passed=True,footprint=footprint,proof=T.sha(O/'build-proof.json'))))
    except Exception as e:T.save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
