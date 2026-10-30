"""Keep original short branches when they fit after explicit state projection."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'build/arthur-projected-leaf-v2';OUT=ROOT/'build/arthur-projected-leaf-v3'
BIN=ROOT/'tools/Windows/cc65/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHORT={'jcc':'BCC','jcs':'BCS','jeq':'BEQ','jne':'BNE','jmi':'BMI','jpl':'BPL','jvc':'BVC','jvs':'BVS'}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    native=(BASE/'native-kernels.s').read_text().splitlines();long={}
    for i,line in enumerate(native):
        x=line.strip().split(' ',1)
        if len(x)==2 and x[0]in SHORT:long[i]=line;native[i]=' '+SHORT[x[0]]+' '+x[1]
    for name in('native-context.inc','component.s','leaf.cfg'):(OUT/name).write_bytes((BASE/name).read_bytes())
    commands=[];expanded=set();failures=[]
    for attempt in range(16):
        (OUT/'native-kernels.s').write_text('\n'.join(native)+'\n')
        args=[str(BIN/'ca65.exe'),'-g','-I',str(OUT),'-o',str(OUT/'native-kernels.o'),str(OUT/'native-kernels.s')]
        q=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);commands.append(args)
        if q.returncode==0:break
        failures.append(q.stdout+q.stderr)
        errors=re.findall(r'\((\d+)\): Error: Range error',q.stdout+q.stderr)
        assert errors,(q.stdout,q.stderr)
        for n in errors:
            i=int(n)-1;assert i in long and i not in expanded,(n,native[i]);native[i]=long[i];expanded.add(i)
    else:raise AssertionError('branch relaxation did not converge')
    args=[str(BIN/'ca65.exe'),'-g','-I',str(OUT),'-o',str(OUT/'component.o'),str(OUT/'component.s')]
    subprocess.run(args,cwd=ROOT,check=True);commands.append(args)
    args=[str(BIN/'ld65.exe'),'-C',str(OUT/'leaf.cfg'),'-o',str(OUT/'leaf.bin'),'-Ln',str(OUT/'leaf.lbl'),
       '--dbgfile',str(OUT/'leaf.dbg'),'-m',str(OUT/'leaf.map'),str(OUT/'native-kernels.o'),str(OUT/'component.o')]
    subprocess.run(args,cwd=ROOT,check=True);commands.append(args)
    if failures:(OUT/'branch-relaxation-negative.txt').write_text('\n'.join(failures))
    p=json.loads((BASE/'projection-proof.json').read_text());p['output_sha256']=sha(OUT/'leaf.bin');p['commands']=commands
    p['branch_relaxation']=dict(original_relative_branches=len(long),long_macro_sites=len(expanded),
       source_lines=[i+1 for i in sorted(expanded)],fixed_point_passes=attempt+1,
       original_short_branches_retained_unless_assembler_range_requires_bridge=True)
    for k in list(p['bindings']):
        if Path(k).parent==BASE:p['bindings'].pop(k)
    p['bindings'].update({str(q.resolve()):sha(q)for q in[Path(__file__),BASE/'cpu-receipt.json',BASE/'projection-proof.json',
       OUT/'native-kernels.s',OUT/'native-context.inc',OUT/'component.s',OUT/'leaf.cfg']})
    target=OUT/'projection-proof.json';target.write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps(dict(leaf_sha256=p['output_sha256'],relaxation=p['branch_relaxation'],proof_sha256=sha(target))))
if __name__=='__main__':main()
