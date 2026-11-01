"""Real FF27/owned object callback composition, no native ROM/shared edits."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
from py65.disassembler import Disassembler
from private_build_outputs_v1 import validate
OUT=ROOT/'build/metal-storm-objects-host-1101-v6'
V5=ROOT/'build/metal-storm-terrain-host-1101-v5'
ACTOR=ROOT/'build/metal-storm-component-1101-v2/source/portable-actor.inc'
REF=ROOT/'tools/reference/metal_storm_objects_host_1101_v6.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[(0x8bcf,0x8bf9),(0xd783,0xd7af),(0xda8f,0xdb1b),(0xdb9b,0xdba0),(0xdcae,0xdcf7),(0xdd06,0xdd0c),(0xdd48,0xde10),(0xde91,0xdea2),(0xdf33,0xdff3),(0xe04c,0xe05e),(0xe1ed,0xe2c4),(0xe32b,0xe32f),(0xfc5e,0xfc8e)]
DATA=[(0xdb1b,0xdb9b),(0xdff3,0xe003),(0xe1dd,0xe1ed)]
inside=lambda a:any(lo<=a<hi for lo,hi in SPANS)
ALIASES={0xab53:'Ms_AB53',0xe2c4:'MsNativeFF33',0xe2e7:'MsNativeFF36',0xda71:'MsNativeFF3F',0xeb22:'MsNativeShotTileQuery',0xe32a:'Ms_E32A',0xdbc6:'MsObjReturn',0xde90:'MsObjReturn',0xfc8e:'MsObjReturn',0x8bf9:'MsObjectUnsupported',0xff6f:'MsObjectUnsupported',0xdd0c:'MsObjectUnsupported',0xde10:'MsObjectUnsupported',0xdea2:'MsObjectUnsupported',0xe05e:'MsObjectUnsupported'}

def donor_source():
    c=M.machine();c.memory.regs[6:8]=[0,1];c.memory.map();d=Disassembler(c);result=[];code={}
    for lo,hi in SPANS:
        p=lo
        while p<hi:
            n,t=d.instruction_at(p);mn,mode=c.disassemble[c.memory[p]];assert t!='???'
            a=c.memory[p+1]+(256*c.memory[p+2]if n==3 else 0)if n>1 else None
            code[p]=dict(size=n,text=t,bytes=list(c.memory[p:p+n]),mnemonic=mn,mode=mode,operand=a)
            if mode=='rel':
                target=(p+2+(a if a<128 else a-256))&65535
                name=f'MsObj_{target:04X}'if inside(target)else ALIASES.get(target);assert name,(hex(p),hex(target))
                t='j'+mn.lower()[1:]+' '+name
            elif mode in['abs','abx','aby','zpg','zpx','zpy','inx','iny','ind']:
                if mn in['JSR','JMP']:
                    target=f'MsObj_{a:04X}'if inside(a)else ALIASES.get(a);assert target,(hex(p),hex(a))
                elif a in[0x8000,0x8001]:target='MsDonorMapperSelect'if a==0x8000 else'MsDonorMapperData'
                elif a in[0x6e,0x6f]:target='MsPointer'+(''if a==0x6e else'+1')
                elif any(lo<=a<hi for lo,hi in DATA):target=f'MsObj_{a:04X}'
                else:
                    assert a<0x800,(hex(p),t);target=f'MsState+${a:04x}'
                old=re.search(r'\$[0-9a-fA-F]+',t);assert old;t=t[:old.start()]+target+t[old.end():]
            result.append(f'MsObj_{p:04X}: {t} ; original ${p:04x}');p+=n
        assert p==hi
        if hi in[0xdba0,0xe32f]:result.append(' jmp MsObjectUnsupported ; ineligible source object path')
        if hi==0xfc8e:result.append(' rts ; pure reset control-option leaf boundary')
    for lo,hi in DATA:
        for a in range(lo,hi):result.append(f'MsObj_{a:04X}: .byte ${c.memory[a]:02x}')
    c.memory.regs[6:8]=[12,13];c.memory.map()
    table=c.memory[0x800e]+256*c.memory[0x800f];meta=c.memory[table]+256*c.memory[table+1]
    masks=list(c.memory[meta+5:meta+13]);assert len(masks)==8
    result+=['MsObjReturn:rts','MsActorAnimationMasks:.byte '+','.join(f'${v:02x}'for v in masks),'.export MsObj_DCAE,MsObj_8BCF,MsObj_DD48,MsObj_DA8F,MsObj_D783']
    return '\n'.join(result)+'\n',code

def labels():
    r={}
    for line in(OUT/'objects.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:r[m[2]]=int(m[1],16)
    return r

def main():
    OUT.mkdir(exist_ok=True);v5=json.loads((V5/'source-stage.json').read_text());assert v5['passed']
    assert sha(V5/'source-proof.zip')==v5['archive_sha256']
    donor,code=donor_source();(OUT/'object-leaves.inc').write_text(donor)
    actor=ACTOR.read_text();(OUT/'actor-relaxed.inc').write_text(actor)
    wrapper=(V5/'terrain.s').read_text().replace('.include "portable-actor.inc"','.include "actor-relaxed.inc"')
    terrain=(ROOT/'tools/reference/metal_storm_terrain_host_1101_v5.inc').read_text()
    assert terrain.count(' jsr MsCtor_943C\n')==1
    terrain=terrain.replace(' jsr MsCtor_943C\n',' jsr MsCtor_943C\n jsr MsObj_FC5E ; original reset validates gravity-control pair119/11A\n jsr MsNativeAnimationMask ; initial original renderer pose metadata\n')
    (OUT/'terrain-adapter.inc').write_text(terrain)
    wrapper=wrapper.replace('.include "metal_storm_terrain_host_1101_v5.inc"','.include "terrain-adapter.inc"')
    for name,target in[('FF27','MsObj_DCAE'),('8BCF','MsObj_8BCF')]:
        old='.import MsExternal_'+name;assert wrapper.count(old)==1;wrapper=wrapper.replace(old,'MsExternal_'+name+'='+target)
    # Refuse unsupported donor enemy/meta forms BEFORE any source actor update.
    before=' lda GameEngineSubroutine\n cmp #8\n bne Rejected\n'
    host=(ROOT/'tools/reference/metal_storm_host_contract_1101_v4.inc').read_text();assert host.count(before)==1
    host=host.replace(before,before+' jsr MsNativeObjectsReady\n bcc Rejected\n')
    assert host.count(' jsr MsFrame\n')==1;host=host.replace(' jsr MsFrame\n',' jsr MsFrame\n jsr MsNativeAnimationMask ; source renderer mask follows actor, before input\n')
    (OUT/'host-step.inc').write_text(host)
    wrapper=wrapper.replace('.include "metal_storm_host_contract_1101_v4.inc"','.include "host-step.inc"')
    wrapper+='\n.include "object-leaves.inc"\n.include "metal_storm_objects_host_1101_v6.inc"\n'
    (OUT/'objects.s').write_text(wrapper)
    symbols=(V5/'symbols.s').read_text()
    for name in['FF27','8BCF']:symbols=re.sub(r'^\.export MsExternal_'+name+r'=\$[0-9a-f]+\n','',symbols,flags=re.M)
    symbols+='.export MsObjectUnsupported=$5020\n';(OUT/'symbols.s').write_text(symbols)
    # Initial non-executed link may be larger than a capsule. Relaxation only
    # shortens genuine branch encodings; final executed size MUST fitBFE0.
    (OUT/'objects.cfg').write_text('MEMORY{CODE:start=$a000,size=$3fe0,file=%O;}SEGMENTS{CODE:load=CODE,type=ro;}\n')
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    def compile():
        for cmd in[[cc/'ca65.exe','-g','-I',OUT,'-I',V5,'-I',ROOT/'tools/reference','-I',ROOT/'build/metal-storm-component-1101-v2/source',OUT/'objects.s','-o',OUT/'objects.o'],[cc/'ca65.exe',OUT/'symbols.s','-o',OUT/'symbols.o'],[cc/'ld65.exe','-C',OUT/'objects.cfg',OUT/'objects.o',OUT/'symbols.o','-o',OUT/'objects.bin','--dbgfile',OUT/'objects.dbg','-Ln',OUT/'objects.lbl']]:
            cmd=list(map(str,cmd));guard=validate(cmd,OUT,cwd=ROOT);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    compile();firstsize=len((OUT/'objects.bin').read_bytes());relaxed=set();iterations=[]
    sources={'actor-relaxed.inc':actor,'object-leaves.inc':donor}
    conditional=r'^(Ms(?:Obj)?_[0-9A-F]{4}): j(eq|ne|cc|cs|mi|pl|vc|vs) (Ms(?:Obj)?_[0-9A-F]{4}) ;'
    # Monotone branch relaxation: no external/public host symbol moves, no
    # opcode substitution except each6502 short/long conditional equivalent.
    for iteration in range(16):
        lab=labels();binary=(OUT/'objects.bin').read_bytes();added=[]
        for m in re.finditer(conditional,'\n'.join(sources.values()),re.M):
            name,op,target=m.groups()
            if name in relaxed:continue
            pc=lab[name];to=lab[target];offset=pc-0xa000
            long=binary[offset+1:offset+3]==bytes([3,0x4c])
            displacement=to-(pc+2)-(3 if long and to>pc else 0)
            if -128<=displacement<=127:added.append(name)
        if not added:break
        relaxed.update(added)
        for filename,text in sources.items():
            out=text
            for name in relaxed:out=re.sub(r'^('+name+r': )j',r'\1b',out,flags=re.M)
            (OUT/filename).write_text(out)
        compile();iterations.append(dict(iteration=iteration+1,new_short_branches=len(added),bytes=len((OUT/'objects.bin').read_bytes())))
    else:raise AssertionError('Branch relaxation did not converge')
    binary=(OUT/'objects.bin').read_bytes();size=len(binary);assert size<=8160,('unfunded capsule bytes',size,8160)
    # Prove every edited conditional is an actual same-target short branch.
    lab=labels();opcodes=dict(eq=0xf0,ne=0xd0,cc=0x90,cs=0xb0,mi=0x30,pl=0x10,vc=0x50,vs=0x70)
    for m in re.finditer(conditional,'\n'.join(sources.values()),re.M):
        name,op,target=m.groups()
        if name not in relaxed:continue
        at=lab[name]-0xa000;assert binary[at]==opcodes[op]
        disp=binary[at+1];assert lab[name]+2+(disp if disp<128 else disp-256)==lab[target]
    deps=[Path(__file__),REF,ACTOR,Path(M.__file__),M.ROM,V5/'source-stage.json',V5/'source-proof.zip',V5/'terrain.s',V5/'symbols.s',V5/'donor-leaves.inc',ROOT/'tools/reference/metal_storm_terrain_host_1101_v5.inc',ROOT/'tools/reference/metal_storm_host_contract_1101_v4.inc',OUT/'objects.s',OUT/'actor-relaxed.inc',OUT/'host-step.inc',OUT/'terrain-adapter.inc',OUT/'object-leaves.inc',OUT/'objects.cfg',OUT/'symbols.s',OUT/'objects.bin',OUT/'objects.dbg',OUT/'objects.lbl',cc/'ca65.exe',cc/'ld65.exe']
    result=dict(passed=True,component_only=True,native=False,installed=False,admitted=False,source_spans=SPANS,original_object_instructions=len(code),source_object_data_bytes=sum(hi-lo for lo,hi in DATA),animation_mask_bytes=8,first_unrelaxed_bytes=firstsize,kernel_bytes=size,remaining_before_BFE0=8160-size,explicit_short_conditionals=len(relaxed),long_branches_shortened=(firstsize-size)//3,code_bytes_saved=firstsize-size,relaxation=iterations,labels=lab,source_fields=json.loads((V5/'assembly.json').read_text())['source_fields'],commands=commands,bindings={str(p.resolve()):sha(p)for p in deps},scope='Original clock/object update for verified negative types80/81 slots1..3. Private branch relaxation only. No resource allocation/native admission. Actual current mutable ROM/debug never read.')
    (OUT/'assembly.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in['labels','source_fields','commands','bindings']}))
if __name__=='__main__':main()
