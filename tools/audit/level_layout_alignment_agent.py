"""List exact unrolled static column spans; alignment is evidence, not an edit plan."""
import collections,difflib,json
from level_layout_inventory_agent import R,O,load
from level_layout_compare_agent import classify,nc
def main():
 m=load(R/'reference/crossover/assets/45_com.smbc.level.LevelData_LevelDataXML.bin');nes=json.loads((O/'nes-column-inventory.json').read_text())['areas'];match=json.loads((O/'topology-comparison.json').read_text());out=[]
 for z in match:
  a=m[z['area']];nk=z['best_nes_area'];off=z['offset'];w=len(a['MAP'][0]);off=0 if z['area']in('1-1a','1-2b')else off
  nw=int(round(w/16))*16 if off==0 else w
  if z['area']=='8-4a':nw=256
  old=[''.join(nc(nes[nk]['rows'][y][x+off])for y in range(13))for x in range(nw)]
  new=[''.join(classify(a['MAP'][y+2][x])if'charHorz'not in a['MAP'][y+2][x]and'charVert'not in a['MAP'][y+2][x]else'0'for y in range(13))for x in range(w)]
  sm=difflib.SequenceMatcher(a=old,b=new,autojunk=False);ops=[]
  for kind,i,j,k,l in sm.get_opcodes():
   if kind=='equal':continue
   ops.append(dict(operation=kind,original_columns=[i+off,j+off],crossover_columns=[k,l],original_cells=[dict(x=x+off,y=y+2,value=old[x][y],raw_tile=nes[nk]['rows'][y][x+off])for x in range(i,j)for y in range(13)if old[x][y]!='0'],crossover_cells=[dict(x=x,y=y+2,value=new[x][y],raw_tile=a['MAP'][y+2][x])for x in range(k,l)for y in range(13)if new[x][y]!='0']))
  out.append(dict(area=z['area'],original_area=nk,offset=off,original_width=nw,crossover_width=w,matching_columns=sum(b.size for b in sm.get_matching_blocks()),column_operations=ops,caveat='8-4a /4-4 /7-4 use different native loop/transport representations; these literal static spans are not equivalent player routes.'if z['area']in('8-4a','4-4a','7-4a')else None))
  if len(ops)>2 or nw!=w:print(z['area'],nk,nw,w,[(v['operation'],v['original_columns'],v['crossover_columns'])for v in ops])
 (O/'static-column-alignments.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
