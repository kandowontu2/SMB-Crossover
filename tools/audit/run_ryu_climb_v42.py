"""Run the frozen independent Ryu primary/climb oracle on a linked checkpoint."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint',type=Path);p.add_argument('--output',type=Path,required=True)
p.add_argument('--expected-mismatches',type=int,default=0);a=p.parse_args()
source=ROOT/'build/verification/ryu-climb-primary-v40-component-b/component.lua'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='1a13c641f3671e49b2d893cf1fe4333c992c763cc5f5712d7a7620913b36a4ba'
a.output.mkdir(parents=True,exist_ok=False)
fixture=a.output/'component.lua';shutil.copyfile(source,fixture)
report={'scope':'RAM-seeded isolated wall/floor source input component; real buttons establish wall grab; not traversal',
 'fixture_sha256':sha(fixture),'expected_mismatches':a.expected_mismatches,
 'status':'confirmed-source-negative'if a.expected_mismatches else'passed-source-component','mappers':{}}
for mapper in('mmc3','mmc5'):
 d=a.output/mapper;d.mkdir()
 rom=a.checkpoint.resolve()/f'smb-crossover-{mapper}.nes'
 script=a.output/f'run-climb-{mapper}.lua'
 script.write_text(f'COMPONENT_OUT=[=[{d.resolve().as_posix()}/]=]\ndofile([=[{fixture.resolve().as_posix()}]=])\n')
 code=run_mesen.run(script,rom,timeout=90)
 log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log';shutil.copyfile(log,d/'native.log')
 result=json.loads((d/'result.json').read_text())if(d/'result.json').exists()else None
 report['mappers'][mapper]={'exit':code,'rom_sha256':sha(rom),'result':result,
  'receipts_sha256':sha(d/'receipts.csv')if(d/'receipts.csv').exists()else None}
 (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 assert code==(1 if a.expected_mismatches else 0)and result and result['completed']==10 and result['mismatches']==a.expected_mismatches,(mapper,code,result)
 if a.expected_mismatches:
  assert [r['case']for r in result['failures']]==[1,2],'Only mirrored ordinary wall-B cases fail'
assert sha(source)==sha(fixture),'Independent frozen fixture remains unchanged'
print(('CONFIRMED NEGATIVE'if a.expected_mismatches else'PASS'),a.expected_mismatches,'source mismatches per mapper; all ten cases completed',flush=True)
