"""Bounded actual-MMC5 audio ownership and immutable pre-optimization APU oracle."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint',type=Path)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
rom=a.checkpoint.resolve()/'smb-crossover-mmc5.nes'
observer=ROOT/'tools/profiling/mmc5_multiplier_ownership_v40.lua'
script=a.output/'run.lua'
script.write_text(f'OWNERSHIP_ROOT=[=[{ROOT.as_posix()}]=]\nOWNERSHIP_OUTPUT=[=[{(a.output.resolve()/"ownership.json").as_posix()}]=]\ndofile([=[{observer.as_posix()}]=])\n')
code=run_mesen.run(script,rom,timeout=90)
log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
(a.output/'native.log').write_bytes(log.read_bytes())
assert code==0,'Hardware ownership observer failed; retain its log'
data=ROOT/f'build/verification/{rom.stem}-guest-audio-flush.bin'
reference=json.loads((ROOT/'tests/guest-audio-flush-reference.json').read_text())
digest=hashlib.sha256(data.read_bytes()).hexdigest()
assert digest==reference['output_sha256']['mmc5'],'Ordered physical APU writes differ from immutable pre-optimization reference'
(a.output/'guest-audio-flush.bin').write_bytes(data.read_bytes())
receipt=json.loads((a.output/'ownership.json').read_text())
receipt.update(rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),apu_sha256=digest,
 apu_records=len(data.read_bytes())//5,apu_matches_immutable_reference=True,
 observer_sha256=hashlib.sha256(observer.read_bytes()).hexdigest(),
 fixture_sha256=hashlib.sha256((ROOT/'tests/guest-audio-flush-differential.lua').read_bytes()).hexdigest())
(a.output/'report.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',receipt,flush=True)
