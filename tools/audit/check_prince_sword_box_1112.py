"""Exact Prince3/9 box admission, support/render/cold/ISR proof; zero files."""

from hashlib import sha256
import json
import sys
from pathlib import Path
from unittest.mock import patch

import check_prince_sword_controls_1112 as Controls
import prince_sword_box_1112 as Source
import check_prince_pickup_reach_1112 as ReachCheck
import prince_pickup_reach_1112 as Reach
import check_prince_moving_support_1112 as Moving

B = Controls.B


def proxy(seed,control=3,identity=6,face=255,**changes):
    model = B.fixture(seed,x=128,native_y=176,face=face,action=0,mode=0)
    model.ram[2][0x617] = 15
    model.ram[2][0xa6] = 2
    model.ram[2][0x60f:0x611] = (136).to_bytes(2,'little')
    values = dict(Enemy_Flag=1,Enemy_ID=identity,Enemy_State=0,Enemy_BoundBoxCtrl=control,
                  Enemy_X_Position=160 if face else 96,Enemy_PageLoc=0,
                  Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2 if face else 1)
    values.update(changes)
    B.N.put(model,**values)
    return model


def proxy_call(model):
    registers = B.I.invoke(model,3,0xddbe,(83,71,109,0x61))['regs']
    registers[3] &= 0xef
    return registers


def render(before,after):
    root = Path(__file__).resolve().parents[2]/'build/prince-actor-1101-v1'
    art = json.loads((root/'source-art.json').read_text())['poses']
    labels = json.loads((root/'native-labels-v153.json').read_text())
    pair = [B.N.fork(before),B.N.fork(after)]
    parts = 0
    for pose in art:
        for model in pair:
            model.raw_page(2,2)
            B.N.put(model,CurrentBankC=2,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0,
                    Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
            model.ram[2][0x617] = pose['source_frame']
            model.ram[2][0x615] = pose['source_facing']
            model[0x200:0x300] = bytes([0xf8])*256
            B.I.invoke(model,3,labels['PpHostProject'],(83,71,109,0x61))
            B.I.invoke(model,3,0xc383,(83,71,109,0x61))
            B.Q.Sonic.O.clear_logs(model)
        results = [B.I.invoke(model,3,labels['PpHostDraw'],(83,71,109,0x61)) for model in pair]
        left,right = pair
        assert results[0]['regs'] == results[1]['regs']
        assert left.rawtags == right.rawtags and left.chr_latches == right.chr_latches
        assert bytes(left[0x200:0x800]) == bytes(right[0x200:0x800]),(pose['source_frame'],pose['source_facing'])
        assert bytes(left[3:11]) == bytes(right[3:11])
        assert bytes(left[0x15a:0x17b]) == bytes(right[0x15a:0x17b])
        assert bytes(left.ram[2][0x200:0x235]) == bytes(right.ram[2][0x200:0x235])
        count = len(pose['parts_8x16'])
        assert B.N.get(left,'SmPose') == B.N.get(right,'SmPose') == count*4
        parts += count
    assert len(art) == 408 and parts == 2578
    return dict(actual_native_poses=408,actual_native_parts=parts,
                source_native_OAM_CHR_registers_and_source_packet_equal=True,
                fixtures='Two reusable cold-derived models; each pose input/OAM reset, preceding equal render state retained')


def matrix(before,after):
    total = 0
    for face in (0,255):
        for identity in range(256):
            for control in (3,9):
                for seed,accepted in ((before,control == 3),(after,True)):
                    model = proxy(seed,control,identity,face)
                    proxy_call(model)
                    assert bool(model.ram[2][0x6e0]) == (accepted and identity<7),(face,identity,control)
                    assert B.N.get(model,'Enemy_BoundBoxCtrl') == control
                    total += 1
    for control in range(256):
        model = proxy(after,control)
        proxy_call(model)
        assert bool(model.ram[2][0x6e0]) == (control in (3,9)),control
        total += 1
    negatives = (dict(Enemy_Flag=0),dict(Enemy_Flag=2),dict(Enemy_State=0x20),
                 dict(Enemy_State=0xff),dict(Enemy_Y_HighPos=0),dict(Enemy_Y_HighPos=2),
                 dict(Enemy_X_Position=0,Enemy_PageLoc=2))
    for options in negatives:
        model = proxy(after,9,**options)
        proxy_call(model)
        assert model.ram[2][0x6e0] == 0,options
        total += 1
    return dict(actual_proxy_calls=total,all256_kind_ids=True,all256_box_controls=True,
                both_facings=True,unchanged_kind_cutoff=7,accepted_boxes=[3,9],negative_controls=len(negatives))


def support(before,after):
    count = 0
    for tile in range(256):
        for action,mode,pose in ((0,0,15),(1,1,6),(1,255,6),(42,1,6)):
            left,right = [Moving.fixture(seed,tile,action=action,mode=mode,pose=pose) for seed in (before,after)]
            old,new = Moving.Idle.call(left),Moving.Idle.call(right)
            assert old == new,(tile,action,old,new)
            assert bytes(left.ram[2][:0x800]) == bytes(right.ram[2][:0x800])
            assert bytes(left[3:11]) == bytes(right[3:11])
            assert bytes(left.ram[3][0x1369:0x136e]) == bytes(right.ram[3][0x1369:0x136e])
            count += 1
    return dict(identical_leaf_decisions=count,all256_tiles=True,actions=[0,1,42])


def main():
    parent = Controls.image()
    raw,chunks,layout = Source.transform(parent)
    assert Source.reverse(raw) == parent
    before,_ = B.cold(parent)
    after,cold = B.cold(raw)
    result = dict(rom_SHA256=sha256(raw).hexdigest(),parent_SHA256=sha256(parent).hexdigest(),
                  exact_reverse=True,layout=layout,cold=cold,output_files=0)
    if '--matrix' in sys.argv or len(sys.argv) == 1:
        result['proxy_matrix'] = matrix(before,after)
        print('PROXY_MATRIX '+json.dumps(result['proxy_matrix']),flush=True)
    if '--support' in sys.argv or len(sys.argv) == 1:
        result['support'] = support(before,after)
        print('SUPPORT_MATRIX '+json.dumps(result['support']),flush=True)
    if '--render' in sys.argv or len(sys.argv) == 1:
        result['render'] = render(before,after)
        print('RENDER '+json.dumps(result['render']),flush=True)
    if '--interrupts' in sys.argv or len(sys.argv) == 1:
        result['interrupts'] = B.Async.stress('actual Goomba9 proxy import',proxy(after,9),proxy_call,
            [(2,0xddbe,0xde89),(2,Source.HELPER,Source.POSE_END),(2,Source.TAIL,0xd756)])
        print('PROXY_INTERRUPTS '+json.dumps(result['interrupts']),flush=True)
        sample = Moving.fixture(after,0xc0,action=1,mode=255,pose=6)
        result['support_interrupts'] = B.Async.stress('compacted moving question support',sample,
            lambda model:Moving.Idle.call(model),[(2,Source.SUPPORT,Source.TAIL)])
        print('SUPPORT_INTERRUPTS '+json.dumps(result['support_interrupts']),flush=True)
    if '--cold' in sys.argv or len(sys.argv) == 1:
        with patch.object(Reach,'transform',Source.transform),patch.object(Reach,'reverse',Source.reverse):
            result['full_cold'] = ReachCheck.full_cold(parent)
    result['receipt_SHA256'] = sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(result))


if __name__ == '__main__':
    main()
