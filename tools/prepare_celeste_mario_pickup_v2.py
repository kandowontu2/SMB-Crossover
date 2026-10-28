"""Private indexed-pickup successor link; preserve all frozen v1 outputs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/celeste-mario-pickup-v2/candidate.nes');a=p.parse_args()
    out=a.output.resolve();overlay=out.parent/'sparse';(overlay/'src').mkdir(parents=True,exist_ok=True)
    entry=ROOT/'src/entrypoint.s';cfg=ROOT/'smb1base-mmc5-expanded.cfg'
    before={str(f):sha(f)for f in [*sorted((ROOT/'src').glob('celeste_mario*')),ROOT/'chr/characters/celeste-mario.chr']}
    text=entry.read_text()+'\n'
    if '.include "celeste_mario.s"'not in text:text+='.include "celeste_mario.s"\n'
    (overlay/'src/entrypoint.s').write_text(text)
    config=cfg.read_text()
    if 'CELESTE_MARIO_CHR_MEM:'not in config:
        old='CELESTE_UNUSED_CHR_MEM: start=$b9000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;'
        assert config.count(old)==1
        config=config.replace(old,old.replace('CELESTE_UNUSED','CELESTE_MARIO'))
    if 'CELESTE_MARIO_CORE:'not in config:
        assert config.count('\n}\nSYMBOLS {')==1
        config=config.replace('\n}\nSYMBOLS {','\n    CELESTE_MARIO_CORE: load=X5_NEW_62,type=ro,start=$b000;\n    CELESTE_MARIO_CHR: load=CELESTE_MARIO_CHR_MEM,type=ro;\n}\nSYMBOLS {')
    (overlay/'smb1base-mmc5-expanded.cfg').write_text(config)
    command=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(overlay),'--output',str(out)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);out.with_suffix('.link.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    assert all(sha(f)==h for f,h in before.items())
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(out),command=command,owned_inputs=before,
      shared_source_context={str(entry):sha(entry),str(cfg):sha(cfg)},sparse_generated={str(f):sha(f)for f in [overlay/'src/entrypoint.s',overlay/'smb1base-mmc5-expanded.cfg']},
      scope='Current shared roster context plus own Celeste leaf. No claim of a pure ROM delta against the older v1 link. No host admission or native claim.')
    out.with_suffix('.link.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=proof['ROM_sha256'])))
if __name__=='__main__':main()
