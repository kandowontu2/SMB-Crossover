"""Compose independently owned ROM changes, rejecting every preimage conflict."""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sha=lambda x:hashlib.sha256(x).hexdigest()

def merge(current,before,after,name):
 assert len(current)==len(before)==len(after)
 changed=[i for i,(a,b)in enumerate(zip(before,after))if a!=b]
 conflicts=[i for i in changed if current[i]!=before[i]]
 assert not conflicts,(name,'preimage conflicts',conflicts[:12])
 spans=[]
 for i in changed:
  if spans and i==spans[-1][1]:spans[-1][1]=i+1
  else:spans.append([i,i+1])
 for i in changed:current[i]=after[i]
 return dict(name=name,before_sha256=sha(before),after_sha256=sha(after),changed_bytes=len(changed),file_spans=spans)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--shinobi',type=Path,required=True);ap.add_argument('--arthur',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 out=args.output.resolve();assert out.is_relative_to(R/'build');out.mkdir(exist_ok=True)
 base=R/'build/shinobi-camera-1101-v20/candidate.nes'
 raw=bytearray(args.shinobi.read_bytes());receipts=[]
 # Shinobi successor must retain every installed change that preceded Metal41.
 sh=base.read_bytes();v40=(R/'build/metal-storm-decline-1101-v40/candidate.nes').read_bytes();v41=(R/'build/metal-storm-idle-shots-1101-v41/candidate.nes').read_bytes()
 assert sha(v41)=='27dee145eead745dfe94cc6e4734a88fdd03811c7f7c3c9d1ee55e54d3057318'
 receipts.append(merge(raw,v40,v41,'Metal Storm installed no-shot fast return'))
 if args.arthur:receipts.append(merge(raw,v41,args.arthur.read_bytes(),'Arthur authentication and camera'))
 rom=out/'candidate.nes';rom.write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(out/('candidate'+suffix)).write_bytes(args.shinobi.with_suffix(suffix).read_bytes())
 q=dict(assembled=True,installed=False,ROM_sha256=sha(raw),shinobi_base_sha256=sha(sh),shinobi_successor_sha256=sha(args.shinobi.read_bytes()),patches=receipts,native_pending=True)
 (out/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
