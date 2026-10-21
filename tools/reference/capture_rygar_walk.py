"""Capture native Rygar walk frames and their logical origins, read-only."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,default=Path('C:/NES/Rygar (USA).nes'))
    a=p.parse_args();digest=hashlib.sha256(a.rom.read_bytes()).hexdigest()
    assert digest=='965330fed9f5b8492452f3b53084752e83b7f899a1f88f3c475ece2fde6f9231'
    out=ROOT/'build/rygar-audit/walk';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'tools/reference/capture_rygar_walk.lua';wrapper=out/'capture.lua'
    wrapper.write_text(f'NATIVE_OUTPUT=[=[{out.as_posix()}/]=]\ndofile([=[{source.as_posix()}]=])\n')
    if run_mesen.run(wrapper,a.rom):return 1
    assert hashlib.sha256(a.rom.read_bytes()).hexdigest()==digest
    (out/'manifest.json').write_text(json.dumps({'rom_sha256':digest,'script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'controller_only':True,'memory_or_register_writes':False,'source_frames':[302,309,316],
        'native_walk_period':21,'updates_per_pose':7,'logical_x_address':0x512,'oam_lag_updates':1},indent=2)+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
