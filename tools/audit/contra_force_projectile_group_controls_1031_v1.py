"""Paired complete native/CF OAM+normalNMI groups after exact mask factor."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
G=A.G;OLD=R/'build/contra-force-world-chr-publisher-1031-v1';NEW=R/'build/contra-force-projectile-contact-1031-v3';O=R/'build/contra-force-projectile-group-controls-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):A.K=p/'kernel';A.bind(p)
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,rows=[])
 try:
  bind(OLD);old=[A.V.scene(v)for v in range(4)]
  bind(NEW);new=[A.V.scene(v)for v in range(4)]
  for v in range(4):
   for epoch in range(4):
    outputs=[]
    for p,m in[(OLD,old[v]),(NEW,new[v])]:
     bind(p);cap,z=G.draw(m);n=A.F.normal(m)
     outputs.append(dict(AXYP=z['AXYP'],CPU=z['CPU'],SP=z['minimum_SP'],rotation=cap['rotation'],early=cap['early'],prelate=cap['prelate'],final=list(m[512:768]),palettes=list(m.vram[0x3f00:0x3f20]),CHR=list(m.chr_latches),maps=m.rawtags[:],SMC=A.T.smc(m),last=A.T.get(m,'SmFreezeLastBlue'),pending=A.T.get(m,'SmFreezePalettePending')))
    a,b=outputs
    assert all(a[k]==b[k]for k in a if k not in('CPU','SP')),(v,epoch,[(k,a[k],b[k])for k in a if a[k]!=b[k]])
    d['rows'].append(dict(variant=v,epoch=epoch,CPU_delta=b['CPU']-a['CPU'],minimum_SP=[a['SP'],b['SP']],Last=b['last'],normalNMI_patterns_palettes_complete_OAM_exact=True))
  d.update(passed=True,actual_complete_DrawAll_normalNMI_pairs=len(d['rows']),four_classes_both_palette_epochs=True,scope='Loader-authenticated explicit existing body+shot+native world scene. Full native-before/CF/late group output+real normalNMI final CHR/palette paired against a441. No new original-action legality or native run claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(A.__file__),Path(G.__file__),OLD/'source-stage.json',NEW/'source-stage.json',NEW/'kernel/runtime.lbl'];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],pairs=len(d['rows']),error=d.get('error'))),flush=True)
if __name__=='__main__':main()
