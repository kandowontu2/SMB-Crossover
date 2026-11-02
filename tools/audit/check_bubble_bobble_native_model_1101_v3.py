"""Bounded legal fixtures for private native adapters; no shared/ROM writes."""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import bubble_bobble_native_model_1101_v3 as B
from check_tmnt_render_oa import address
O=B.O


def enemy(h,i=0,x=112,y=184,ident=6):
 for n,v in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_PageLoc',x>>8),('Enemy_X_Position',x&255),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1),('Enemy_X_Speed',8),('Enemy_Y_Speed',0),('Enemy_MovingDir',1)]:h.m[h.at(n)+i]=v
 h.put(ObjectOffset=i)


def main():
 b=B.scoped_load(B.BASE);results={};all_calls={};maxs=0
 for identity in [0,1]:
  h=B.Host(identity,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);start=h.worldx();ys=[];size=h.get('PlayerSize')
  for f in range(100):h.step(1|(128 if f==25 else 0),epoch=f);ys.append(h.worldy()-256)
  assert h.worldx()>start+50 and min(ys)==133 and h.worldy()==432,(identity,h.worldx(),min(ys),h.worldy())
  assert h.get('PlayerSize')==size,'Adapter must not change arbitrary native power-state policy'
  before=bytes(h.s[:1024]);assert not h.step(1,epoch=99)and bytes(h.s[:1024])==before
  h.put(GamePauseStatus=1);assert not h.step(1,epoch=100);h.put(GamePauseStatus=0)
  results['motion'+str(identity)]=dict(x=h.worldx(),apex=min(ys),landed_y=h.worldy()-256,source_epochs=h.original(0x1f))
  if identity==0:all_calls=dict(h.calls)
 # World page crossing and real native scrolling use exact compiled service.
 h=B.Host(0,b);h.setx(250);h.terrain(lambda x,y:0x54 if y>=208 else 0);h.transport_in();h.put(ScreenLeft_X_Pos=144,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=143,ScreenRight_PageLoc=1,Player_Pos_ForScroll=106)
 for f in range(40):h.step(1,epoch=f,scroll=True)
 assert h.worldx()>256 and h.camera()>144,(h.worldx(),h.camera());results['world_camera']=dict(x=h.worldx(),camera=h.camera())
 # Source rise is retained; a native solid ceiling clips at its actual bottom.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 or(144<=y<160 and 48<=x<112)else 0);tops=[]
 for f in range(60):h.step(128 if f==0 else 0,epoch=f);tops.append(h.worldy()-256)
 assert any(e[0]=='solid-ceiling'for e in h.events)and min(tops)>=144,(min(tops),h.events)
 results['ceiling']=dict(apex=min(tops),events=[e for e in h.events if e[0]=='solid-ceiling'])
 # Native pit fatality invokes real KillPlayer once; source never wraps to sky.
 h=B.Host(0,b);h.terrain(lambda x,y:0);h.sety(256+224);h.transport_in()
 for f in range(40):
  h.step(0,epoch=f)
  if h.s[0x307]:break
 assert h.s[0x307]and h.get('GameEngineSubroutine')==11 and h.calls['native:KillPlayer']==1
 results['pit']=dict(update=f+1,y=h.worldy(),engine=h.get('GameEngineSubroutine'),kill_calls=h.calls['native:KillPlayer'])
 # Actual source shot request/growth traps a staged legal Goomba16px body.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,x=100,y=184)
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 assert h.tokens[0],(h.events,h.original(0x88),h.original(0x6a));trap_frame=f
 original_x=h.get('Enemy_X_Position');assert not h.enemy_step(0);assert h.get('Enemy_X_Position')==original_x
 assert not any(e[0]=='native-defeat-credit'for e in h.events)
 # Force no contact with the trapped body, retain actual source40-update timer.
 h.setx(32);h.transport_in();timer=h.original(0x413)
 for f in range(trap_frame+1,trap_frame+60):
  h.step(0,epoch=f)
  if h.tokens[0]is None:break
 assert any(e[0]=='release'for e in h.events)and h.get('Enemy_X_Speed')==8
 assert h.calls['native:ShellOrBlockDefeat']==0
 resumed=h.enemy_step(0);assert resumed
 results['trap_release']=dict(trap_frame=trap_frame,remaining_timer=timer,release_epoch=f,native_AI_resumed=resumed)
 # A captured actor is popped with the original contact/chain state, then the
 # real native defeat service supplies exactly one score/drop lifecycle.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,x=100,y=184)
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 assert h.tokens[0]
 h.setx(h.get('Enemy_X_Position'));h.sety(256+h.get('Enemy_Y_Position')-8);h.transport_in()
 for k in range(8):h.step(0,epoch=f+1+k)
 assert h.calls['native:ShellOrBlockDefeat']==1 and h.get('Enemy_State')&32,(h.events,h.get('Enemy_State'))
 results['pop']=dict(native_defeats=h.calls['native:ShellOrBlockDefeat'],state=h.get('Enemy_State'),events=[e for e in h.events if e[0]in['trap','native-defeat-credit']])
 # Bounded native OAM uses the real emitter, across capacity/rotation prefixes.
 draw=[]
 for prefix in[0,24,248,252]:
  h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);h.put(CurrentOAMOffset=prefix,GuestOamRotationActive=0)
  h.m[512:768]=[248,0,0,0]*64
  for i,x in enumerate(range(0x88,0xc4,4)):
   y=0x88+8*i
   for j,v in enumerate([2,100,3,8]):h.setoriginal(x+j,v)
   for j,v in enumerate([64,0x26,3,32+12*i,64,0x28,3,40+12*i]):h.setoriginal(0x200+y+j,v)
  d=h.draw();assert h.get('CurrentOAMOffset')%4==0 and h.get('CurrentOAMOffset')<=256;draw.append(d)
 results['native_OAM']=draw
 h=B.Host(0,b);h.put(CurrentOAMOffset=25);assert h.draw()['rejected']=='misaligned cursor'
 # Compiled native leaves agree with the independent Python adapter oracle.
 pair=[B.Host(1,b,leaves=v)for v in[False,True]]
 for h in pair:h.terrain(lambda x,y:0x54 if y>=208 else 0)
 for f in range(150):
  keys=(1 if f<110 else 2)|(128 if f in[20,95]else 0)|(64 if f in[10,70]else 0)
  for h in pair:h.step(keys,epoch=f)
  assert bytes(pair[0].s[:768])==bytes(pair[1].s[:768]),('leaf/source state',f)
  for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir','Player_X_Speed','Player_Y_Speed','Player_Pos_ForScroll']:
   assert pair[0].get(n)==pair[1].get(n),(f,n)
 results['compiled_oracle_epochs']=150
 h=B.Host(0,b);h.terrain(lambda x,y:[0,0x10,0x11,0x14,0x15,0x54][((x//16)+(y//16))%6]);query_cases=0
 for cam in[0,250,512]:
  h.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8)
  for row in[0,1,2,7,16,22,23]:
   for col in[0,1,2,15,16,30,31]:
    ptr=0x500+row*32+col
    for name,cursor in[('BbNativeTile23',0x23),('BbNativeTile84',0x84)]:
     h.setoriginal(cursor,ptr&255);h.setoriginal(cursor+1,ptr>>8)
     for flags in[0x30,0x31,0xf1]:
      c=h.source(name,x=7,y=91,p=flags);expected=0 if h.query(cam+col*8-16,row*8+32)else 1
      assert(c.a,c.x,c.y,c.p&0x7d)==(expected,7,91,flags&0x7d),(cam,row,col,name,flags,c.a,c.p)
      query_cases+=1
 results['compiled_native_query_cases']=query_cases
 h=B.Host(0,b);contacts=0
 for dx in range(-10,11):
  for dy in range(-10,11):
   h.setoriginal(0x21,100);h.setoriginal(0x22,116)
   for off,val in[(0x210,100+dy),(0x213,116+dx)]:h.setoriginal(off,val)
   c=h.source('BbOriginal_C43E',y=0x10,a=9);actual=h.native_contact((116,100),(116+dx,100+dy))
   assert actual==(not bool(c.p&1))and actual==(abs(dx)<9 and abs(dy)<9)
   contacts+=1
 results['separate_contact_cases']=contacts
 # Source injury animation, native death handoff, explicit new-life event.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);assert h.hurt()
 for f in range(120):
  h.step(0,epoch=f)
  if h.s[0x307]:break
 assert h.s[0x307]and h.calls['native:KillPlayer']==1
 h.put(NumberofLives=1,GameEngineSubroutine=8,Player_Y_Position=176,Player_Y_HighPos=1);h.new_life()
 assert h.original(h.actor)==2 and h.original(h.actor+17)==200 and not h.s[0x307]
 results['injury_newlife']=dict(source_death_updates=f+1,source_lives=h.original(h.actor),source_grace=h.original(h.actor+17))
 # Retire and recycle never restore or credit an unrelated native actor.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,x=100,y=184)
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 assert h.tokens[0];h.m[h.at('Enemy_Flag')]=0;h.observe();assert h.tokens[0]is None
 enemy(h,x=200,y=184,ident=0);h.observe();assert h.tokens[0]is None and h.get('Enemy_State')==0 and h.calls['native:ShellOrBlockDefeat']==0
 h.retire();snapshot=bytes(h.s[:1024]);assert not h.step(1,epoch=100)and bytes(h.s[:1024])==snapshot
 results['recycle_retire']=True
 # Actual direct farcall draw preserves caller scratch/SMC and aligned rings.
 rotation=[]
 for offset in[0,4,252]:
  h=B.Host(0,b);h.put(CurrentOAMOffset=24,GuestOamRotationActive=1,RgOamRotation=offset)
  h.m[3:11]=list(range(8));before=bytes(h.m[3:11]);smc=bytes(h.m[0x15a:0x17b]);maps=list(h.m.rawtags)
  d=h.draw();assert bytes(h.m[3:11])==before and bytes(h.m[0x15a:0x17b])==smc and h.m.rawtags==maps
  assert h.get('CurrentOAMOffset')%4==0 and h.m[h.at('SmPosePtr')]+256*h.m[h.at('SmPosePtr')+1]==h.at('ObjectMetasprite')
  h.bounds();rotation.append(dict(rotation=offset,draw=d,min_SP=h.minimum_SP))
 h=B.Host(0,b);h.put(CurrentOAMOffset=24,GuestOamRotationActive=1,RgOamRotation=1);assert h.draw()['rejected']=='misaligned rotation'
 results['native_rotation_ABI']=rotation
 # Held A rides a genuine source bubble without a new A edge. The adapter
 # keeps the same43px jump, and the epoch/camera transport does not erase09.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);h.setx(100);h.sety(256+84);h.transport_in();h.setoriginal(h.actor+3,2)
 for j,v in enumerate([2,100,3,8]):h.setoriginal(0x88+j,v)
 for j,v in enumerate([112,0x26,3,116,112,0x28,3,124]):h.setoriginal(0x288+j,v)
 h.step(128,epoch=0);assert h.original(h.actor+9)
 rise=[]
 for f in range(1,29):h.step(128,epoch=f);rise.append(h.worldy()-256)
 assert min(rise)==41 and h.original(h.actor+3)==2 and any(e[0]=='source-score'for e in h.events),(min(rise),h.original(h.actor+3),h.events)
 results['native_heldA_ride']=dict(start_y=84,apex=min(rise),rise=84-min(rise),ascent_updates=28)
 # All15 logical slots are exercised through real fresh-B requests. Saturation
 # retains original retirement/request behavior; no smaller model cap exists.
 h=B.Host(1,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);maximum=0
 for f in range(450):
  h.step(64 if f%25==0 else 0,epoch=f)
  active=sum(bool(h.original(x))for x in range(0x88,0xc4,4));maximum=max(maximum,active);assert active<=15
 assert maximum==15,maximum
 h.put(CurrentOAMOffset=0,GuestOamRotationActive=0);d=h.draw();assert d['sprites']<=32
 results['logical15_pool']=dict(maximum=maximum,source_updates=450,draw=d)
 # Native victim art remains visible inside a source bubble overlay.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,x=100,y=184)
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 h.put(CurrentOAMOffset=0,GuestOamRotationActive=0);d=h.draw();assert d['sprites']>=6,(d,h.get('EnemyMetasprite'))
 assert h.original(0x211)==0x26 and h.original(0x215)==0x28
 h.retire();assert h.get('Enemy_X_Speed')==8 and h.tokens[0]is None
 results['trapped_native_art']=d
 # Every native slot and viewport/page edge agrees with the independent
 # adapter oracle. All fixtures are legal isolated slot/terrain arrangements.
 proxy_cases=0
 variants=[{},dict(flag=0),dict(flag=128),dict(ident=12),dict(ident=20),dict(ident=21),dict(state=32),dict(high=0),dict(y=216),dict(y=248),dict(dx=-17),dict(dx=-16),dict(dx=223),dict(dx=224)]
 for cam in[0,250,512]:
  pair=[B.Host(0,b,leaves=v)for v in[False,True]]
  for v in variants:
   for h in pair:
    h.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8)
    for i in range(6):
     enemy(h,i,x=max(0,cam+v.get('dx',100)),y=v.get('y',184),ident=v.get('ident',6))
     for n,val in [('Enemy_Flag',v.get('flag',1)),('Enemy_State',v.get('state',0)),('Enemy_Y_HighPos',v.get('high',1))]:h.m[h.at(n)+i]=val
    h.proxies_in()
   assert bytes(pair[0].s[:768])==bytes(pair[1].s[:768]),('proxy input',cam,v)
   proxy_cases+=6
 results['compiled_proxy_input_cases']=proxy_cases
 validation_cases=0
 native_names=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']
 for i in range(6):
  for action in['BbNativeProxyPosition','BbNativeProxyRestore']:
   for fault in['none','flag-zero','flag-change','id-change','generation','defeated','record-empty']:
    h=B.Host(0,b);enemy(h,i,x=300,y=184);h.put(ScreenLeft_X_Pos=250,ScreenLeft_PageLoc=0);h.observe()
    saved={n:h.get(n,i)for n in native_names[2:3]+native_names[7:]}
    h.tokens[i]=dict(id=6,flag=1,generation=h.generation[i],saved=saved);h.sync_tokens()
    h.setoriginal(0x68+4*i,1);h.setoriginal(0x6a+4*i,16)
    h.setoriginal(0x213+8*i,220);h.setoriginal(0x210+8*i,160)
    if fault=='flag-zero':h.m[h.at('Enemy_Flag')+i]=0
    if fault=='flag-change':h.m[h.at('Enemy_Flag')+i]=2
    if fault=='id-change':h.m[h.at('Enemy_ID')+i]=0
    if fault=='generation':h.s[0x310+2*i]^=1
    if fault=='defeated':h.m[h.at('Enemy_State')+i]=32
    if fault=='record-empty':h.s[0x320+16*i]=0
    before=[h.get(n,i)for n in native_names];c=h.source(action,x=i)
    assert bool(c.p&1)==(fault=='none'),(i,action,fault)
    if fault!='none':assert before==[h.get(n,i)for n in native_names],(action,fault)
    elif action.endswith('Position'):assert h.get('Enemy_X_Position',i)+256*h.get('Enemy_PageLoc',i)==454 and h.get('Enemy_Y_Position',i)==152 and h.get('Enemy_X_Speed',i)==0
    else:assert all(h.get(n,i)==v for n,v in saved.items())and h.s[0x320+16*i]==0
    validation_cases+=1
 results['compiled_proxy_validation_cases']=validation_cases
 # Same-ID/flag replacement is an explicit required birth ingress. It must
 # invalidate the old association before the replacement can be restored.
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,x=100,y=184)
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 assert h.tokens[0];old=h.generation[0];enemy(h,x=180,y=184);h.actor_birth(0)
 assert h.tokens[0]is None and h.generation[0]==(old+1)&65535 and h.get('Enemy_X_Speed')==8
 h.retire();assert h.get('Enemy_X_Position')==180 and h.calls['native:ShellOrBlockDefeat']==0
 results['same_ID_birth_ingress']=dict(generation=h.generation[0],shared_hook_installed=False)
 # Actual native death leaf preserves live foreground scratch/SMC/maps, and
 # duplicate calls do not issue a second native KillPlayer event.
 h=B.Host(0,b);h.sety(256+240);h.m[3:11]=list(range(8));before=bytes(h.m[3:11]);smc=bytes(h.m[0x15a:0x17b]);maps=list(h.m.rawtags)
 assert h.source('BbNativeDeath').p&1 and not h.source('BbNativeDeath').p&1
 assert h.calls['native:KillPlayer']==1 and bytes(h.m[3:11])==before and bytes(h.m[0x15a:0x17b])==smc and h.m.rawtags==maps
 assert h.minimum_SP>=0xa0,h.minimum_SP
 results['native_death_ABI']=dict(native_kill_calls=1,min_SP=h.minimum_SP)
 for prefix,rotation in[(25,0),(24,1)]:
  h=B.Host(0,b);h.put(CurrentOAMOffset=prefix,GuestOamRotationActive=1,RgOamRotation=rotation);before=bytes(h.m[512:768]);c=h.source('BbNativeDraw',a=71,x=93,y=101,p=0xf1)
  assert not c.p&1 and(c.a,c.x,c.y,c.p&0xfe)==(71,93,101,0xf0)and h.get('CurrentOAMOffset')==prefix and bytes(h.m[512:768])==before
 results['compiled_OAM_rejection_cases']=2
 # Actual compiled contact replacement retains original9px hurt geometry;
 # ordinary one-screen-away actors cannot alias through8-bit source OAM.
 hurt_cases=0
 for identity in[0,1]:
  h=B.Host(identity,b)
  for dx in range(-10,11):
   for dy in range(-10,11):
    enemy(h,x=64+dx,y=184+dy);h.setoriginal(h.actor+3,0);h.setoriginal(h.actor+17,0)
    c=h.source('BbNativeBodyContact',x=0);assert c.p&1
    assert bool(h.original(h.actor+3)&128)==(abs(dx)<9 and abs(dy)<9),(identity,dx,dy)
    hurt_cases+=1
  for x in[64+256,64+512]:
   enemy(h,x=x,y=184);h.setoriginal(h.actor+3,0);h.setoriginal(h.actor+17,0);h.source('BbNativeContacts');assert not h.original(h.actor+3)&128
  enemy(h,x=64,y=184);h.setoriginal(h.actor+3,0);h.setoriginal(h.actor+17,200);h.source('BbNativeContacts');assert not h.original(h.actor+3)&128
  h.setoriginal(h.actor+17,0);h.setoriginal(0x68,1);h.setoriginal(0x6a,16);h.source('BbNativeBodyContact',x=0);assert not h.original(h.actor+3)&128
  h.retire();before=bytes(h.s[:768]);c=h.source('BbNativeBodyContact',x=0);assert not c.p&1 and bytes(h.s[:768])==before
 results['compiled_source_hurt_cases']=hurt_cases
 # Repeat genuine source bubble capture/pop in every native enemy slot. R1
 # and ObjectOffset must credit the correct actual actor, exactly once.
 slots=[]
 for i in range(6):
  h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);enemy(h,i,x=100,y=184)
  for f in range(30):
   h.step(64 if f==0 else 0,epoch=f)
   if h.tokens[i]:break
  assert h.tokens[i],i
  h.setx(h.get('Enemy_X_Position',i));h.sety(256+h.get('Enemy_Y_Position',i)-8);h.transport_in()
  h.m[3:11]=list(range(8));smc=bytes(h.m[0x15a:0x17b]);maps=list(h.m.rawtags)
  for k in range(8):h.step(0,epoch=f+1+k)
  assert h.calls['native:ShellOrBlockDefeat']==1 and h.get('Enemy_State',i)&32,(i,h.events)
  assert all(h.get('Enemy_Flag',j)==0 for j in range(6)if j!=i)and bytes(h.m[0x15a:0x17b])==smc and h.m.rawtags==maps
  slots.append(dict(slot=i,defeat_calls=1,state=h.get('Enemy_State',i)))
 results['all6_compiled_source_trap_pop_slots']=slots
 # Full signed16-bit camera translation agrees with the original model for
 # all15 bubbles and six valid trapped associations, including page jumps.
 camera_cases=0
 for delta in[0,1,17,127,128,239,240,255,256,-1,-17,-128,-256]:
  pair=[B.Host(0,b,leaves=v)for v in[False,True]]
  for h in pair:
   h.put(ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=2);h.s[0x305:0x307]=(512).to_bytes(2,'little');h.setx(576);h.transport_in()
   for i in range(6):enemy(h,i,x=612+15*i,y=184)
   h.proxies_in()
   for i in range(6):h.setoriginal(0x6a+4*i,18);h.setoriginal(0x413+4*i,40)
   h.proxies_out()
   for i,x in enumerate(range(0x88,0xc4,4)):
    y=0x88+8*i;h.setoriginal(x,2);h.setoriginal(x+2,3)
    for j,val in enumerate([100,0x26,3,20+14*i,100,0x28,3,28+14*i]):h.setoriginal(0x200+y+j,val)
   camera=512+delta;h.put(ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
  pair[0].shift_camera();pair[1].source('BbNativeShiftCamera')
  assert bytes(pair[0].s[:768])==bytes(pair[1].s[:768]),('camera source',delta)
  for name in native_names:
   assert [pair[0].get(name,i)for i in range(6)]==[pair[1].get(name,i)for i in range(6)],('camera native',delta,name)
  assert pair[1].s[0x305:0x307]==(512+delta).to_bytes(2,'little');camera_cases+=1
 results['compiled_camera21_actor_cases']=camera_cases
 # Execute the real private JMP vectors, including every possible preserved
 # WWF/CF group-bit combination. Only bit7 selects Bub versus Bob.
 fresh_cases=0
 for groups in range(256):
  h=B.Host(0,b);h.s[0x304]=0;h.put(FmGroups=groups)
  h.source(0xa000+15*3,a=85,x=71,y=109)
  identity=groups>>7;actor=0x42 if identity else 0x2e
  assert h.s[0x300]==identity and h.s[0x304]==0xa7 and h.original(actor)==3 and h.get('FmGroups')==groups
  before=bytes(h.s);h.source(0xa000+36*3,a=19,x=37,y=55);assert bytes(h.s)==before,'warm same-life scene preserves source state'
  h.s[0x307]=1;h.put(NumberofLives=1);h.source(0xa000+15*3,a=85,x=71,y=109)
  assert h.original(actor)==2 and h.original(actor+17)==200 and h.s[0x307]==0
  fresh_cases+=1
 h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);h.put(FrameCounter=77,SavedJoypadBits=1)
 start=h.worldx();assert h.source(0xa000).p&1 and h.worldx()==start+1
 before=bytes(h.s);assert not h.source(0xa000).p&1 and bytes(h.s)==before
 h.put(CurrentOAMOffset=24,GuestOamRotationActive=0);assert h.source(0xa000+2*3).p&1 and h.get('CurrentOAMOffset')==32
 rejected=0
 for row in range(37):
  if row in[0,1,2,15,17,18,26,30,36]:continue
  c=h.source(0xa000+row*3,a=85,x=71,y=109,p=0x71);assert not c.p&1 and(c.a,c.x,c.y)==(85,71,109);rejected+=1
 results['real_private_service_vectors']=dict(fresh_and_newlife_group_states=fresh_cases,warm_scene_states=fresh_cases,update_epoch_gate=True,draw_with_existing_prefix=True,other_rows_reject=rejected,shared_ingress_installed=False)
 # Actual whole-update and body/pool draw CPU cycles; excludes resident
 # transport and Main/audio/ISR. No frame-rate or fullstage claim follows.
 profiles={}
 for label,keys in[('idle',0),('walk',1)]:
  h=B.Host(0,b);h.terrain(lambda x,y:0x54 if y>=208 else 0);cycles=[]
  for f in range(60):
   before=h.source_cycles+h.native_cycles;h.step(keys,epoch=f);h.put(CurrentOAMOffset=0,GuestOamRotationActive=0);h.draw();cycles.append(h.source_cycles+h.native_cycles-before)
  profiles[label]=dict(updates=60,mean_CPU=sum(cycles)/60,max_CPU=max(cycles),min_SP=h.minimum_SP)
 results['whole_private_update_draw_CPU']=profiles
 q=dict(passed=True,base_ROM_SHA256=B.PIN,model_only=True,ROM_written=False,public_service_rows_still_reject=True,checks=results,actual_native_calls=all_calls,compiled_leaf_layout=json.loads((O/'native-leaves-layout.json').read_text()),scope='Isolated legal flat/ceiling/pit andGoomba fixtures in exactv30 bus. Whole update/camera transport, original actor and native input/world/query/draw/bounds/admission/proxy capture-observe-position-restore/contact/pop-credit/birth/ceiling/death/init/retire execute as6502. Python supplies native actor-birth observation, trapped-victim art/circle orchestration and explicit remaining sound/score/UI/stage import callbacks. Actual ScrollHandler,KillPlayer,ShellOrBlockDefeat,EnemiesAndLoopsCore,SprObjectCollisionCore andMetaspriteRenderLoop execute. No physical loader/shared routing/menu/native emulator/Main/IRQ/full1-1 claim.')
 q.update(public_service_rows_still_reject=False,private_vector_rows_bound=[0,1,2,15,17,18,26,30,36],shared_owner_admitted=False,scope=q['scope']+' Real private37-row vectors and immutable helper rows are bound; all28remainingrows reject. Actual shared Hu/Main ingress is still absent.')
 q['scope']=q['scope'].replace('exactv30','exactcf')
 (O/'native-model-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=list(results),ROM_written=False)))


if __name__=='__main__':main()
