"""Current whole-Main branch parity and exact original pickup-bit comparison."""
import itertools,json,sys
from pathlib import Path
from py65.devices.mpu6502 import MPU
from prepare_selected_native_packet_v1 import R,sha
import measure_bub_landing_1102_v21 as L
import check_bubble_bobble_native_stomp_1102_v7 as V
import prepare_bub_original_upgrades_1102_v48 as U
O=R/'build/bub-upgrades-root-qualification-1102-v49'
N,Q,address=L.N,L.Q,L.address

def bundles():
    q=json.loads((U.O/'proposal.json').read_text())
    for name,h in q['bindings'].items():assert sha(R/name)==h,name
    _,old,_,route=L.E.bundle();raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();assert U.PIN==L.P.sha(raw)
    old=dict(old,raw=raw);newraw=bytearray(raw);image=(U.O/'private-image.bin').read_bytes()
    for i,page in enumerate(q['pages']):newraw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    newraw[q['cookie_offset']:q['cookie_offset']+16]=bytes.fromhex(q['new_cookie'])
    assert L.P.sha(newraw)==q['expected_memory_only_ROM_SHA256']
    return old,dict(old,raw=bytes(newraw)),route,q

def donor_item(rom,identity,kind,flags):
    c=MPU();c.memory[0x8000:0xc000]=rom[16+6*16384:16+7*16384];c.memory[0xc000:]=rom[16+7*16384:16+8*16384]
    actor=0x42 if identity else 0x2e;c.memory[actor+2]=flags;c.memory[0x410]=kind|(128 if identity else 0);c.memory[0x411]=14;c.pc=0x9a3a;c.sp=253
    for _ in range(500):
        if c.pc==0xa064:break
        c.step()
    else:raise AssertionError(('original item dispatcher bound',identity,kind,hex(c.pc)))
    assert c.memory[0x410]==c.memory[0x411]==0
    return c.memory[actor+2]

def main():
    O.mkdir(exist_ok=True);old,new,route,q=bundles();cycles=[];motion=[];seeds={}
    fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed','NumberofLives','Player_X_Scroll','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Pos_ForScroll']
    for identity in[0,1]:
        for direction,jump in[(0,False),(1,False),(2,False),(1,True),(2,True)]:
            pair=[Q.fresh(b,route,identity)for b in[old,new]]
            for m in pair:L.E.main_fields(m);N.put(m,Player_X_Position=96)
            for epoch in range(100):
                keys=direction|(128 if jump and epoch==1 else 0);out=[]
                for m in pair:
                    N.put(m,FrameCounter=epoch&255,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    out.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
                a,b=pair
                if[N.get(a,n)for n in fields]!=[N.get(b,n)for n in fields]:
                    diagnostic=dict(passed=False,identity=identity,direction=direction,jump=jump,epoch=epoch,native={n:[N.get(a,n),N.get(b,n)]for n in fields},private_first_differences=[dict(offset=i,old=a.ram[2][i],new=b.ram[2][i])for i in range(1024)if a.ram[2][i]!=b.ram[2][i]][:32],out=out)
                    (O/'negative.json').write_text(json.dumps(diagnostic,indent=2)+'\n');raise AssertionError(diagnostic)
                assert a.ram[2][:1024]==b.ram[2][:1024],(identity,direction,jump,epoch,'source-state')
                assert a.ram[2][0x1000:0x1400]==b.ram[2][0x1000:0x1400]
                assert bytes(a[3:11])==bytes(b[3:11])and a.rawtags==b.rawtags
                assert[out[0][k]for k in['A','X','Y','P']]==[out[1][k]for k in['A','X','Y','P']]
                cycles.append((out[0]['CPU'],out[1]['CPU']))
            motion.append(dict(identity=identity,direction=direction,jump=jump,Main_epochs=100,coordinates_source_state_and_AXYP_exact=True))
        seeds[identity]=Q.fresh(new,route,identity)
    donor=Path('C:/NES/Bubble Bobble (USA).nes');rom=donor.read_bytes();assert sha(donor)=='e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0'
    count=0;immature=0;native=0
    for identity,item,slot,flags,mature in itertools.product([0,1],range(4),[0,5],range(256),[False,True]):
        m=N.fork(seeds[identity]);actor=0x42 if identity else 0x2e;m.ram[2][actor+2]=flags
        m[address(new,'PowerUpType')+slot]=item;m[address(new,'Enemy_State')+slot]=128 if mature else 1
        before=bytes(m.ram[2][:1024]);r=V.target(m,q['labels']['BbNativePickup'],a=83,x=slot,y=199,p=0x71)
        expected=flags
        if item<2 and mature:expected=donor_item(rom,identity,4 if item==0 else 2,flags)
        assert m.ram[2][actor+2]==expected,(identity,item,slot,flags,mature,expected)
        assert r['A']==83 and r['X']==slot and r['Y']==199
        # The synchronous bank gateway loads original A immediately before
        # entry, setting NZ from83; private leaf otherwise preserves P/C policy.
        ep=((0x71|0x30)&~0x82)|(83&128)
        assert r['P']==(ep|1 if item<2 and not mature else ep&~1),(identity,item,mature,r,ep)
        after=bytearray(m.ram[2][:1024]);after[actor+2]=before[actor+2];assert bytes(after)==before
        if item>=2:native+=1
        elif not mature:immature+=1
        count+=1
    # Actual authenticated resident row14 forwards the same regular pickup.
    resident=[]
    for identity,item in itertools.product([0,1],[0,1]):
        m=N.fork(seeds[identity]);actor=0x42 if identity else 0x2e
        m[address(new,'PowerUpType')]=item;m[address(new,'Enemy_State')]=128
        m.ram[2][actor+2]=0;r=V.target(m,0xb08c+14*3,bank=193,a=83,x=0,y=199,p=0x71)
        assert m.ram[2][actor+2]==(1 if item==0 else 6)and not r['P']&1
        resident.append(dict(identity=identity,item=item,flags=m.ram[2][actor+2],actual_resident_row14=True))
    result=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,parent_ROM_SHA256=U.PIN,successor_memory_SHA256=q['expected_memory_only_ROM_SHA256'],whole_Main_cases=motion,whole_Main_pairs=len(cycles),old_Main_cycles=[min(a for a,b in cycles),max(a for a,b in cycles)],new_Main_cycles=[min(b for a,b in cycles),max(b for a,b in cycles)],cycle_saving=[min(a-b for a,b in cycles),max(a-b for a,b in cycles)],pickup_cases=count,immature_regular_claims=immature,native_star_1up_forwards=native,actual_resident_pickups=resident,scope='Whole actual GameCore1000paired idle/walk/jump calls retain native coordinates, complete1KBprivate state, scratch/maps/AXYP; branch relaxation may change CPU time only. 8192 pickup combinations compare actual original bank6 dispatcher9A3A/common9C9D flags for mushroom->item4 andflower->item2; original clears native donor pickup. New leaf preserves AXYP, rejects immature regulars and forwards star/1up. Real authenticated resident row14 reached. Complete PowerUpObjHandler, earned block emergence/collection, native SFX/power bookkeeping, life/stage/IRQ/lagNMI/fullstage/render closure remain required.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),U.O/'proposal.json',U.O/'private-image.bin',S]if False})
    result['bindings']={str(p.relative_to(R)):sha(p)for p in[Path(__file__),Path(U.__file__),U.O/'proposal.json',U.O/'private-image.bin',U.O/'labels.json']}
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
