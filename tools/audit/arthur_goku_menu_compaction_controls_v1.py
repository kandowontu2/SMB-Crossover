"""Same original pending OAM/palette output for the coordinate compaction."""
from pathlib import Path
import json,traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_visuals58_v1 as B
R=B.R;P=R/'build/functional-roster-coherent62-v4/joint';J=R/'build/arthur-goku-select-remap-v3/joint';O=J.parent;T=A.T

def main():
 out=O/'preview-compaction-controls.json';assert not out.exists();d=dict(passed=False,native=False);rows=[]
 try:
  base=[T.bus(x)for x in[P,J]]
  for index in range(33):
   if index==9:continue # Intentionally retired Goku pending art -> blankBT.
   for p in A.FLAGS:
    mm=[T.fork(m)for m in base]
    zz=[A.S.execute(m,'FmDrawPreviewSelected',A=index,X=0x5a,Y=0xc7,P=p)for m in mm]
    assert zz[0][0]==zz[1][0],('actual returned AXYP/SP',index,p,zz)
    assert mm[0].ram[:0x100]==mm[1].ram[:0x100],('ZP',index,p)
    assert mm[0].ram[0x200:0x300]==mm[1].ram[0x200:0x300],('original complete64OAM',index,p)
    assert mm[0].get('CurrentOAMOffset')==mm[1].get('CurrentOAMOffset')
    for name in['VRAM_Buffer1','CurrentCHRBank']:
     size=84 if name=='VRAM_Buffer1'else 12
     assert bytes(mm[0].ram[mm[0].lab[name]:mm[0].lab[name]+size])==bytes(mm[1].ram[mm[1].lab[name]:mm[1].lab[name]+size]),(index,p,name)
    assert mm[0].chr==mm[1].chr and mm[0].upper==mm[1].upper and mm[0].wram==mm[1].wram
    rows.append([index,p,zz[1][1]-zz[0][1]])
  d.update(passed=True,all64flags=64,unchanged_pending_portrait_indices=32,actual_OAM_palette_CHR_pairs=len(rows),CPU_delta=[min(r[2]for r in rows),max(r[2]for r in rows)],rows=rows,scope='Actual same original16x32/24x32 pending renderer output for every unchanged index, not screenshot normalization. BTindex9 deliberatelyblank and pending; no authenticatedBTpixels joined yet.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc(),completed_pairs=len(rows))
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg']}
 B.write(out,json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings','traceback']}));assert d['passed'],d.get('error')

if __name__=='__main__':main()
