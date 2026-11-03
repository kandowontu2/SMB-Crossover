"""Keep162 grounded-Y negative; trace actual export/BG/render/Main order."""
from pathlib import Path
from collections import Counter
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
O,N,I=V.O,V.N,V.I


def main():
 text=inspect.getsource(V.main);mark=' e,m,labels=first8();';assert mark in text
 text=text[:text.index(mark)]+''' return dict(base=base,manifest=manifest,cold=cold,colors=colors,names=names,events=dict(events))
'''
 env=dict(V.__dict__);exec(compile(text,str(Path(V.__file__)),'exec'),env);services=env['main']()
 e,m,lab=V.first8();base=services['base'];points={}
 for name in ['PlayerBGCollision','PlayerGfxHandler','GameCoreRoutine','MovePlayerVertically','PlayerMovementSubs','ScrollHandler']:
  if name in base['syms']:points[I.address(base,name),((I.location(base,name)-16)//8192)|128]=name
 actual=N.NesMPU;rows=[];epoch=0
 def sample(event,pc,old=None):
  rows.append(dict(epoch=epoch,event=event,PC=pc,Amap=m.rawtags[1],Cmap=m.rawtags[2],X=N.get(m,'Player_X_Position'),Y=N.get(m,'Player_Y_Position'),previousY=old,foot=m.ram[2][0x84]+256*m.ram[2][0x85],sourceY=m.ram[2][0x611],delta=m.ram[2][0x88],origin=m.ram[2][0x89]+256*m.ram[2][0x8a],sourceAction=m.ram[2][0x616],sourceState=m.ram[2][0x618],nativeState=N.get(m,'Player_State'),nativeYSpeed=N.get(m,'Player_Y_Speed')))
 class Trace(actual):
  def step(self):
   tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None;pc=self.pc;old=N.get(m,'Player_Y_Position')
   if(pc,tag)in points:sample(points[pc,tag],pc)
   result=super().step()
   if N.get(m,'Player_Y_Position')!=old:sample('nativeY-write',pc,old)
   return result
 N.NesMPU=Trace
 try:
  for epoch in range(49):
   if epoch:m.controller_pad=1;N.put(m,SavedJoypad1Bits=1,SavedJoypadBits=1)
   e['run'](m,'GameLoop',lab);sample('completed-GameLoop',0)
 finally:N.NesMPU=actual
 completed=[r for r in rows if r['event']=='completed-GameLoop'];draw=[r for r in rows if r['event']=='PlayerGfxHandler']
 assert completed[0]['Y']==176 and completed[0]['foot']==208 and completed[-1]['X']>completed[0]['X']
 q=dict(passed_native_service_subset=True,grounded_stability_qualified=False,source_code_injected=False,ROM_written=False,memory_SHA256=services['manifest']['expected_memory_only_SHA256'],actual_fullcold_CPU=services['cold']['CPU'],actual_colors_cases=services['colors'],actual_status_cases=services['names'],complete_WriteGameText_PRINCE=True,actual_ingress_counts=services['events'],strict_native_advance=[completed[0]['X'],completed[-1]['X']],completed_Main_Y=sorted({r['Y']for r in completed}),render_ingress_Y=sorted({r['Y']for r in draw}),first8_exact_Y176_foot208=True,trace=rows,scope='All160 actual backdrop/name/fullcold/faultretry assertions complete before tracing original49GameLoops. Keeps162 constantgroundY negative unresolved; no completed-Main or render stability relaxation/physics edit. Trace identifies every actual nativeY write and BG/render ingress with sourcefoot/delta and completeMain endpoint. Palette/status subset is qualified, traversal/playability/nativebody remains pending.',bindings={p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'backdrop-manifest-v159.json',O/'backdrop-native-negative-v162.json',O/'walk-height-diagnostic-v161.json']})
 (O/'grounded-order-v163.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','trace']}));print(json.dumps([r for r in rows if r['epoch']in [26,27,28]]))


if __name__=='__main__':main()
