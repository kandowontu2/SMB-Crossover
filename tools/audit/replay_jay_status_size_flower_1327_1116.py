"""Strict1327 genuine heart/brick/Flower/credit/pistol native observer."""
from functools import lru_cache
from pathlib import Path
import json,re
import replay_jay_status_size_sl_1327_1116 as SL
import check_jay_status_size_flower_1327_1116 as Source

J=SL.J
SOURCE_SHA='c280f40ee897e91899cd9206867ee35caaffa089bdc102d683b89ea4e002ad34'


def body():
    assert J.H(Path(Source.__file__).read_bytes())==SOURCE_SHA
    s=SL.Frozen.Frozen.BODY
    s=s.replace('local music64=0','local music64=0\nlocal bricks,cells,noise,attacks={},{},{},{}\nlocal scorePending=nil')
    s=s.replace('head=heads,births=births,','brick=bricks,brick_cells=cells,brick_noise=noise,attack=attacks,head=heads,births=births,')
    s=s.replace("hp=r('JnHealth'),maximum=","size=r('PlayerSize'),upgrade_parity=r('JnStars'),hp=r('JnHealth'),maximum=")
    start=s.index('local function afterMain()');end=s.index('local function settle()',start)
    functions=r'''local function label(a)return a.owner==16 and(a.private==129 and'mushroom'or a.private==130 and'flower')or'other'end
local function afterMain()
 if not game then return end
 updates=updates+1;local s=state();local aa={}
 assert(identity()and s.hp>0 and s.engine~=11 and s.lives==2,'Living genuine Jay Flower route')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'1-1 no cheats')
 assert(updates<2400,'Finite ordinary Flower route')
 for bank=2,3 do local h={};for i=0x1fe0,0x1fef do h[#h+1]=string.format('%02x',w(bank,i))end;assert(table.concat(h)==C.cookie,'Complete owning Jay header')end
 for _,cell in ipairs(cells)do if not cell.erased and emu.read(cell.address,emu.memType.nesDebug)==0 then cell.erased=updates end end
 for i=0,5 do local a=actor(i);if a.flag~=0 then aa[#aa+1]=a
  if a.id==46 then
   local key=a.slot..'/'..a.private..'/'..a.owner
   if not seen[key]then assert(#births<8);births[#births+1]={label=label(a),actor=a,player=s};seen[key]=true end
  end
 end end
 if target and award and not credit and s.score>=target.before.score+1000 then credit={Main=updates,motor=motor,state=s,writer=award}end
 if credit and motor>=credit.motor+25 and #attacks>0 then
  assert(s.tier==2 and s.maximum==4 and s.hp>0 and s.weapon==target.before.weapon,'Inherited reward and original weapon retained')
  local shattered=false;for _,c in ipairs(cells)do if c.before==81 and c.erased and c.player.size==0 and c.player.status==1 then shattered=true end end
  assert(shattered and #bricks>=2 and #noise>0,'Actual brick51 erasure/debris/cue')
  assert((counts.JayIntegrate_entries or 0)==(counts.JayIntegrate_returns or 0),'Balanced original donor returns')
  finish(true,'Genuine heart, brick51 shatter, physical Flower, original reward/credit plus25 returns and pistol defeat');return
 end
 local bits=policy:decide(s,aa);assert(type(bits)=='number'and bits>=0 and bits<=255);pad=bits
 if policy.phase~=lastphase then bounded(changes,{Main=updates,motor=motor,phase=policy.phase,x=s.x,y=s.y},8);lastphase=policy.phase end
 bounded(tail,{state=s,phase=policy.phase,pad=pad},8)
end
local function returned(p,c)
 count(p.name..'_returns')
 if p.name=='GameLoop'then main=main+1;afterMain()
 elseif p.name=='JayIntegrate'then motor=motor+1
 elseif p.name=='JnCollectPickup'then counts.last_private_C=c['cpu.ps']&1
 elseif p.name=='BrickShatter'or p.name=='SpawnBrickChunks'then
  local i=p.index;local chunk={state=r('Block_State',i),replace=r('Block_RepFlag',i),metasprite=r('BlockMetasprite',i),vx=r('Block_X_Speed',i),vy=r('Block_Y_Speed',i),vy2=r('Block_Y_Speed',i+2)}
  if p.name=='SpawnBrickChunks'then assert(chunk.state==18 and chunk.replace==1 and chunk.metasprite==0 and chunk.vx==240 and chunk.vy==250 and chunk.vy2==252,'Real native brick debris')end
  bounded(bricks,{name=p.name,Main=updates,motor=motor,before=p.before,after=state(),chunk=chunk},8)
 elseif p.name=='JayCaptureAmmoDefeat'and target then
  local a=actor(p.victim.slot);assert(p.victim.flag~=0 and p.victim.id==6 and p.victim.state&32==0 and(a.flag==0 or a.state&32~=0),'Actual post-Flower pistol defeat')
  bounded(attacks,{before=p.victim,after=a,Main=updates,motor=motor,player=state()},8)
 elseif p.name=='HandlePowerUpCollision'and p.actor.flag~=0 and p.actor.id==46 and r('Enemy_Flag',p.actor.slot)==0 then
  local a=p.actor;local s=state();local name=label(a)
  assert(counts.last_private_C==1 and(sounds[32]or 0)>p.cue32_before,'Actual owning C1 collector/cue32')
  assert(a.owner==16 and a.state==128 and #births>0,'Physical mature owning item')
  local node={label=name,item=a,before=p.before,after=s,Main=updates,motor=motor,popup=r('FloateyNum_Control',a.slot)}
  if name=='mushroom'then assert(#collects==0 and s.hp==8 and s.maximum==4 and s.tier==1,'Genuine first heart')
  else
   assert(name=='flower'and not target and #collects==1 and a.private==130 and a.x==1248 and a.y==120,'Actual authored final Flower')
   assert(s.tier==2 and s.maximum==4 and s.hp==p.before.hp and node.popup==6,'Inherited tier2/refill policy and popup6')
   assert(s.weapon==p.before.weapon and s.ammo==p.before.ammo,'Flower does not grant an original Silius gun/ammo')
   assert(s.score>=collects[1].before.score+1000,'Earlier heart credit retained')
   target=node
  end
  collects[#collects+1]=node;policy:collect(name)
 end
end
'''
    s=s[:start]+functions+s[end:]
    start=s.index(" if name=='PlayerHeadCollision'then",s.index('local function enter('));end=s.index(' count(name..',start)
    specials=r''' if name=='PlayerHeadCollision'then
  local st=state();local tile=c['cpu.a'];bounded(heads,{tile=tile,player=st},8)
  if tile==81 then
   local at=r('R6')+256*r('R7')+r('R2');assert(#cells<8)
   cells[#cells+1]={address=at,before=emu.read(at,emu.memType.nesDebug),player=st,Main=updates}
  end
  return
 end
 if name=='SetupFloateyNumber'then bounded(popups,c['cpu.a'],16);return end
 if name=='ScoreDigitWrite'then
  if not target or award then return end
  scorePending={pc=h.pc+3,sp=c['cpu.sp'],tag=h.tag,Main=updates,motor=motor,PC=h.pc}
  if not registered.score then registered.score=true;emu.addMemoryCallback(guard('Actual score digit result',function()
   local p=scorePending;if not p or mapped(p.pc)~=p.tag or emu.getState()['cpu.sp']~=p.sp then return end
   local st=state();if st.score>=target.before.score+1000 then award={PC=p.PC,tag=p.tag,Main=updates,motor=motor,state=st};scorePending=nil end
  end),emu.callbackType.exec,h.pc+3)end
  return
 end
'''
    s=s[:start]+specials+s[end:]
    a="if name=='HandlePowerUpCollision'then p.actor=actor(c['cpu.x']);p.before=state();p.cue32_before=sounds[32]or 0;p.music64_before=music64 end"
    b=a+"\n if name=='BrickShatter'or name=='SpawnBrickChunks'then p.index=c['cpu.x'];p.before=state()end\n if name=='JayCaptureAmmoDefeat'then p.victim=actor(c['cpu.x'])end"
    assert s.count(a)==1;s=s.replace(a,b)
    a="local function pause(n)for _=1,n do coroutine.yield()end end"
    b="emu.addMemoryCallback(guard('Actual brick cue',function(_,v)if game and v&1~=0 then bounded(noise,{Main=updates,motor=motor,value=v},8)end end),emu.callbackType.write,F.NoiseSoundQueue)\n"+a
    assert s.count(a)==1;s=s.replace(a,b)
    return s.replace('POLICY_TEXT',Source.text())


@lru_cache(maxsize=1)
def bindings(raw,kind='flower'):
    assert kind=='flower'and J.H(raw)==J.PIN
    q=dict(SL.bindings(raw,'star'));q['ram']=dict(q['ram']);q['hooks']={k:dict(v)for k,v in q['hooks'].items()if k!='LifeINC'}
    b=J.bindings(raw)['bundle']
    for name in('PlayerSize','JnStars','R2','R6','R7','NoiseSoundQueue','Block_State','Block_RepFlag','BlockMetasprite','Block_X_Speed','Block_Y_Speed'):
        q['ram'][name]=J.W.address(b,name)
    for name in('BrickShatter','SpawnBrickChunks'):
        at=J.W.location(b,name);q['hooks'][name]=dict(pc=J.W.address(b,name),tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+16].hex(),bank_SHA256=J.H(raw[16+((at-16)//8192)*8192:16+(((at-16)//8192)+1)*8192]))
    pc=0x89d5;at=16+126*8192+(pc&8191);assert raw[at]==0x99
    q['hooks']['ScoreDigitWrite']=dict(pc=pc,tag=254,offset=at-16,hex=raw[at:at+16].hex(),bank_SHA256=J.H(raw[16+126*8192:16+127*8192]))
    world=raw[1048592+234*1024+0x230:1048592+234*1024+0x2d4]
    match=list(re.finditer(b'\x98\xaa\x86.\x20(..)\x68\x85.\xae..\xa9\x1d\x4c',world,re.S));assert len(match)==1
    pc=int.from_bytes(match[0].group(1),'little');assert 0xb800<=pc<0xbe30
    if pc<0xbc00:at=1048592+232*1024+pc-0xb800
    else:at=1048592+234*1024+pc-0xbc00
    q['hooks']['JayCaptureAmmoDefeat']=dict(pc=pc,tag=3,offset=3*8192+(pc&8191),hex=raw[at:at+16].hex())
    q.update(kind='flower',source_policy_SHA256=J.H(Source.text().encode()),source_flower_receipt='d9d0c3f972e381dbe04ee851a7f875fa3776c805a9d49959103eb0aeaa9dcbc2',
        original_reward='Inherited tier2, max4/HP retained; original Silius weapon/ammo unchanged; actual pistol defeat',
        credit_gate='Actual score digit STA return before25 completed original workers')
    return q


@lru_cache(maxsize=1)
def controller(raw,kind='flower'):
    q=bindings(raw,kind)
    def value(v):
        if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
        if isinstance(v,bool):return'true'if v else'false'
        if v is None:return'nil'
        return json.dumps(v,separators=(',',':'))
    return'local JAY_CONFIG='+value(q)+'\n'+body()
