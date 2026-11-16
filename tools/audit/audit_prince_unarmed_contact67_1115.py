"""Read-only current native inclusivity and authenticated donor control audit."""
from pathlib import Path
from unittest.mock import patch
import json
import current_prince_oneup_67e3_1115 as Current
import audit_prince_sword_control_map_1115 as Map

C,W=Current.C,Current.W

def run(raw):
    Current.prepare(raw);parts=C.Packet.extract(raw)[1]
    b=dict(W.Symbols.bundle(),raw=raw)
    def native(name,size):
        at=W.location(b,name);return raw[at:at+size]
    ul=W.address(b,'BoundingBox_UL_XPos');dr=W.address(b,'BoundingBox_DR_XPos')
    first=W.address(b,'FirstBoxGreater');found=W.address(b,'CollisionFound')
    code=native('FirstBoxGreater',12)
    assert code[:3]==bytes((0xdd,ul&255,ul>>8))and code[3]==0xf0
    assert code[5:8]==bytes((0xdd,dr&255,dr>>8))and code[8]==0x90 and code[10]==0xf0
    for at in(3,8,10):assert(first+at+2+(code[at+1]if code[at+1]<128 else code[at+1]-256))&65535==found
    contact=native('CollisionFound',9);assert contact[-4:]==bytes((0x38,0xa4,W.address(b,'R6'),0x60))
    core=C.R/'build/prince-actor-1101-v1/contact-core';labels=Map.labels(core.with_suffix('.lbl'))
    def private(name,size,stream=0):
        pc=labels[name];origin=0xa000 if stream==0 else 0xc800
        return parts[stream][pc-origin:pc-origin+size]
    unarmed=private('PpN_7_F03D',5)
    assert unarmed[:4]==bytes.fromhex('adeec6f0')
    assert(labels['PpN_7_F03D']+5+(unarmed[4]if unarmed[4]<128 else unarmed[4]-256))&65535==labels['PpN_7_F075']
    hurt=private('PpN_7_E9A4',21)
    expected=bytes((0x20,labels['PpMap5']&255,labels['PpMap5']>>8))+bytes((0x20,labels['PpN_5_8710']&255,labels['PpN_5_8710']>>8))*5+bytes((0x4c,labels['PpMap4']&255,labels['PpMap4']>>8))
    assert hurt==expected
    donor=Map.Original.donor();at=16+7*16384+0xe9a4-0xc000
    assert donor[at:at+21]==bytes.fromhex('2010d0'+'201087'*5+'4cfcd8')
    battle=C.R/'build/prince-actor-1101-v1/native-battle-v145'
    bl=Map.labels(battle.with_suffix('.lbl'));blob=battle.with_suffix('.bin').read_bytes();origin=bl['PpBattle_4_ACCD']
    assert parts[1][origin-0xc800:origin-0xc800+len(blob)]==blob
    at=bl['PpBattle_4_AD0C']-0xc800
    assert parts[1][at:at+7]==bytes.fromhex('adeec6c902d003')
    at=16+4*16384+0xad0c-0x8000;assert donor[at:at+13]==bytes.fromhex('adee06c902d0034c5ae920a4e9')
    q=dict(passed=True,ROM_SHA256=C.digest(raw),donor_SHA256=Map.Original.SHA,
        current_native_inclusive_edge_branches=dict(PC=first,bytes=code.hex(),equal_edges_reach=found,collision_carry_set=contact.hex()),
        actual_peak_boxes=dict(player=[132,169,144,193],Koopa=[137,193,149,205],shared_y=193,interpretation='Native inclusive boundary contact; no false-collision claim'),
        current_unarmed_gate=dict(PC=labels['PpN_7_F03D'],bytes=unarmed.hex(),Sword0_target=labels['PpN_7_F075']),
        five_original_damage_calls=dict(PC=labels['PpN_7_E9A4'],bytes=hurt.hex(),calls=5),
        exact_current_donor_battle=dict(origin=origin,bytes=len(blob),SHA256=C.digest(blob)),
        controls=dict(unarmed_A='Standing3 from idle; running4 only through original running pose gate',
            unarmed_B='Original careful step/grab, no swordless parry',Up='Original reach/ledge control, horizontal held direction takes priority',
            back='Original turn5 while unarmed',armed='Only owned Sword1 can automatically draw to2 against active opponent; then A58 attack/B62 parry'),
        source_scope='Static owning-byte and donor authentication only; no CPU gameplay or seeded primitive',
        gameplay_state_seeds=0,ROM_written=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Unarmed source audit attempted output/native launch')
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
