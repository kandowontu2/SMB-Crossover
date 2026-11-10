"""Restore Getsu's missing native head probe as well as its upgrade callback."""
import argparse,json
from pathlib import Path
import check_getsu_powerup_callback_1110 as Q
from check_tmnt_render_oa import address

R=Q.R;PRIOR=R/'build/getsu-powerup-callback-1110/proof.json'
BASE=R/'build/getsu-callback-native-1110/candidate.nes'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert out.is_relative_to(R/'build');out.mkdir(exist_ok=True)
 prior=json.loads(PRIOR.read_text());raw=BASE.read_bytes();assert Q.sha(raw)==prior['expected_memory_only_SHA256']
 for name,h in prior['bindings'].items():assert Q.sha((R/name).read_bytes())==h,name
 image=bytearray(raw);assert image[Q.K+30:Q.K+33]==bytes.fromhex('1860ea')
 image[Q.K+30:Q.K+33]=bytes.fromhex('4c8795')
 # The prior optimization bypassed this declared empty service before loading it.
 gate=16+65*8192+0x10aa
 assert image[gate:gate+3]==bytes.fromhex('4ce4a7')
 image[gate:gate+3]=bytes.fromhex('4c40a7')
 cookie=bytes((0xa7,42,1))+bytes.fromhex(Q.sha(image[Q.K:Q.K+2048]+image[Q.ATLAS:Q.ATLAS+1024]))[:13]
 at=16+65*8192+0xb81;image[at:at+16]=cookie
 bundle=Q.Earned.D.Current.Getsu.W.bundle(bytes(image));m=Q.Earned.H.prepare(bundle);N=Q.Earned.N
 # A genuine native head collision on the real first powerup cell.
 # Fixture places the already-authenticated player, then runs the ordinary BG core.
 N.put(m,Player_X_Position=74,Player_PageLoc=1,Player_Y_Position=149,Player_Y_HighPos=1,
       Player_Y_Speed=0xfc,Player_State=1,PlayerSize=0,CrouchingFlag=0,PlayerStatus=0,
       BlockBounceTimer=0,GuestHurtTicks=0,NmiDisable=255)
 cell=0x300+0xd0+((144&0xf0)-32)+5 # world336/page1 column5
 old=m[cell];m[cell]=0xc1
 calls=[];Original=N.NesMPU
 class Trace(Original):
  def step(self):
   tag,pc=Q.Earned.H.point(self)
   if tag==3 and 0xa000<=pc<0xa072 and (pc-0xa000)%3==0:
    calls.append(('row',(pc-0xa000)//3,self.a,self.x,self.y))
   if pc in (0x9ef5,0x9587,0x95d7):calls.append((hex(pc),tag,self.a,self.x,self.y,list(self.memory[3:11])))
   return super().step()
 try:N.NesMPU=Trace;N.invoke(m,'PlayerBGCollision')
 finally:N.NesMPU=Original
 print('calls',calls,flush=True)
 states=[N.get(m,'Block_State',i) for i in (0,1)]
 print('Head collision',old,m[cell],states,list(m[3:11]),
       [N.get(m,'Block_Orig_YPos',i) for i in (0,1)],flush=True)
 assert m[cell]==0x23 and any(s for s in states),(old,m[cell],states)
 # The drawing and gait bytes remain identical to the fully verified prior.
 assert image[Q.K+0x4be:Q.K+2048]==raw[Q.K+0x4be:Q.K+2048]
 q=dict(prior);q.update(expected_memory_only_SHA256=Q.sha(image),head_probe=0x9587,
    cookie=cookie.hex(),head_fixture=dict(original_tile=old,final_tile=m[cell],block_states=states),
    scope='Missing row10 head probe restored. Renderer/gait/IRQ proof inherited byte-exact; row33 callback retained.')
 q['patches']=[dict(row) for row in prior['patches']]
 for row in q['patches']:
  at=row['file_offset'];row['new_hex']=image[at:at+len(bytes.fromhex(row['new_hex']))].hex()
 q['patches'].append(dict(file_offset=gate,old_hex=raw[gate:gate+3].hex(),new_hex=image[gate:gate+3].hex()))
 q['bindings']=dict(prior['bindings'])|{str(p.relative_to(R)):Q.sha(p.read_bytes()) for p in (Path(__file__).resolve(),PRIOR,BASE)}
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(Q.sha(image))

if __name__=='__main__':main()
