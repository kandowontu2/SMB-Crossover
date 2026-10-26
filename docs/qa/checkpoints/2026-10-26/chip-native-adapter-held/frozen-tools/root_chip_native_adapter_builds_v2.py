"""Canonical rebuild and ordinary mapper controls for private Chip routing."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
EXP=D/'root-chip-native-adapter-v5'
OUT=EXP/'build-controls-v2'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    rows={}
    for name,mapper,expected in [
            ('canonical',None,'f7cf83bb7b3bfd7ecc138dd3a7dcf2e8a3caa27bcece32ba89ef1fa6e958f7d2'),
            ('ordinary-mmc3','mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
            ('ordinary-mmc5','mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        cmd=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),
             '--source-overlay',str(EXP/'source'),'--output',str(OUT/(name+'.nes'))]
        if mapper:cmd+=['--flag-off',mapper]
        proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        log=OUT/(name+'.log');log.write_text(proc.stdout+proc.stderr)
        assert proc.returncode==0,(name,proc.stdout[-2000:],proc.stderr[-2000:])
        assert sha(OUT/(name+'.nes'))==expected,name
        rows[name]=dict(ROM_sha256=expected,log_sha256=sha(log))
        print(name+' passed',flush=True)
    result=dict(passed=True,accepted=False,native_run=False,builds=rows,
                checker_sha256=sha(__file__),limits='Build reproducibility and ordinary flagoff controls only.')
    (OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
