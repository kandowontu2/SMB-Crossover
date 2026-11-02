"""Narrow actual-B source projectile/native enemy contact diagnosis; no ROM edits."""
from pathlib import Path
import json
import check_arthur_side_clamp_1101_v8 as C
P=C.P;M=C.M;O=P.O


def main():
 rom=O/'maturity-candidate.nes';assert P.sha(rom)=='b9e685ffd0620a213a2fc05219e2bae415ee81aa07ab0e994db79455792ef6c4'
 b=C.scoped_load(rom);m=C.seed(b);M.put(m,SelectedCharacter=32,ArHostReady=0,OperMode_Task=3,DisableScreenFlag=1,Mirror_PPUMASK=0,CurrentPlayer=0,NumberofLives=2)
 M.invoke(m,'HuFresh');assert M.get(m,'ArHostReady')==167
 M.put(m,CurrentBankC=191);m[0x5116]=191
 rows=[];step=M.NesMPU.step;active={}
 names=['HuWeapons','ArHostShotContacts','ArNativeShotContact','ArNativeMarkShotHit','HandleEnemyFBallCol','ArNativeLance','ArNativeDagger','ArStep']
 points={((C.location(b,n)-16)//8192|128,C.address(b,n)):n for n in names}
 def record(c):
  if c.pc>=0x8000:
   n=points.get((c.memory.rawtags[(c.pc-0x8000)//8192],c.pc))
   if n:active[n]=active.get(n,0)+1
  return step(c)
 M.NesMPU.step=record
 try:
  for kind in [0,6]:
   q=M.fork(m);M.put(q,Player_X_Position=247,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=120,ScreenLeft_PageLoc=0,ObjectOffset=0)
   for n,v in [('Enemy_Flag',1),('Enemy_ID',kind),('Enemy_State',0),('Enemy_X_Position',44),('Enemy_PageLoc',1),('Enemy_Y_Position',184 if kind==6 else 176),('Enemy_Y_HighPos',1)]:q[C.address(b,n)]=v
   M.invoke(q,'ArHostImport');active.clear();sequence=[]
   for age in range(36):
    keys=64 if age%6<2 else 0
    M.invoke(q,'ArStep',a=keys,x=0)
    shots=[dict(slot=i,flags=M.get(q,'ArR_04F0',i),kind=M.get(q,'ArR_0631',i),world_x=M.get(q,'ArR_05AF',i)+256*M.get(q,'ArR_0583',i),screen_x=M.get(q,'ArR_0554',i),screen_y=M.get(q,'ArR_0509',i),source_y=M.get(q,'ArR_0599',i),source_page=M.get(q,'ArR_056D',i))for i in range(1,4)if M.get(q,'ArR_04F0',i)]
    M.invoke(q,'HuWeapons',a=32,x=0)
    sequence.append(dict(source_age=age,pad=keys,shots=shots,enemy_state=M.get(q,'Enemy_State'),calls=dict(active)))
    if M.get(q,'Enemy_State')&32:break
   rows.append(dict(enemy_id=kind,enemy_start_world_x=300,enemy_start_y=184 if kind==6 else 176,starting_source_weapon=M.get(q,'ArR_053A'),defeated=bool(M.get(q,'Enemy_State')&32),calls=dict(active),sequence=sequence))
 finally:M.NesMPU.step=step
 receipt=dict(source_CPU_only=True,native=False,ROM_sha256=P.sha(rom),diagnostic=True,all_natural_B_source_lance_contacts_defeat=all(v['defeated']for v in rows),scope='Genuine constructor and nativeB-driven ArStep followed by actual HuWeapons/native enemy hit consumer. Enemy position/floor/source scheduling is an isolated CPU fixture, not controller-earned native combat. No shot coordinates or contact results are seeded. Initial sourceweapon64 is lance; dagger66 is a later source upgrade.',rows=rows,bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),rom]})
 (O/'weapon-contact-CPU.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['rows','bindings']}));print(json.dumps([dict(enemy_id=v['enemy_id'],defeated=v['defeated'],calls=v['calls'],first_shots=next((a['shots']for a in v['sequence']if a['shots']),[]))for v in rows]))


if __name__=='__main__':main()
