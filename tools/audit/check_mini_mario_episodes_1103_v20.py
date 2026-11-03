"""Whole source-state episodes and guarded private writes, no emulator."""
from pathlib import Path
import json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
import check_mini_mario_step_1103_v18 as T
R,O=W.R,W.O

class Guarded(list):
 def __init__(self,values):super().__init__(values);self.live=False;self.writes=set()
 def __setitem__(self,key,value):
  if self.live:
   keys=range(key.start or 0,key.stop or len(self),key.step or 1)if isinstance(key,slice)else[key]
   for k in keys:
    assert 0x100<=k<0x200 or 0xc200<=k<=0xc280 or 0xc2e0<=k<=0xc2e9,hex(k)
    self.writes.add(k)
  super().__setitem__(key,value)

def main():
 T.compile_c();data=(O/'world-step-v16.bin').read_bytes();r=json.loads((O/'world-step-v16.json').read_text());L=r['exports']
 scenarios=[('idle',0,0,[0]*180),('right-left-run',0,0,[1]*100+[2]*100+[0x41]*150+[0]*100),('jump-held',0,0,[0]*8+[0x80]*80+[0]*90),('jump-tap',0,0,[0]*8+[0x80]+[0]*90),('walk-jump',0,0,[1]*40+[0x81]*80+[0]*60),('run-jump',0,0,[0x41]*40+[0xc1]*80+[0]*60),('crouch-small',0,0,[0]*8+[4]*40+[0]*20+[0x84]*4+[0]*80),('crouch-powered',0,1,[0]*8+[4]*40+[0]*20+[0x84]*4+[0]*80),('powered-ceiling',2,1,[0]*8+[0x80]*80+[0]*90),('wall',1,0,[0x41]*180),('step-up',4,0,[0x41]*20+[0xc1]*80+[1]*80)]
 records=[];outputs=[];summaries=[];allwrites=set();cycles=[]
 for name,f,t,buttons in scenarios:
  m=T.memory(data,L,f);m.memory=Guarded(m.memory);T.call(m,L['MiniInit']);state=T.initial(3,48*16,200*16-1,0,t);m.memory[0xc200:0xc281]=state;m.memory[0xc22a:0xc22c]=[0,2]
  m.memory.live=True;ys=[];xs=[];q=[];head=0
  for b in buttons:
   m.memory.live=False;m.memory[0xc248]=b;m.memory.live=True
   before=bytes(m.memory[0xc200:0xc281]);records.append(before+bytes([f]));cycles.append(T.call(m,L['MiniStep']));outputs.append(bytes(m.memory[0xc200:0xc281]))
   x=m.memory[0xc250]|m.memory[0xc251]<<8;y=m.memory[0xc252]|m.memory[0xc253]<<8;xs.append(x);ys.append(y);q.append(m.memory[0xc228]);head+=m.memory[0xc25c]
  allwrites|=m.memory.writes
  summaries.append(dict(name=name,updates=len(buttons),X_range16_4=[min(xs),max(xs)],Y_range16_4=[min(ys),max(ys)],final_X16_4=xs[-1],final_Y16_4=ys[-1],queued_states=sorted(set(q)),head_requests=head))
  assert m.memory[0xc247]==0,name
  if name=='idle':assert xs[0]==xs[-1]and q[-1]==4 and ys[-1]==3215
  if name=='jump-held':assert 3215-min(ys)==600,(name,min(ys))
  if name=='jump-tap':assert 3215-min(ys)<600,name
  if name=='powered-ceiling':assert head>0,name
  if name=='wall':assert max(xs)==1439,(name,max(xs))
 p=subprocess.run([str(O/'original-world-v18.exe')],input=b''.join(records),capture_output=True);assert p.returncode==0 and len(p.stdout)==129*len(records)
 for i,actual in enumerate(outputs):
  expected=p.stdout[i*129:(i+1)*129];diffs=[(hex(0xc200+j),actual[j],expected[j])for j in T.CHECK if actual[j]!=expected[j]];assert not diffs,(i,diffs)
 # Explicit coyote and buffer fixtures: original values2; decrement sameframe.
 edges=[]
 for kind,initial,inputs in [('coyote-available',T.initial(1,48*16,180*16,0),[128,128]),('coyote-expired',T.initial(1,48*16,180*16,0),[0,0,128]),('buffer-landing',T.initial(1,48*16,199*16,0),[128,0,128])]:
  initial[65]=2 if kind.startswith('coyote')else 0;initial[32:34]=(8192).to_bytes(2,'little')
  m=T.memory(data,L,0);m.memory[0xc200:0xc281]=initial;m.memory[0xc22a:0xc22c]=[0,2];trace=[]
  for held in inputs:
   m.memory[0xc248]=held;b=bytes(m.memory[0xc200:0xc281]);T.call(m,L['MiniStep']);a=bytes(m.memory[0xc200:0xc281]);p=subprocess.run([str(O/'original-world-v18.exe')],input=b+b'\0',capture_output=True);assert all(a[j]==p.stdout[j]for j in T.CHECK)
   trace.append(dict(q=a[40],ct=a[65],jb=a[66],hold=a[36]))
  if kind=='coyote-available':assert trace[0]['q']==12 and trace[1]['hold']==0
  if kind=='coyote-expired':assert trace[-1]['q']==1 and trace[-1]['jb']==1
  if kind=='buffer-landing':assert trace[0]['q']==3 and trace[0]['jb']==1 and trace[1]['q']==12
  edges.append(dict(name=kind,trace=trace))
 # Explicit worldX extension: shift both player and legal native terrain by2048.
 ext=0
 for x in [0,1,7,8,15,16,39,40,79,80,89,90,111,112,150]:
  for b in [0,1,2,0x80,0x81]:
   a=T.memory(data,L,0);z=T.memory(data,L,0);v=T.initial(3,(48+x)*16,3215,b);v[90:92]=(190*16).to_bytes(2,'little');a.memory[0xc200:0xc281]=v
   v[80:82]=(int.from_bytes(v[80:82],'little')+32768).to_bytes(2,'little');v[88:90]=(32768).to_bytes(2,'little');v[90:92]=(190*16+32768).to_bytes(2,'little');z.memory[0xc200:0xc281]=v
   for m in[a,z]:m.memory[0xc22a:0xc22c]=[0,2];T.call(m,L['MiniStep'])
   assert ((z.memory[0xc250]|z.memory[0xc251]<<8)-(a.memory[0xc250]|a.memory[0xc251]<<8))==32768
   assert a.memory[0xc252:0xc254]==z.memory[0xc252:0xc254]and a.memory[0xc228]==z.memory[0xc228];ext+=1
 out=dict(passed=True,source_C_whole_step_updates=len(records),episodes=summaries,coyote_buffer=edges,worldX_2048_translation_cases=ext,cycles=[min(cycles),max(cycles)],write_domain=dict(private_bytes=len([x for x in allwrites if x>=0xc200]),host_ZP_writes=0,headers_writes=0,native_BlockBuffer_writes=0,allowed=['C200..C280','C2E0..C2E9','stack0100..01FF']),component_SHA256=W.sha(data),native_admitted=False,scope='Source C literal dispatcher plus ground/fall/crouch/skid/jump bodies. Flat floor, wall,32pxstep,poweredceiling,held/tapped/running jumps and crouch legal noactor fixtures. Native16px terrain adapted to source8px flags. 16-bit worldX extension explicitly tested, not claimed donor GB behavior.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),R/'tools/reference/mini_mario_world_1103_v16.inc',O/'world-step-CPU-v18.json']})
 (O/'world-episodes-CPU-v20.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
