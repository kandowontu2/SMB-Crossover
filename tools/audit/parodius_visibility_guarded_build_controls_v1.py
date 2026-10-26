"""Fresh canonical and matched ordinary builds; external outputs only."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','compiler','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    for name,source,mapper in [('canonical',a.candidate/'source',None),('parent-mmc3',a.parent/'source','mmc3'),('candidate-mmc3',a.candidate/'source','mmc3'),('parent-mmc5',a.parent/'source','mmc5'),('candidate-mmc5',a.candidate/'source','mmc5')]:
        rom=a.output/(name+'.nes');cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(a.compiler),'--output',str(rom)]
        if mapper:cmd+=['--flag-off',mapper]
        result=subprocess.run(cmd,capture_output=True,text=True);log=a.output/(name+'.log');log.write_text(result.stdout+result.stderr)
        assert result.returncode==0,(name,result.stdout,result.stderr)
        rows.append(dict(name=name,ROM_sha256=sha(rom),log_sha256=sha(log)))
    assert sha(a.output/'canonical.nes')==sha(a.candidate/'candidate.nes')
    for m in ['mmc3','mmc5']:assert(a.output/f'parent-{m}.nes').read_bytes()==(a.output/f'candidate-{m}.nes').read_bytes()
    q=dict(passed=True,native_run=False,canonical_rebuild_exact=True,ordinary_MMC3_MMC5_parent_bytes_exact=True,ROM_sha256=sha(a.candidate/'candidate.nes'),tool_sha256=sha(Path(__file__)),compiler_sha256=sha(a.compiler),builds=rows,limits='Fresh source reproduction/ordinary conditional builds only; no gameplay/native claim.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
