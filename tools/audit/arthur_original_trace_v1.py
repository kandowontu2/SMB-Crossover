from pathlib import Path
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'));import run_mesen
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'build/arthur-source-v1/native/original-discovery-v1';out.mkdir(parents=True,exist_ok=False)
os.environ['SMB_RUN_OUTPUT']=str(out)
rom=Path("C:/NES/Ghosts'n Goblins (USA).nes");script=Path(__file__).with_suffix('.lua')
assert sha(rom)=='a263db625853b563aca356a8651f69c9092428dd2b665b6fd5c75ea5b1439d31'
record=dict(ROM=str(rom),ROM_sha256=sha(rom),script=str(script),script_sha256=sha(script),bound_frames=1800,
 controller_only=True,memory_writes=False,status='SOURCE_DISCOVERY_ONLY_NO_COMPONENT_OR_HOST_ADMISSION')
code=run_mesen.run(script,rom,timeout=100,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
record['exit_code']=code;record['evidence']={str(p.resolve()):sha(p)for p in out.iterdir()if p.is_file()}
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(exit_code=code,manifest_sha256=sha(out/'manifest.json'))));raise SystemExit(code)
