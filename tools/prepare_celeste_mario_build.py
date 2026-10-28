"""Private fixed-bank Celeste leaf link; two-file sparse wrapper, no shared edits."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'build/celeste-mario-module';overlay=out/'sparse';(overlay/'src').mkdir(parents=True,exist_ok=True)
    entry=ROOT/'src/entrypoint.s';cfg=ROOT/'smb1base-mmc5-expanded.cfg'
    before={str(p):sha(p)for p in [entry,cfg,*sorted((ROOT/'src').glob('celeste_mario*')),ROOT/'chr/characters/celeste-mario.chr']}
    text=entry.read_text()+'\n'
    if '.include "celeste_mario.s"'not in entry.read_text():text+='.include "celeste_mario.s"\n'
    (overlay/'src/entrypoint.s').write_text(text)
    config=cfg.read_text()
    old='MIKE_UNUSED_CHR_MEM: start=$b5000,size=$8000,type=ro,fill=yes,file=%O,fillval=$00;'
    assert config.count(old)==1
    config=config.replace(old,'MIKE_UNUSED_CHR_MEM: start=$b5000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;\n    CELESTE_MARIO_CHR_MEM: start=$b9000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;')
    assert config.count('\n}\nSYMBOLS {')==1
    config=config.replace('\n}\nSYMBOLS {','\n    CELESTE_MARIO_CORE: load=X5_NEW_62,type=ro,start=$b000;\n    CELESTE_MARIO_CHR: load=CELESTE_MARIO_CHR_MEM,type=ro;\n}\nSYMBOLS {')
    (overlay/'smb1base-mmc5-expanded.cfg').write_text(config)
    rom=out/'candidate.nes'
    command=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(overlay),'--output',str(rom)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'link.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    assert all(sha(Path(p))==h for p,h in before.items()),'Source changed during private link'
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(rom),command=command,inputs=before,
      sparse_generated=[dict(path=str(p),sha256=sha(p))for p in [overlay/'src/entrypoint.s',overlay/'smb1base-mmc5-expanded.cfg']],
      allocation='physical98 B000..BFFF; CHR740..755; no canonical/menu routing added')
    (out/'link.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=proof['ROM_sha256'])))
if __name__=='__main__':main()
