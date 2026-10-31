"""True original CF14 recovery/grapple closure, isolated selected source."""
from pathlib import Path
import json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import wwf_c2_relocation_model_v2 as M
T=M.T;L=R/'build/wwf-selected-contact-v2';H=R/'build/wwf-isolated-host-phase-v4';O=R/'build/wwf-frame-recovery-v1'
CURRENT=R/'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
BRANCH={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}

def main():
    assert not O.exists();O.mkdir();logs=[]
    try:
        parent=R/'docs/qa/checkpoints/2026-10-31/wwf-selected-host-lab-v1/handoff.json'
        for f in [parent,CURRENT]:
            q=json.loads(f.read_text())
            for p,h in q['bindings'].items():assert T.sha(p)==h,p
        raw=T.W.W.raw();mem=bytearray(65536);mem[0x8000:]=raw[:32768];c=MPU(memory=mem);d=Disassembler(c);ins={};pc=0xce2a
        while pc<0xd0b3:
            n,text=d.instruction_at(pc);mn,mode=c.disassemble[mem[pc]];value=int.from_bytes(mem[pc+1:pc+n],'little');target=(pc+2+(value if value<128 else value-256))&65535 if mode=='rel'else None
            ins[pc]=dict(size=n,mn=mn,mode=mode,value=value,text=text,target=target);pc+=n
        assert pc==0xd0b3
        sizes={pc:3 if v['mode']in['zpg','zpx','zpy','iny']else v['size']for pc,v in ins.items()};long=set()
        while True:
            cursor=0xcc00;locations={}
            for pc in ins:locations[pc]=cursor;cursor+=sizes[pc]
            new={pc for pc,v in ins.items()if v['mode']=='rel'and v['target']in ins and not -128<=locations[v['target']]-(locations[pc]+2)<=127}
            if new<=long:break
            long|=new
            for pc in long:sizes[pc]=5
        outside={0xce17:'WfEnv_WfCbRandom',0xd0b3:'WfContactN_D0B3',0xcdd4:'WfContactN_CDD4',0xa243:'WfCbAudio12'}
        lines=['.setcpu "6502"\n.macpack longbranch\n.import WfState,WfHostContext,WfReadPair1F,WfContactCmpPair1F\n.import '+','.join(outside.values())+'\n.importzp '+','.join(f'WfR{i}'for i in range(8))+'\n.segment "WF_FRAME_RECOVERY"\n']
        for pc,v in ins.items():
            if pc==0xcf14:lines.append('.export WfFrameRecoveryCore\nWfFrameRecoveryCore:\n')
            lines.append(f'.export WfRecoveryN_{pc:04X}\nWfRecoveryN_{pc:04X}: ; native {v["text"]}\n.assert *=${locations[pc]:04x},lderror,"Recovery layout"\n')
            mode,mn,a=v['mode'],v['mn'],v['value']
            def ref(target):
                if target in ins:return f'WfRecoveryN_{target:04X}'
                assert target in outside,hex(target);return outside[target]
            if mode=='rel':operand=ref(v['target']);mn=BRANCH[mn]if pc in long else mn.lower()
            elif mode=='iny':
                assert a==0x1f and mn in ['LDA','CMP'];mn,operand='jsr','WfReadPair1F'if mn=='LDA'else'WfContactCmpPair1F'
            elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
                if mn in ['JMP','JSR']:operand=ref(a)
                elif a<0x2000:operand=f'WfState+${a&2047:03x}'
                else:raise AssertionError((pc,v))
                operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
            elif mode=='imm':operand=f'#${a:02x}'
            elif mode=='imp':operand=''
            elif mode=='acc':operand='a'
            else:raise AssertionError((pc,mode))
            lines.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
        # Direct API tests use the same eight-byte scope as the foreground.
        # HostFrame calls Core, avoiding recursive use of its own context.
        lines.append('.export WfFrameRecovery\nWfFrameRecovery:\n sta WfHostContext+12\n php\n pla\n sta WfHostContext+13\n')
        lines+=[''.join(f' lda WfR{i}\n pha\n'for i in range(8))]
        lines+=[' lda WfHostContext+13\n pha\n lda WfHostContext+12\n plp\n jsr WfFrameRecoveryCore\n sta WfHostContext+12\n php\n pla\n sta WfHostContext+13\n']
        lines+=[''.join(f' pla\n sta WfR{i}\n'for i in reversed(range(8)))]
        lines+=[' lda WfHostContext+13\n pha\n lda WfHostContext+12\n plp\n rts\n.export WfFrameRecoveryEnd\nWfFrameRecoveryEnd:\n.assert *<=$d400,lderror,"Lab recovery limit"\n']
        (O/'recovery.s').write_text(''.join(lines))
        (O/'contact.s').write_text((L/'contact.s').read_text()+'\n.export WfContactCmpPair1F\n')
        host=(H/'host.s').read_text().replace('.import WfState,','.import WfFrameRecoveryCore,WfState,').replace('WfHostFrameAdvance:\n','WfHostFrameAdvance:\n jsr WfFrameRecoveryCore\n')
        (O/'host.s').write_text(host)
        cfg=(L/'private.cfg').read_text().replace(L.as_posix(),O.as_posix()).replace('WF_DESCRIPTORS:load=C2,type=ro,start=$c8c0;','WF_DESCRIPTORS:load=C2,type=ro,start=$c8c0; WF_FRAME_RECOVERY:load=C2,type=ro,start=$cc00;')
        (O/'private.cfg').write_text(cfg)
        def run(name,cmd):
            guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(name+'.json');T.save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(name,z.stderr)
        ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
        for name in ['contact','host','recovery']:run(name+'-build',[str(ca),'-g',str(O/(name+'.s')),'-o',str(O/(name+'.o')),'-l',str(O/(name+'.lst')),'--create-dep',str(O/(name+'.dep'))])
        objects=[M.L/(n+'.o')for n in ['vm','data','helpers','environment','irq']]+[L/'aliases.o']+[O/(n+'.o')for n in ['contact','host','recovery']]
        run('link',[str(ld),'-C',str(O/'private.cfg'),'-o',str(O/'lab.out'),'-Ln',str(O/'lab.lbl'),'-m',str(O/'lab.map'),'--dbgfile',str(O/'lab.dbg'),*map(str,objects)])
        labels={m[2]:int(m[1],16)for line in(O/'lab.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
        assert(O/'vm.bin').read_bytes()==(M.L/'vm.bin').read_bytes()
        result=dict(source=True,isolated_lab=True,no_host_allocation=True,native_host=False,labels=labels,instructions=ins,host_candidate=json.loads(CURRENT.read_text())['candidate'],host_handoff=T.sha(CURRENT),footprint=dict(original_CF14_closure_bytes=649,relocated_CF14_closure_bytes=cursor-0xcc00,public_scope_bytes=84,total_selected_recovery_bytes=labels['WfFrameRecoveryEnd']-0xcc00,range=[0xcc00,labels['WfFrameRecoveryEnd']],new_state_bytes=0,new_ZP_bytes=0,long_branches=sorted(long)),semantics='Genuine CE2A..D0B2, nativeCF14 entry. Existing selected contact descriptor helper/CDD4/RNG and original sound callback remain genuine imports. Original seemingly odd D00E LDA#35 before LDA(pointer),Y is retained unchanged.',phase_order='Actor0 source update, then originalCF14 recovery/grapple once on every unpaused accepted frame, then phase71 increment; matches AE26..AE29.')
        result['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),parent,CURRENT,L/'build-proof.json',*objects,O/'recovery.s',O/'contact.s',O/'host.s',O/'private.cfg',O/'vm.bin',O/'c2.bin',O/'lab.dbg',O/'lab.lbl',*logs]}
        T.save(O/'build-proof.json',result);print(json.dumps(dict(passed=True,footprint=result['footprint'],proof=T.sha(O/'build-proof.json'))))
    except Exception as e:T.save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
