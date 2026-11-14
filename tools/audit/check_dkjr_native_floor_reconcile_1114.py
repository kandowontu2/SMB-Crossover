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
    print('DKJR_NATIVE_FLOOR_RECONCILE '+json.dumps(dict(passed=True,
        ROM_SHA256=Current.PIN,existing_private_SHA256=S.PIN,
        native_receipt='165ce7e64c854ef8584b13b923d76f261a560dfe4ea378b74621b178ab4bdc55',
        post_BG_current_trace=trace,post_BG_named_hits=dict(hits),post_BG_result=post_result,
        post_BG_source_state_unchanged=post_source_unchanged,
        offbottom_entry_PC=labels['D_d640'],offbottom_state_store_PC=labels['D_d64d'],
        offbottom_declared_source216_kills=True,controls=controls,
        existing_post_validation_landing_controls=landing_controls,
        outputs_written=0,ROM_written=False,gameplay_change=False,native_claim=False,
        scope='Exact current source CPU postBG path plus declared native-ground split controls. Existing camera shift then anchor import reconciles position while preserving original fall state/origin/limit/velocity; not an allocated repair or route qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
