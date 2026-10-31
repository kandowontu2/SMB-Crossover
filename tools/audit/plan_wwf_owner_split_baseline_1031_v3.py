"""CFG-only identity proof, retaining old owners and adding no WWF producer."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
import wwf_resource_inventory_1031_v1 as I
J=I.J;O=R/'build/wwf-owner-split-baseline-1031-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();O.mkdir();cfg=(J/'private.cfg').read_text()
    plans=[('CD_CHR_MEM',0x67000,0xc000,0x3800),('M3_CHR_MEM',0x83000,0x14000,0x5800),('TMNT_CHR_MEM',0x97000,0x10000,0x6400)]
    splits=[]
    for name,start,size,keep in plans:
        pat=rf'(?m)^\s*{name}:\s*start\s*=\s*\${start:x},\s*size\s*=\s*\${size:x},([^\n]*);'
        hits=list(re.finditer(pat,cfg,re.I));assert len(hits)==1,(name,len(hits))
        suffix=hits[0][1]
        replacement=f'    {name}: start=${start:x},size=${keep:x},{suffix};\n    {name}_RETAINED_UNUSED_TAIL: start=${start+keep:x},size=${size-keep:x},{suffix};'
        cfg=re.sub(pat,lambda m:replacement,cfg,count=1,flags=re.I)
        splits.append(dict(original_owner=name,prefix=[start,start+keep],retained_unused_tail=[start+keep,start+size],allocated_to_WWF=False))
    def side(m):
        old=Path(m[1]);assert old.is_relative_to(J),(m[0],old)
        new=O/'sideoutputs'/old.relative_to(J);new.parent.mkdir(parents=True,exist_ok=True)
        return 'file="'+new.as_posix()+'"'
    cfg=re.sub(r'file="([^"\r\n]+)"',side,cfg);(O/'private.cfg').write_text(cfg)
    old=json.loads((J.parent/'final-link.json').read_text())['command'];cmd=[]
    for i,arg in enumerate(old):
        if i and old[i-1]=='-C':arg=str(O/'private.cfg')
        elif i and old[i-1]=='-Ln':arg=str(O/'candidate.lbl')
        elif i and old[i-1]=='-o':arg=str(O/'candidate.nes')
        elif i and old[i-1]=='-m':arg=str(O/'candidate.map')
        elif arg.startswith('--dbgfile,'):arg='--dbgfile,'+str(O/'candidate.dbg')
        cmd.append(arg)
    objects={Path(a)for a in cmd if a.endswith('.o')};before={str(p):sha(p)for p in sorted(objects)}
    guard=validate(cmd,O,cwd=R)
    z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    (O/'link.json').write_text(json.dumps(dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
    assert z.returncode==0,z.stderr
    prepare(R,O/'candidate.nes')
    assert (O/'candidate.nes').read_bytes()==(J/'candidate.nes').read_bytes()
    syms=lambda p:sorted(re.findall(r'al ([A-Fa-f0-9]+) \.(\w+)',Path(p).read_text()))
    assert syms(O/'candidate.lbl')==syms(J/'candidate.lbl')
    for p,h in before.items():assert sha(p)==h,p
    q=dict(passed=True,source=True,CFG_only=True,read_only_original_inputs=True,no_WWF_allocation_or_producer=True,candidate=sha(O/'candidate.nes'),parent=sha(J/'candidate.nes'),all_public_and_private_labels_exact=True,all_ROM_bytes_exact=True,retained_owner_splits=splits,actual_object_count=len(objects),bindings=before)
    q['bindings'].update({str(p.resolve()):sha(p)for p in [Path(__file__),Path(I.__file__),R/'tools/audit/private_build_outputs_v1.py',R/'tools/audit/plan_wwf_owner_split_baseline_1031_v1.py',R/'build/wwf-owner-split-baseline-1031-v1/negative.json',J/'private.cfg',J/'candidate.nes',J/'candidate.lbl',J.parent/'final-link.json',O/'private.cfg',O/'link.json',O/'candidate.nes',O/'candidate.lbl',O/'candidate.dbg',O/'candidate.cv3-mirror.json',R/'tools/prepare_cv3_dmc_mirror.py',R/'audio/cv3/primary72.dmc',R/'audio/cv3/sypha75.dmc',R/'tools/audit/plan_wwf_owner_split_baseline_1031_v2.py',R/'build/wwf-owner-split-baseline-1031-v2/negative.json']})
    (O/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','retained_owner_splits']}))
if __name__=='__main__':main()
