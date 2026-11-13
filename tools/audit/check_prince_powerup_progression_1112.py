"""Inspect actual native reveal classification for current Prince cold state."""
import json
from hashlib import sha256
from pathlib import Path
import check_prince_brick_support_1111 as B


def main():
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(raw).hexdigest() == '6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2'
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
    print(json.dumps(dict(rows=rows, mushroom_then_reveal=collected,
                         scope='Controlled native actor/pickup/reveal, not naturally earned', output_files=0)))


if __name__ == '__main__':
    main()
