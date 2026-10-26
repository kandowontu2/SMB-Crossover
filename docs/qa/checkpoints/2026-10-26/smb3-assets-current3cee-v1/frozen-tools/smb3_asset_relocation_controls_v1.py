"""Fresh canonical/ordinary config-only relocation builds, externally written."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);a=p.parse_args()
    out=a.packet/'build-controls-v1';out.mkdir(exist_ok=False)
    rows=[]
    for mode in ['expanded','mmc3','mmc5']:
        target=out/(mode+'.nes');cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(a.packet/'source'),'--output',str(target)]
        if mode!='expanded':cmd+=['--flag-off',mode]
        run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        (out/(mode+'.launch.json')).write_text(json.dumps(dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr),indent=2)+'\n')
        assert run.returncode==0,(mode,run.stdout,run.stderr)
        expected=sha(a.packet/'candidate.nes')if mode=='expanded'else {'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}[mode]
        assert sha(target)==expected,(mode,sha(target),expected)
        rows.append(dict(mode=mode,ROM=str(target),sha256=sha(target),exact_expected=True))
    proof=dict(passed=True,native_run=False,builds=rows,checker_sha256=sha(__file__),source_cfg_sha256=sha(a.packet/'source/smb1base-mmc5-expanded.cfg'))
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
