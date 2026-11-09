"""Replay the exact Prince lip failure over native player GameLoops."""

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from check_prince_player_pipeline_1102_v67 import terrain
import check_prince_source_support_1110 as Support


R,N,P = Support.R,Support.N,Support.P
BASE = R/'build/mini-shared-game-loop-tail-native-1110/candidate.nes'
BASE_PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
SHAFT = Support.MANIFEST
HISTORICAL = R/'build/mini-box-terrain-visible-1110/candidate.nes'
NATIVE = R/'build/prince-full11-native-1110-v5/capture/full11.json'
OLD_PROOF = R/'build/prince-source-support-1110/source-support-CPU.json'
PRINCE_PIN = 'f6ecaabfc8d0ca164859ad9ffa210945eb22ba85d60afce7b2d656e98d856c74'
LEFT,RIGHT,TOP = 192,224,144


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def apply(raw,rows):
    result = bytearray(raw)
    for row in rows:
        at = row['offset']
        old,new = (bytes.fromhex(row[k]) for k in ('preimage','replacement'))
        assert len(old)==len(new) and result[at:at+len(old)]==old,row['role']
        result[at:at+len(old)] = new
    return bytes(result)


def current():
    proof,native,previous = (read(p) for p in (SHAFT,NATIVE,OLD_PROOF))
    assert native['ROM_sha256']==previous['ROM_sha256']==proof['expected_memory_only_SHA256']
    assert not native['passed'] and native['first_pipe'] and native['route']['index']==2
    assert native['HP']==5 and native['initial_lives']==native['final_lives']==2
    assert native['route']['clears'][0]['left']==608
    top = native['route']['on_top']
    assert (top['world_x'],top['physical_foot'])==(723,145)
    old = HISTORICAL.read_bytes()
    assert P.sha(old)==proof['parent_SHA256']
    assert apply(old,proof['patches'])==Support.ROM.read_bytes()
    base = BASE.read_bytes()
    assert P.sha(base)==BASE_PIN
    private = apply(base,proof['patches'])
    assert P.sha(private)==PRINCE_PIN
    return dict(Support.M.image(),raw=private),bytes.fromhex(proof['Prince_cookie']),previous


def row(m,epoch):
    s = m.ram[2]
    get = lambda k:N.get(m,k)
    return dict(epoch=epoch,x=get('Player_X_Position')+256*get('Player_PageLoc'),
                y=get('Player_Y_Position'),dy=get('Player_Y_Speed'),native_state=get('Player_State'),
                engine=get('GameEngineSubroutine'),lives=get('NumberofLives'),hp=s[0x6cf],
                source_x=int.from_bytes(s[0x60f:0x611],'little'),source_y=s[0x611],
                foot=int.from_bytes(s[0x84:0x86],'little'),action=s[0x616],frame=s[0x617],mode=s[0x618])


def replay(seed,base,worker=None):
    e,m,labels = P.Q.first8(base,seed)
    area = lambda x,y: (0x54 if y>=208 else 0 if not LEFT<=x<RIGHT or y<TOP
                        else (0x12 if x<LEFT+16 else 0x13) if y<TOP+16
                        else (0x14 if x<LEFT+16 else 0x15))
    terrain(m,area)
    assert bytes(m.ram[3][Support.CALL-0xa000:Support.CALL-0xa000+6])==bytes.fromhex('20e2bdc911f0')
    if worker is not None:
        m[Support.PROBE:Support.PROBE+len(worker)] = worker
        m.ram[3][Support.CALL-0xa000+1:Support.CALL-0xa000+3] = Support.PROBE.to_bytes(2,'little')
    hits,checkpoints,steps = Counter(),{},[]
    actual = N.NesMPU

    class Trace(actual):
        def step(self):
            if self.pc==Support.PROBE or self.pc in (Support.CALL,0xc42a):
                cpu = self.pc
                tag = self.memory.rawtags[(cpu-0x8000)//8192] if cpu>=0x8000 else None
                if (cpu,tag) in ((Support.PROBE,None),(Support.CALL,3),(0xc42a,2)):
                    hits[cpu] += 1
            return super().step()

    stage = 'approach'
    N.NesMPU = Trace
    try:
        for epoch in range(640):
            a = row(m,epoch)
            if stage=='approach' and a['x']>=LEFT-48:
                checkpoints['release'] = a
                stage = 'settle'
            if stage=='settle' and a['mode']==0 and a['frame']==15:
                checkpoints['stand'] = a
                stage = 'up'
            if stage=='up' and a['mode'] in (2,6):
                checkpoints.setdefault('hang',a)
            if stage=='up' and a['action']==10 and a['foot']<=TOP+1:
                checkpoints['climb'] = a
                stage = 'cross'
            if stage=='cross' and TOP<=a['foot']<=TOP+4 and a['native_state']==0:
                checkpoints.setdefault('supported',a)
            if stage=='cross' and a['x']>=RIGHT+8 and a['foot'] in range(208,212):
                checkpoints['far_ground'] = a
                break
            if a['engine']!=8 or a['lives']!=2 or a['hp']!=5:
                break
            pad = {'approach':1,'settle':0,'up':8,'cross':1}[stage]
            m.controller_pad = pad
            N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
            e['run'](m,'GameLoop',labels)
            if epoch%16==0 or stage=='cross' and len(steps)<100:
                steps.append(a)
    finally:
        N.NesMPU = actual
    return dict(probe=worker is not None,checkpoints=checkpoints,hits=dict(hits),last=row(m,epoch),trace=steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    result = out/'trajectory.json'
    assert not result.exists()
    base,cookie,previous = current()
    seed,_ = P.Q.C.C.cold(base,38)
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    with tempfile.TemporaryDirectory(dir=out) as name:
        worker,labels = P.assemble(Path(name),'support',Support.SOURCE,P.one_segment(Support.PROBE,160))
    assert len(worker)==previous['prototype_bytes']==131 and labels['PpD297Support']==Support.PROBE
    before,after = (replay(seed,base,probe) for probe in (None,worker))
    positive = 'far_ground' in after['checkpoints'] and 'far_ground' not in before['checkpoints']
    refs = (Path(__file__),Path(Support.__file__),BASE,HISTORICAL,SHAFT,NATIVE,OLD_PROOF,Support.ROM)
    evidence = dict(passed=positive,ROM_written=False,native_run=False,
                    parent_SHA256=BASE_PIN,private_memory_SHA256=PRINCE_PIN,worker_bytes=len(worker),
                    fixture=dict(left=LEFT,right=RIGHT,top=TOP,active_support_loaded_by_actual_cold=True,
                                 CPU_only_probe_at=Support.PROBE),baseline=before,prototype=after,
                    bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    result.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=positive,baseline=before['checkpoints'],prototype=after['checkpoints'],
                          baseline_last=before['last'],prototype_last=after['last'])),flush=True)


if __name__=='__main__':
    main()
