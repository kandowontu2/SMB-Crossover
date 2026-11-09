"""Trace the post-brick landing writer and measure an earlier real enemy birth."""

import argparse
from collections import deque
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_prince_post_pit_brick_x1483_1110 as Brick


Delayed, Pair, R, Route = Brick.Delayed, Brick.Pair, Brick.R, Brick.Route
N = Delayed.N
OLD = R/'build/prince-post-pit-delayed-group-1110/brick-x1483.json'
OLD_SHA = 'ad54399ba63b7e136a2b6e9d7430f80ae2f6d02971927e79baecf8a8345eb47e'


def replay(env, seed, labels, low):
    code = inspect.getsource(Delayed.climb_and_hop)
    assert code.count('1484<=x<=1501')==1
    oracle = vars(Delayed).copy()
    exec(compile(code.replace('1484<=x<=1501',f'{low}<=x<=1501'),str(Path(__file__)),'exec'),oracle)
    return oracle['climb_and_hop'](env,seed,labels)


def trace(env, seed, labels):
    original, controls = N.NesMPU, Route.controls
    step = -1
    pcs = deque(maxlen=86)
    changes, nearby, entries = [],[],[]
    snapshots = {}
    names = {pc:name for name,pc in labels.items() if name.startswith('Pp')}
    core = R/'build/prince-actor-1101-v1/contact-core.lbl'
    for line in core.read_text().splitlines():
        _,pc,name = line.split()
        if name.startswith(('.PpN_', '.PpTerrainContact')):
            names.setdefault(int(pc,16),name[1:])

    def state(m):
        s = m.ram[2]
        return (s[0x60f]+256*s[0x610],s[0x611],s[0x616],s[0x617],s[0x618],s[0x4b1])

    def drive(e,m,lab,pad):
        nonlocal step
        step += 1
        return controls(e,m,lab,pad)

    class Trace(original):
        def step(self):
            if not 188<=step<=191:
                return super().step()
            m,pc = self.memory,self.pc
            before = state(m)
            bank = m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else None
            regs = (self.a,self.x,self.y,self.p,self.sp)
            row = (step,bank,pc,names.get(pc) if bank==3 else None,m[pc],regs,before)
            pcs.append(row)
            if bank==3 and pc==0xa5d9:
                entries.append(row)
                snapshots[step] = dict(ram=bytes(m.ram[2][:0x800]),registers=regs)
            answer = super().step()
            after = state(m)
            if before!=after:
                changes.append(dict(PC=row,after=after))
            if abs(before[0]-after[0])>=24:
                nearby.extend(pcs)
            return answer

    N.NesMPU, Route.controls = Trace,drive
    try:
        result = replay(env,seed,labels,1483)
    finally:
        N.NesMPU, Route.controls = original,controls
    assert result['terminal']=='contact-or-death' and result['end']['x']==1534
    return result,dict(entries=entries,changes=changes,nearby=nearby),snapshots


def earlier_birth(env, seed, labels):
    m = N.fork(seed)
    stage = 'finish-step'
    pads = {'finish-step':0,'face-left':2,'settle-left':0,'face-right':1,'settle-right':0}
    events, births = [],[]
    tracked = set()
    for epoch in range(155):
        q = Pair.observation(m,epoch)
        x = q['x']
        for a in Pair.targets(q):
            if a['slot'] not in tracked and q['enemy_cursor']==17:
                tracked.add(a['slot'])
                births.append(dict(actor=a,player=q))
        if (q['hp'],q['lives'],q['engine'])!=(4,2,8) or not 1455<=x<=1501:
            break
        idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
        previous = stage
        if stage=='finish-step' and idle:
            stage = 'face-left'
        elif stage=='face-left' and q['facing']==0:
            stage = 'settle-left'
        elif stage=='settle-left' and idle:
            stage = 'face-right'
        elif stage=='face-right' and q['facing']==255:
            stage = 'settle-right'
        elif stage=='settle-right' and idle:
            return m,events,births,q
        if stage!=previous:
            events.append(dict(stage=stage,state=q))
        Route.controls(env,m,labels,pads[stage])
    return None,events,births,q


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    assert sha256(OLD.read_bytes()).hexdigest()==OLD_SHA
    old = Pair.Second.First.Pit.Current.read(OLD)
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    print('Parsed the exact authored terrain',flush=True)
    env,model,labels,_ = Pair.arrival(base,columns)
    print('Replayed both original supported pit crossings',flush=True)
    moves,q,ready = Brick.Turn.align(env,model,labels)
    assert ready and q==old['arrival'] and moves==old['moves']
    print('Replayed the exact careful-step alignment',flush=True)
    failure, writer, snapshots = trace(env,model,labels)
    for change in writer['changes']:
        if change['PC'][-1][:1]!=change['after'][:1] or change['PC'][-1][2]!=change['after'][2]:
            print('Writer',change,flush=True)
    print('Entries',[(r[0],r[2],r[-1]) for r in writer['entries']],flush=True)
    later,events,births,arrived = earlier_birth(env,model,labels)
    print('Extra original turn',[(e['stage'],e['state']['x'],e['state']['camera_right']) for e in events],
          'arrived',arrived['x'],arrived['camera_right'],'births',[(a['actor']['x'],a['player']['epoch']) for a in births],flush=True)
    timing = replay(env,later,labels,1480) if later else None
    if timing:
        print('Extra-turn result',timing['terminal'],timing['end']['x'],timing['end']['hp'],
              [(e['stage'],e['state']['x'],e['state']['camera_right']) for e in timing['events']],flush=True)
    refs = (Path(__file__),OLD,Route.ROM,Path(Brick.__file__),Path(Delayed.__file__))
    report = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                  writer=writer,retained_D17A_inputs={k:dict(v,ram=v['ram'].hex()) for k,v in snapshots.items()},
                  first_failure=failure['end'],timing=dict(events=events,births=births,arrived=arrived,replay=timing),
                  bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    out.mkdir()
    (out/'writer.json').write_text(json.dumps(report,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
