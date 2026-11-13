"""Isolated Ryu28 equivalence and direct-foreign source fitting, no lease."""
import argparse
from hashlib import sha256
from itertools import product
import json

import check_dkjr_ryu_bridge_funding_1113 as F
import compose_dkjr_descending_platform_1113 as T

Q,P,H,N,W,L=F.Q,F.P,F.H,F.N,F.W,F.L
SOURCE=P.B.R/'tools/reference/dkjr_direct_foreign_proposal_1113.s'
LAYOUT=dict(RYU=(0xb963,28),NATIVE=(0xb97f,59),POLICY=(0xb707,11),
    WORKER_A=(0xbd5b,26),WORKER_B=(0xbdd5,26))


def requested_resources(parent):
    """Exact review payload only; do not apply or enable the proposed packing."""
    current,_=T.transform(parent);linked=H.T.assemble(SOURCE.read_text(),LAYOUT)
    atomic=(linked['images']['RYU']+linked['images']['NATIVE'].ljust(59,b'\xea'))
    rows=[]
    for bank,pc,size,after in((0,0xb963,87,atomic),(0,0xb43f,3,bytes.fromhex('207fb9')),
            (0,0xb707,11,linked['images']['POLICY'].ljust(11,b'\xea')),
            (58,0xbd5b,26,linked['images']['WORKER_A']),
            (58,0xbdd5,26,linked['images']['WORKER_B'].ljust(26,b'\xea'))):
        at=16+bank*8192+(pc&8191);before=current[at:at+size]
        assert len(after)==len(before)==size
        rows.append(dict(physical_PRG=bank,CPU_start=pc,bytes=size,file_offset=at,
            original_e73_preimage_hex=parent[at:at+size].hex(),
            current_14ae_preimage_hex=before.hex(),current_14ae_preimage_SHA256=sha256(before).hexdigest(),
            proposed_hex=after.hex(),proposed_SHA256=sha256(after).hexdigest()))
    return dict(current14_SHA256=T.PIN,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        requested_resources=rows,used=linked['used'],new_RAM_bytes=0,new_CHR_bytes=0,
        new_native_bytes=0,proposed_dispatch_entry=0xb97f,
        packing_enabled=False,grant=False)


def parts(parent):
    _,old=F.parts(parent)
    linked=H.T.assemble(SOURCE.read_text(),LAYOUT)
    assert linked['used']==dict(RYU=28,NATIVE=58,POLICY=9,WORKER_A=26,WORKER_B=25)
    out=bytearray(parent);at=16+0x1963
    out[at:at+43]=linked['images']['RYU'].ljust(43,b'\xea')
    return bytes(out),dict(old_Ryu43_hex=old['old_hex'],
        new_Ryu28_hex=linked['images']['RYU'].hex(),used=linked['used'],
        proposed_dispatch_entry=0xb97f,atomic_native_bytes=87,additional_native_bytes=0,
        additional_RAM_bytes=0,ROM_written=False,lease_granted=False,
        scope='Only the isolated Ryu bridge is executed. Full direct-fast packing is assembled, not installed or enabled.')


def callbacks(seed,parent,fixture):
    count=allow=0;smc=set()
    for scene,profile,kind in product(('ordinary','authored_underside','outside'),(25,27),(37,40)):
        base=L.clone(seed);slot=3
        N.put(base,SelectedCharacter=10,Player_X_Position=113,Player_PageLoc=0,Player_Y_Position=160,
            Player_Y_HighPos=1,Player_State=1,Player_Y_Speed=252,
            WorldNumber=0,LevelNumber=3 if scene!='ordinary'else 0,AreaType=3,
            SecondaryHardMode=0,GuestHurtTicks=0,RgCrouch=0,RgAttack=0,XgWall=0,RyPlatformSlot=0,
            RyWallSupported=1,RyWallOldHeight=25,RyWallWasGround=1,RyWallOldX=113,
            RyWallOldPage=0,RyWallOldY=192,RyuSourceBodyProfile=profile,
            ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ObjectOffset=slot)
        for field,value in dict(Enemy_ID=kind,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
            Enemy_X_Position=111 if scene!='outside'else 200,Enemy_PageLoc=0,
            Enemy_Y_Position=184,Enemy_Y_HighPos=1).items():base[W.address(base.bundle,field)+slot]=value
        N.invoke(base,'RelativePlayerPosition',x=0);N.invoke(base,'HuFullBox',x=0)
        N.invoke(base,'GetEnemyOffscreenBits',x=slot);N.invoke(base,'RelativeEnemyPosition',x=slot)
        N.invoke(base,'LargePlatformBoundBox',x=slot)
        for saved_a,p in product((0,1,40,255),range(256)):
            results=[];models=[];seen=[]
            for raw in(parent,fixture):
                q=Q.mounted(base,raw);q[3]=184;q[0x16a]=saved_a;calls=[]
                def watch(cpu):
                    tag=cpu.memory.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                    if(tag,cpu.pc)in((150,0xb854),(128,0xb979),(254,0x9a2c)):
                        calls.append((tag,cpu.pc,cpu.p&1))
                r=Q.direct(q,0xb963,a=85,x=slot,y=4*(slot+1),p=p,observe=watch)
                assert r['P']&12==p&12
                results.append((bytes(q[:0x100]),bytes(q[0x200:0x800]),tuple(bytes(a)for a in q.ram),
                    tuple(q.rawtags),r['X'],r['Y'],r['SP']))
                models.append(q);seen.append(calls)
            assert results[0]==results[1],(scene,profile,kind,saved_a,p)
            if kind==37:
                assert sum(t==150 and pc==0xb854 for t,pc,_ in seen[1])==1
                assert(128,0xb979,1)in seen[1]and any(t==254 and pc==0x9a2c for t,pc,_ in seen[1]),seen[1]
                allow+=1
            smc.update(at for at in range(0x15a,0x17b)if models[0][at]!=models[1][at])
            count+=1
    assert all(m[0x178]==0xa9 and m[0x17a]==0x60 for m in models),'Actual FarCallCommon return-A immediate'
    assert smc<={0x162,0x16a,0x16c,0x16d,0x179},smc
    return dict(cases=count,wrong_ID37_source_worker_ALLOW_C1_then_native=allow,
        all256_incoming_P_and_four_prior_SavedA_values=True,I_D_XYSP_and_all_game_WRAM_maps_equal=True,
        intermediate_SMC_differences=sorted(hex(at)for at in smc),
        intermediate_A_NZCV_and_SMC_caller_liveness_pending=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--callbacks',action='store_true')
    ap.add_argument('--mains',action='store_true');a=ap.parse_args()
    parent,_=T.load_inputs(reuse_private=True);fixture,info=parts(parent)
    print('DKJR_DIRECT_FOREIGN_FIT '+json.dumps(info,separators=(',',':')),flush=True)
    print('DKJR_DIRECT_FOREIGN_REQUEST '+json.dumps(requested_resources(parent),separators=(',',':')),flush=True)
    if a.callbacks:
        b=W.Symbols.bundle();b['raw']=parent
        _,seed=Q.Roster.cold(b,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
        print('DKJR_RYU28_CALLBACKS '+json.dumps(callbacks(seed,parent,fixture),separators=(',',':')),flush=True)
    if a.mains:F.mains(parent,fixture)
    print('DKJR_DIRECT_FOREIGN_SCOPE '+json.dumps(dict(parent_SHA256=sha256(parent).hexdigest(),
        isolated_Ryu28_fixture_SHA256=sha256(fixture).hexdigest(),outputs_written=0,
        full_fast_dispatch_candidate=False,grant=False,native_ready=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
