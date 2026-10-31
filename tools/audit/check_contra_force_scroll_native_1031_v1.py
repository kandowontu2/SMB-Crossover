"""Read-only full binding preflight; never starts an emulator."""
from pathlib import Path
import argparse,hashlib,json
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepared',type=Path,required=True);a=ap.parse_args()
 p=a.prepared.resolve();q=json.loads(p.read_text());assert q['prepared']and not q['native']and q['no_launch_performed']
 assert q['source_candidate']=='1cbbd1ccfb22614b206d2e6fe75c55795f31bd47c2bbeda127f0b1645baf9b7d'
 assert q['bounds']==dict(physical_frames=1800,gameplay_frames=1000,PNGs=4,files=64,bytes=536870912,emulator_timeout_seconds=90,process_timeout_seconds=105)
 for n,h in q['bindings'].items():assert sha(n)==h,('Prepared binding drift',n)
 rows=[]
 for packet in q['packets']:
  ready=Path(packet['ready']);assert sha(ready)==packet['ready_sha256'];v=json.loads(ready.read_text())
  for n,h in v['bindings'].items():assert sha(n)==h,('Packet binding drift',n)
  assert v['maximum_physical_frames']==1800 and v['gameplay_physical_frames']==1000 and v['host_timeout_seconds']==90
  assert v['normal_eight_sprites']and v['power_on']=='AllZeros'and not v['emulated_writes']and not v['movie']
  script=(ready.parent/'controller.lua').read_text();assert "OUTPUT..name..'.png','wb'"in script
  assert "maxX>=369 and maxCamera>=257"in script and'routeAfterMain()'in script
  assert not any(x in script for x in['emu.write(','emu.setState(','emu.loadSavestate('])
  rows.append(dict(identity=packet['name'],bindings=len(v['bindings']),ready_sha256=sha(ready)))
 print(json.dumps(dict(preflight=True,launched=False,prepared=str(p),prepared_sha256=sha(p),packets=rows),indent=2))
if __name__=='__main__':main()
