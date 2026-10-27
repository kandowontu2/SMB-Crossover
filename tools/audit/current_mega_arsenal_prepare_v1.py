"""Prepare earned Mega/Proto Hard arsenals on accepted9ea. Never launches Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua
from current_roster_compact_11_v1 import navigation

EXPECTED='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
ALLOWED='''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits InvDropKind Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce ScrollThirtyTwo AreaParserTaskNum MmVX MmVY MmXFraction MmYFraction ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc Player_X_Position Player_PageLoc MmOldX Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_SprAttrib PowerUpType InvPickupOwner InvPickup AvPickupAmmoItem Enemy_Y_MoveForce Enemy_MovingDir EnemyOffscrBitsMasked MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun MmFrictionYActive'''.split()
FORBIDDEN='''InvOwnedLo InvOwnedHi InvViewedLo InvViewedHi InvSelected InvAmmo PlayerStatus PlayerSize GuestPowerupActive MmChargeFrames MmCharging MmBulletType RgShotType SsMode MmRushLandRequest GameEngineSubroutine InjuryTimer GuestHurtTicks MmDeathFlag CheatInvincible'''.split()
CONTACT=[0,9,10,11,12,19,16,17,0,0,0]
SFX=[0,0,64,22,61,65,22,67,0,0,0]

def scene(q,item=None):
    assert not any(q.get('RgShotType',i) for i in range(10))
    assert not any(q.get('MmBulletType',i) for i in range(4))
    assert q.get('SsHeld')==q.get('MmSliding')==0
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in [0,1]:
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',0x54,page*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    for i in range(4):q.set('InvDropKind',0,i)
    q.put(Player_X_Position=64,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255,
          MmOldX=64,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,
          ScreenRight_PageLoc=0,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0,
          Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0)
    for n,size in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:q.array(n,[0]*size)
    if item is not None:
        for n,v in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_BoundBoxCtrl=3,
                        Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=184,
                        Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_SprAttrib=0,
                        PowerUpType=0 if item==0 else 1,InvPickupOwner=1,InvPickup=item).items():q.set(n,v,5)
        if item==254:q.set('AvPickupAmmoItem',0,5)

def target(q,item):
    x=y=None
    if item==5:
        if q.get('SsKick')==1 and q.get('MmSliding'):
            x=q.get('Player_X_Position')+22;y=q.get('Player_Y_Position')+8
    else:
        for i in range(10):
            if q.get('RgShotType',i)!=CONTACT[item] or q.get('SsHidden',i):continue
            if item==1 and q.get('SsMode',i)!=0:continue
            if item==3 and q.get('RgShotAge',i)<10:continue
            if item==7 and not(q.get('SsWaterExpand') and q.get('SsWaterRadius')>=42):continue
            sx,sy=q.get('RgShotX',i),q.get('RgShotY',i)
            if q.get('RgShotPage',i)==0 and abs(sx-q.get('Player_X_Position'))>=30 and 16<=sx<232 and q.get('RgShotYHigh',i)==1 and 48<=sy<216:
                x,y=sx-6,sy-8;break
    if x is None:return False
    assert 0<=x<240 and 32<=y<216
    for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,
                    Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,
                    Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,Enemy_BoundBoxCtrl=9,
                    EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,
                    MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0).items():q.set(n,v,0)
    return True

def campaign(b,variant):
    q=Arena(b,1)
    q.put(ProtoVariant=variant,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit')
    raw=lambda n,i=0:b['raw'][location(b,n)+i]
    rows=[];current={};age=0;calls=0;phase='initial';pending=None
    names=['GameLoop','X5BounceUiDispatch','InventoryUiTick','InventoryCycle',
           'MarioSourcePowerupCollision','InventoryCollect','InventoryGrant','GuestPowerupUpdate',
           'MegaManWeapons::Spawn','MegaManRushAttack','MegaManRushBounce',
           'SpecialWeapons','SpecialWeapons::MegaAttack','MegaManSuperArmThrow',
           'InventorySpend','InventorySpend::Done','MegaManWeapons::DamageEnemy']
    owners={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    original=NesMPU.step
    def step(cpu):
        nonlocal pending
        bank=q.m.banks[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1
        n=owners.get((cpu.pc,bank))
        if n:
            if n not in current['owners']:current['owners'].append(n)
            if n=='MarioSourcePowerupCollision':
                assert cpu.x==5 and q.get('Enemy_Flag',5) and q.get('InvPickupOwner',5)==1
                current['collision']+=1
            elif n=='InventoryCollect':
                assert q.get('Enemy_Flag',5)==q.get('Enemy_State',5)==0 and current['collision']==1
                current['collect']+=1
            elif n=='InventoryGrant':current['grants'].append(cpu.a)
            elif n=='GuestPowerupUpdate' and q.get('GuestPowerupActive'):current['growth']+=1
            elif n=='InventorySpend' and phase=='use':
                assert pending is None and cpu.a==current['item'] and cpu.y==current['cost']
                pending=(cpu.a,q.get('InvAmmo',16+cpu.a),cpu.y,cpu.sp)
            elif n=='InventorySpend::Done' and pending:
                i,before,cost,sp=pending;assert cpu.sp==sp and q.get('InvAmmo',16+i)==before-cost
                current['debits'].append(dict(before=before,cost=cost,after=q.get('InvAmmo',16+i),age=age));pending=None
            elif n=='MegaManWeapons::DamageEnemy' and phase=='use':
                assert cpu.x==0 and q.get('MmBulletType')==current['proxy']
                current['contacts']+=1
            elif n=='MegaManWeapons::Spawn' and phase in ['charge','rush-existing']:
                assert cpu.a in ([1,3] if phase=='charge' else [1])
                if cpu.a==3:assert q.get('MmChargeFrames')==87
                current['primary'].append(dict(type=cpu.a,charge=q.get('MmChargeFrames'),age=age))
            elif n=='MegaManRushBounce':
                assert phase=='rush-contact' and q.get('StarInvincibleTimer')==0
                current['bounce'].append(q.get('InvAmmo',24))
        original(cpu)
    def fresh(item):
        nonlocal current
        current=dict(item=item,owners=[],collision=0,collect=0,grants=[],growth=0,debits=[],
                     contacts=0,hp_writes=0,types=[],sounds=[],primary=[],bounce=[])
        rows.append(current)
    def tick(bits=0):
        nonlocal calls
        q.put(SavedJoypadBits=bits)
        _,writes=q.invoke('GameLoop');calls+=1
        assert q.get('MmDeathFlag')==q.get('InjuryTimer')==q.get('GuestHurtTicks')==0,(phase,age,'hurt')
        assert (q.get('GameEngineSubroutine')==8 or phase=='collect' and current['item']==0 and q.get('GuestPowerupActive') and q.get('GameEngineSubroutine')==9) and q.get('ProtoVariant')==variant,(phase,age,current['item'],q.get('GameEngineSubroutine'),q.get('ProtoVariant'),q.get('Player_Y_Position'))
        for w in writes:
            if address(b,'RgShotType')<=w['address']<address(b,'RgShotType')+10 and w['value']:
                if w['value'] not in current['types']:current['types'].append(w['value'])
            if w['address'] in [address(b,'MmEnemyHealthLo'),address(b,'MmEnemyHealthHi')]:current['hp_writes']+=1
            if w['address']==address(b,'SsAudioRequest') and w['value'] not in current['sounds']:current['sounds'].append(w['value'])
        # CPU environment services the real queued Buffer1 consumer between
        # updates. Then model only resident InitBuffer's two zero stores; no
        # resource, actor, timer, selection or tested outcome is changed here.
        ptr=address(b,'VRAM_Buffer1')
        q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0)
        q.invoke('SamusFreezeUpdateScreen')
        q.put(VRAM_Buffer1_Offset=0,VRAM_Buffer1=0)
        return writes
    def empty():return not any(q.get('RgShotType',i) for i in range(10)) and not any(q.get('MmBulletType',i) for i in range(4))
    NesMPU.step=step
    try:
        for item in range(10):
            fresh(item);phase='collect';scene(q,item)
            before=[q.get('InvAmmo',i) for i in range(17,25)]
            assert not(q.get('InvOwnedLo',1)+256*q.get('InvOwnedHi',1))&(1<<item)
            for age in range(240):
                tick()
                if current['collect'] and not q.get('GuestPowerupActive') and not q.get('TimerControl'):break
            assert current['collision']==current['collect']==1 and q.get('PlayerStatus')==1
            assert (q.get('InvOwnedLo',1)+256*q.get('InvOwnedHi',1))&(1<<item)
            assert before==[q.get('InvAmmo',i) for i in range(17,25)]
            current['earned_collection']=dict(item=item,collision=current['collision'],collect=current['collect'],
                                             ownedLo=q.get('InvOwnedLo',1),ownedHi=q.get('InvOwnedHi',1),
                                             ammo_unchanged=before)
            if item==0:
                assert current['growth']==60 and q.get('InvOwnedHi',1)&4
                phase='charge'
                for age in range(211):tick(64 if 4<=age<113 else 0)
                assert [x['type'] for x in current['primary']]==[1,3] and empty() and q.get('MmChargeFrames')==0
                continue
            assert current['grants']==[item]
            phase='select';want=item if item<9 else 0
            for age in range(180):
                tick(32 if age%8==1 else 0)
                if q.get('InvSelected',1)==want:break
            assert q.get('InvSelected',1)==want
            # Match the native20-update HUD settlement, without claiming CPU PPU timing.
            for age in range(20):tick()
            if item<8:
                phase='use';scene(q)
                if item==1:q.set('Block_Buffer_1',0x51,165)
                current.update(cost=raw('InvCosts',16+item),proxy=raw('SpecialWeapons::DamageTypes',CONTACT[item]-9))
                placed=False;held=False;paid=False;expanded=False
                for age in range(480):
                    if not placed:placed=target(q,item)
                    bits=(4 if 4<=age<9 else 0)|(128 if 5<=age<8 else 0) if item==5 else 64 if ((5<=age<9 or 16<=age<20) if item==1 else (5<=age<8 or 125<=age<128) if item==7 else 5<=age<8) else 0
                    tick(bits)
                    held|=bool(q.get('SsHeld'));paid|=q.get('SsKick')==1 and bool(q.get('MmSliding'));expanded|=bool(q.get('SsWaterExpand'))
                    if age>=210 and empty() and not q.get('SsHeld') and not q.get('MmSliding'):break
                assert age<479 and placed and current['contacts'] and current['hp_writes'],(item,age,current)
                assert len(current['debits'])==1 and CONTACT[item] in current['types']
                assert not SFX[item] or SFX[item] in current['sounds']
                assert item!=1 or held;assert item!=5 or paid;assert item!=7 or expanded
                current.update(updates=age+1,actual_target=True,held=held,paid_slide=paid,expanded=expanded)
            elif item==8:
                phase='rush-summon';scene(q);stock=q.get('InvAmmo',24);modes=set();slot=None
                for age in range(300):
                    tick(64 if 5<=age<9 else 0)
                    for i in range(10):
                        if q.get('RgShotType',i)==20:
                            slot=i;modes.add(q.get('SsMode',i))
                    if slot is not None and q.get('SsMode',slot)==1:break
                assert age<299 and q.get('RgShotY',slot)==208 and q.get('InvAmmo',24)==stock
                for age in range(24):tick()
                phase='rush-existing'
                for age in range(100):
                    tick(64 if 5<=age<9 else 0)
                    if age>=55 and not any(q.get('MmBulletType',i) for i in range(4)):break
                assert current['primary'] and q.get('InvAmmo',24)==stock
                # Complete falling-position fixture; never seed Rush state or a debit.
                x=q.get('RgShotX',slot)-8
                q.put(Player_X_Position=x,MmOldX=x,Player_PageLoc=q.get('RgShotPage',slot),
                      Player_Y_Position=160,Player_Y_HighPos=1,Player_State=2,Player_Y_Speed=2,
                      Player_X_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0,MmFrictionYActive=0)
                for n in ['MmVX','MmVY']:q.array(n,[0,0,0])
                q.set('MmVY',2,2)
                for n in ['MmXFraction','MmYFraction']:q.array(n,[0,0])
                phase='rush-contact';launch=False
                for age in range(300):
                    tick()
                    if q.get('RgShotType',slot)==20:modes.add(q.get('SsMode',slot))
                    if current['bounce'] and q.get('Player_State')==1:
                        assert q.get('MmVY',2)>=128 and q.get('MmJumpReleased')==1 and q.get('MmFrictionYActive')==0
                        launch=True;break
                assert launch and current['bounce']==[stock] and q.get('InvAmmo',24)==stock-12
                phase='rush-depart'
                for age in range(300):
                    tick()
                    if q.get('RgShotType',slot)==20:modes.add(q.get('SsMode',slot))
                    if age>=100 and empty() and q.get('Player_State')==0:break
                assert age<299 and modes=={0,1,2,3,4} and q.get('InvAmmo',24)==stock-12
                current.update(rush_modes=sorted(modes),free_summon_stock=stock,bounce_after=stock-12,launch=True)
            else:
                phase='balance';before=[q.get('InvAmmo',16+i) for i in range(1,9)]
                low=min(before);chosen=before.index(low)+1;assert low<112
                # Reset counters for the separate physical FE energy actor.
                current['collision']=0;current['collect']=0;scene(q,254)
                for age in range(240):
                    tick()
                    if current['collect'] and q.get('InvRefill')==q.get('TimerControl')==0:break
                after=[q.get('InvAmmo',16+i) for i in range(1,9)]
                assert after==[min(112,v+40) if i==chosen else v for i,v in enumerate(before,1)]
                assert current['collect']==current['collision']==1 and 63 in current['sounds'] and 242 in current['sounds']
                current.update(refill_before=before,refill_after=after,chosen_index=16+chosen,amount=40)
    finally:NesMPU.step=original
    assert pending is None and calls<5000
    return dict(passed=True,ROM_sha256=EXPECTED,variant=variant,mode=1,complete_GameLoop_calls=calls,
                actual_collections=list(range(10))+[254],auto_Charge10=True,source_CPU_only=True,
                consumer_environment='Between complete GameLoops, actual SamusFreezeUpdateScreen consumes Buffer1, followed by the same two InitBuffer zero stores. This avoids a fictitious forever-full VRAM queue in the CPU arena; no NMI/timing claim.',
                cases=rows,limits='No native menu, PPU/timing, screenshots, Lua execution, acquisition emergence/RNG or sound waveform proof.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--identity',choices=['megaman','proto'],required=True)
    ap.add_argument('--rom',type=Path,default=ROOT/'build/bill_early_cache.nes');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--refresh-unrun',action='store_true')
    a=ap.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve();assert sha(a.rom)==EXPECTED
    if a.output.exists():
        prior=json.loads((a.output/'prepared-not-run.json').read_text())
        assert a.refresh_unrun and prior['status']=='PREPARED_DO_NOT_RUN' and not prior['native_run'] and prior['identity']==a.identity and prior['ROM_sha256']==EXPECTED
        assert {p.name for p in a.output.iterdir()}=={'prepared-not-run.json','source-controls.json','config.json','run.lua','command.json'},'Never overwrite native evidence or any unrecognized file'
    b=scoped_load(a.rom);raw=b['raw'];variant=int(a.identity=='proto')
    fixture=ROOT/'tools/audit/current_mega_arsenal_v1.lua';text=fixture.read_text();parent=ROOT/'tests/current-inventory-powerups.lua';old=parent.read_text()
    start='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    guard=text[text.index(start):text.index(end)];assert guard==old[old.index(start):old.index(end)]
    assert text.count('emu.write(')==2 and text.count('emu.takeScreenshot(')==1 and 'images<8' in text
    assert not set(ALLOWED)&set(FORBIDDEN) and not set(re.findall(r"\bw\('([^']+)'",text))&set(FORBIDDEN)
    assert 'removeMemoryCallback' not in text and 'dofile(' not in text
    byte=lambda n,i=0:raw[location(b,n)+i]
    def hook(n,delta=0,count=3):
        at=location(b,n)+delta;k=(at-16)//8192;bs=list(raw[at:at+count]);banks=[k]
        if k==127:
            off=(at-16)%8192;assert raw[16+125*8192+off:16+125*8192+off+count]==bytes(bs);banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    hooks={k:hook(n) for k,n in dict(PhysicalPickup='MarioSourcePowerupCollision',InventoryCollect='InventoryCollect',InventoryGrant='InventoryGrant',InventorySpend='InventorySpend',GuestPowerupUpdate='GuestPowerupUpdate',DamageEnemy='MegaManWeapons::DamageEnemy',PrimarySpawn='MegaManWeapons::Spawn',RushAttack='MegaManRushAttack',RushBounce='MegaManRushBounce',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
    at=location(b,'GameLoop');nd=address(b,'NmiDisable');assert raw[at:at+5]==bytes([169,255,141,nd&255,nd>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
    for k,n,op in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        d=int(b['syms'][n]['size'],0)-1;assert byte(n,d)==op;hooks[k]=hook(n,d,1)
    assert byte('InventorySpend::Done')==96;hooks['InventorySpendDone']=hook('InventorySpend::Done',0,1)
    mirror=address(b,'Mirror_PPUMASK');load=bytes([165,mirror]) if mirror<256 else bytes([173,mirror&255,mirror>>8]);post=location(b,'PostDmaMaskEnable')
    assert raw[post-3:post]==b'\x8d\x14\x40' and raw[post:post+len(load)+3]==load+b'\x8d\x01\x20';hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load));assert hooks['DmaComplete']['pc']==0xe008
    menu=list(raw[location(b,'X5MenuCharacters'):location(b,'X5MenuCharacters')+19]);assert menu.count(1)==1;slot=menu.index(1)
    assert byte('InvItemCount',1)==10 and byte('InvMushroomHi',1)==4
    items={}
    for i in range(11):
        idx=16+i;ptr=byte('InvNameLo',idx)+256*byte('InvNameHi',idx);g=b['segs'][b['syms']['InvNameLo']['seg']];p=int(g['ooffs'],0)+ptr-int(g['start'],0)
        items[i]=dict(id=i,hud_name=list(raw[p:p+7]),cost=byte('InvCosts',idx),initial_ammo=byte('InvInitialAmmo',idx),max_ammo=byte('InvMaxAmmo',idx),selectable=byte('InvSelectable',idx),auto_equip=byte('InvAutoEquip',idx),contact_type=CONTACT[i],damage_type=byte('SpecialWeapons::DamageTypes',CONTACT[i]-9) if CONTACT[i] else 0,sfx=SFX[i])
    assert [items[i]['cost'] for i in range(1,9)]==[8,4,8,4,4,4,16,12]
    assert all(items[i]['selectable']==1 and items[i]['initial_ammo']==items[i]['max_ammo']==112 for i in range(1,9))
    assert items[9]['selectable']==items[10]['selectable']==0
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))|set(ALLOWED)|{'CurrentBank','CurrentBankC','Sprite0HitDetectFlag','ProtoVariant'}
    ram={n:address(b,n) for n in names if n in b['syms']}
    for n in set(ALLOWED)|set(re.findall(r"\b[rw]\('([^']+)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text)):assert n in ram,n
    store=location(b,'MegaManWeapons::FoundSlot')+3;pc=address(b,'MegaManWeapons::FoundSlot')+3
    assert raw[store-3:store]==bytes([173,address(b,'MmTemp')&255,address(b,'MmTemp')>>8]) and raw[store:store+3]==bytes([157,address(b,'MmBulletType')&255,address(b,'MmBulletType')>>8])
    cfg=dict(ROM_sha256=EXPECTED,identity=a.identity,character=1,slot=slot,variant=variant,mode=1,frame_limit=12000,update_limit=5000,charge_full=87,rush=dict(summon_gate=4,bounce_cost=12,playable_Jet=False),navigation=navigation(raw,lambda n:location(b,n),slot),hooks=hooks,ram=ram,items=items,primary_store=dict(pc=pc,after=pc+3,bank=(store-16)//8192,bytes=list(raw[store:store+3])),setup_allowed={n:True for n in ALLOWED},powerup_sfx=address(b,'Sfx_PowerUpGrab'),dma_store_return=address(b,'PostDmaMaskEnable'),metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192) for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    mirrored=[]
    for name in ['NonMaskableInterrupt','IrqScrollSplit','OAMandReadJoypad']:
        pos=location(b,name);size=int(b['syms'][name]['size'],0);k=(pos-16)//8192
        assert size>0
        off=(pos-16)%8192;body=raw[pos:pos+size];banks=[k]
        if k==127:
            assert raw[16+125*8192+off:16+125*8192+off+size]==body,'Full actual bank125/127 owner equality'
            banks=[125,127]
        else:assert name=='IrqScrollSplit' and k==126 and address(b,name)==0x8000
        mirrored.append(dict(symbol=name,PC=address(b,name),banks=banks,bytes=size,sha256=hashlib.sha256(body).hexdigest()))
    source=campaign(b,variant)
    source.update(static_hardware_guard_sha256=hashlib.sha256(guard.encode()).hexdigest(),whole_mirrored_interrupt_input_owners=mirrored)
    a.output.mkdir(parents=True,exist_ok=True);put(a.output/'source-controls.json',source);put(a.output/'config.json',cfg)
    (a.output/'run.lua').write_text('CURRENT_MEGA_ARSENAL='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),str(a.output/'run.lua'),str(a.rom),'--timeout','1800','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths=[a.rom,a.rom.with_suffix('.dbg'),a.rom.with_suffix('.lbl'),fixture,parent,Path(__file__),ROOT/'tests/current-mega-body-components.lua',ROOT/'tools/audit/current_mega_body_components_prepare_v1.py',ROOT/'docs/qa/current37-powerup-reuse-index-2026-10-27.json']
    paths += [ROOT/'tools/audit'/n for n in ['link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','observe_chip_committed_write.py','current_roster_compact_11_v1.py','run_mesen_isolated.py','capture_budget.py']]+[ROOT/'tools/run_mesen.py']
    paths += [ROOT/'src'/n for n in ['inventory.s','inventory_data.inc','inventory_drops.s','game.s','object.s','guest_powerups.s','mario_source.s','megaman_weapons.s','megaman_physics.s','megaman_rush.s','megaman_super_arm.s','special_weapons.s','special_art.inc','special_art_ids.inc','megaman_special_poses.inc','megaman_special_pose_ids.inc','protoman_cold.s','proto_palette_ack.s']]
    paths += [a.output/n for n in ['config.json','run.lua','source-controls.json','command.json']]
    put(a.output/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=EXPECTED,identity=a.identity,character=1,variant=variant,actual_numeric_mode=1,scope='Real mature0 mushroom/60transform/autoCharge10/full87 release; actual typed1..7 pickups/Select/action/live-effect target/contact/source cost/cleanup; Rush8 free summon/existing buster/real12 spring/departure; passive9 Balancer plus actual FE254 refill40 into least genuinely spent pool.',source_controls_passed=True,full_GameLoop_CPU_calls=source['complete_GameLoop_calls'],hardware_guard_literal_from_current_Bass=True,hardware_guard_sha256=hashlib.sha256(guard.encode()).hexdigest(),caps=dict(updates=5000,wall_frames=12000,host_seconds=1800,bytes=2000000000,files=64,PNGs=8),setup='Only complete scene/player position/motion, mature actor metadata and live-effect-aligned default-health enemy in private GameLoop+5/NmiDisableFF; Rush contact discloses a descending player placement. No ownership/tier/ammo/selection/fuel/charge/projectile/form/outcome seeds. Earlier drops are cleared only between declared independent scenes; genuine later ammo credits are not suppressed.',limits='Hard only; one facing; no block reveal/full rise/RNG or natural encounter claim; no empty/full-pool/exhaustion, charged Pharaoh8 debit, Rush zero4 gate/clamp/Jet, duplicate caps, star/1up, hurt/reacquire, every-pose/opaque visibility/audio fidelity/cadence claim. Seven effect samples plus one Rush spring maximum; charge graphics not sampled. Native success not inferred from CPU; Lua syntax/execution pending actual reviewed launch.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]))
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',identity=a.identity,ROM_sha256=EXPECTED,ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),full_GameLoop_calls=source['complete_GameLoop_calls'])))

if __name__=='__main__':main()
