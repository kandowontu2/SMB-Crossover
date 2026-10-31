"""Compile real donor contact/depth/RNG into selected C2 lab source."""
from pathlib import Path
import json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import wwf_c2_relocation_model_v2 as M
T=M.T;L=R/'build/wwf-isolated-host-phase-v4';O=R/'build/wwf-selected-contact-v2'
BRANCH={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}

def main():
    assert not O.exists();O.mkdir();logs=[]
    try:
        parent=json.loads((L/'build-proof.json').read_text())
        for p,h in parent['bindings'].items():assert T.sha(p)==h,p
        raw=T.W.W.raw();mem=bytearray(65536);mem[0x8000:]=raw[:32768];c=MPU(memory=mem);d=Disassembler(c)
        instructions={}
        for lo,hi in [(0xcd02,0xce2a),(0xd0b3,0xd0c0)]:
            pc=lo
            while pc<hi:
                n,text=d.instruction_at(pc);mn,mode=c.disassemble[mem[pc]];v=int.from_bytes(mem[pc+1:pc+n],'little');target=(pc+2+(v if v<128 else v-256))&65535 if mode=='rel'else None
                instructions[pc]=dict(size=n,mn=mn,mode=mode,value=v,text=text,target=target);pc+=n
            assert pc==hi
        sizes={pc:(3 if v['mode']in['zpg','zpx','zpy','iny']else v['size'])for pc,v in instructions.items()};long=set()
        while True:
            cursor=0xdc00;locations={}
            for pc in instructions:locations[pc]=cursor;cursor+=sizes[pc]
            new={pc for pc,v in instructions.items()if v['mode']=='rel'and not -128<=locations[v['target']]-(locations[pc]+2)<=127}
            if new<=long:break
            long|=new
            for pc in long:sizes[pc]=5
        assert cursor<0xdfd0
        exports={0xcd02:'WfEnv_WfCbActorDepthProbe',0xcd25:'WfEnv_WfCbActorContact',0xce17:'WfEnv_WfCbRandom'}
        lines=['.setcpu "6502"\n.macpack longbranch\n.import WfState,WfDescriptorPointers,WfReadPair1F,WfCbAudio12\n.segment "WF_SELECTED_CONTACT"\n']
        for pc,v in instructions.items():
            if pc in exports:lines.append(f'.export {exports[pc]}\n{exports[pc]}:\n')
            lines.append(f'.export WfContactN_{pc:04X}\nWfContactN_{pc:04X}: ; native {v["text"]}\n.assert *=${locations[pc]:04x},lderror,"Contact instruction layout"\n')
            mn,mode,a=v['mn'],v['mode'],v['value']
            if mode=='rel':operand=f'WfContactN_{v["target"]:04X}';mn=BRANCH[mn]if pc in long else mn.lower()
            elif mode=='iny':assert mn in ['LDA','CMP']and a==0x1f
            if mode=='iny':
                # Original CMP(pointer),Y must keep A. Its read helper phase is
                # factored to a true compiled CMP helper below, not LDA output.
                mn,operand=('jsr','WfReadPair1F'if v['mn']=='LDA'else'WfContactCmpPair1F')
            elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
                if mn in ['JSR','JMP']:
                    assert a in instructions or a==0xa243;operand='WfCbAudio12'if a==0xa243 else f'WfContactN_{a:04X}'
                elif a<0x2000:operand=f'WfState+${a&2047:03x}'
                elif a in [0xbb28,0xbb29]:operand='WfDescriptorPointers'+(''if a==0xbb28 else'+1')
                else:raise AssertionError((pc,a))
                operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
            elif mode=='imm':operand=f'#${a:02x}'
            elif mode=='imp':operand=''
            elif mode=='acc':operand='a'
            elif mode!='rel':raise AssertionError((pc,mode))
            lines.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
        lines+=['''.importzp WfR0,WfR1
WfContactCmpPair1F:
 pha
 lda WfState+$1f
 sta WfR0
 lda WfState+$20
 sta WfR1
 pla
 cmp (WfR0),y
 rts
.export WfContactEnd
WfContactEnd:
.assert *<=$dfd0,lderror,"Selected contact code limit"
''']
        (O/'contact.s').write_text(''.join(lines))
        aliases=(M.L/'aliases.s').read_text()
        for name in exports.values():aliases=re.sub(r'\.export '+re.escape(name)+r'\n'+re.escape(name)+r':=\$[0-9a-f]+\n','',aliases)
        (O/'aliases.s').write_text(aliases)
        cfg=(L/'private.cfg').read_text().replace(L.as_posix(),O.as_posix())
        cfg=cfg.replace('WF_HOST_CODE:load=C2,type=ro,start=$d900;','WF_HOST_CODE:load=C2,type=ro,start=$d900; WF_SELECTED_CONTACT:load=C2,type=ro,start=$dc00;')
        (O/'private.cfg').write_text(cfg)
        def run(name,cmd):
            guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);p=O/(name+'.json');T.save(p,dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p);assert z.returncode==0,(name,z.stderr)
        ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
        for name in ['contact','aliases']:run(name+'-build',[str(ca),'-g',str(O/(name+'.s')),'-o',str(O/(name+'.o')),'-l',str(O/(name+'.lst')),'--create-dep',str(O/(name+'.dep'))])
        objects=[M.L/(name+'.o')for name in ['vm','data','helpers','environment','irq']]+[L/'host.o',O/'aliases.o',O/'contact.o']
        run('link',[str(ld),'-C',str(O/'private.cfg'),'-o',str(O/'lab.out'),'-Ln',str(O/'lab.lbl'),'-m',str(O/'lab.map'),'--dbgfile',str(O/'lab.dbg'),*map(str,objects)])
        labels={m[2]:int(m[1],16)for line in(O/'lab.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
        assert(O/'vm.bin').read_bytes()==(M.L/'vm.bin').read_bytes()
        footprint=dict(original_instruction_bytes=309,selected_code_bytes=labels['WfContactEnd']-0xdc00,range=[0xdc00,labels['WfContactEnd']],extra_C2_state=0,new_ZP=0,long_branches=sorted(long))
        proof=dict(source=True,isolated_lab=True,native_host=False,no_host_allocation=True,labels=labels,instructions=instructions,footprint=footprint,source_environment_replacements=exports,remaining_oracle_callbacks=['AI','RingClamp','RingBounds','Audio09','Audio0F','Audio12'],limits=['Original contact still models another wrestler; native SMB enemy marshaling/terrain callbacks are not implemented.','Three genuine source callback bodies now execute selected code, with existing public scoped wrappers. No prerecorded contact outcomes are used.'])
        proof['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),L/'build-proof.json',*objects,O/'contact.s',O/'aliases.s',O/'private.cfg',O/'lab.lbl',O/'lab.dbg',O/'vm.bin',O/'c2.bin',*logs]}
        T.save(O/'build-proof.json',proof);print(json.dumps(dict(passed=True,footprint=footprint,proof=T.sha(O/'build-proof.json'))))
    except Exception as e:T.save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
