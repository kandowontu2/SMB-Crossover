from pathlib import Path
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/arthur-source-v1'
sys.path.insert(0,str(ROOT/'tools'));import run_mesen
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=OUT/'native/leaf-arena-v1';out.mkdir(parents=True,exist_ok=False);os.environ['SMB_RUN_OUTPUT']=str(out)
    rom=OUT/'arena.nes';script=Path(__file__).with_suffix('.lua')
    assert sha(rom)=='784ac7427fc849535871336d7c118d6c3d1e7ccf054bed904cd7a1a989478535'
    record=dict(ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),bound_frames=1000,controller_only=True,memory_writes=False)
    code=run_mesen.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    record['exit_code']=code;record['evidence']={str(p.resolve()):sha(p)for p in out.iterdir()if p.is_file()}
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(exit_code=code,manifest_sha256=sha(out/'manifest.json'))));raise SystemExit(code)
if __name__=='__main__':main()
