"""One read of the root-authorized current debug; retain only palette callers."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
OUT=ROOT/'build/metal-storm-coexistence-1101-v9'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=OUT/'palette-inputs.json';inputs=json.loads(p.read_text());assert inputs['passed']
 witness=OUT/'native-palette-callers.json'
 if witness.exists():
  q=json.loads(witness.read_text());assert q['passed']and q['source_clauses']==inputs['native_palette_callers']and q['root_successor_ROM_sha256']==inputs['successor_ROM_sha256']
  # The one authorized debug read is already captured. Rebind a changed input
  # inventory only after confirming the exact used caller clauses are equal.
  q['bindings']={str(p.resolve()):sha(p.read_bytes()),str(Path(__file__).resolve()):sha(Path(__file__).read_bytes())}
  witness.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,reused_captured_debug=True,retained_callers=[s['size']for s in q['spans']])));return
 dbg=ROOT/'build/karnov-host-resource-base-1101-v1/candidate.dbg';data=dbg.read_bytes();syms={};segs={}
 names=set('DrawBlock DrawBrickChunks DrawPowerUp PowerUpGfxTable SprObjectOffscrChk ObjectOffset AreaType Block_SprAttrib Block_Metatile BlockMetasprite PowerUpType FrameCounter Enemy_SprAttrib EnemyMetasprite LmPrivateGate'.split())
 for line in data.decode().splitlines():
  if not line.startswith(('sym\t','seg\t')):continue
  z=dict(x.split('=',1)for x in line[4:].split(',')if'='in x)
  if line.startswith('seg\t'):segs[z['id']]=z
  elif 'val'in z and z['name'].strip('"')in names:
   name=z['name'].strip('"')
   if name not in syms or z.get('type')=='lab':syms[name]=z
 assert set(syms)==names,(names-set(syms))
 installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=installed.read_bytes();pin=sha(raw)
 assert pin in[inputs['baseline_ROM_sha256'],inputs['successor_ROM_sha256']]
 def loc(name):
  s=syms[name];g=segs[s['seg']];return int(g['ooffs'],0)+int(s['val'],0)-int(g['start'],0)
 spans=[]
 for name,end in [('DrawPowerUp','PowerUpGfxTable'),('DrawBlock','DrawBrickChunks')]:
  lo,hi=loc(name),loc(end)+(4 if end=='PowerUpGfxTable'else 0);assert 0<hi-lo<200
  spans.append(dict(name=name,pc=int(syms[name]['val'],0),offset=lo,size=hi-lo,hex=raw[lo:hi].hex(),sha256=sha(raw[lo:hi])))
 q=dict(passed=True,native=False,installed=False,baseline_ROM_sha256=pin,root_successor_ROM_sha256=inputs['successor_ROM_sha256'],actual_current_debug=dict(path=str(dbg),sha256=sha(data),bytes=len(data),read_once=True,retained_copy=False),syms=syms,segs={k:v for k,v in segs.items()if k in{s.get('seg')for s in syms.values()}},spans=spans,source_clauses=inputs['native_palette_callers'],scope='Only current linked caller metadata and exact inherited native DrawBlock/DrawPowerUp bytes. Current99 successor ownership proves these intervals unchanged from installed1c. No wholeROM/debug copy, native game run or global ownership grant.',bindings={str(p.resolve()):sha(p.read_bytes()),str(Path(__file__).resolve()):sha(Path(__file__).read_bytes())})
 witness.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,source_debug_bytes=len(data),retained_callers=[s['size']for s in spans],ROM=pin)))
if __name__=='__main__':main()
