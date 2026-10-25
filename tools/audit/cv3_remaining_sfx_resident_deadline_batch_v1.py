"""Four bounded HELD cases with exact NMI/IRQ return observations, sequential only."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);a=p.parse_args();receipt=a.prepared/'deadline-batch-v1';receipt.mkdir(exist_ok=False);shutil.copyfile(__file__,receipt/Path(__file__).name);rows=[]
 for mode,label,event,profile in [(0,'easy-lightning',0x1e,'basic'),(0,'easy-priority',0x21,'priority'),(1,'hard-ice',0x21,'basic'),(1,'hard-priority',0x21,'priority')]:
  for version,rom in [('candidate',a.prepared/'candidate.nes'),('baseline',D/'cv3-remaining-current50b-v1/baseline.nes')]:
   out=a.prepared/'native-timing-v2'/f'{version}-{label}';cmd=[sys.executable,str(ROOT/'tools/audit/cv3_remaining_sfx_resident_native_v2.py'),'--rom',str(rom),'--output',str(out),'--mode',str(mode),'--event',hex(event),'--profile',profile,'--run']
   with(receipt/(out.name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
   assert not r.returncode,(out.name,(receipt/(out.name+'.host.log')).read_text()[-4000:]);j=json.loads((out/'native-proof.json').read_text());assert j['passed']and j['ROM_sha256']==sha(rom);rows.append(dict(case=out.name,proof_sha256=sha(out/'native-proof.json')));(receipt/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(case=out.name,passed=True,draws=j['draws'],updates=j['updates'])),flush=True)
 (receipt/'proof.json').write_text(json.dumps(dict(passed=True,accepted=False,cases=rows,one_sequential_worker=True,tool_sha256=sha(__file__),scope='Four original HELD same-work cases; added timing only, no gameplay or assertion changes.'),indent=2)+'\n')
if __name__=='__main__':main()
