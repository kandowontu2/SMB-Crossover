"""Bounded legal Bill/Lance Hard inventory and real compiled weapon owners."""
from pathlib import Path
import argparse
import json
from final_samus_hard_gallery_source_v1 import TraceArena, OWNER_NAMES, D, ROOT, sha, put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

PARENT = D/'root-current-roster-composition-v1'
SHA = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
GUNS = [0, 2, 3, 4, 5]
NAMES = {0:'normal', 2:'laser', 3:'flare', 4:'machine', 5:'spread'}
EXTRA_OWNERS = [
    'InventoryCollect', 'InventoryGrant', 'InventoryPreparePickup::Available',
    'RosterWeapons', 'RosterWeapons::BillInput', 'RosterWeapons::BillFire',
    'RosterWeapons::SpawnBill', 'RosterWeapons::MachineCadence',
    'BillSpreadFanOrdered', 'AvBillInput', 'AvBillSpeedIndex',
    'BillSourceProjection', 'BillAdvancedBirth', 'BillAdvancedExpiry',
    'BillAdvancedFlareStep', 'BillAdvancedDrawArt', 'BillLaserSpacingParameters',
    'RosterEnemyHit', 'RosterBlockHit', 'BillLaserSourceBlocks',
]


def plans():
    specs = [(0,[],0,1,1), (4,[4],4,17,2), (5,[5],5,33,3),
             (2,[2],2,5,42), (3,[3],3,9,43),
             (1,[4,1],4,19,2), (6,[4,1,6],4,83,2)]
    rows=[]
    for i,(item,grants,selected,owned,typ) in enumerate(specs,1):
        name = 'machine-rapid1' if item==1 else 'machine-rapid2' if item==6 else NAMES[item]
        rows.append(dict(case=i,name=name,upgrade=item,grant_sequence=grants,
            initial_mushroom_owned=1,expected_owned=owned,expected_selected=selected,
            shot_type=typ,expected_initial_emissions=5 if typ==3 else 4 if typ==42 else 1,
            passive=bool(item in [1,6]),tasks=[
                dict(kind='free',face=1),dict(kind='contact',face=2),
                dict(kind='terrain',face=1),dict(kind='auto-cadence' if typ==2 else 'second-edge',face=2)],
            acquisition=False))
    return rows


class BillArena(TraceArena):
    def __init__(self,b,variant=0):
        super().__init__(b)
        self.put(SelectedCharacter=3,BillVariant=variant,CrossoverBehaviorVersion=1,
                 Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
                 ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,
                 ScreenRight_X_Pos=255,DisableScreenFlag=0,PlayerStatus=1)
        self.set('InvOwnedLo',0,2)
        self.set('InvOwnedLo',1,3)

    def grant(self,item):
        self.set('InvPickup',item,5)
        self.set('InvPickupOwner',3,5)
        c,_=self.invoke('InventoryCollect',x=5)
        assert c.p&1 and c.x==5
        assert any(q['owner']=='InventoryGrant' for q in self.calls[-1]['entries'])

    def buttons(self,b):
        old=self.get('A_B_Buttons')
        self.put(SavedJoypadBits=b,SavedJoypad1Bits=b,A_B_Buttons=b&192,
                 PreviousA_B_Buttons=old,InvFresh=b&~self.get('InvPrevious'))
        self.put(InvPrevious=b)
        return self.invoke('ProcFireball_Bubble')


def state(q):
    return dict(owned=q.get('InvOwnedLo',3),selected=q.get('InvSelected',3),
                types=[q.get('RgShotType',i)for i in range(10)])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(PARENT/'candidate.nes')==SHA
    b=scoped_load(PARENT/'candidate.nes')
    for n in EXTRA_OWNERS:
        if n in b['syms'] and n not in OWNER_NAMES:OWNER_NAMES.append(n)
    source=PARENT/'source'
    manifest=json.loads((PARENT/'source-manifest.json').read_text())
    for n,h in manifest.items():assert sha(source/n)==h,n
    refs=ROOT/'reference/crossover2/extracted/scripts/com/smbc'
    reference_files=[ROOT/'reference/crossover2/source.swf',refs/'characters/Bill.as',
                     refs/'characters/Character.as',refs/'projectiles/BillBullet.as',refs/'data/PickupInfo.as']
    assert sha(reference_files[0])=='6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    bill=(refs/'characters/Bill.as').read_text()
    assert 'SINGLE_UPGRADES_ARR:Array = [[BILL_LASER,BILL_FLARE,BILL_MACHINE,BILL_SPREAD]]' in bill
    assert 'REPLACEABLE_UPGRADES_ARR:Array = [[BILL_RAPID_1,BILL_RAPID_2]]' in bill
    value=lambda n,i=0:b['raw'][location(b,n)+i]
    tables={n:[value(n,48+i)for i in range(7)]for n in
            ['InvSelectable','InvAutoEquip','InvSingleLo','InvAvailability','InvCosts','InvAmmoIndex']}
    assert tables['InvSelectable']==[0]*7 and tables['InvAutoEquip']==[0,0,1,1,1,1,0]
    assert tables['InvSingleLo']==[0,0,56,52,44,28,0]
    assert tables['InvAvailability']==[0,255,255,255,255,255,1]
    assert tables['InvCosts']==[0]*7 and tables['InvAmmoIndex']==[255]*7
    rows=[];calls=0
    # Every tested initial state is reachable by a legal gun and two sequential
    # passive upgrades. No mutually-exclusive all-guns-owned seed is admitted.
    for variant in [0,1]:
      for gun in GUNS:
       for rapid in [0,1,2]:
        for upgrade in [1,2,3,4,5,6]:
         if upgrade==6 and rapid==0:continue
         q=BillArena(b,variant)
         for item in ([gun]if gun else[])+([1]if rapid else[])+([6]if rapid==2 else[]):q.grant(item)
         before=state(q)
         assert (before['owned']&60).bit_count()<=1
         q.grant(upgrade);after=state(q)
         expected=(before['owned']&~tables['InvSingleLo'][upgrade])|(1<<upgrade)
         assert after['owned']==expected and (expected&60).bit_count()<=1
         assert after['selected']==(upgrade if 2<=upgrade<=5 else before['selected'])
         rows.append(dict(kind='complete-physical-collect-grant-consumer',variant=variant,
             before=before,upgrade=upgrade,after=after,calls=q.calls))
         calls+=len(q.calls)
    availability=[]
    for owned,want in [(1,False),(3,True),(67,False)]:
        q=BillArena(b);q.set('InvOwnedLo',owned,3);q.put(InvCandidate=6)
        c,_=q.invoke('InventoryPreparePickup::Available')
        assert bool(c.p&1)==want,(owned,c.p)
        availability.append(dict(owned=owned,Rapid2_available=want,calls=q.calls))
    emitted=[];cleanup=[];palettes={}
    for variant in [0,1]:
      for plan in plans():
       for face in [1,2]:
        q=BillArena(b,variant);q.put(PlayerFacingDir=face,Player_MovingDir=face)
        for item in plan['grant_sequence']:q.grant(item)
        assert state(q)['owned']==plan['expected_owned'] and state(q)['selected']==plan['expected_selected']
        c,_=q.invoke('AvBillSpeedIndex')
        expected_index=(1 if plan['shot_type']==2 else 2 if plan['shot_type']==3 else 0)+(6 if plan['upgrade']==6 else 3 if plan['upgrade']==1 else 0)
        assert c.a==expected_index,(plan['name'],c.a,expected_index)
        q.buttons(0);c,trace=q.buttons(64)
        active=[dict(slot=i,type=q.get('RgShotType',i),vx=q.get('RgShotVXLo',i)+256*q.get('RgShotVXHi',i),
            vy=q.get('RgShotVYLo',i)+256*q.get('RgShotVYHi',i),hidden=q.get('SsHidden',i),dir=q.get('RgShotDir',i))
            for i in range(10)if q.get('RgShotType',i)]
        assert len(active)==plan['expected_initial_emissions'] and {v['type']for v in active}=={plan['shot_type']},(plan['name'],active)
        assert all(v['dir']==face for v in active)
        owners={v['owner']for v in q.calls[-1]['entries']}
        assert {'ProcFireball_Bubble','RosterWeapons','AvBillInput'}<=owners,(plan['name'],owners)
        if plan['shot_type']in[42,43]:assert 'BillAdvancedBirth'in owners
        else:assert 'BillSourceProjection'in owners
        speed=abs(active[-1]['vx']-65536 if active[-1]['vx']>=32768 else active[-1]['vx'])
        emitted.append(dict(variant=variant,case=plan['name'],face=face,speed_index=expected_index,
                            horizontal_q8_speed=speed,active=active,calls=q.calls))
        expired=None
        for tick in range(1,401):
            q.buttons(0)
            if not any(q.get('RgShotType',i)for i in range(10)):
                expired=tick;break
        assert expired is not None,(variant,plan['name'],face,state(q))
        cleanup.append(dict(variant=variant,case=plan['name'],face=face,natural_empty_after_updates=expired,
                            final=state(q),calls=q.calls[-1:]))
        q.invoke('GetPlayerColors');length=q.get('VRAM_Buffer1_Offset')
        packet=[q.get('VRAM_Buffer1',i)for i in range(length+1)]
        palettes[f'{variant}:{plan["expected_owned"]}']=packet
        calls+=len(q.calls)
    cadence=[]
    for variant in [0,1]:
      for rapid in [0,1,2]:
        q=BillArena(b,variant)
        for item in [4]+([1]if rapid else[])+([6]if rapid==2 else[]):q.grant(item)
        births=[]
        for tick in range(80):
            c,t=q.buttons(64)
            stores=[v for v in t if address(b,'RgShotType')<=v['address']<address(b,'RgShotType')+10 and v['value']==2]
            if stores:births.append(tick)
        assert births[:6]==[0,7,14,20,27,33],(rapid,births)
        cadence.append(dict(variant=variant,rapid=rapid,birth_updates=births,
            first_six_delta=[b-a for a,b in zip(births[:5],births[1:6])],
            scope='Actual complete held input path; Rapid changes source bullet speed, not110ms machine cadence.'))
    protocols=dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,
        lane='B controlled use; no cold physical block/reveal/rise/transform acquisition claim',
        cases_per_identity=7,identities=['Bill','Lance'],numeric_mode=1,
        legal_single_gun_bitmask=60,passive_rapid_bits=[2,64],Rapid2_prerequisite=1,
        grants='Native InventoryCollect -> InventoryGrant auto-equips guns2..5; passive1/6 leave current gun selected.',
        no_Select_cycle=True,no_weapon_ammo=True,
        native_seed_policy='At a guarded GameLoop entry seed only legal mushroom/carried passive state and a complete controlled physical pickup actor for the next upgrade. Actual pickup collision/InventoryCollect/InventoryGrant must commit each requested grant; never seed InvSelected or outcome/hit/HP/RNG/mode.',
        plans=plans(),tables=tables,references={str(f):sha(f)for f in reference_files},
        compiled_owner_metadata={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192,
            bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in EXTRA_OWNERS if n in b['syms']},
        remaining=['Prepare controlled native observer/controller with original static/DMA/NMI/5SMC/CHR guards.',
            'Native real emit/contact/terrain/render/HUD/cadence/cleanup and actual imagery unproved. No native grant.'])
    put(a.output/'inventory-protocol.json',protocols)
    put(a.output/'grant-controls.json',dict(passed=True,cases=len(rows),rows=rows,availability=availability))
    put(a.output/'emission-controls.json',dict(passed=True,cases=len(emitted),rows=emitted,cleanup=cleanup,
        cadence=cadence,palette_packets=palettes,limits='Actual assembled isolated complete gateways. No emulated NMI/PPU/native waveform/campaign claim.'))
    files={Path(__file__),PARENT/'candidate.nes',PARENT/'candidate.dbg',PARENT/'source-manifest.json'}
    files.update(source/n for n in ['src/inventory.s','src/inventory_data.inc','src/remaining_weapons.s','src/roster_weapons.s','src/guest_powerups.s','src/bill_flare_lifetime.inc','src/roster.s'])
    files.update(reference_files);files.update(a.output.iterdir())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=SHA,
        grant_cases=len(rows),availability_cases=len(availability),emission_cases=len(emitted),
        cleanup_cases=len(cleanup),cadence_cases=len(cadence),cases_per_identity=7,
        manifest_sha256=sha(a.output/'manifest.json'),checker_sha256=sha(__file__)))
    print(json.dumps(json.loads((a.output/'proof.json').read_text())))


if __name__=='__main__':main()
