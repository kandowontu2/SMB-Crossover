"""Run the frozen independently negative40 fixture on a new linked candidate."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint',type=Path)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
source=ROOT/'build/verification/simon-walkoff-v40-component-b/component.lua'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='3bfe5df63cf0df9a4621c740aab1da5a06ce76622f181d05ff48c12c0cd06046'
a.output.mkdir(parents=True,exist_ok=False)
fixture=a.output/'component.lua';shutil.copyfile(source,fixture)
report={'scope':'Seeded ability component on native authored ledge, unchanged frozen40 independent oracle; not traversal','fixture_sha256':sha(fixture),'mappers':{}}
for mapper in ('mmc3','mmc5'):
 d=a.output/mapper;d.mkdir()
 rom=a.checkpoint.resolve()/f'smb-crossover-{mapper}.nes'
 script=a.output/f'run-{mapper}.lua'
 script.write_text(f'COMPONENT_OUT=[=[{d.resolve().as_posix()}/]=]\ndofile([=[{fixture.resolve().as_posix()}]=])\n')
 code=run_mesen.run(script,rom,timeout=90)
 log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log';shutil.copyfile(log,d/'native.log')
 result=json.loads((d/'result.json').read_text())if(d/'result.json').exists()else None
 report['mappers'][mapper]={'exit':code,'rom_sha256':sha(rom),'result':result,'receipts_sha256':sha(d/'receipts.csv')if(d/'receipts.csv').exists()else None}
 (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 assert code==0 and result and result['completed']==12 and result['mismatches']==0,(mapper,code,result)
assert sha(source)==sha(fixture),'Original independently negative fixture remains unchanged'
print('PASS twelve source cases on each mapper; real ledge walk-off, whip cancellation, armed/unarmed, exhaustion and real landing controls')
