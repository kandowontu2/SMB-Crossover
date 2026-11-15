"""Authenticate donor sword handlers and explicit CPU control primitives."""
from hashlib import sha256
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as Original
import prince_cold_packet_1111 as Packet

PINS={'590e0ae60414d98d4b0a4d74874af58b93c6e720e8156220e0648966128b5f1f',
      '16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb'}


def labels(path):
    pairs=re.findall(r'^al ([0-9a-fA-F]+) \.?(\S+)$',path.read_text(),re.M);result={}
    for number,name in pairs:
        value=int(number,16)
        if name in result:assert result[name]==value
        result[name]=value
    return result


def leaf(bank,pc,fields,*,stop_action=None):
    c=Original.machine();m=c.memory;m.switch(bank)
    for at,value in fields.items():m[at]=value
    c.pc=pc;c.a,c.x,c.y,c.p,c.sp=83,71,0,0x21,224;c.stPushWord(0x5aff)
    trace=[]
    for steps in range(12000):
        if c.pc==0x5b00:reason='returned';break
        if stop_action is not None and m[0x616]==stop_action:reason='declared_action_store_before_external_terrain';break
        assert m[c.pc],('Donor control primitive BRK',hex(c.pc),bank)
        trace.append([7 if c.pc>=0xc000 else m.bank,c.pc]);c.step()
    else:raise AssertionError('Donor control primitive bound')
    return dict(action=m[0x616],pose=m[0x617],sword=m[0x6ee],marker=m[0x6de],
        forward=m[0x3a],back=m[0x3b],steps=steps,stop=reason,
        source_points=[row for row in trace if row[1]in(0xfe67,0xfe7a,0x8999,0x8afc,0x8972,0x8943,0x8735)])


def run(current):
    assert sha256(current).hexdigest()in PINS
    donor=Original.donor();parts=Packet.extract(current)[1]
    battle=R/'build/prince-actor-1101-v1/native-battle-v145'
    source=battle.with_suffix('.s').read_text();names=labels(battle.with_suffix('.lbl'));blob=battle.with_suffix('.bin').read_bytes()
    origin=names['PpBattle_4_ACCD'];assert parts[1][origin-0xc800:origin-0xc800+len(blob)]==blob,'Current battle differs from retained exact assembly'
    originals=re.findall(r'; original([457]):([\da-fA-F]{4}) ([\da-fA-F]+) ',source)
    for bank,pc,encoded in originals:
        bank=int(bank);pc=int(pc,16);offset=16+bank*16384+pc-(0xc000 if bank==7 else 0x8000)
        expected=bytes.fromhex(encoded);assert donor[offset:offset+len(expected)]==expected,(bank,hex(pc))
    core=R/'build/prince-actor-1101-v1/contact-core';core_names=labels(core.with_suffix('.lbl'));core_blob=core.with_suffix('.bin').read_bytes()
    lo=core_names['PpN_5_839F'];hi=core_names['PpN_5_842A']+1
    assert parts[0][lo-0xa000:hi-0xa000]==core_blob[lo-0xa000:hi-0xa000]
    rows=[]
    for facing in(0,255):
        for pad in(0,1,2,64,128):
            d=leaf(5,0x839f,{0x615:facing,0x618:255,0x40a:pad})
            assert d['forward']==(pad&(1 if facing==255 else 2))and d['back']==(pad&(2 if facing==255 else 1))
            rows.append(dict(kind='direction_decode',facing=facing,pad=pad,**d))
    for pose in(15,170,171,172):
        for action in(0,58,62,67,74):
            for pad in(0,64,128,192):
                a=leaf(5,0xfe67,{0x617:pose,0x616:action,0x40a:pad})
                assert a['action']==(58 if pad&128 and action!=67 else action)
                b=leaf(5,0xfe7a,{0x617:pose,0x616:action,0x40a:pad})
                expected=62 if pad&64 and pose==171 else 0 if pad&64 and pose==170 else action
                assert b['action']==expected
                rows.append(dict(kind='attack_and_parry',pose=pose,initial_action=action,pad=pad,attack=a,parry=b))
    movement=[]
    for facing in(0,255):
        for direction in(1,2):
            for action in(0,56,58):
                # Explicit movement-admission primitive. A source-left actor
                # at x32 avoids entering the unrelated terrain-alignment leaf.
                player=32 if facing==0 else 512;enemy=(player+(-80 if facing==0 else 80))&65535
                fields={0x615:facing,0x616:action,0x617:171,0x618:255,0x40a:direction,
                    0x60f:player&255,0x610:player>>8,0x61d:enemy&255,0x61e:enemy>>8,
                    0x3a:direction&(2 if facing==0 else 1),0x3b:direction&(1 if facing==0 else 2)}
                forward=leaf(5,0x8972,fields)
                back=leaf(5,0x8943,fields)
                assert forward['action']==(56 if fields[0x3a]and action!=58 else action)
                assert back['action']==(57 if fields[0x3b]and action not in(56,58)else action)
                movement.append(dict(facing=facing,pad=direction,initial_action=action,forward=forward,retreat=back))
    draw=[]
    base={0x615:255,0x623:0,0x616:0,0x617:15,0x6ee:1,0x6e0:1,0x6de:0,
        0x60f:0,0x610:2,0x61d:64,0x61e:2,0x611:128,0x61f:128,0x401:0,0x40a:0}
    for active in(0,1):
        fields=dict(base);fields[0x6e0]=active
        d=leaf(5,0xf090,fields,stop_action=55)
        assert d['sword']==(2 if active else 1)and d['action']==(55 if active else 0)
        draw.append(dict(active=active,**d))
    chords=[]
    for pad,expected in((0,0),(128,58),(64,62),(192,62),(1,56),(2,57),(65,56),(66,57),(129,58),(130,58)):
        fields=dict(base);fields.update({0x617:171,0x6ee:2,0x40a:pad,0x3a:pad&1,0x3b:pad&2})
        d=leaf(5,0xf090,fields);assert d['action']==expected,(pad,d)
        chords.append(dict(pad=pad,final_action=expected,**{k:v for k,v in d.items()if k!='action'}))
    sheath=[]
    for same in(False,True):
        fields=dict(base);fields.update({0x617:171,0x6ee:2,0x6de:1,0x623:255 if same else 0})
        d=leaf(5,0xf090,fields,stop_action=93)
        assert d['sword']==(2 if same else 1)
        sheath.append(dict(equal_facing=same,**d))
    q=dict(passed=True,current_ROM_SHA256=sha256(current).hexdigest(),donor_SHA256=Original.SHA,
        retained_battle_source_SHA256=sha256(source.encode()).hexdigest(),retained_battle_SHA256=sha256(blob).hexdigest(),
        exact_current_battle_envelope=[origin,origin+len(blob)],all_donor_comment_instruction_preimages=len(originals),
        current_input_decoder_envelope=[lo,hi],direction_and_button_cases=len(rows),movement_cases=movement,
        automatic_draw_cases=draw,sheath_cases=sheath,whole_combat_input_priority=chords,
        button_map={'A128':'FE67: action58 attack unless current action67; no button-edge test',
            'B64':'FE7A: action62 only at actual pose171 after DBB9; pose170 clears action0 but does not parry',
            'forward':'Facing255 Right1, facing0 Left2; action56 admitted through8972 distance gate',
            'retreat':'Opposite direction;8943 action57, blocked while action56 or58; A128 suppresses normal retreat'},
        no_target_free_draw=False,equal_facing_F090_exit_open=True,
        scope='Authenticated donor code plus explicitly seeded control-admission primitives; no ordinary gameplay or full-stage qualification',
        ROM_written=False,Mesen=False,outputs=0)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()),separators=(',',':')),flush=True)
