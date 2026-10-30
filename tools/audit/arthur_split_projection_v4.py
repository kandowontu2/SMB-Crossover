"""Abstract split at genuine routine boundaries; no cartridge leases/link."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'build/arthur-projected-leaf-v3';OUT=ROOT/'build/arthur-projected-leaf-v4'
BIN=ROOT/'tools/Windows/cc65/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    text=(BASE/'native-kernels.s').read_text().replace('.segment "ARTHUR_NATIVE"','.segment "ARTHUR_BODY"')
    text=text.replace('.export ArNativeLance\n','.segment "ARTHUR_SHOTS"\n.export ArNativeLance\n',1)
    text=text.replace('ArO_EFDA:\n','.segment "ARTHUR_COMMON"\nArO_EFDA:\n',1)
    (OUT/'native-kernels.s').write_text(text)
    for n in('native-context.inc','component.s'):(OUT/n).write_bytes((BASE/n).read_bytes())
    (OUT/'leaf.cfg').write_text('''# Abstract CPU placement only, not host CPU/physical leases.
MEMORY {
 PTR:start=$0003,size=$0002,type=rw,file="";
 EXRAM:start=$5C00,size=$00B0,type=rw,file="";
 CODE:start=$8000,size=$4000,type=ro,file=%O,fill=yes,fillval=$FF;
}
SEGMENTS {
 ARTHUR_PTR:load=PTR,type=zp;
 ARTHUR_SCALARS:load=EXRAM,type=bss;
 ARTHUR_STATE:load=EXRAM,type=bss;
 ARTHUR_BODY:load=CODE,type=ro,start=$8000;
 ARTHUR_COMMON:load=CODE,type=ro,start=$9000;
 ARTHUR_SHOTS:load=CODE,type=ro,start=$9800;
 ARTHUR_LEAF:load=CODE,type=ro,start=$A000;
}
''')
    commands=[]
    for n in('native-kernels','component'):
        cmd=[str(BIN/'ca65.exe'),'-g','-I',str(OUT),'-o',str(OUT/(n+'.o')),str(OUT/(n+'.s'))]
        commands.append(cmd);subprocess.run(cmd,check=True,cwd=ROOT)
    cmd=[str(BIN/'ld65.exe'),'-C',str(OUT/'leaf.cfg'),'-o',str(OUT/'leaf.bin'),'-Ln',str(OUT/'leaf.lbl'),
         '--dbgfile',str(OUT/'leaf.dbg'),'-m',str(OUT/'leaf.map'),str(OUT/'native-kernels.o'),str(OUT/'component.o')]
    commands.append(cmd);subprocess.run(cmd,check=True,cwd=ROOT)
    p=json.loads((BASE/'projection-proof.json').read_text());p['commands']=commands;p['output_sha256']=sha(OUT/'leaf.bin')
    p['layout']='Abstract BODY8000, COMMON9000, SHOTS9800, LEAFA000. No physical host banks, mapper hooks or shared edits.'
    p['bindings'].update({str(q.resolve()):sha(q)for q in[Path(__file__),BASE/'cpu-receipt.json',OUT/'native-kernels.s',OUT/'native-context.inc',OUT/'component.s',OUT/'leaf.cfg']})
    (OUT/'projection-proof.json').write_text(json.dumps(p,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('abstract_split_oracle',ROOT/'tools/audit/arthur_check_projection_v2.py')
    A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
    A.OUT=OUT;A.S=A.symbols(OUT/'leaf.lbl');A.RAW=(OUT/'leaf.bin').read_bytes();A.Q=p
    exact=A.instructions();diff=A.differential();leaf=A.leaf_cases()
    segments={}
    for line in(OUT/'leaf.dbg').read_text().splitlines():
        if line.startswith('seg\t')and(m:=re.search(r'name="(ARTHUR_[^"]+)".*size=(0x[0-9A-Fa-f]+)',line)):
            segments[m[1]]=int(m[2],0)
    assert segments['ARTHUR_BODY']==965 and segments['ARTHUR_COMMON']==1074 and segments['ARTHUR_SHOTS']==482 and segments['ARTHUR_LEAF']==675
    result=dict(status='PASS_ABSTRACT_SPLIT_SOURCE_INSTRUCTION_CPU_PROJECTION_NO_HOST_LEASE',
       leaf_sha256=sha(OUT/'leaf.bin'),segments=segments,native_instruction_check=exact,differential=diff,leaf_controller_cases=leaf,
       binding_proof_sha256=sha(OUT/'projection-proof.json'),
       physical_host_resources_allocated=[],mapper_bank_wrappers_tested=False,
       bindings={str(q.resolve()):sha(q)for q in[Path(__file__),ROOT/'tools/audit/arthur_check_projection_v2.py',OUT/'projection-proof.json',
           OUT/'leaf.bin',OUT/'leaf.lbl',OUT/'leaf.dbg',OUT/'native-kernels.s',OUT/'component.s',BASE/'cpu-receipt.json']},
       limits='Exact code/state/placement semantics under actual6502 in an abstract CPU arena. C-bank save/restore, native IRQ/NMI interruptions, world/host controller routes and admission remain future proof.')
    target=OUT/'cpu-receipt.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],segments=segments,differential_cases=diff['cases'],receipt_sha256=sha(target))))
if __name__=='__main__':main()
