"""Existing valid-CF groups on the private59B factoring, no own CF edits."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
G=A.G;P=R/'build/contra-force-world-roles-1031-v2';J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-valid-cf-palette-rebind-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(child):
 A.K=P/'kernel';A.bind(P)
 if child:A.T.B=A.T.qualified(J/'candidate.nes');A.U.B=A.T.B
def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,rows=[])
 try:
  bind(False);old=[A.V.scene(v)for v in range(4)]
  bind(True);new=[A.V.scene(v)for v in range(4)]
  for v in range(4):
   for epoch in range(4):
    result=[]
    for child,m in[(False,old[v]),(True,new[v])]:
     bind(child);cap,z=G.draw(m);n=A.F.normal(m)
     result.append(dict(AXYP=z['AXYP'],CPU=z['CPU'],SP=z['minimum_SP'],rotation=cap['rotation'],early=cap['early'],prelate=cap['prelate'],final=list(m[512:768]),palettes=list(m.vram[0x3f00:0x3f20]),CHR=list(m.chr_latches),maps=m.rawtags[:],last=A.T.get(m,'SmFreezeLastBlue'),pending=A.T.get(m,'SmFreezePalettePending'),cache=[bytes(a).hex()for a in m.ram]))
    a,b=result;assert all(a[k]==b[k]for k in a if k not in ['CPU','SP']),(v,epoch,[k for k in a if a[k]!=b[k]])
    q['rows'].append(dict(variant=v,epoch=epoch,CPU_delta=b['CPU']-a['CPU'],minimum_SP=[a['SP'],b['SP']],native_CF_whole_groups_PPU_CHR_state_exact=True))
  q.update(passed=True,candidate=sha(J/'candidate.nes'),actual_valid_CF_paired_groups=len(q['rows']),native=False,scope='Existing legal loader-authenticated explicit body+shot+Koopa-P1 scene, all4classes and4epochs. Exact native/CF prelate/final whole OAM, PPU/CHR, own state and returnedAXYP against unchanged a126. Extra transport CPU disclosed; no CF source or new readiness.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(G.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/cf-stream.bin',P/'joint/cf-cookie.bin',P/'kernel/runtime.lbl']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in['passed','candidate','actual_valid_CF_paired_groups','error']}))
if __name__=='__main__':main()
