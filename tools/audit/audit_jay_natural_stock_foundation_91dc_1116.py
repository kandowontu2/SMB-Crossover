"""Strict current Jay F/S/L foundation; no pickup/actor seeds or replay."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import argparse,json
import contra_force_checked_resolver_model_1116 as Metadata

R=Path(__file__).resolve().parents[2]
PIN='91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
H=lambda data:sha256(data).hexdigest()
N,W,Frames=Metadata.N,Metadata.W,Metadata.Frames
PAGES=(218,222,232,234,331,332)
CHR=1048592


def prg(bank,pc):return 16+bank*8192+(pc&8191)


def fields(m):
    row={n:N.get(m,n)for n in('SelectedCharacter','PlayerStatus','NumberofLives','JnHealth','JnMaxHearts',
        'JnOwnedTier','JnSelected','JnStars','StarInvincibleTimer','GuestPowerupActive','GameEngineSubroutine')}
    row.update(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        donor_flags=m.ram[2][0x12],donor_control=m.ram[2][0x13],donor_weapon=m.ram[2][0x20],donor_ammo=m.ram[2][0xbe])
    return row


def run(raw,actual_cold=False):
    assert isinstance(raw,bytes)and H(raw)==PIN,'Exact current91dc input only'
    # This frozen facade supplies authenticated current symbol metadata.
    # Its typed6a3 inverse is bindings-only; every CPU byte below is raw91dc.
    b=Metadata.symbols(raw);assert b['raw']is raw
    cookie=raw[prg(94,0xb2ef):prg(94,0xb2ef)+16]
    assert cookie[:4]==bytes.fromhex('aa10200c'),('Current shared Mike/Jay/Steve cookie',cookie.hex())
    cold_at=prg(65,0xa696);cold=raw[cold_at:cold_at+162]
    assert cold.count(cookie)==1
    cookie_at=cold_at+cold.index(cookie)
    assert cookie_at==prg(65,0xa728),'Exact current packet cookie location'
    hooks=[]
    for name in('IdleLoop','GameLoop','SetupPowerUp','PlayerHeadCollision','HandlePowerUpCollision',
        'JnPreparePickup','JnCollectPickup','JnRisePickup','JnPickupCollision','GuestPowerupUpdate',
        'MarioSourcePowerupCollision','JnHeadDispatch','JnMovement'):
        at=W.location(b,name);pc=W.address(b,name)
        assert 16<=at<CHR
        hooks.append(dict(name=name,PC=pc,physical_PRG=(at-16)//8192,file=at,
            first16_hex=raw[at:at+16].hex(),first16_SHA256=H(raw[at:at+16])))
    source_files=('tools/audit/replay_jay_powerups_1113.py','tools/audit/replay_jay_pickup_helper_1113.py',
        'tools/audit/replay_jay_stage_current_1113.py','tools/reference/jay_pickup_helper_1113.s',
        'src/mike_jones_pickups.s','src/mike_jones_state.inc')
    q=dict(actual_parent_SHA256=PIN,metadata_facade_SHA256=H(Path(Metadata.__file__).read_bytes()),
        identity=dict(name='JAY MCCRAY',slot=15,raw=16,Select_cycles=1,alternate_mask=96,alternate_value=32),
        shared_cookie_hex=cookie.hex(),cookie_files=[cookie_at,prg(94,0xb2ef)],
        retained_observer_negative='Source23776 rejected the historical A727 cookie address before any new cold CPU. Actual current packet cookie is A728, independently located inside exact162B cold code.',
        cold65_162_SHA256=H(cold),
        Jay_carriers=[dict(page=p,SHA256=H(raw[CHR+p*1024:CHR+(p+1)*1024]))for p in PAGES],
        hook_bindings=hooks,source_inventory={p:H((R/p).read_bytes())for p in source_files},
        existing_helpers=[dict(stage='1-1',left=x,center=x+16,initial_top=192,width=32)for x in(384,688,880)],
        historical_closed=dict(ROM='aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1',
            first_health_receipt='abe9281690573229b2b45fec8ca414c7fbbc9f823ce1b545b86344e23f73b0ca',
            stage_machinegun_receipt='4e1140c6872cc1e91b7cbb0055a4938d614f51ed1ebc8d4f2d4fb3d2a089b9da',
            not_replayed=True),
        missing_natural=['Flower','Star','1UP'],controller_inventory_scope='Old frozen factories are pinned historical-only; no old inverse/factory/assembler is called.',
        no_items_actors_terrain_health_position_abilities_or_game_bytes_seeded=True,
        root_native_controller_authorization_or_cadence_claim=False,outputs=0)
    if actual_cold:
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        W.UI.key(m,4)
        for _ in range(7):W.UI.key(m,1)
        assert N.get(m,'CrossoverMenuIndex')==15
        W.UI.key(m,32)
        assert W.UI.menu_name(m)[0]=='JAY MCCRAY'
        assert N.get(m,'SelectedCharacter')==16 and m[0x730b]&96==32
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for epoch in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Frames.frame(m,cold=True,whole_pass=True)
        else:raise AssertionError('Current Jay ordinary cold bound')
        assert m.bundle['raw']is raw
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(cookie,cookie)
        activation=fields(m);initialization=[]
        # Engine8 is published before the first donor movement runs. The
        # historical60-update opener hid that distinction; do not seed ammo.
        for _ in range(4):
            if m.ram[2][0x20]==0 and m.ram[2][0xbe]==63:break
            m.controller_pad=0;Frames.frame(m,whole_pass=True);initialization.append(fields(m))
        assert m.ram[2][0x20]==0 and m.ram[2][0xbe]==63,(activation,initialization)
        assert tuple(N.get(m,n)for n in('JnHealth','JnMaxHearts','JnOwnedTier','NumberofLives'))==(6,3,1,2)
        assert N.get(m,'PlayerStatus')==N.get(m,'StarInvincibleTimer')==N.get(m,'GuestPowerupActive')==0
        helper=raw[CHR+234*1024+0x120:CHR+234*1024+0x217]
        assert bytes(m.ram[3][0x1d20:0x1e17])==helper and len(helper)==247
        tables=bytes.fromhex('b07080020301a9a1a9010204')
        assert helper.endswith(tables),'Current three physical helper records'
        assert bytes(m.ram[3][0x48c:0x48f])==bytes.fromhex('4c3da8'),'Current native-head bridge'
        q['ordinary_cold']=dict(epochs=epoch,activation_state=activation,initialization_neutral_updates=initialization,
            retained_observer_negative_57938='Historical ammo63 assertion was made at engine8 before the first donor update; corrected observer waits at most4 real neutral Main updates and never supplies ammo.',
            state=fields(m),PPU_reads=m.ppu_reads,
            headers_RAM2_RAM3_exact=True,helper247_SHA256=H(helper),helper_readback_exact=True,
            original_three_records_exact=True,head_bridge_6_hex=bytes(m.ram[3][0x48c:0x492]).hex(),
            runtime_segments_SHA256={name:H(bytes(m.ram[k][lo:hi]))for name,k,lo,hi in(
                ('Jay_primary',3,0,0x8c0),('shotgun_support',3,0x1400,0x1800),('motion',3,0x1800,0x1c00),('extra_before_header',3,0x1c00,0x1fe0))})
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cold',action='store_true');a=p.parse_args()
    raw=ROM.read_bytes();assert H(raw)==PIN
    def deny(*a,**kw):raise AssertionError('Jay foundation attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.cold)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
