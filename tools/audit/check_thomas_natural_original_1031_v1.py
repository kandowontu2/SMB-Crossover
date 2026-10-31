"""Original donor actor oracle with the explicit native-SMB actor projection.

Original omitted enemy slots87..8C are inactive; player slot8D is retained.
Real linked source is acquired by ThLoad, not fixture-preloaded. The separate
natural receipt covers actual menu/parser/Main and terrain reconciliation.
"""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import thomas_original_cpu_1031_v1 as T
import check_thomas_actual_host_vectors_1031_v1 as A
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
J=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-natural-original-controls-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def original_hunk(c,start,stop):
 c.pc=start;c.sp=224
 for i in range(20000):
  if c.pc==stop:return
  if c.pc==0xacdf:c.pc=(c.stPopWord()+1)&65535;continue
  c.step()
 raise AssertionError(('original hunk bound',hex(start),hex(c.pc)))
def original_cold(player):
 c=T.machine();c.memory[0x55]=player;c.memory[0x5f]=0
 T.run(c,0x84f0);T.run(c,0x8563);c.memory[0x52]=0;T.run(c,0xa8eb)
 # Source-owned host projection: none of the six donor enemies is integrated
 # into SMB. Keep the original player slot6 ($8D) completely intact.
 for i in range(0x87,0x8d):c.memory[i]=0
 return c
def original_frame(c,pad):
 original_hunk(c,0x830d,0x8319);original_hunk(c,0x8321,0x8338)
 T.run(c,0x9002,a=pad,x=c.memory[0x55]);c.memory[0x6a]=c.memory[0x14+c.memory[0x55]*2]
 original_hunk(c,0x87b5,0x87e0);c.pc=0xc208
 for _ in range(20):
  if c.pc in[0xc218,0xc224]:break
  c.step()
 else:raise AssertionError('original attack boundary')
 if c.pc==0xc224:
  c.memory[0x0a]=0;T.run(c,0xc65b,x=6);attack=(1,c.memory[0x379],bytes(c.memory[:4]))
 else:T.run(c,0xc218);attack=(0,0,bytes(4))
 T.run(c,0xa826)
 if c.memory[0x38f]:T.run(c,0xa8eb)
 return attack
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False)
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(J/'candidate.nes');s=T.labels(J/'candidate.lbl')
  def candidate(player):
   m=L.make(b,SelectedCharacter=10,FmAlts=64,CurrentPlayer=player,Player_Rel_XPos=120,Player_Rel_YPos=160)
   L.call(m,'ThLoad');m.__class__=A.HostMemory;m.observe(s)
   m.raw_page(1,3);m.raw_page(2,2);H.put(m,CurrentBank=3,CurrentBankC=2)
   return m
  def invoke(m,name,a=0,x=1,y=0,p=48):
   c=A.CPU(memory=m,pc=s[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5aff)
   for n in range(50000):
    if c.pc==0x5b00:break
    assert m[c.pc]!=0,(name,hex(c.pc));c.step()
   else:raise AssertionError(('actual linked worker bound',name,hex(c.pc)))
   assert c.sp==224
   return c
  def projected(m):
   a=bytearray(m.ram[2][:2048]);a[:16]=m.logical;return bytes(a[:256]+a[512:])
  def reference(c):return bytes(c.memory[:256]+c.memory[512:2048])
  policies=[('walk',[1]*36+[0]*8),('reverse',[1]*16+[2]*24),('jump',[8]*3+[0]*40),('punch',[0]*2+[64]*6+[0]*32),('kick',[0]*2+[128]*6+[0]*32),('crouch',[4]*3+[68]*6+[4]*24)]
  rows=[];frames=0;actions=set();cold=0
  for player,(label,policy)in itertools.product(range(2),policies):
   m=candidate(player);r=original_cold(player);invoke(m,'ThEnsure')
   for off,v in[(0xd4,H.get(m,'Player_X_Position')+8),(0xe5,H.get(m,'Player_PageLoc')+int(H.get(m,'Player_X_Position')>=248)),(0x94,H.get(m,'Player_Rel_XPos')+8)]:r.memory[off]=v&255
   assert projected(m)==reference(r),('actual projected cold',player,label,[(hex(i),r.memory[i],m.ram[2][i])for i in range(2048)if not 256<=i<512 and r.memory[i]!=m.ram[2][i]][:15]);cold+=1
   for i,pad in enumerate(policy):
    for off,v in[(0xd4,H.get(m,'Player_X_Position')+8),(0xe5,H.get(m,'Player_PageLoc')+int(H.get(m,'Player_X_Position')>=248)),(0x94,H.get(m,'Player_Rel_XPos')+8)]:r.memory[off]=v&255
    attack=original_frame(r,pad);flags=L.flags(i%64);c=invoke(m,'ThomasHostFrame',pad,1,(i+1)&255,flags)
    assert(c.a,c.x,c.y,c.p,c.sp)==(pad,1,(i+1)&255,flags,224),('actual caller flags',player,label,i)
    assert projected(m)==reference(r),('original accepted state',player,label,i,[(hex(k),r.memory[k],m.ram[2][k])for k in range(2048)if not 256<=k<512 and r.memory[k]!=m.ram[2][k]][:15])
    assert(m.ram[2][0x808],m.ram[2][0x809],bytes(m.ram[2][0x80a:0x80e]))==attack
    actions.add(r.memory[0x69]&0x3e);frames+=1
   rows.append(dict(player=player,policy=label,frames=len(policy),native_player_slot=m.ram[2][0x8d],native_omitted_enemy_slots=list(m.ram[2][0x87:0x8d]),x=H.get(m,'Player_X_Position'),original_B6=r.memory[0xb6]))
  q.update(passed=True,physical_loader_acquisitions=cold,original_accepted_frame_pairs=frames,actions=sorted(actions),rows=rows,source_enemy_projection='Clear only original six omitted native-enemy active slots87..8C after actual constructor; retain original player8D. SMB owns real world actors. No original movement/jump/melee instruction bodies changed.',CPU_model='NesMPU binary ADC/SBC even when P.D set',limits=['Finite source actor projection/caller proof, not original enemy-engine/audio port','This lower-worker oracle is separate from natural Main/terrain and actual host-vector receipts'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(T.__file__),Path(A.__file__),Path(L.__file__),Path(H.__file__),R/'tools/audit/verify_native_relocation.py',J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',T.DONOR]}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','rows','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
