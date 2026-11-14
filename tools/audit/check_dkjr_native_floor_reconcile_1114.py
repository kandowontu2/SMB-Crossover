"""Current post-BG source trace and declared anchor-reconciliation controls.

This is not a gameplay repair or a native replay. It calls existing bytes in
CPU memory and keeps the original fall origin, threshold and state unchanged.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_oneway_current_1114 as Current
import check_dkjr_platform_query_lifecycle_1114 as Life
import compose_smb2_postbg_mirror_1113 as Post

S=Current.S;F=S.Replay;G=F.Gate
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def state(m):
    r=m.ram[2]
    return dict(native_x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        native_y=N.get(m,'Player_Y_Position'),native_state=N.get(m,'Player_State'),
        native_vy=N.get(m,'Player_Y_Speed'),source=r[0x6b],prior=r[0x6c],
        source_x=r[0x213],source_y=r[0x210],origin=r[0x76],limit=r[0x7b],
        saved_camera=r[0x435]+256*r[0x436],world_ready=r[0x437])


def main():
    parent=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw,private,_=Current.source_projection(parent,kind='hidden-421')
    _,old=F.load_inputs();_,labels=Life.closure(old)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    seed=Q.mounted(seed,raw)
    for bank in (119,120,125,127):
        at=16+bank*8192+(Post.BRIDGE&8191)
        assert raw[at:at+49]==Post.CANONICAL
    native_names=('RyuSourceBodyAfterBGBridge','ThPostNativeHot','HuAfterTerrainGate',
        'HuQuickAfterProbe','HuQuickAfterOriginal','HuLegacyPostBG')
    points={}
    for name in native_names:
        pc=W.address(seed.bundle,name);tag=((W.location(seed.bundle,name)-16)//8192)|128
        points[(tag,pc)]=name
    assert points[(194,0xb438)]=='ThPostNativeHot'
    for name in ('DkjrNativeImportAnchor','DkjrNativePublishAnchor','DkjrNativeShiftCamera',
                 'DkjrNativeCameraSync','DkNativeAnchorReady'):
        assert name in labels,name
        points[(2 if labels[name]>=0xc000 else 3,labels[name])]=name

    # Declared component values from the separate native46 receipt. Body
    # cells are still the real cold constructor; only actor0 is positioned.
    def fixture(source_y=216,source_x=255,camera=2561,saved_camera=2561):
        m=L.clone(seed)
        N.put(m,Player_X_Position=2569&255,Player_PageLoc=2569>>8,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,
            Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,
            Player_Y_Speed=0,GameEngineSubroutine=8)
        r=m.ram[2];r[0x6b]=r[0x6c]=4;r[0x210]=source_y;r[0x213]=source_x
        r[0x76]=194;r[0x7b]=24;r[0x8fe]=2
        r[0x435:0x438]=bytes((saved_camera&255,saved_camera>>8,0xd7))
        return m

    m=fixture();before=state(m);source_before=bytes(m.ram[2][:0x800])
    trace=[];hits=Counter();base=N.NesMPU
    class Probe(base):
        def step(self):
            memory=self.memory
            if self.pc>=0x8000:
                tag=memory.rawtags[(self.pc-0x8000)//8192]
                name=points.get((tag,self.pc))
                if name:
                    hits[name]+=1
                    trace.append(dict(name=name,raw_bank=tag,PC=self.pc,
                        bytes=bytes(memory[self.pc:self.pc+12]).hex()))
            return base.step(self)
    with patch.object(N,'NesMPU',Probe):
        post_result=N.invoke(m,'RyuSourceBodyAfterBGBridge',a=83,x=71,y=91,p=0x61)
    assert state(m)==before,(before,state(m))
    assert bytes(m.ram[2][:0x800])==source_before
    post_source_unchanged=True
    assert hits['ThPostNativeHot']==hits['HuAfterTerrainGate']==1,hits
    assert not any(hits[n]for n in ('DkjrNativeImportAnchor','DkjrNativePublishAnchor',
        'DkjrNativeShiftCamera','DkjrNativeCameraSync','DkNativeAnchorReady'))

    controls=[]
    for source_y,source_x,camera_delta in ((194,255,0),(216,255,0),(194,16,1),(194,16,8),(194,16,-8)):
        m=fixture(source_y,source_x,2561,2561-camera_delta);prior=state(m)
        preserved=bytes(m.ram[2][0x6b:0x88]);other_before=bytes(m.ram[2][0x200:0x300])
        shift=H.call(m,labels['DkjrNativeShiftCamera'],p=0x61)
        assert shift.p&1
        imported=H.call(m,labels['DkjrNativeImportAnchor'],p=0x61)
        assert imported.p&1
        after=state(m)
        assert after['source_x']==0 and after['source_y']==191,after
        assert after['saved_camera']==2561 and after['world_ready']==0xd7
        assert bytes(m.ram[2][0x6b:0x88])==preserved
        assert bytes(m.ram[2][0x200:0x210])!=other_before[:16] or camera_delta==0
        next_shift=H.call(m,labels['DkjrNativeShiftCamera'],p=0x61)
        assert next_shift.p&1 and state(m)==after,'Repeated camera transport changed anchor'
        # Original landing/fall primitive remains in force. Reconciliation
        # changes neither its threshold nor its retained origin194.
        injury=H.call(m,labels['D_da34'],p=0x61)
        assert injury.a==0
        controls.append(dict(before=prior,after=after,fall_reject=injury.a,
            source_state_origin_limit_and_velocity_preserved=True))
    original=fixture();offbottom=H.call(original,labels['D_d640'],p=0x61)
    assert original.ram[2][0x6b]==5

    # Reuse the existing *post-validation* landing continuation as a source
    # diagnostic, without fabricating an enemy/passenger. It compares the
    # pre-snap original Y before ImportAnchor and executes original Land only
    # when safe. Native-ground validation and an allocation are still absent.
    # Import alone is not a complete landing repair: it leaves source4.
    landing_controls=[]
    for source_y,origin,limit in ((194,178,24),(216,194,24),(194,170,24),
                                (194,171,24),(191,63,22),(194,63,22)):
        m=fixture(source_y=source_y);r=m.ram[2];r[0x76]=origin;r[0x7b]=limit
        expected=int(source_y>=origin and source_y-origin>=limit)
        verdict=H.call(m,labels['DkjrFallDistance'],p=0x61).a
        assert verdict==expected
        original_body=bytes(r[0x210:0x230])
        r[labels['CarryPhase']-0xc000]=4;r[labels['CarryTop']-0xc000]=208
        result=H.call(m,labels['CarryAccepted'],p=0x61)
        assert result.p&1
        assert r[0x6b]==(5 if expected else 1)
        assert r[0x76]==origin,'Original fall origin changed'
        if expected:
            assert bytes(r[0x210:0x230])==original_body,'Injury snapped the body'
            assert r[0x7b]==limit
        else:
            assert r[0x213]==0 and r[0x210]==191
        landing_controls.append(dict(original_source_y=source_y,origin=origin,limit=limit,
            original_pre_snap_reject=verdict,after=state(m),original_injury_body_unsnapped=bool(expected)))

    floor_controls=[]
    for floor,disabled,incoming in ((True,0,2),(False,0,2),(True,1,2),
                                    (True,0,0),(False,0,0),(True,1,0)):
        m=fixture(source_y=194);N.put(m,Player_Y_Position=179,Player_State=2,
            DisableCollisionDet=disabled,SwimmingFlag=0,JumpspringAnimCtrl=0,
            PlayerSize=0,CrouchingFlag=0,AreaType=1)
        N.put(m,Player_State=incoming)
        for name in ('Block_Buffer_1','Block_Buffer_2'):
            at=W.address(m.bundle,name);m[at:at+208]=bytes(208)
            if floor:m[at+176:at+208]=bytes((0x54,))*32
        N.invoke(m,'RelativePlayerPosition',x=0);N.invoke(m,'HuFullBox',x=0)
        prior=state(m);box=list(m[0x658:0x65c]);floor_writes=[]
        class FloorProbe(base):
            def step(self):
                memory=self.memory
                if bytes(memory[self.pc:self.pc+2])==bytes((0x85,0x1e)):
                    tag=memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
                    floor_writes.append(dict(raw_bank=tag,PC=self.pc,pending_A=self.a,
                        native_y=N.get(memory,'Player_Y_Position')))
                return base.step(self)
        with patch.object(N,'NesMPU',FloorProbe):N.invoke(m,'PlayerBGCollision',x=0)
        after=state(m)
        assert after['source_y']==194 and after['source']==4
        if floor and not disabled:
            assert after['native_y']==176 and after['native_state']==0,(prior,after,box)
            assert any(row['pending_A']==0 for row in floor_writes)
        else:assert after['native_state']==(incoming if disabled else 2)and after['native_y']==179
        floor_controls.append(dict(static_floor_present=floor,collision_disabled=disabled,
            before=prior,body_box=box,actual_native_state_writes=floor_writes,after=after))

    asymmetric=[]
    for near_floor in (True,False):
        m=fixture(source_y=194)
        for index,name in enumerate(('Block_Buffer_1','Block_Buffer_2')):
            at=W.address(m.bundle,name);m[at:at+208]=bytes(208)
            if (index==0)==near_floor:m[at+176:at+208]=bytes((0x54,))*32
        m.ram[2][0x3e:0x42]=bytes((255,194,16,209));m.ram[2][0x8db]=3
        cells=[]
        def cell_watch(memory,cpu):
            if cpu.pc==0xb3b7 and memory.rawtags[1]==3:
                r=memory.ram[2];cells.append((r[0x8de]+256*r[0x8df],r[0x8e2]))
                assert len(cells)<=3
        H.call(m,labels['DkjrNativeWorldBuild'],observe=cell_watch)
        assert cells==[(2560,208),(2576,208)],cells
        assert bool(m.ram[2][0x8dd])==near_floor
        asymmetric.append(dict(near_page10_floor=near_floor,far_page11_floor=not near_floor,
            modular_query=[255,194,16,209],actual_world_cells=cells,
            static_support_rects=list(m.ram[2][0x800:0x800+m.ram[2][0x8dd]])))

    # Observe the existing after-effects callback in one complete scheduled
    # native Main. No callback is redirected or given a new implementation.
    m=fixture(source_y=194);N.put(m,Player_Y_Position=179,Player_State=2,
        DisableCollisionDet=0,SwimmingFlag=0,JumpspringAnimCtrl=0,
        PlayerSize=0,CrouchingFlag=0,AreaType=1,TimerControl=0,FamilyMainCommit=1)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        at=W.address(m.bundle,name);m[at:at+208]=bytes(208)
        m[at+176:at+208]=bytes((0x54,))*32
    order_points={}
    for name in ('GameCoreRoutine','HuMovement','PlayerBGCollision','HuAfterEffects'):
        order_points[(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name))]=name
    order_points[(2,0xd65e)]='DK_Main'
    order_points[(193,0xb08c+34*3)]='DK_public_row34'
    order_points[(254,40044)]='native_BG_ground_state_store'
    callback_order=[]
    def observe(memory,cpu):
        if cpu.pc<0x8000:return
        tag=memory.rawtags[(cpu.pc-0x8000)//8192]
        name=order_points.get((tag,cpu.pc))
        if (tag,cpu.pc)==(193,0xaee2):
            target=memory[0x16c]+256*memory[0x16d]
            if target==0xb08c+34*3:name='DK_row34_auth'
        if name:callback_order.append(dict(name=name,raw_bank=tag,PC=cpu.pc,
            pending_A=cpu.a,state=state(memory)))
    Q.frame(m,0,observe=observe)
    assert len(callback_order)<=32
    assert any(row['name']=='DK_row34_auth'for row in callback_order),callback_order
    print('DKJR_NATIVE_FLOOR_RECONCILE '+json.dumps(dict(passed=True,
        ROM_SHA256=Current.PIN,existing_private_SHA256=S.PIN,
        native_receipt='165ce7e64c854ef8584b13b923d76f261a560dfe4ea378b74621b178ab4bdc55',
        post_BG_current_trace=trace,post_BG_named_hits=dict(hits),post_BG_result=post_result,
        post_BG_source_state_unchanged=post_source_unchanged,
        offbottom_entry_PC=labels['D_d640'],offbottom_state_store_PC=labels['D_d64d'],
        offbottom_declared_source216_kills=True,controls=controls,
        existing_post_validation_landing_controls=landing_controls,
        real_native_BG_declared_floor_controls=floor_controls,
        asymmetric_modular_X_current_regressions=asymmetric,
        complete_scheduled_Main_callback_order=callback_order,
        outputs_written=0,ROM_written=False,gameplay_change=False,native_claim=False,
        scope='Exact current source CPU postBG path plus declared native-ground split controls. Existing camera shift then anchor import reconciles position while preserving original fall state/origin/limit/velocity; not an allocated repair or route qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
