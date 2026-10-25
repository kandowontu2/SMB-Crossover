"""Explicit sequential native pilot/control batches; never more than one worker."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--group',choices=['pilots','controls','remaining'],required=True);a=p.parse_args();target=a.prepared/'native-v1';target.mkdir(exist_ok=True)
 groups={'pilots':[('ice',0x21,'basic'),('lightning',0x1e,'basic'),('priority',0x21,'priority')],'controls':[('idle-pressure',0,'pressure'),('fireball-pressure',0x1f,'pressure'),('fireball',0x1f,'basic'),('scene',0x2f,'scene'),('death',0x2f,'death')],'remaining':[('dagger',0x13,'basic'),('axe',0x15,'basic'),('flame',0x24,'basic'),('bat',0x2f,'basic'),('ice-pause',0x21,'pause')]}
 receipt=a.prepared/('native-batch-'+a.group+'-v1');receipt.mkdir(exist_ok=False);shutil.copyfile(__file__,receipt/Path(__file__).name);rows=[]
 for mode,name in [(0,'easy'),(1,'hard')]:
  for label,event,profile in groups[a.group]:
   for version,rom in [('candidate',a.prepared/'candidate.nes'),('baseline',D/'cv3-remaining-current50b-v1/baseline.nes')]:
    out=target/f'{version}-{name}-{label}'
    if out.exists():
     proof=json.loads((out/'native-proof.json').read_text());assert proof['passed']and proof['ROM_sha256']==sha(rom)and proof['mode']==mode and proof['event']==event and proof['profile']==profile;rows.append(dict(case=out.name,status='existing_exact_run_retained',proof_sha256=sha(out/'native-proof.json')));continue
    cmd=[sys.executable,str(ROOT/'tools/audit/cv3_remaining_sfx_resident_native_v1.py'),'--rom',str(rom),'--output',str(out),'--mode',str(mode),'--event',hex(event),'--profile',profile,'--run']
    with(receipt/(out.name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert not r.returncode,(out.name,(receipt/(out.name+'.host.log')).read_text()[-4000:]);proof=json.loads((out/'native-proof.json').read_text());assert proof['passed']and proof['ROM_sha256']==sha(rom);rows.append(dict(case=out.name,status='fresh_native',proof_sha256=sha(out/'native-proof.json')))
    (receipt/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(case=out.name,passed=True,draws=proof['draws'],updates=proof['updates'])),flush=True)
 result=dict(passed=True,accepted=False,group=a.group,cases=rows,one_sequential_worker=True,tool_sha256=sha(__file__),scope='Explicit granted native scope; per-case raw/cadence comparison remains separate.')
 (receipt/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
