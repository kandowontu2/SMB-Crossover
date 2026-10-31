"""Retained stale CF C1 packet through actual completed normal-NMI consumer."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_loader_isr_controls_v2 as U
import contra_force_p1_native_first_controls_v3 as V
Q,T,C=V.Q,V.T,V.C;U.B=T.B;O=R/'build/contra-force-p1-stale-palette-ppu-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def normal(m):
 T.put(m,NmiDisable=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,SavedJoypadBits=0)
 m[21028]=128;m.ppu_log.clear();c=T.NesMPU(memory=m,pc=32767);c.sp=192;c.p=0x30
 proof=U.interrupt(m,c,'NMI',keep_ppu=False)
 return dict(**proof,paletteP1=list(m.vram[0x3f15:0x3f18]),PPU=m.ppu_log,hardwareCHR=m.chr_latches[:],pending=T.get(m,'SmFreezePalettePending'))
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,ready=False,checks={})
 try:
  m=V.scene();rows=[]
  for age in range(5):
   d=V.draw(m);n=normal(m);rows.append(dict(draw=d,normalNMI=n))
  out['checks']['completed_five_draw_palette_pairs']=rows
  assert [r['draw']['Last']for r in rows]==[193,192,193,192,193]
  m.ram[2][0x1fe0]^=1;d=V.draw(m);n=normal(m)
  out['checks']['rejected_cache_native_frame']=dict(draw=d,normalNMI=n,visibleP1=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240 and m[514+i]&3==1])
  assert d['hits']==['nativeDraw']
  assert n['paletteP1']==[26,48,39],('stale CF yellow through actual normalNMI',n['paletteP1'])
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(V.__file__),Path(U.__file__),V.P/'source-stage.json',V.P/'joint/candidate.nes',R/'build/contra-force-p1-stale-palette-ppu-v1/controls.json',R/'build/contra-force-p1-native-first-controls-v3/controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'))),flush=True)
if __name__=='__main__':main()
