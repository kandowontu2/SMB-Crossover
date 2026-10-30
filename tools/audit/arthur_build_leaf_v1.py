from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/arthur-source-v1'
BIN=ROOT/'tools/Windows/cc65/bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    commands=[]
    for name in ('native-kernels','component'):
        args=[str(BIN/'ca65.exe'),'-g','-I',str(OUT),'-o',str(OUT/(name+'.o')),str(OUT/(name+'.s'))]
        commands.append(args);subprocess.run(args,check=True,cwd=ROOT)
    args=[str(BIN/'ld65.exe'),'-C',str(OUT/'leaf.cfg'),'-o',str(OUT/'leaf.bin'),'-Ln',str(OUT/'leaf.lbl'),
          '--dbgfile',str(OUT/'leaf.dbg'),'-m',str(OUT/'leaf.map'),str(OUT/'native-kernels.o'),str(OUT/'component.o')]
    commands.append(args);subprocess.run(args,check=True,cwd=ROOT)
    deps=[OUT/'native-kernels.s',OUT/'native-context.inc',OUT/'component.s',OUT/'leaf.cfg',
          OUT/'kernel-source-proof.json',Path(__file__),BIN/'ca65.exe',BIN/'ld65.exe']
    p=OUT/'build-proof.json';p.write_text(json.dumps(dict(status='PRIVATE_LEAF_SOURCE_BUILT_CPU_REVIEW_PENDING',
        output=str((OUT/'leaf.bin').resolve()),output_sha256=sha(OUT/'leaf.bin'),commands=commands,
        bindings={str(q.resolve()):sha(q)for q in deps},
        limits='Isolated CPU addresses only; no shared host PRG/CHR/ZP/RAM lease or native gameplay admission.'),indent=2)+'\n')
    print(json.dumps(dict(leaf_sha256=sha(OUT/'leaf.bin'),build_proof_sha256=sha(p))))
if __name__=='__main__':main()
