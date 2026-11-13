"""Current native flower collection and original sword controller audit; no files."""

from hashlib import sha256
import json
import sys
from pathlib import Path
from unittest.mock import patch

import check_prince_brick_support_1111 as B
import prince_pickup_reach_1112 as Reach
import prince_cold_packet_1111 as Packet

R = Path(__file__).resolve().parents[2]
PIN = '3b7990bc59b490a1c5e488133a7c65d05526944d63b7e987f0b3f44df733343d'


def image():
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    if sha256(raw).hexdigest() == 'c5ce8c1557f6eb27c97f1fb1b0404c7854f59feb18717f27171d7dcb890efbbd':
        from compose_prince_menu_1112 import transform
        raw = transform(raw,reverse=True)[0]
    if sha256(raw).hexdigest() == 'a0dc025be05d1a9e697bb47f1affaea9d33f70be3d7fbee240b520e433f12327':
        from prince_sword_box_1112 import reverse
        raw = reverse(raw)
    if sha256(raw).hexdigest() == 'cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7':
        raw,_,_ = Reach.transform(raw)
    assert sha256(raw).hexdigest() == PIN
    Packet.extract(raw)
    return raw


def row(model):
    ram = model.ram[2]
    return dict(x=B.N.get(model,'Player_X_Position')|B.N.get(model,'Player_PageLoc')<<8,
                y=B.N.get(model,'Player_Y_Position'),hp=ram[0x6cf],sword=ram[0x6ee],
                action=ram[0x616],pose=ram[0x617],mode=ram[0x618],facing=ram[0x615],
                phase=ram[0xa6],guard=ram[0x6e0],guard_uid=ram[0x61c],guard_hp=ram[0x6d0],
                guard_dead=ram[0x6de],enemy_state=B.N.get(model,'Enemy_State'),
                enemy_flag=B.N.get(model,'Enemy_Flag'))


class Scene:
    def __init__(self,seed):
        self.model = B.Q.Sonic.slim_fork(seed)
        self.epoch = 0
        self.rows = []
        self.previous = None
        self.events = []
        self.sword_writes = []
        B.N.put(self.model,SelectedCharacter=38,OperMode=1,OperMode_Task=3,
                GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,
                Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,
                Player_Y_HighPos=1,PlayerSize=1,PlayerStatus=1,NmiDisable=255,
                DisableScreenFlag=0,Mirror_PPUMASK=30,Mirror_PPUCTRL=160,
                FamilyMainCommit=1,ReloadCHRBank=0,NumberofLives=2,
                TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,
                ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
                ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
        B.terrain(self.model,lambda x,y:0x54 if y>=208 else 0)
        self.points = {B.N.address(self.model.bundle,n):n for n in (
            'ShellOrBlockDefeat','PowerUpObjHandler','HandlePowerUpCollision','HuPickup')}
        self.points[0x9af8] = 'NativeDefeatInterior'
        native = B.N.NesMPU
        scene = self
        class Trace(native):
            def step(self):
                if self.memory is not scene.model:
                    return super().step()
                tag = self.memory.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
                if self.pc in scene.points:
                    scene.events.append(dict(epoch=scene.epoch,pc=self.pc,tag=tag,
                                             name=scene.points[self.pc],state=row(scene.model)))
                before = self.memory.ram[2][0x6ee]
                pc = self.pc
                result = super().step()
                after = self.memory.ram[2][0x6ee]
                if before != after:
                    scene.sword_writes.append(dict(epoch=scene.epoch,pc=pc,tag=tag,
                                                   before=before,after=after,state=row(scene.model)))
                return result
        self.Trace = Trace

    def tick(self,pad,weapon=True):
        model = self.model
        B.N.put(model,FrameCounter=self.epoch&255,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        with patch.object(B.N,'NesMPU',self.Trace):
            B.N.invoke(model,'PlayerCtrlRoutine',a=83,x=0,y=0,p=0x21)
            if weapon:
                B.N.invoke(model,'ProcFireball_Bubble',a=0,x=0,y=0,p=0x21)
        state = row(model)
        key = tuple(state[n] for n in ('x','y','sword','action','pose','mode','guard','guard_hp','guard_dead','enemy_state'))
        if key != self.previous:
            self.rows.append(dict(epoch=self.epoch,pad=pad,**state))
            self.previous = key
        assert state['hp'] > 0 and B.N.get(model,'NumberofLives') == 2,state
        self.epoch += 1
        return state

    def settle(self):
        for _ in range(8):self.tick(0)
        for _ in range(8):self.tick(1)
        for _ in range(80):
            state = self.tick(0)
            if state['action'] == 0 and state['pose'] == 15 and state['mode'] == 0:
                break
        assert state['facing'] == 255 and state['sword'] == 0,state

    def collect_flower(self):
        model = self.model
        state = row(model)
        B.N.put(model,ObjectOffset=5,Player_Rel_XPos=state['x'],Player_Rel_YPos=state['y'],
                TimerControl=1)
        for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=1,
                Enemy_X_Position=state['x'],Enemy_PageLoc=0,Enemy_Y_Position=state['y']+7,
                Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():
            model[B.N.address(model.bundle,field)+5] = value
        with patch.object(B.N,'NesMPU',self.Trace):
            B.N.invoke(model,'HuFullBox',x=0)
            B.N.invoke(model,'PowerUpObjHandler',x=5)
        assert model.ram[2][0x6ee] == 1
        assert B.N.get(model,'Enemy_Flag',5) == 0
        B.N.put(model,TimerControl=0)
        self.flower = dict(placed_mature_actor=True,slot=5,after=row(model),
                           erased=B.N.get(model,'Enemy_Flag',5))
        for _ in range(400):
            state = self.tick(0)
            if state['action'] == 0 and state['pose'] == 15 and state['mode'] == 0:
                break
        assert state['sword'] == 1 and state['action'] == 0 and state['mode'] == 0,state

    def face(self,facing):
        for _ in range(160):
            state = row(self.model)
            pad = (1 if facing == 255 else 2) if state['facing'] != facing else 0
            state = self.tick(pad)
            if state['facing'] == facing and state['action'] == 0 and state['mode'] == 0:
                return
        raise AssertionError(('Controller turn did not settle',row(self.model)))

    def enemy(self,control=3,identity=0,gap=64):
        state = row(self.model)
        self.direction = 1 if state['facing'] == 255 else -1
        x = state['x']+gap*self.direction
        for field,value in dict(Enemy_Flag=1,Enemy_ID=identity,Enemy_State=0,
                Enemy_BoundBoxCtrl=control,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,
                Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2 if self.direction == 1 else 1).items():
            B.N.put(self.model,**{field:value})
        self.enemy_x = x


def episode(seed,control,identity,facing=255):
    scene = Scene(seed)
    scene.settle()
    scene.collect_flower()
    scene.face(facing)
    scene.enemy(control,identity)
    stage = 'draw'
    parry = False
    for _ in range(420):
        state = row(scene.model)
        pad = 0
        if stage == 'draw' and state['sword'] == 2 and state['pose'] == 171:
            stage = 'parry'
        if stage == 'parry':
            pad = 64
            if state['action'] == 62:
                parry = True
                stage = 'parry-finish'
                pad = 0
        elif stage == 'parry-finish' and state['pose'] == 171 and state['action'] != 62:
            stage = 'approach'
        if stage == 'approach':
            gap = (scene.enemy_x-state['x'])*scene.direction
            pad = (1 if scene.direction == 1 else 2) if gap >= (38 if facing == 255 else 32) else 128
        state = scene.tick(pad)
        if state['enemy_state']&0x20:
            for _ in range(80):scene.tick(0)
            break
    if control == 3 or '--candidate' in sys.argv:
        assert parry and state['enemy_state']&0x20,row(scene.model)
        assert [write['after'] for write in scene.sword_writes] == [1,2,1]
        assert sum(event['name'] == 'NativeDefeatInterior' for event in scene.events) == 1
        assert {55,58,62,91,93} <= {state['action'] for state in scene.rows}
        assert row(scene.model)['sword'] == 1 and row(scene.model)['action'] == 0
    assert B.N.get(scene.model,'Enemy_BoundBoxCtrl') == control
    return dict(control=control,identity=identity,facing=facing,flower=scene.flower,
                parry_seen=parry,stage=stage,
                sword_writes=scene.sword_writes,events=scene.events,rows=scene.rows,
                terminal=row(scene.model))


def main():
    raw = image()
    layout = None
    if '--candidate' in sys.argv:
        import prince_sword_box_1112 as Source
        parent = raw
        raw,_,layout = Source.transform(parent)
        assert Source.reverse(raw) == parent
    seed,_ = B.cold(raw)
    report = dict(rom_SHA256=sha256(raw).hexdigest(),layout=layout,
                  scope='Placed flower and native enemies; real collector/controller/ProcFireball_Bubble entries; no drawn-mode seed, no enemy AI or Mesen',
                  episodes=[episode(seed,control,identity,facing) for control,identity in ((3,0),(9,6)) for facing in (255,0)],output_files=0)
    report['receipt_SHA256'] = sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if '--trace' not in sys.argv:
        for result in report['episodes']:
            result['action_set'] = sorted({state['action'] for state in result['rows']})
            result['rows'] = []
    print(json.dumps(report))


if __name__ == '__main__':
    main()
