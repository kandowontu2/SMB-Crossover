"""Qualify the genuine Ryu alternate ingress and its preserved native label."""
from pathlib import Path
import itertools,json,re
import check_arthur_side_clamp_1101_v8 as C
P=C.P;M=C.M;O=P.O


def main():
 old,new=C.bundle();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'new-wall.lbl').read_text(),re.M)}
 assert labels['NativeGuest']==C.address(old,'SamusStopAtWallBanked::NativeGuest')==0xa29d
 assert labels['SamusStopAtWallBanked']==0xa290 and labels['End']==C.address(old,'SamusHeadProbe')==0xa367
 entries=[];cls=M.NesMPU;step=cls.step
 def traced(c):
  if c.pc==0xa29d and c.memory.rawtags[1]==138:
   assert c.y==M.get(c.memory,'R0')and c.y in [1,2],('Actual Ryu side contract',c.y,M.get(c.memory,'R0'))
   entries.append(c.a)
  return step(c)
 cls.step=traced;cases=0
 try:
  for side,standing,x,flag in itertools.product([1,2],[0,1,2],[0,32,240,255],[0x20,0x31,0x61,0xa9]):
   pair=[]
   for b in [old,new]:
    m=C.seed(b);M.put(m,SelectedCharacter=10,R0=side,Player_State=standing,Player_X_Position=x,Player_X_Speed=254,RyWallResolved=0,RyWallSide=0)
    z=M.invoke(m,'RyuSourceSideDispatch',a=85,x=19,y=side,p=flag);pair.append((m,z))
   (a,za),(b,zb)=pair;low=min(za['minimum_SP'],zb['minimum_SP'])
   assert C.result(za)==C.result(zb)and C.fields(a,low)==C.fields(b,low)and a.ram==b.ram and a.rawtags==b.rawtags,('Ryu actual caller',side,standing,x,flag)
   cases+=1
 finally:cls.step=step
 assert entries and len(entries)==2*cases
 q=dict(passed=True,base_sha256=P.SHA,proposed_candidate_sha256=__import__('hashlib').sha256(new['raw']).hexdigest(),actual_RyuSourceSideDispatch_cases=cases,reached_native_guest_calls=len(entries),observed_incoming_A=sorted(set(entries)),native_guest_address_preserved='10:A29D',actual_native_guest_Y_equals_R0_side=True,original_samus_head_entry_preserved='10:A367',scope='Real original Ryu side admission and alternate native farcall, source NativeGuest arbitrary-A ABI separately covered by coreCPU receipt; actual selected byte gates Arthur.',bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),Path(C.__file__),P.SOURCE,O/'new-wall.bin',O/'new-wall.lbl',P.R/'src/ryu_side_overlap.s',P.R/'src/ryu_platform.s']})
 (O/'callers-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
