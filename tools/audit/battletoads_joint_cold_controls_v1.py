"""Prepared genuine BT menu/Start/parser/Main CPU cohort; no native replay.

Accepts a NEW immutable shared source cart after its mixed-cold rows are joined.
Never stages RAM3 code, cookies or host readiness. Native initial scene inputs
and controller bytes are explicit CPU-fixture inputs, as in the qualified FF
and Bowser parser controls. Product callbacks and interrupts execute untrapped.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
import battletoads_native_adapter_controls_v1 as T
from check_tmnt_render_oa import load, address, location
H = C.H

RAM = ['BtConstruct','BtFresh','BtScene','BtEnsure','BtMovement','BtCoreStep',
       'BtPhysicsStep','BtSrc_update_frame_counters','BtGraphics','BtDraw',
       'BtWeapons','BtHostHit','BtInjury','BtPickup']
ROM = ['BtColdPortrait','BtColdColors','BtAcquire','BtLoad','BtCheck','BtRetire',
       'BwBtResolve','FmStartRetireFlags','CmHostFresh','JnResetDispatch',
       'IcGlobalInit','SunnyGlobalInit','QwBoot','S2InitScreenPrepare',
       'QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen',
       'PlayerBGCollision','ScrollHandler','HandleEnemyFBallCol']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def invoke(m, name, **kw):
    points = {}
    for n in RAM + ROM:
        if n not in m.bundle['syms']:
            continue
        tag = 3 if n in RAM else ((location(m.bundle,n)-16)//8192)|128
        points[(address(m.bundle,n),tag)] = n
    events = []
    old = m.rawtags[:]
    c = H.start(m,name,**kw)
    live = bytes(list.__getitem__(m,slice(0x1e1,0x200)))

    def watch(mem,c,i):
        if c.pc >= 0x8000:
            key = (c.pc,mem.rawtags[(c.pc-0x8000)//8192])
            if key in points:
                events.append([i,points[key]])

    c, low = H.finish(m,c,watch)
    assert c.sp == kw.get('sp',224)
    assert bytes(list.__getitem__(m,slice(0x1e1,0x200))) == live
    assert m.rawtags[1] == old[1]
    assert m.rawtags[2] == H.get(m,'CurrentBankC')
    return dict(entry=name,CPU=c.processorCycles,minimum_SP=low,
                AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],counts=dict(collections.Counter(n for _,n in events)),
                events=events, X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),
                Y=H.get(m,'Player_Y_Position'),state=H.get(m,'Player_State'),
                HP=T.get(m,'BtSrc_Objects_Life',H.get(m,'CurrentPlayer')&1),
                source_clock=T.get(m,'BtSrc_FrameCounter'),
                source_pose=T.get(m,'BtSrc_player1_obj_wanted_frame',H.get(m,'CurrentPlayer')&1),
                source_ready=T.get(m,'BtHostReady'),PPU_reads=m.ppu_reads)


def cohort(b,player,variant):
    m = C.fresh(b,0)
    H.put(m,CurrentPlayer=player,CrossoverMenuIndex=23,FmGroups=variant<<5,SelectedCharacter=0)
    assert not any(m.ram[3]), 'No cache/code/state may be seeded into RAM3'
    cold = []
    for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
        r = invoke(m,name)
        cold.append(r)
        assert H.get(m,'SelectedCharacter') == 33
        assert m.ppu_reads == 0 and not m.ram_writes, ('cold menu must not initialize cache',name,r)
    assert cold[-1]['counts'].get('BtColdPortrait') == 1
    assert H.get(m,'CurrentOAMOffset') == 32
    assert all(m[0x200+i] < 240 for i in range(0,32,4)), 'All original standing parts must be visible'
    assert m.chr_latches[0] == 915
    H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
    start = invoke(m,'GameMenuRoutine')
    assert H.get(m,'OperMode') == 1 and H.get(m,'OperMode_Task') == 0
    assert H.get(m,'FmGroups') == variant<<5
    assert start['counts'].get('IcGlobalInit') == 1 and start['counts'].get('QwBoot') == 1
    invoke(m,'PauseRoutine',a=0)
    setup = []
    for tick in range(1000):
        if H.get(m,'OperMode_Task') == 3 and H.get(m,'GameEngineSubroutine') == 8:
            break
        H.put(m,SavedJoypad1Bits=0,SavedJoypadBits=0,SavedJoypad2Bits=0,
              A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        r = invoke(m,'GameLoop')
        normal = C.A.consume(m)
        setup.append(dict(tick=tick,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),
                          engine=H.get(m,'GameEngineSubroutine'),Main=r,NMI=normal))
    else:
        raise AssertionError(('real native parser bound',player,variant,setup[-1]))
    assert m.ppu_reads == 16400, ('one genuine eight-page copy/verify',m.ppu_reads)
    assert T.get(m,'BtHostReady') == 1 and T.get(m,'BtVariant') == variant<<5
    assert T.get(m,'BtSrc_Objects_Life',player) == 47
    assert m.ram[3][0x1fe0:0x1fe4] == bytes([167,33,1,117])
    block = address(b,'Block_Buffer_1')
    assert any(m[block:block+416]), 'Actual native parser must construct the world'
    frames = []
    for age in range(120):
        # Both directions, real held-A jump/release and a new B edge. No
        # support/position/health corrections are supplied between updates.
        keys = (1 if age < 80 else 2) | (128 if 8 <= age < 16 else 0) | (64 if age in [35,95] else 0)
        H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,
              A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,NmiDisable=255)
        before = T.get(m,'BtSrc_FrameCounter')
        r = invoke(m,'GameLoop')
        for n in ['BtMovement','BtCoreStep','BtPhysicsStep','BtSrc_update_frame_counters','PlayerBGCollision']:
            assert r['counts'].get(n) == 1, ('sole actual source/native update',player,variant,age,n,r)
        assert r['source_clock'] == (before+1)&255
        assert r['HP'] > 0 and not H.get(m,'MmDeathFlag')
        assert T.get(m,'BtSrc_Objects_death_timer',player) == 0
        normal = C.A.consume(m)
        assert T.get(m,'BtSrc_FrameCounter') == r['source_clock'], 'NMI must not advance source clock'
        frames.append(dict(age=age,input=keys,Main=r,NMI=normal,
                           source_attack=T.get(m,'BtSrc_Objects_AnimID',player)))
    assert max(r['Main']['X'] for r in frames) > min(r['Main']['X'] for r in frames)
    assert min(r['Main']['Y'] for r in frames) < 150, 'Actual jump must leave parsed native floor'
    assert any(r['source_attack'] for r in frames), 'B edge must enter original source punch'
    assert any(r['Main']['counts'].get('BtHostHit') for r in frames), 'Original script must emit its E2 event'
    return dict(player=player,variant=variant,cold=cold,start=start,setup=setup,frames=frames,
                no_cache_or_cookie_staging=True,no_per_frame_support_or_HP_edits=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    H.O=args.candidate.parent
    q=dict(passed=False,native=False,source_CPU_fixture=True,cohorts=[])
    try:
        b=load(args.candidate)
        for player in range(2):
            for variant in range(2):
                q['cohorts'].append(cohort(b,player,variant))
        q['passed']=True
    except Exception as e:
        q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(f.resolve()):sha(f) for f in [Path(__file__),Path(C.__file__),Path(T.__file__),
        Path(H.__file__),args.candidate,args.candidate.with_suffix('.dbg')]}
    (args.output/'controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=q['passed'],cohorts=len(q['cohorts']),error=q.get('error'),traceback=q.get('traceback'))))
    assert q['passed'],q.get('error')


if __name__=='__main__':
    main()
