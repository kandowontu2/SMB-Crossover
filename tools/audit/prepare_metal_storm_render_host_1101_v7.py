"""Link separate original-source lifecycle/native renderer; no host resource grant."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
from py65.disassembler import Disassembler
from private_build_outputs_v1 import validate
OUT=ROOT/'build/metal-storm-render-host-1101-v7'
V6=ROOT/'build/metal-storm-objects-host-1101-v6'
REF=ROOT/'tools/reference/metal_storm_render_host_1101_v7.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[(0x8e54,0x8ef3),(0xeeae,0xeec6)]
def life_source():
    c=M.machine();c.memory.regs[6:8]=[4,5];c.memory.map();d=Disassembler(c);lines=[];proof={}
    for lo,hi in SPANS:
        p=lo
        while p<hi:
            n,t=d.instruction_at(p);mn,mode=c.disassemble[c.memory[p]];a=c.memory[p+1]+(256*c.memory[p+2]if n==3 else 0)if n>1 else None
            proof[f'{p:04X}']=dict(bytes=list(c.memory[p:p+n]),instruction=t)
            if mode=='rel':
                target=(p+2+(a if a<128 else a-256))&65535
                name=f'MsLife_{target:04X}'if any(l<=target<h for l,h in SPANS)else'MsLifeUnsupported'
                t='j'+mn.lower()[1:]+' '+name
            elif mode in['abs','abx','aby','zpg','zpx','zpy','inx','iny','ind']:
                assert a<0x800,(hex(p),t)
                old=re.search(r'\$[0-9a-fA-F]+',t);t=t[:old.start()]+f'MsState+${a:04x}'+t[old.end():]
            lines.append(f'MsLife_{p:04X}: {t} ; original ${p:04x}');p+=n
        assert p==hi
    return '\n'.join(lines)+'\n',proof
def labels():
    return {m[2]:int(m[1],16)for l in(OUT/'render.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',l))}
def main():
    witness=json.loads((OUT/'native-render-witness.json').read_text());old=json.loads((V6/'source-stage.json').read_text());assert old['passed']and sha(V6/'source-proof.zip')==old['archive_sha256']
    life,proof=life_source();(OUT/'render-life.inc').write_text(life)
    wrapper=(V6/'objects.s').read_text()+ '\n.export MsState\n.import MsObjectLifecycle\n'
    wrapper=wrapper.replace('.include "metal_storm_objects_host_1101_v6.inc"','.include "objects-ready.inc"')
    (OUT/'actor.s').write_text(wrapper)
    step=(V6/'host-step.inc').read_text();assert step.count(' jsr MsFrame\n')==1
    step=step.replace(' jsr MsFrame\n',' jsr MsFrame\n jsr MsObjectLifecycle ; actual original entityAI before rendering\n')
    (OUT/'host-step.inc').write_text(step)
    objects=(V6/'object-leaves.inc').read_text();needle=' jmp MsObjectUnsupported ; ineligible source object path'
    at=objects.index(needle);objects=objects[:at]+objects[at:].replace(needle,' lda MsState+$600,x ; original DB A0 qualified positiveflags\n jpl MsObjReturn\n'+needle,1)
    (OUT/'object-leaves.inc').write_text(objects)
    ready=(ROOT/'tools/reference/metal_storm_objects_host_1101_v6.inc').read_text()
    start=ready.index(' cmp #$80\n');end=ready.index('NextObject:',start)
    ready=ready[:start]+''' cmp #$83
 beq CheckImpactFlags
 cmp #$80
 beq CheckObjectFlags
 cmp #$81
 bne BadObject
CheckObjectFlags:
 lda MsState+$600,x
 cmp #$0a
 bne BadObject
 beq NextObject
CheckImpactFlags:
 lda MsState+$600,x
 cmp #5
 bne BadObject
 lda MsState+$618,x
 bne BadObject
 lda MsState+$630,x
 cmp #3
 bcs BadObject
'''+ready[end:]
    (OUT/'objects-ready.inc').write_text(ready)
    (OUT/'renderer.s').write_text('.setcpu "6502"\n.macpack longbranch\n.import MsState,MsLifeUnsupported\n.include "metal_storm_render_host_1101_v7.inc"\n')
    symbols=(V6/'symbols.s').read_text();existing=set(re.findall(r'^\.export (\w+)=',symbols,re.M))
    names='MetaspriteRenderLoop X5SetPhysicalChr FarCallCommon SafecallA_SMC FarcallJmpTarget_SMC CurrentBank CurrentBankC ScreenLeft_X_Pos ScreenLeft_PageLoc Player_SprAttrib CurrentOAMOffset SsChrActive VRAM_Buffer1 VRAM_Buffer1_Offset ObjectMetasprite SmPosePtr SelectedCharacter OperMode GameEngineSubroutine'.split()
    for name in names:
        if name not in existing:symbols+=f'.export {name}=${int(witness["syms"][name]["val"],0):04x}\n'
    for i in range(8):symbols+=f'.exportzp R{i}=${3+i:02x}\n'
    for i in range(5):symbols+=f'.export MsBodyPhysical{i}={800+i}\n'
    symbols+='.export MsShotPhysical=805\n.export MS_NATIVE_DRAW_BANK=$84\n.export MS_NATIVE_CHR_BANK=$be\n.export MsLifeUnsupported=$5023\n'
    (OUT/'symbols.s').write_text(symbols)
    (OUT/'render.cfg').write_text('MEMORY{CODE:start=$a000,size=$1fe0,file="'+(OUT/'actor.bin').as_posix()+'";RENDER:start=$cd00,size=$12e0,file="'+(OUT/'render.bin').as_posix()+'";GATE:start=$9000,size=$0200,file="'+(OUT/'gate.bin').as_posix()+'";}SEGMENTS{CODE:load=CODE,type=ro;RENDER:load=RENDER,type=ro;GATE:load=GATE,type=ro;}\n')
    for name in['actor-cookie.bin','render-cookie.bin']:(OUT/name).write_bytes(bytes(16))
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    def compile():
        for source in['actor','renderer','symbols']:
            cmd=[cc/'ca65.exe','-g','-I',OUT,'-I',V6,'-I',ROOT/'build/metal-storm-terrain-host-1101-v5','-I',ROOT/'tools/reference',OUT/(source+'.s'),'-o',OUT/(source+'.o')]
            guard=validate(cmd,OUT,cwd=ROOT);q=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);commands.append(dict(command=list(map(str,cmd)),guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
        cmd=[cc/'ld65.exe','-C',OUT/'render.cfg',OUT/'actor.o',OUT/'renderer.o',OUT/'symbols.o','-o',OUT/'unused.bin','--dbgfile',OUT/'render.dbg','-Ln',OUT/'render.lbl']
        guard=validate(cmd,OUT,cwd=ROOT);q=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);commands.append(dict(command=list(map(str,cmd)),guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    compile();actor=(OUT/'actor.bin').read_bytes();render=(OUT/'render.bin').read_bytes()
    (OUT/'actor-cookie.bin').write_bytes(bytes([167,35,7])+hashlib.sha256(actor).digest()[:13])
    (OUT/'render-cookie.bin').write_bytes(bytes([167,35,7])+hashlib.sha256(render+(OUT/'body.chr').read_bytes()+(OUT/'shots.chr').read_bytes()).digest()[:13]);compile()
    assert actor==(OUT/'actor.bin').read_bytes()and render==(OUT/'render.bin').read_bytes()
    lab=labels();assert len(actor)<=8160 and len(render)<=4832 and len((OUT/'gate.bin').read_bytes())<=512
    deps=[Path(__file__),REF,ROOT/'tools/audit/capture_metal_storm_native_render_1101_v7.py',ROOT/'tools/audit/prepare_metal_storm_render_assets_1101_v7.py',V6/'source-stage.json',V6/'source-proof.zip',V6/'objects.s',V6/'actor-relaxed.inc',V6/'terrain-adapter.inc',V6/'object-leaves.inc',V6/'host-step.inc',V6/'symbols.s',ROOT/'tools/reference/metal_storm_objects_host_1101_v6.inc']
    deps += [OUT/n for n in['native-render-witness.json','actor.s','host-step.inc','object-leaves.inc','objects-ready.inc','renderer.s','render-life.inc','symbols.s','render.cfg','body.chr','body-meta.bin','shots.chr','shot-meta.bin','art.json','actor-cookie.bin','render-cookie.bin']]
    result=dict(passed=True,admitted=False,native=False,installed=False,scope='Compilable split A3actor/C2renderer + unfunded ROM authentication fragment; CHR800..805 are model fixtures only.',actor_bytes=len(actor),actor_remaining=8160-len(actor),renderer_bytes=len(render),renderer_remaining=4832-len(render),gate_bytes=len((OUT/'gate.bin').read_bytes()),labels=lab,life_original_instructions=proof,commands=commands,bindings={str(p):sha(p)for p in deps})
    (OUT/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in['passed','actor_bytes','actor_remaining','renderer_bytes','gate_bytes']}))
if __name__=='__main__':main()

