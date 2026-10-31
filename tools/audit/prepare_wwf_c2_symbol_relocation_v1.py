"""Isolated genuine WWF state/code relocation, no common-cart resources."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import prepare_wwf_action_source_lab_v2 as S
W=S.W;O=R/'build/wwf-c2-symbol-relocation-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')
BRANCH={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}
PAIR={0x1f:0,0x25:0,0xc3:2,0x21:4,0x23:6}

def main():
    assert not O.exists();O.mkdir();logs=[]
    try:
        prior=R/'docs/qa/checkpoints/2026-10-31/wwf-host-resource-fit-v1/handoff.json';q=json.loads(prior.read_text())
        for p,h in q['bindings'].items():assert sha(p)==h,p
        original=W.W.raw();mem=bytearray(65536);mem[0x8000:]=original[:32768];m=MPU(memory=mem);d=Disassembler(m);chars=W.W.tables(original)
        ins={}
        for seg,lo,hi in S.BLOCKS:
            pc=lo
            while pc<hi:
                n,text=d.instruction_at(pc);mn,mode=m.disassemble[mem[pc]];value=int.from_bytes(mem[pc+1:pc+n],'little')
                target=(pc+2+(value if value<128 else value-256))&65535 if mode=='rel'else None
                ins[pc]=dict(size=n,mn=mn,mode=mode,value=value,text=text,target=target,segment=seg);pc+=n
            assert pc==hi
        # Solve short/long encodings monotonically, then let ca65 validate every branch.
        sizes={pc:(3 if v['mode']in['zpg','zpx','zpy','iny']else v['size'])for pc,v in ins.items()};long=set()
        while True:
            cursor=0xa000;locations={}
            for pc in ins:locations[pc]=cursor;cursor+=sizes[pc]
            new={pc for pc,v in ins.items()if v['mode']=='rel'and not -128<=locations[v['target']]-(locations[pc]+2)<=127}
            if new<=long:break
            long|=new
            for pc in long:sizes[pc]=5
        assert cursor+180+3634<=0xc000,('VM/code/data',hex(cursor+180+3634))
        native_handlers=[mem[0xe6ea+2*i]+256*mem[0xe6eb+2*i]for i in range(90)]
        aliases={pc:[]for pc in ins}
        for name,pc in S.EXPORTS.items():aliases[pc].append(name+'Core'if name in['WfAdoptRequests','WfSelectAction','WfInitDescriptors','WfVmTick']else name)
        for op,pc in enumerate(native_handlers,8):aliases[pc].append(f'WfOpcode{op:02X}')
        def ref(a,control=False):
            if a in ins:return f'WfN_{a:04X}'
            if a in [0xbb28,0xbb29]:return 'WfDescriptorPointers'+(''if a==0xbb28 else'+1')
            if a in [0xe6ea,0xe6eb]:return 'WfOpcodeTable'+(''if a==0xe6ea else'+1')
            if control:assert a in S.CALLBACKS,hex(a);return S.CALLBACKS[a]
            if a<0x2000:return f'WfState+${a&2047:03x}'
            return f'${a:04x}'
        lines=['; Actual original instructions with selected-state symbols; no host lease.\n.setcpu "6502"\n.macpack longbranch\n.import WfState,WfDescriptorPointers\n.import '+','.join(S.CALLBACKS.values())+'\n.import '+','.join(f'WfReadPair{p:02X}'for p in PAIR)+'\n.export WfOpcodeTable\n']
        for seg,lo,hi in S.BLOCKS:
            lines.append('.segment "WF_VM"\n')
            for pc,v in ins.items():
                if not lo<=pc<hi:continue
                for name in aliases[pc]:lines.append(f'.export {name}\n{name}:\n')
                lines.append(f'.export WfN_{pc:04X}\nWfN_{pc:04X}: ; native {pc:04X} {v["text"]}\n.assert *=${locations[pc]:04x},lderror,"Relocation sizing mismatch {pc:04X}"\n')
                mode,mn,a=v['mode'],v['mn'],v['value']
                if mode=='rel':operand=ref(v['target'],True);mn=BRANCH[mn]if pc in long else mn.lower()
                elif mode=='iny':assert mn=='LDA'and a in PAIR;(mn,operand)=('jsr',f'WfReadPair{a:02X}')
                elif mode=='ind':assert mn=='JMP'and a==0x1f;operand='(WfState+$01f)'
                elif mode=='imm':operand=f'#${a:02x}'
                elif mode=='imp':operand=''
                elif mode=='acc':operand='a'
                elif mode in['zpg','zpx','zpy']:operand=ref(a)+dict(zpg='',zpx=',x',zpy=',y')[mode]
                elif mode in['abs','abx','aby']:operand=ref(a,mn in['JSR','JMP'])+dict(abs='',abx=',x',aby=',y')[mode]
                else:raise AssertionError((pc,mode))
                lines.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
        lines.append('.export WfCodeEnd\nWfCodeEnd:\n.segment "WF_TABLE"\nWfOpcodeTable:\n')
        lines.extend(f' .word WfOpcode{op:02X}\n'for op in range(8,0x62))
        (O/'vm.s').write_text(''.join(lines))
        # Exact source data: relocate directory words and descriptor script pointers.
        desc=[]
        for c in chars:desc.append(bytes(mem[c['descriptor']:c['descriptor']+81]))
        ds=['.export WfDescriptorPointers\n.segment "WF_DESCRIPTORS"\nWfDescriptorPointers:\n']
        ds.extend(f' .word WfDescriptor{i}\n'for i in range(6))
        for i,b in enumerate(desc):
            ds.append(f'.export WfDescriptor{i}\nWfDescriptor{i}:\n.byte '+','.join(str(x)for x in b[:21])+'\n')
            ds.append(f'.word WfScript_{int.from_bytes(b[21:23],"little"):04X}\n.byte '+','.join(str(x)for x in b[23:])+'\n')
        ds.append('.segment "WF_SCRIPTS"\n.export WfScriptStart\nWfScriptStart:\n')
        # Six source directory spans end at the authentic first script F140.
        dirs=sorted(c['script_table']for c in chars);dir_end=0xf140;pc=0xf01e
        while pc<0xfe50:
            ds.append(f'.export WfScript_{pc:04X}\nWfScript_{pc:04X}:\n')
            if pc<dir_end:
                target=mem[pc]+256*mem[pc+1]
                ds.append(f'.word {ref(target,True)if target in ins else f"WfScript_{target:04X}"}\n');pc+=2
            else:ds.append(f'.byte {mem[pc]}\n');pc+=1
        (O/'data.s').write_text(''.join(ds))
        hp=['.setcpu "6502"\n.import WfAdoptRequestsCore,WfSelectActionCore,WfInitDescriptorsCore,WfVmTickCore\n.import '+','.join('WfEnv_'+n for n in S.CALLBACKS.values())+'\n']
        hp+=['.segment "WF_STATE"\n.export WfState\nWfState:.res $800\n.segment "WF_PRIVATE"\nWfScopeScratch:.res2\nWfCallbackScratch:.res2\n.segment "WF_HELPERS"\n']
        for p,pair in PAIR.items():
            hp.append(f'.export WfReadPair{p:02X}\nWfReadPair{p:02X}:\n lda WfState+${p:02x}\n sta WfR{pair}\n lda WfState+${p+1:02x}\n sta WfR{pair+1}\n lda (WfR{pair}),y\n rts\n')
        # Scoped API frames: two private bytes per nonreentrant phase, eight real saved scratch bytes.
        def scope(name,target,scratch):
            s=f'.export {name}\n{name}:\n sta {scratch}\n php\n pla\n sta {scratch}+1\n'
            s+=''.join(f' lda WfR{i}\n pha\n'for i in range(8))
            s+=f' lda {scratch}+1\n pha\n lda {scratch}\n plp\n jsr {target}\n sta {scratch}\n php\n pla\n sta {scratch}+1\n'
            s+=''.join(f' pla\n sta WfR{i}\n'for i in reversed(range(8)))
            return s+f' lda {scratch}+1\n pha\n lda {scratch}\n plp\n rts\n'
        for n in ['WfAdoptRequests','WfSelectAction','WfInitDescriptors','WfVmTick']:hp.append(scope(n,n+'Core','WfScopeScratch'))
        for n in S.CALLBACKS.values():hp.append(scope(n,'WfEnv_'+n,'WfCallbackScratch'))
        hp.append('.export WfHelpersEnd\nWfHelpersEnd:\n.assert *<$dfd0,lderror,"Private isolated helper limit"\n')
        (O/'helpers.s').write_text(''.join(hp))
        # Pin the current scoped R0..7 values as imported lab aliases, not allocations.
        dbg=R/'build/bt-ready-menu-1031-v2/joint/candidate.dbg';text=dbg.read_text().splitlines();rp=[]
        for i in range(8):
            values={int(re.search(r'val=(0x[0-9A-Fa-f]+)',l)[1],16)for l in text if l.startswith('sym\t')and f'name="R{i}"'in l and 'val='in l};assert len(values)==1;rp.append(values.pop())
        assert rp==list(range(3,11))
        helper_text=(O/'helpers.s').read_text();(O/'helpers.s').write_text('.importzp '+','.join(f'WfR{i}'for i in range(8))+'\n'+helper_text)
        env=['.setcpu "6502"\n']+['.exportzp '+f'WfR{i}:=${a:02x}\n'for i,a in enumerate(rp)]
        for i,n in enumerate(S.CALLBACKS.values()):env.append(f'.export WfEnv_{n}\nWfEnv_{n}:=${0x7000+i*16:04x}\n.export WfOracle_{n}\nWfOracle_{n}:=${0x7100+i*4:04x}\n')
        (O/'aliases.s').write_text(''.join(env))
        # Real environment stubs deliberately clobber all scratch with STA/STX/STY after oracle execution.
        es=['.setcpu "6502"\n.importzp '+','.join(f'WfR{i}'for i in range(8))+'\n.import '+','.join('WfOracle_'+n for n in S.CALLBACKS.values())+'\n.segment "WF_ENV"\n']
        for i,n in enumerate(S.CALLBACKS.values()):
            es.append(f'.res ${0x7000+i*32:04x}-*,$ea\n.export WfStub_{n}\nWfStub_{n}:\n jsr WfOracle_{n}\n sta WfR0\n stx WfR1\n sty WfR2\n')
            es.extend(f' sta WfR{k}\n'for k in range(3,8));es.append(' rts\n')
        # Env export aliases must point at actual 32-byte stride stub entries.
        alias=(O/'aliases.s').read_text()
        for i,n in enumerate(S.CALLBACKS.values()):alias=alias.replace(f'WfEnv_{n}:=${0x7000+i*16:04x}',f'WfEnv_{n}:=${0x7000+i*32:04x}')
        (O/'aliases.s').write_text(alias);(O/'environment.s').write_text(''.join(es))
        irq=['.setcpu "6502"\n.importzp '+','.join(f'WfR{i}'for i in range(8))+'\n.segment "WF_IRQ"\n.export WfProbeIRQ\nWfProbeIRQ:\n pha\n txa\n pha\n tya\n pha\n']
        irq.extend(f' lda WfR{i}\n pha\n'for i in range(8));irq.append(' lda #$5a\n')
        irq.extend(f' sta WfR{i}\n'for i in range(8));irq.extend(f' pla\n sta WfR{i}\n'for i in reversed(range(8)))
        irq.append(' pla\n tay\n pla\n tax\n pla\n rti\n');(O/'irq.s').write_text(''.join(irq))
        cfg='MEMORY { VM:start=$a000,size=$2000,type=ro,file="'+(O/'vm.bin').as_posix()+'",fill=yes; C2:start=$c000,size=$2000,type=ro,file="'+(O/'c2.bin').as_posix()+'",fill=yes; STATE:start=$c000,size=$800,type=rw,file=""; PRIVATE:start=$dfd0,size=4,type=rw,file=""; ENV:start=$7000,size=$200,type=ro,file="'+(O/'environment.bin').as_posix()+'",fill=yes; IRQ:start=$7800,size=$100,type=ro,file="'+(O/'irq.bin').as_posix()+'",fill=yes;}\nSEGMENTS {WF_VM:load=VM,type=ro; WF_TABLE:load=VM,type=ro; WF_SCRIPTS:load=VM,type=ro; WF_DESCRIPTORS:load=C2,type=ro,start=$c8c0; WF_HELPERS:load=C2,type=ro,start=$d400; WF_STATE:load=STATE,type=bss; WF_PRIVATE:load=PRIVATE,type=bss; WF_ENV:load=ENV,type=ro; WF_IRQ:load=IRQ,type=ro;}\n'
        (O/'private.cfg').write_text(cfg)
        def run(name,cmd):
            guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(name+'.json');save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(name,z.stderr)
        ca=str(R/'tools/Windows/cc65/bin/ca65.exe');ld=str(R/'tools/Windows/cc65/bin/ld65.exe')
        for n in ['vm','data','helpers','aliases','environment','irq']:run(n+'-build',[ca,'-g','-l',str(O/(n+'.lst')),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))])
        run('link',[ld,'-C',str(O/'private.cfg'),'-o',str(O/'lab.out'),'-Ln',str(O/'lab.lbl'),'-m',str(O/'lab.map'),'--dbgfile',str(O/'lab.dbg'),*[str(O/(n+'.o'))for n in ['vm','data','helpers','aliases','environment','irq']]])
        labels={n:int(v,16)for v,n in re.findall(r'al ([A-Fa-f0-9]+) \.(\w+)',(O/'lab.lbl').read_text())}
        assert labels['WfCodeEnd']==cursor
        proof=dict(source=True,isolated_lab=True,no_host_allocation=True,native=False,installed=False,state_base=0xc000,state_bytes=2048,scoped_R0_R7=rp,private_phase_scratch=[0xdfd0,0xdfd4],source_public_stack_extra=10,source_callback_oracle_stack_extra=22,pair_helpers={hex(p):pair for p,pair in PAIR.items()},code_bytes=cursor-0xa000,dispatch_bytes=180,script_bytes=3634,VM_used_bytes=cursor-0xa000+180+3634,descriptor_bytes=498,helper_bytes=labels['WfHelpersEnd']-0xd400,long_branch_sites=sorted(long),instructions=ins,labels=labels,callback_original=S.CALLBACKS,original_descriptors={str(c['id']):c['descriptor']for c in chars},descriptor_script_word_offset=21,native_script_range=[0xf01e,0xfe50],data_word_projection='Descriptor script pointers,145 native directory entries,90 code dispatch words; other data bytes literal original.',limits=['No host mapper,scene,contacts,music or grant.','Native callbacks are explicit dynamic oracle environment boundaries.','Scope helpers are nonreentrant per-phase; interrupts must preserve live scratch and never recursively enter foreground VM.'])
        proof['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(S.__file__),Path(W.__file__),Path(W.W.__file__),W.W.ROM,prior,dbg,*[p for p in O.iterdir()if p.is_file()]]}
        save(O/'build-proof.json',proof);print(json.dumps({k:proof[k]for k in ['code_bytes','dispatch_bytes','script_bytes','VM_used_bytes','descriptor_bytes','helper_bytes','long_branch_sites']}))
    except Exception as e:save(O/'negative.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
