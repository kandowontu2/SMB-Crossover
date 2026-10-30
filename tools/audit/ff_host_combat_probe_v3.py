"""Retained fixture diagnosis; no product mutations or native execution."""
import json
import ff_host_combat_controls_v2 as C
b=C.C.bundle(C.R/'build/final-fantasy-host-combat-v2')
m=C.make(b);C.put(m,SelectedCharacter=0);before=C.state(m);C.run(m,'FfHostWeapons');after=C.state(m)
print('guarddiff',[(i,x,y)for i,(x,y)in enumerate(zip(before[0],after[0]))if x!=y][:15])
m=C.make(b);C.actor(m,kind=C.address(b,'Goomba'));C.put(m,FfHits=63)
for off in [0,12,24]:C.setv(m,'FfProjectile',63,off+9)
parent=C.qualified(C.C.E.P/'candidate.nes');phys=(C.location(parent,'CheckpointEnemyID')-16)//8192
C.direct(m,'CheckpointEnemyID',x=0,bank=phys|128)
C.direct(m,'FfHostNewEnemy',a=0x59,x=0,y=0xa7,p=0x30,bank=3)
C.actor(m,x=0,px=140,y=160);C.put(m,FfVariant=0,FfPower=0,FfAction=1)
c,tr,_=C.run(m,'FfHostContact',a=255,x=0)
print('reuse',{n:C.get(m,n)for n in ['FfHits','FfDamage','FfTargetX','FfTargetY','FfTargetW','FfTargetH','Player_X_Position','Player_Y_Position','PlayerFacingDir']},'hp',C.C.hp(m),'p',c.p)
for variant,keys,spell in [(0,64,0),(1,64,0),(3,64,0),(2,64,1),(2,72,2),(2,68,3),(1,68,4)]:
 m=C.make(b);C.put(m,FfVariant=variant,FfPower=2,SavedJoypadBits=keys);out=[]
 for tick in range(50):
  C.actor(m,kind=C.address(b,'HammerBro'),px=150,y=116 if spell else 160)
  if tick==0:C.setv(m,'MmEnemyHealthLo',76);C.setv(m,'MmEnemyHealthHi',4)
  C.run(m,'FfMovement');C.run(m,'FfHostWeapons')
  out.append([tick,C.get(m,'FfAction'),C.get(m,'FfAge'),C.get(m,'FfProjectile'),C.C.hp(m),C.get(m,'FfFresh'),C.get(m,'FfPrevious')])
 print('timeline',variant,keys,spell,out[:2],out[29:32],min(z[4]for z in out))
