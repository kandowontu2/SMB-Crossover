"""Original sustained jump, complete Main, and retained native short-hold facts."""
from pathlib import Path
import csv,itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_control_controls_v1 as source
import rogue_dawn_side_controls_v1 as host
v,q,get,put=host.v,host.q,host.get,host.put
O=R/'docs/qa/rogue-dawn-jump-hold-source-2026-10-29.json'

class Source(source.Runner):
 def callback(self,c,n):
  before=self.get(0x30d);super().callback(c,n)
  # Genuine E4EC is part of a committed downpixel. The old rectangle
  # adapter omitted it; frozen original control/proof files stay untouched.
  if n=='RdHostMoveDown'and self.get(0x30d)!=before:self.set(0x30f,self.get(0x30f)-1)

def main():
 assert not O.exists(),'Preserve proof'
 b=v.scoped_load(host.O/'candidate.nes');p=R/'build/rogue-dawn-control-v1'
 compiled=((p/'control.bin').read_bytes(),(p/'aux.bin').read_bytes(),(p/'art.bin').read_bytes(),source.symbols(p/'control.lbl'),{})
 raw=source.ref.ROM.read_bytes();assert source.ref.digest(raw)==source.ref.EXPECTED
 rows=[]
 for style,left in itertools.product(['stand','run','aim'],[False,True]):
  direction=2 if left else 1;pre=[0]*8+([direction]*12 if style=='run'else[8]*4 if style=='aim'else[])
  jump=128|(direction if style=='run'else 8 if style=='aim'else 0)
  s=source.state(gear=0x41,y=193,x=128);s.update({0x301:15,0x302:4,0x4d:int(left)})
  n=Source(raw,compiled,False,source.World(floor=208,ceiling=0,left=0,right=255),s)
  m=host.ready(b,0,px=128);source_rows=[];host_rows=[]
  for kind in['source','completeMain']:
   records=[]
   for i in range(len(pre)+140):
    if i<len(pre):pad=pre[i]
    elif i==len(pre):pad=jump
    else:
     action=n.get(0x300)if kind=='source'else get(m,'RdAction')
     vy=n.get(0x308)if kind=='source'else get(m,'RdVY')
     pad=(jump&~128)|(128 if action in[1,2,6]and vy>=128 else 0)
    if kind=='source':
     n.step(pad,i);r=dict(i=i,pad=pad,y=n.get(0x30d),VY=n.get(0x308),action=n.get(0x300),gravity=n.get(0x314))
    else:
     put(m,SavedJoypadBits=pad);q.mainstep(m);r=dict(i=i,pad=pad,y=get(m,'RdY'),VY=get(m,'RdVY'),action=get(m,'RdAction'),gravity=get(m,'RdGravity'));v.nmi(m)
    records.append(r)
    if i>len(pre)+20 and r['y']==193 and r['VY']==0:break
   target=source_rows if kind=='source'else host_rows;target.extend(records)
  peakS=min(r['y']for r in source_rows);peakH=min(r['y']for r in host_rows)
  assert peakS==peakH==109,(style,left,peakS,peakH)
  assert source_rows[-1]['y']==host_rows[-1]['y']==193,(style,left,source_rows[-1],host_rows[-1])
  air_actions=sorted({r['action']for r in host_rows if r['VY']>=128})
  if style=='run':assert1=1 in air_actions;assert assert1
  rows.append(dict(style=style,left=left,original_peak_centerY=peakS,host_peak_centerY=peakH,
   native_PlayerY_at_peak=peakH-16,rise=193-peakH,original_updates=len(source_rows),actual_Main_updates=len(host_rows),
   actual_ascending_actions=air_actions,source_rows=source_rows,actual_Main_rows=host_rows))
 native=R/'build/verification/rogue-dawn-side-native-easy-v1'
 result=json.loads((native/'result.json').read_text());assert result['passed']is False and result['reason']=='finite frame bound'
 trace=list(csv.DictReader((native/'trace.csv').open()));segs=[]
 for r in trace:
  if int(r['frame'])<3000 or int(r['x'])not in range(281,285):continue
  on=bool(int(r['mask'])&128)
  if not segs or segs[-1]['A']!=on:segs.append(dict(A=on,rows=[]))
  segs[-1]['rows'].append(r)
 arcs=[]
 for i,s in enumerate(segs[:-1]):
  if not s['A']or len(s['rows'])!=32:continue
  a=s['rows'];following=segs[i+1]['rows'];arc=a+following
  arcs.append(dict(A_first_PPU=int(a[0]['frame']),A_last_PPU=int(a[-1]['frame']),A_polls=len(a),
   observed_Main_counter_increments_while_A=int(a[-1]['loops'])-int(a[0]['loops']),
   min_native_PlayerY=min(int(r['y'])for r in arc),observed_rise=177-min(int(r['y'])for r in arc)))
 assert arcs and all(a['observed_Main_counter_increments_while_A']<32 for a in arcs)
 proof=dict(passed=True,source_CPU_only=True,native_successor_run=False,
  canonical='Original normal no-HighJump held jump rises84px, and actual completeMain rises84px (PlayerY177->93). The52px hypothesis is not a canonical jump limit. Native short-hold peaks vary with lag; no physics/delivery/platform change is justified.',
  source_provenance='Actual original CFC3 starts VYFC/gravity18hex; D002..D014 cuts ascent after at least32px if heldA is released. Complete genuine action dispatch/draw/motion uses declared external flat geometry, body-only original decoder metadata. Source room pipeline is not reconstructed.',
  input_only_criterion='After an actual requested fresh jump, preserve A while actual RdAction is1,2or6 and signedRdVY<0. Action1 is genuine running/spinning jump and cannot be omitted. Ceilings/apex makeVYnonnegative; no state/physics writes.',
  comparisons=rows,native_short_hold_arcs=arcs,
  native_scope='Read-only closed native trace: per-PPU rows can omit intermediate Main states/catch-up updates. Report observed counter increments and captured peaks, not a fabricated per-Main RAM timeline. Original finite7000FALSE retained.',
  bindings=[v.ref.binding(x)for x in[Path(__file__),host.O/'handoff.json',host.O/'candidate.nes',host.O/'candidate.dbg',host.O/'candidate.lbl',
   source.ref.ROM,p/'control.bin',p/'aux.bin',p/'art.bin',p/'control.lbl',R/'tools/rogue_dawn_control_controls_v1.py',R/'tools/playthroughs/rogue_dawn_opening_route_v1.lua',
   native/'result.json',native/'trace.csv',native/'inputs.csv']])
 O.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,source_cases=len(rows),rise=84,native_short_hold_arcs=len(arcs),report=v.ref.binding(O))))
if __name__=='__main__':main()
