"""Detached two-byte Rogue missile target proposal; no CPU or code overlay."""
from hashlib import sha256
from pathlib import Path
import json,struct
import check_ff_white_mushroom_current_1110 as W

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
DONOR=Path('C:/NES/the stash/Metroid - Rogue Dawn 1.21 (header fixed).nes')
PARENT='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
DONOR_SHA='9271411a20cc26c09f4d4bffe74c0d69a1bf91b815f7716fcf4610c4cee61077'
SOURCE_SHA='075fa975f98aba6578daecd6998ee3391cd409f7ad8441eea01e3dbda6e82bee'
AT=995207;OLD=bytes.fromhex('afaf');NEW=bytes.fromhex('e2af')
def H(b):return sha256(b).hexdigest()


def descriptor(raw):
    assert isinstance(raw,bytes)and len(raw)==2097168 and H(raw)==PARENT
    source=(R/'src/rogue_dawn_host_weapons.s').read_bytes();assert H(source)==SOURCE_SHA
    assert source.count(b'cmp #11\n jeq Projectile')==1 or source.count(b'cmp #11\r\n jeq Projectile')==1
    assert raw[AT-1:AT+2]==bytes.fromhex('4cafaf')
    assert raw[995184:995216]==bytes.fromhex('ae2f5cbd705bd0034c0ab1c908b0034cafafc90bd0034cafafc90a90034c80af')
    assert raw[995263:995314]==bytes.fromhex('c904d0034ca5b0c901d0034ce2afc902d0034c19b0c903f0034c0ab18d6a01a9008d6c01a9b78d6d01a9fc205a01f0034c19b0')
    assert raw[995314:995322]==bytes.fromhex('a9018d3d5c20cfae')
    donor=DONOR.read_bytes();assert H(donor)==DONOR_SHA
    d=16+62*8192+(0xd4d3&8191);table=struct.unpack('<12H',donor[d:d+24])
    assert table==(0xc45c,0xd4eb,0xd52c,0xd5c1,0xd5c8,0xd65e,0xd670,0xd691,0xd65e,0xd670,0xd691,0xd4eb)
    def dispatch(action,new):
        if action==0:return 'Empty'
        if action>=8 and action!=11:return 'Bomb'
        if action==11 and new:return 'Normal'
        return {1:'Normal',2:'Wave',3:'Ice',4:'Impact'}.get(action,'Empty')
    differences=[a for a in range(256)if dispatch(a,False)!=dispatch(a,True)];assert differences==[11]
    # Read retained linker symbols only. No metadata UI CPU and no proposed CPU.
    b=W.Symbols.bundle();rows={}
    names=('WxEnabled','RdHostEnabled','RdWxPreStep','RdWxRemainingGate','RdWxUpdateSlot','RdWxRememberColor',
        'RdWxViewport','RdCheckProjectileOnScreen','RdProjectileImpact','RdWxCell','RdWxMove',
        'RdProjectileTerrainImpact','RdAnimateProjectile','RdFinishProjectileRender','RdClearProjectileColor',
        'WeaponAnimationHigh','RdRenderWeapon','RdWeaponIndex0','RdWeaponRadiusY','RdWeaponRadiusX')
    for name in names:
        pc,at=W.address(b,name),W.location(b,name)
        rows[name]=dict(PC=pc,file=at,physical_bank=(at-16)//8192,first32=raw[at:at+32].hex())
    assert(rows['RdWxUpdateSlot']['file'],rows['RdWxUpdateSlot']['PC'])==(995184,0xaf60)
    assert rows['RdWxRememberColor']['file']-995184==427
    ps,pe=rows['RdWxPreStep']['file'],rows['RdWxRemainingGate']['file']
    assert raw[ps:ps+22]==bytes.fromhex('2060adb0034c38aead77072901f0034c38aea50fc908')
    calls=[ps+i for i in range(pe-ps-2)if raw[ps+i:ps+i+3]==bytes.fromhex('2060af')];assert len(calls)==1
    animations=bytes.fromhex('4bff4e4fff3c4a494a4d4a4df7ff26ff25ff27ff676767686869f7ff')
    aa=rows['WeaponAnimationHigh']['file'];assert raw[aa:aa+len(animations)]==animations
    frames=[animations[a-0x7d]for a in(0x8b,0x8d,0x8f,0x91,0x92,0x93,0x94,0x95,0x96)]
    records=[]
    for frame in sorted(set(frames)):
        assert frame<106
        idx=raw[rows['RdWeaponIndex0']['file']+frame]
        assert 54<=idx<81,(frame,idx)
        records.append(dict(source_frame=frame,world_record=idx,radiusY=raw[rows['RdWeaponRadiusY']['file']+frame],radiusX=raw[rows['RdWeaponRadiusX']['file']+frame]))
    h=sha256();h.update(raw[:AT]);h.update(NEW);h.update(raw[AT+2:])
    result=dict(passed=True,parent_SHA256=PARENT,source_SHA256=SOURCE_SHA,
        donor_SHA256=DONOR_SHA,donor_dispatch_PC=0xd4d3,donor_dispatch=list(table),
        span=dict(file_start=AT,file_end_exclusive=AT+2,old=OLD.hex(),new=NEW.hex(),old_SHA256=H(OLD),new_SHA256=H(NEW)),
        predicted_SHA256=h.hexdigest(),owned_bytes=2,changed_bytes=1,code_growth=0,new_RAM=0,
        original_instruction_PC=0xaf76,original_target=0xafaf,proposed_target=0xafe2,
        action_changes=differences,all_other_255_actions_identical=True,dispatch_extra_cycles=0,
        downstream_update_cost_not_zero_or_measured=True,sole_current_typed_JSR=calls,
        current_update427_SHA256=H(raw[995184:995611]),hooks=rows,animation_frames=frames,world_records=records,
        native_PRG_only=True,no_cookie_or_carrier_bytes_proposed=True,
        cookie_claim='Actual owner guards are SelectedCharacter2/RdVariant1; no new cookie assumption. Cold/public/auth/foreign checks still required under a source lease.',
        Mini_Sonic_or_shared_bytes_proposed=False,proposed_CPU=False,installed_metadata_UI_CPU=False,
        candidate_image_composed=False,outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':print('RESULT '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')))
