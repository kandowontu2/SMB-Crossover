"""Read-only actual Metal carriers/menu and compact immutable input inventory."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,re,zipfile
import current_sunny_stock_91dc_1116 as Current

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
PACKET=R/'docs/qa/checkpoints/2026-11-02/metal-reservation-v42/inputs.zip'
PACKET_SHA='f1548d2f32972aa150939ab9b33ab829aa4f19f60013cf813031ac21888724e9'
ACTOR_PAGES=(247,248,249,250,827,828,829,830)
RENDER_PAGES=(831,500,494)
EXTRA_AT=1048592+499*1024+672
MEMBERS=('component.s','component.lbl','native-cookie.bin','native-auth.bin','native-finish.bin')


def inspect(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Exact actual91dc Metal inspection only'
    assert digest(PACKET.read_bytes())==PACKET_SHA
    with zipfile.ZipFile(PACKET)as z:
        data={n:z.read(n)for n in MEMBERS};assert sum(map(len,data.values()))<2_000_000
    labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)[ \t\r]*$',data['component.lbl'].decode(),re.M)}
    old=Current.reference(raw);b=dict(W.Symbols.bundle(),raw=raw)
    actor=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in ACTOR_PAGES)
    renderer=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in RENDER_PAGES)
    extra=raw[EXTRA_AT:EXTRA_AT+352]
    rows=[]
    for name,pages in(('actor8192',ACTOR_PAGES),('renderer3072',RENDER_PAGES)):
        for p in pages:
            at=1048592+p*1024;assert raw[at:at+1024]==old[at:at+1024],(name,p)
        blob=actor if name=='actor8192'else renderer
        rows.append(dict(role=name,pages=list(pages),bytes=len(blob),SHA256=digest(blob)))
    assert extra==old[EXTRA_AT:EXTRA_AT+352]
    rows.append(dict(role='extra352',file=EXTRA_AT,bytes=352,SHA256=digest(extra)))
    cookie=None;residents=[]
    for role,bank,offset in(('auth',25,0x1f9e),('finish',99,0x176e)):
        base=data['native-'+role+'.bin'];at=16+bank*8192+offset;assert base.count(data['native-cookie.bin'])==1
        k=base.index(data['native-cookie.bin']);actual=raw[at:at+len(base)];c=actual[k:k+16]
        assert c[:3]==bytes.fromhex('a7232e')and base.replace(data['native-cookie.bin'],c)==actual,(role,'Unexpected resident owner delta')
        assert actual==old[at:at+len(actual)]
        assert cookie is None or cookie==c;cookie=c
        residents.append(dict(role=role,file=at,PRGbank=bank,bytes=len(actual),SHA256=digest(actual),cookie_file=at+k))
    assert actor[0x10a3:0x10a8]==bytes.fromhex('a901eaeaea')
    assert actor[0x1fba:0x1fc0]==bytes.fromhex('b51f0a60eaea')
    rowbase=labels['Ms12CacheRows'];at=rowbase-0xcd00
    assert renderer[at+23*3:at+24*3]==bytes.fromhex('4cbabf')
    assert renderer[at+10*3:at+11*3]==bytes.fromhex('4cafd8')
    services=[]
    for i in range(37):
        code=renderer[at+3*i:at+3*i+3];assert code[0]==0x4c
        services.append(dict(row=i,PC=rowbase+3*i,target=int.from_bytes(code[1:],'little')))
    worker=labels['Ms12Movement'];worker_bytes=renderer[worker-0xcd00:worker-0xcd00+180]
    lives=W.address(b,'NumberofLives');needle=bytes((0xad,lives&255,lives>>8,0xcd,0x3e,0xc8,0xf0))
    life_hits=[i for i in range(len(worker_bytes)-len(needle))if worker_bytes[i:i+len(needle)]==needle]
    assert len(life_hits)==1
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    navigation=(1,1,1,4,32)
    for pad in navigation:W.UI.key(m,pad)
    selected={n:N.get(m,n)for n in('CrossoverMenuIndex','SelectedCharacter','MarioVariant','X5ChrMode','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel')}
    menu_name=W.UI.menu_name(m)[0];assert(menu_name,selected['SelectedCharacter'])==('METAL STORM',35),(menu_name,selected)
    hooks={}
    for name in('GameLoop','PlayerMovementSubs','HandlePowerUpCollision','NrPickupCollision','NrPickup','FloateyNumbersCore'):
        pc,where=W.address(b,name),W.location(b,name);bank=(where-16)//8192;lo=16+bank*8192
        assert raw[lo:lo+8192]==old[lo:lo+8192]
        hooks[name]=dict(PC=pc,file=where,PRGbank=bank,prefix=raw[where:where+8].hex(),bank_SHA256=digest(raw[lo:lo+8192]))
    required=('Ms8Load','Ms8Auth','Ms12Movement','MsHostStep','MsNativeConstruct','MsNativeApplyDelta','Ms12Fresh','Ms25Pickup',
        'Ms12Common','Ms12Veneers','MsHostServiceRows','Ms12CacheRows','MsHostSavePoint','MsHostReadDelta')
    assert all(n in labels for n in required)
    return dict(passed=True,actual_image_SHA256=PIN,reference_bc5_SHA256=Current.BC5,reference_only=True,
        immutable_packet=dict(path=str(PACKET.relative_to(R)),SHA256=PACKET_SHA,read_only_members={n:dict(bytes=len(v),SHA256=digest(v))for n,v in data.items()}),
        actual_carriers_exact_bc5=rows,residents_exact_bc5=residents,full16_cookie=cookie.hex(),
        retained_repairs=dict(column_ack_PC=0xb0a3,head_getter_PC=0xd8af,maturity_row_PC=rowbase+23*3,maturity_worker_PC=0xbfba),
        typed_services=services,public_labels={n:labels[n]for n in required},native_hooks=hooks,
        compiled_menu=dict(name=menu_name,navigation=list(navigation),selected=selected,source_title_vblank_limit=True),
        source_state=dict(bank=2,CPU_base=0xc000,armor_offset=0x5d0,weapon_offset=0x718,ready_offset=0x800,epoch_offset=0x801),
        life_snapshot=dict(PC=worker+life_hits[0],hex=needle.hex(),saved_life_CPU=0xc83e,
            readonly_lead='Current movement compares native lives with saved snapshot; unequal falls toward constructor. Natural INC effects require real-earned qualification, not a seeded conclusion'),
        controller_inventory=dict(immutable_armor_policy='tools/reference/metal_storm_natural_armor_1101_v26.lua',
            legacy_factory='replay_metal_current_1112.py reads mutable build controller paths; never invoked here',
            retained_native_MF='8fc57b8b/9312b808 and upgraded-shot scope; no retest requested',
            missing='Genuine natural S/L and25 actual returned original movement at authenticated Main'),
        no_mutable_Metal_build_inputs=True,canonical_native_symbols_reused='Existing retained W.Symbols inputs; bundle raw replaced by actual91dc',
        no_archive_extraction=True,gameplay_CPU=False,new_controllers=False,game_bytes_changed=0,outputs=0,Mesen=False)


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Readonly Metal inspection attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=inspect(ROM.read_bytes())
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
