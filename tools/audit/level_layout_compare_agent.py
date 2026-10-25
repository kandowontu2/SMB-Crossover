"""Compare solid/interactable topology without confusing map-skin renames with edits."""
from pathlib import Path
import collections,json,re,sys
from level_layout_inventory_agent import R,O,load
def classify(v):
 name=v.split('&&')[0]
 if name.startswith('itemBlock'):return 'H'if 'Invisible'in name else 'Q'
 if name.startswith('brick'):return'B'
 if name.startswith('spring'):return'J'
 if 'flagPole'in name:return'F'
 if name.startswith(('ground','block','box','cloudFace','bowserBridge')):return'S'
 return'0'
def nc(v):
 if v in(0x24,0x25,0x6d):return'F'
 if v in(0x5f,0x60):return'H'
 if v in(0xc0,0xc1):return'Q'
 if v in(0xc2,0xc3,0xc5):return'0'
 if v==0x67:return'0' # Invisible upper rendering half of the spring object.
 if v==0x68:return'J'
 if 0x51<=v<=0x53 or 0x55<=v<=0x5e:return'B'
 if 0x10<=v<=0x23 or 0x54==v or 0x61<=v<=0x66 or 0x69<=v<=0x6c or v in(0x88,0x89,0xc4):return'S'
 return'0'
def cells(a):return{(x,y):classify(v)for y,row in enumerate(a['MAP'])for x,v in enumerate(row)if 'charHorz'not in v and'charVert'not in v and classify(v)!='0'}
def main():
 paths=[R/'reference/crossover/assets/45_com.smbc.level.LevelData_LevelDataXML.bin',R/'reference/crossover2/extracted/binaryData/322_com.smbc.level.LevelData_LevelDataXML.bin']
 maps=[load(p)for p in paths];nes=json.loads((O/'nes-column-inventory.json').read_text())['areas'];out=[]
 old={z['area']:z for z in json.loads((O/'topology-comparison.json').read_text())}if'--reuse-mapping'in sys.argv else{}
 for k,a in maps[0].items():
  c=cells(a);width=max(map(len,a['MAP']));c={p:v for p,v in c.items()if p[1]>=2}
  matches=[]
  for nk,n in nes.items():
   offsets=range(0,400-width+1)
   if old:
    if nk!=old[k]['best_nes_area']:continue
    offsets=[old[k]['offset']]
   for off in offsets:
    dif=[]
    for y in range(2,15):
     row=a['MAP'][y]
     for x in range(width):
      v=c.get((x,y),'0');u=nc(n['rows'][y-2][x+off])
      if u!=v:dif.append((x,y,u,v))
    matches.append((len(dif),nk,off,dif))
  matches.sort(key=lambda x:x[:3]);best=matches[0]
  b=maps[1][k];cc={p:v for p,v in cells(b).items()if p[1]>=2};changes=[]
  for p in sorted(set(c)|set(cc)):
   if c.get(p,'0')!=cc.get(p,'0'):changes.append(dict(x_tile=p[0],y_tile=p[1],early=c.get(p,'0'),later=cc.get(p,'0'),early_raw=a['MAP'][p[1]][p[0]],later_raw=b['MAP'][p[1]][p[0]]))
  out.append(dict(area=k,dimensions=[width,15],best_nes_area=best[1],offset=best[2],mismatches=len(best[3]),nes_early_differences=best[3],next_matches=[m[:3]for m in matches[:4]],early_later_topology_changes=changes))
  print(k,best[:3],'early-later=',len(changes),flush=True)
 (O/'topology-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
