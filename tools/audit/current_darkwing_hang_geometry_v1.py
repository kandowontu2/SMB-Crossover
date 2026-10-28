"""Additional actual full-caller geometry/foreign controls for the narrow hang fix."""
from pathlib import Path
import hashlib,json
from current_darkwing_hang_floor_cpu_v1 import OLD,NEW,BUILD,ROOT,setup,invoke,world,sha
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location

def call_pair(old,new,kind,face,geometry):
    qa,qb=setup(old,kind,face),setup(new,kind,face)
    for q in [qa,qb]:
        # A complete typed logical scene; zero cells except declared source
        # floor/ceiling/side. No outcome/resource updates after this setup.
        q.array('Block_Buffer_1',[0]*416)
        px=world(q);py=q.get('Player_Y_Position')
        def cell(x,y):q.set('Block_Buffer_1',84,x//256%2*208+(y-32)//16*16+x%256//16)
        if geometry=='floor':
            for x in range(px-16,px+48,16):cell(x,py+32)
        elif geometry=='ceiling':
            for x in range(px-16,px+48,16):cell(x,py-8)
        elif geometry in ['left','right']:
            for y in range(max(32,py-16),min(232,py+48),16):cell(px-8 if geometry=='left'else px+16,y)
        elif geometry=='carry':
            # Real unblocked descending vertical-platform motion. State0
            # permits native carry; falling-state80 is tested separately.
            q.set('PlatformCollisionFlag',0,4)
    ca,ta,_=invoke(qa,'GameLoop');cb,tb,_=invoke(qb,'GameLoop')
    assert(ca.a,ca.x,ca.y,ca.p,ca.sp,qa.m.banks)==(cb.a,cb.x,cb.y,cb.p,cb.sp,qb.m.banks)
    delta=[i for i in range(32768)if qa.m[i]!=qb.m[i]]
    assert all(0x1c0<=i<512 for i in delta),(kind,face,geometry,[(hex(i),qa.m[i],qb.m[i])for i in delta])
    assert[(a,v)for a,v in qa.m.writes if not 0x180<=a<512]==[(a,v)for a,v in qb.m.writes if not 0x180<=a<512]
    return dict(kind=kind,face=face,geometry=geometry,AXYP_SP_RAM_ordered_writes_exact=True,ending=[world(qb),qb.get('Player_Y_Position'),qb.get('DwHang')],delta=cb.processorCycles-ca.processorCycles,dead_return_stack_differences=delta)

def foreign(b,char):
    q=Arena(b,char);q.put(PlayerStatus=0,OperMode_Task=3,AreaType=1,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScrollLock=1,CrossoverBehaviorVersion=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in [0,1]:
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,page*208+row*16+col)
    end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0,SavedJoypadBits=0)
    c,trace,_=invoke(q,'GameLoop')
    assert not any(k==67 and address(b,'DwHangUpdate')<=p<address(b,'DwHangUpdate')+259 for p,k in trace)
    return q,c

def main():
    old,new=scoped_load(OLD),scoped_load(NEW)
    rows=[call_pair(old,new,k,f,g)for k in ['stable','falling-free','stable-jump-through']for f in [1,2]for g in ['empty','floor','ceiling','left','right','carry']]
    others=[]
    for char in [0,1,2,5,7,9,11,13,18,19]:
        qa,ca=foreign(old,char);qb,cb=foreign(new,char)
        assert(ca.a,ca.x,ca.y,ca.p,ca.sp,ca.processorCycles,qa.m.banks)==(cb.a,cb.x,cb.y,cb.p,cb.sp,cb.processorCycles,qb.m.banks)
        assert qa.m[:32768]==qb.m[:32768]and qa.m.writes==qb.m.writes
        others.append(dict(character=char,full_GameLoop_return_RAM_cycles_ordered_writes_exact=True,hang_path_not_entered=True))
    z=dict(passed=True,source_only=True,native_run=False,parent_sha256=sha(OLD),candidate_sha256=sha(NEW),geometry_cases=rows,foreign_GameLoops=others,
        scope='36actual complete Main geometry comparisons plus10 initialized foreign Main controls. Source logical scenes, not native/instruction-all-state/campaign/PPU proofs. Both stablejump-through80 and unblocked falling carry retain original complete outputs; only falling disabledterrain hang is intentionally released.',
        bindings={str(p):sha(p)for p in [Path(__file__).resolve(),ROOT/'tools/audit/current_darkwing_hang_floor_cpu_v1.py',BUILD/'darkwing_hang_floor_controls.json',OLD,NEW]})
    out=BUILD/'darkwing_hang_geometry_controls.json';assert not out.exists();out.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,geometry=len(rows),foreign=len(others),path=str(out),sha256=sha(out))))

if __name__=='__main__':main()
