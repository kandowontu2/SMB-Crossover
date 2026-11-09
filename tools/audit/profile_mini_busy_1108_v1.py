"""Attribute exact installed Mini busy GameCore cost to actual compiled calls."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import re

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location

R = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'
OUT = R / 'build/mini-busy-1108-v1'
KERNEL = R / 'build/mini-two-fireballs-1103/mini-zero.lbl'
NATIVE = ['GameCoreRoutine', 'GuestGameRoutinesBridge', 'PlayerCtrlRoutine',
          'PlayerBGCollision', 'BlockBufferColli_Feet', 'BlockBufferColli_Head',
          'BlockBufferColli_Side', 'BlockBufferCollision', 'PlayerHeadCollision',
          'AreaParserTaskHandler', 'AreaParserCore', 'ProcessAreaData', 'RenderAreaGraphics',
          'RenderAttributeTables', 'CrossoverLevelColumnBridge', 'CrossoverLevelColumn',
          'MegaManResetBlockHealth', 'CrossoverLevelObjectOverride', 'EnemiesAndLoopsCore', 'RunNormalEnemies',
          'RunEnemyObjectsCore', 'EnemiesCollision', 'PlayerEnemyCollision',
          'EnemyToBGCollisionDet', 'Mmc5GroundGoombaTerrain', 'EnemyGraphicsEngine',
          'NormalEnemyOffscreenBits', 'RelativeEnemyPosition', 'NormalEnemyBoundBox',
          'EnemyMovementSubs', 'MoveNormalEnemy', 'OffscreenBoundsCheck',
          'ProcFireball_Bubble', 'FireballEnemyCollision', 'PlayerGfxHandler',
          'ScrollHandler', 'PlayerOAMReservation', 'DoNothing']
MINI = ['MiniHostMain', 'MiniStep', 'MiniNativeTile', 'MiniAnimate', 'MiniHostBox',
        'MiniHostDraw', 'MiniNativeDraw', 'MiniHostGraphics']
sha = lambda data: hashlib.sha256(data).hexdigest()


def fixture(b, enemies, terrain, parser):
    m = N.fresh(b)
    N.put(m, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
          DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    N.invoke(m, 'MiniScene')
    N.put(m,AreaPointer=0x25)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaType') == 1 and N.get(m,'AreaAddrsLOffset') == 5
    N.put(m, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3,
          GameEngineSubroutine=8, PlayerStatus=0, PlayerSize=1, Player_X_Position=40,
          Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1,
          AreaType=1, AreaParserTaskNum=7, ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0,
          ScreenRight_X_Pos=255, ScreenRight_PageLoc=0)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        a = address(b,name)
        m[a:a+208] = bytes(176)+bytes([0x54])*32
    m[address(b,'GameTimerDisplay')] = 4
    for slot in range(enemies):
        for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                           ('Enemy_X_Position',88+slot*24),('Enemy_PageLoc',0),
                           ('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),('Enemy_MovingDir',2),
                           ('Enemy_BoundBoxCtrl',3)]:
            m[address(b,name)+slot] = value
    N.put(m,FrameCounter=1)
    N.invoke(m,'GameCoreRoutine',x=0,y=0)
    slots = [m[address(b,'Enemy_Flag')+i] for i in range(6)]
    assert all(slots[:enemies]), ('fixture lost its intended actors',enemies,slots)
    if terrain:
        for row in [8,9,10]:
            m[address(b,'Block_Buffer_1')+row*16+3] = 0xc3
    if parser:
        N.put(m,AreaParserTaskNum=1,ScrollThirtyTwo=32)
    return m


def profile(m, points, trials):
    main = N.NesMPU
    pairs = defaultdict(lambda: [0,0,0])
    transport = Counter(); ops = Counter(); totals = []
    for label,key in trials:
        active = []
        N.put(m,FrameCounter=(N.get(m,'FrameCounter')+1)&255, SavedJoypadBits=key,
              SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
        class Trace(main):
            def step(self):
                pc, sp, start = self.pc,self.sp,self.processorCycles
                while active and active[-1][1:3] == (pc,sp):
                    name,_,_,first = active.pop()
                    delta = start-first
                    cell = pairs[name]
                    cell[0] += 1; cell[1] += delta; cell[2] = max(cell[2],delta)
                tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
                names = points.get((tag,pc), ())
                if names:
                    ret = (1 + m[0x100+((sp+1)&255)] + 256*m[0x100+((sp+2)&255)]) & 65535
                    for name in names:
                        active.append((name,ret,(sp+2)&255,start))
                if pc == 0x15a:
                    caller = (1 + m[0x100+((sp+1)&255)] + 256*m[0x100+((sp+2)&255)]) & 65535
                    caller_tag = m.rawtags[(caller-0x8000)//8192] if caller >= 0x8000 else -1
                    transport[(caller_tag,caller,self.a,m[0x16c]+256*m[0x16d])] += 1
                main.step(self)
                ops[tag,pc] += self.processorCycles-start
        N.NesMPU = Trace
        try:
            z = N.invoke(m,'GameCoreRoutine',x=0,y=0)
        finally:
            N.NesMPU = main
        # The invocation loop recognizes its sentinel before Trace.step().
        assert all(rec[1] == 0x5b00 for rec in active), active
        for name,_,_,first in active:
            cell = pairs[name]; delta = z['CPU']-first
            cell[0] += 1; cell[1] += delta; cell[2] = max(cell[2],delta)
        totals.append([label,z['CPU'],N.get(m,'GameEngineSubroutine'),N.get(m,'Player_Y_Position'),
                       sum(0 < m[address(m.bundle,'Enemy_Flag')+i] < 128 for i in range(6))])
    assert sum(t[1] for t in totals) == sum(ops.values())
    return dict(totals=totals,inclusive={k:dict(calls=n,cycles=c,maximum=d) for k,(n,c,d) in sorted(pairs.items(),key=lambda item:-item[1][1])},
                trampoline_exclusive=sum(c for (_,pc),c in ops.items() if 0x15a <= pc < 0x17b),
                top_calls=[dict(caller_bank=t&127 if t>=0 else t,caller=f'{p:04X}',target_bank=b&127 if b>=128 else b,target=f'{d:04X}',calls=n)
                           for (t,p,b,d),n in transport.most_common(25)],
                top_OP=[dict(bank=t&127 if t>=128 else t,pc=f'{p:04X}',cycles=c) for (t,p),c in ops.most_common(35)])


def main():
    raw = ROM.read_bytes(); assert sha(raw) == PIN
    native = bundle(raw); points = defaultdict(list); missing = []
    for name in NATIVE:
        if name not in native['syms']:
            missing.append(name); continue
        at = location(native,name)
        points[((at-16)//8192|128,address(native,name))].append(name)
    for pc,name in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',KERNEL.read_text(),re.M):
        if name in MINI: points[3,int(pc,16)].append(name)
    for tag,pc,name in [(148,0xbdf4,'MiniBackground'),(193,0xaee2,'CoCheckCode'),
                        (193,0xaf27,'CoCheckHeaders'),(132,0xa325,'EnemyRenderSequence')]:
        points[tag,pc].append(name)
    result = {}
    trials = [('stand',0)]*4+[('jump',129)]*4
    for name,enemies,terrain,parser in [('empty',0,False,False),('four_actors',4,False,False),
            ('six_actors',6,False,False),('two_actors_pipe_side',2,True,False),
            ('four_actors_parser',4,False,True)]:
        row = profile(fixture(native,enemies,terrain,parser),points,trials)
        result[name] = row
        print(name,row['totals'],flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT/'profile-v4.json').write_text(json.dumps(dict(passed=True, ROM_SHA256=PIN,
        source_SHA256=sha(Path(__file__).read_bytes()), missing_symbol_hooks=missing,
        scope='Exact cartridge CPU fixture with real cold loader, native floor and explicit legal actor/terrain scenarios. No Mesen or physical-frame claim.',
        scenes=result),indent=2)+'\n')


if __name__ == '__main__':
    main()
