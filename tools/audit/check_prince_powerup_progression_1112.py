"""Inspect actual native reveal classification for current Prince cold state."""
import json
import argparse
from hashlib import sha256
from pathlib import Path
import check_prince_brick_support_1111 as B


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', action='store_true')
    args = parser.parse_args()
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(raw).hexdigest() == '6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2'
    if args.candidate:
        from prince_pickup_progression_1112 import transform
        raw, packing = transform(raw)
    seed, _ = B.cold(raw)
    rows = []
    for status in (0, 1, 2):
        model = B.fixture(seed)
        B.N.put(model, PlayerStatus=status, ObjectOffset=5)
        model[B.N.address(model.bundle, 'PowerUpType')+5] = 0
        B.N.invoke(model, 'PwrUpJmp', x=5)
        rows.append(dict(status=status, revealed=model[B.N.address(model.bundle, 'PowerUpType')+5]))
    model = B.fixture(seed)
    B.N.put(model, PlayerStatus=0, ObjectOffset=5, Player_Rel_XPos=48,
            Player_Rel_YPos=112, Player_X_Position=48, Player_PageLoc=0,
            ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0,
            ScreenRight_X_Pos=255, ScreenRight_PageLoc=0,
            TimerControl=1, FrameCounter=0)
    model.ram[2][0x6cf] = 4
    for field, value in dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128,
            PowerUpType=0, Enemy_X_Position=48, Enemy_PageLoc=0,
            Enemy_Y_Position=119, Enemy_Y_HighPos=1, Enemy_BoundBoxCtrl=9,
            Enemy_MovingDir=1).items():
        model[B.N.address(model.bundle,field)+5] = value
    B.N.invoke(model, 'HuFullBox', x=0)
    original_cpu = B.N.NesMPU
    calls = []
    points = {B.N.address(model.bundle,n): n for n in (
        'NrPickupCollision','HuMature','HandlePowerUpCollision','NrPickup','HuPickup')}
    class Trace(original_cpu):
        def step(self):
            if self.pc in points:
                calls.append(points[self.pc])
            return super().step()
    B.N.NesMPU = Trace
    try:
        B.N.invoke(model, 'PowerUpObjHandler', x=5)
    finally:
        B.N.NesMPU = original_cpu
    collected = dict(hp=model.ram[2][0x6cf], status=B.N.get(model,'PlayerStatus'),
                     flag=model[B.N.address(model.bundle,'Enemy_Flag')+5])
    assert collected['hp'] == 5 and collected['flag'] == 0, (collected,calls,
        bytes(model[B.N.address(model.bundle,'BoundingBox_UL_XPos'):B.N.address(model.bundle,'BoundingBox_UL_XPos')+28]).hex())
    model[B.N.address(model.bundle,'PowerUpType')+5] = 0
    B.N.invoke(model, 'PwrUpJmp', x=5)
    collected['next_reveal'] = model[B.N.address(model.bundle,'PowerUpType')+5]
    assert collected['status'] == int(args.candidate), collected
    assert collected['next_reveal'] == int(args.candidate), collected
    assert model.ram[2][0x6ee] == 0, 'Mushroom must not grant sword'
    matrix = 0
    for hp in range(6):
        for status in range(3):
            for kind in (0, 1):
                for mature in (0, 128):
                    m = B.fixture(seed)
                    B.N.put(m, PlayerStatus=status, ObjectOffset=5)
                    m.ram[2][0x6cf] = hp
                    m[B.N.address(m.bundle,'Enemy_Flag')+5] = 1
                    m[B.N.address(m.bundle,'Enemy_State')+5] = mature
                    m[B.N.address(m.bundle,'PowerUpType')+5] = kind
                    B.I.invoke(m, 3, 0xc7b3, (0, 5, 0, 0x20))
                    accepted = bool(hp and mature)
                    expected_status = 1 if args.candidate and accepted and kind == 0 else status
                    assert B.N.get(m,'PlayerStatus') == expected_status, (hp,status,kind,mature)
                    assert m.ram[2][0x6cf] == (min(5,hp+1) if accepted and kind == 0 else hp)
                    assert m.ram[2][0x6ee] == int(accepted and kind == 1)
                    assert m[B.N.address(m.bundle,'Enemy_Flag')+5] == int(not accepted)
                    matrix += 1
    print(json.dumps(dict(rows=rows, mushroom_then_reveal=collected,
                         pickup_matrix=matrix,
                         candidate=args.candidate, rom_sha256=sha256(raw).hexdigest(),
                         scope='Controlled native actor/pickup/reveal, not naturally earned', output_files=0)))


if __name__ == '__main__':
    main()
