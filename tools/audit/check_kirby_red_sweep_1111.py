"""Build a bounded red-shell sweep inside the existing Kirby helper span."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch

import check_kirby_red_return_1111 as Control
import check_sonic_native_effects_vectors_1110 as Clone


N, A = Control.N, Control.Authority
SOURCE = Control.R / 'tools/reference/kirby_red_sweep_1111.s'
START, SIZE = 0xab19, 163
STOP = (0x5b00,224)
sys.path.insert(0, str(SOURCE.parent))
from sonic_sms_compact_cold_worker_1110 import assemble


def proposal(raw, bundle):
    parent = sha256(raw).hexdigest()
    assert parent in Control.PARENTS
    at = A.location(bundle,'KbShellEnemyContact')
    assert A.address(bundle,'KbShellEnemyContact')==START and at==16+74*8192+(START&8191)
    assert int(bundle['syms']['KbShellEnemyContact']['size'],0)==SIZE
    exact = A.AUTHORITY.read_bytes()
    assert A.sha(A.AUTHORITY)==A.AUTHORITY_ROM and raw[at:at+SIZE]==exact[at:at+SIZE]
    owned = raw[16+74*8192:16+75*8192]
    refs = [i for i in range(len(owned)-2) if owned[i:i+3]==bytes.fromhex('2019ab')]
    assert refs == [A.address(bundle,'KbWeapons::ShellContact')-0xa000]
    # This helper is private to the exact type3/kind2-or-3 caller.
    admission = bytes.fromhex('b9405cc903d016b9675cc902f004c903d00b')
    assert owned[refs[0]-len(admission):refs[0]] == admission
    text = SOURCE.read_text(encoding='ascii')
    names = set(re.findall(r'\b(?:Enemy_\w+|BoundBoxCtrlData|Kb(?:SavedSlot|Shot\w+|Temp\w*))\b',text))
    imports = ''.join(f'{n}=${A.address(bundle,n):04x}\n' for n in sorted(names))
    p = assemble(imports+text,{'KIRBY_SHELL':(START,SIZE)})
    body = p['images']['KIRBY_SHELL']
    assert len(body)==SIZE
    image = raw[:at]+body+raw[at+SIZE:]
    assert raw[:at]==image[:at] and raw[at+SIZE:]==image[at+SIZE:]
    return image,p,dict(parent_SHA256=parent,image_SHA256=sha256(image).hexdigest(),
        file_offset=at,span_bytes=SIZE,changed_bytes=sum(x!=y for x,y in zip(raw[at:at+SIZE],body)),
        preimage_SHA256=sha256(raw[at:at+SIZE]).hexdigest(), source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def view(seed,image):
    m = N.fork(seed)
    m.bundle = dict(m.bundle,raw=image)
    return m


def set_box(m, ctrl, ex, ey, sx, sy, vx, kind, *, page=1):
    Control.place_enemy(m,ex,ey)
    Control.put_slot(m,Control.SLOT,Enemy_Y_HighPos=page,Enemy_BoundBoxCtrl=ctrl)
    Control.place_shot(m,sx,vx)
    N.put(m,KbSavedSlot=0,KbShotY=sy,KbShotKind=kind)


def native_boxes(seed, trial):
    at = A.location(seed.bundle,'BoundBoxCtrlData')
    data = seed.bundle['raw'][at:at+48]
    boxes = [tuple(data[i:i+4]) for i in range(0,48,4)]
    counts, costs = Counter(), {}
    for ctrl, (l,t,r,b) in enumerate(boxes):
        for ex,vx,kind in product((510,513),(3,-3),(2,3)):
            ey = 160
            lo,hi = l-7,r+8
            for dx,dy in product((lo-4,lo-3,lo-1,lo,hi,hi+1,hi+3,hi+4),(t-8,t-7,b+8,b+9)):
                sx,sy = ex+dx,ey+dy
                e = {'x':ex,'y':ey}
                endpoint = Control.point(boxes[ctrl],e,sx,sy)
                swept = endpoint or (kind==3 and Control.point(boxes[ctrl],e,sx-vx,sy))
                values = []
                for source,want in ((seed,endpoint),(trial,swept)):
                    m = N.fork(source)
                    set_box(m,ctrl,ex,ey,sx,sy,vx,kind)
                    cpu,_ = Control.call(m,'KbShellEnemyContact',x=Control.SLOT)
                    assert (cpu.x,cpu.sp,bool(cpu.p&1))==(Control.SLOT,224,want), (ctrl,kind,vx,dx,dy,cpu.p,want)
                    values.append(cpu.processorCycles)
                counts['green' if kind==2 else 'red'] += 1
                if swept!=endpoint:
                    counts['red_swept_only'] += 1
                else:
                    costs.setdefault(kind,set()).add(values[1]-values[0])
    for source,ctrl,yp in product((seed,trial),(3,12,255),(0,1,2)):
        if (ctrl,yp)==(3,1):
            continue
        m = N.fork(source)
        set_box(m,ctrl,626,151,651,180,3,3,page=yp)
        c,_ = Control.call(m,'KbShellEnemyContact',x=Control.SLOT)
        assert not c.p&1
        counts['hidden_or_unsupported_rejects'] += 1
    assert counts['red_swept_only']
    return dict(cases=dict(counts),equivalent_outcome_cycle_delta={k:[min(v),max(v)]for k,v in costs.items()})


def return_contacts(seed, trial):
    rows = []
    for vx in (3,-3):
        for source, expected in ((seed,0),(trial,1)):
            m = N.fork(source)
            last = 648 if vx>0 else 621
            facing = 2 if vx>0 else 1
            player = 660 if vx>0 else 610
            Control.place_enemy(m,626,151)
            Control.place_shot(m,last,-vx,facing=facing,age=31)
            N.put(m,Player_X_Position=player&255,Player_PageLoc=player>>8)
            _, events = Control.call(m,'KbWeapons::Shots')
            assert events['native_defeat']==expected
            shell = Control.shot(m)
            assert (shell['age'],shell['vx'],shell['x'],shell['direction'])==(32,vx,last+vx,facing)
            assert shell['type']==(0 if expected else 3)
            if expected:
                rows.append(dict(vx=vx,launch_facing=facing,age=32,old_center=last,new_center=shell['x']))
    return rows


def terrain_precedence(seed, trial):
    rows = []
    for src in (seed,trial):
        m = N.fork(src)
        Control.place_enemy(m,626,151)
        Control.place_shot(m,648,3)
        m[0x300:0x4a0]=bytes([0x54])*0x1a0
        _,events=Control.call(m,'KbWeapons::Shots')
        assert not events and Control.shot(m)['type']==0 and Control.enemy(m)['state']==0
        rows.append((bytes(m[0:0x100]),bytes(m[0x200:0x800]),tuple(m.rawtags)))
    assert rows[0]==rows[1]
    return dict(actual_terrain_first_pairs=1)


def green_full_pairs(seed, trial):
    outcomes, cycles = Counter(), []
    for vx, sx, ey, box in product((3,-3),(621,626,648,651),(150,151,168,178),(3,9)):
        pair = []
        for src in (seed,trial):
            m = N.fork(src)
            Control.place_enemy(m,626,ey)
            Control.put_slot(m,Control.SLOT,Enemy_BoundBoxCtrl=box,Enemy_ID=6 if box==9 else 3)
            Control.place_shot(m,sx-vx,vx)
            N.put(m,KbShotKind=2)
            cpu,events=Control.call(m,'KbWeapons::Shots')
            scratch = {A.address(m.bundle,n) for n in ('KbTemp','KbTemp2','KbTempX','KbTempPage','KbTempY')}
            guest = bytes(m[i] for i in range(0x5c00,0x5d00) if i not in scratch)
            state = (cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,Control.shot(m),Control.enemy(m),events,
                     tuple(m.rawtags),tuple(bytes(bank) for bank in m.ram),bytes(m[0:0x100]),
                     bytes(m[0x15a:0x17b]),bytes(m[0x200:0x800]),guest,m.ppu_log,
                     tuple((a,v) for a,v in m.writes if 0x5113<=a<=0x5117))
            pair.append((state,cpu.processorCycles))
        assert pair[0][0]==pair[1][0], (vx,sx,ey,box,
            [(i,a,b) for i,(a,b) in enumerate(zip(pair[0][0],pair[1][0])) if a!=b and i<9],
            [i for i,(a,b) in enumerate(zip(pair[0][0],pair[1][0])) if a!=b])
        outcomes['hit' if pair[0][0][7]['native_defeat'] else 'miss'] += 1
        cycles.append(pair[1][1]-pair[0][1])
    assert outcomes['hit'] and outcomes['miss']
    return dict(green_complete_shot_pairs=dict(outcomes),green_cycles_delta=[min(cycles),max(cycles)])


def vectors(seed,p):
    irq = Clone.ISR
    irq.DEEPEST = None
    irq.PATHS.clear()
    stats = Counter()
    reached = set()

    def live(m,c):
        return (irq.regs(c),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
            bytes(m[0x200:0x800]),bytes(m[0x5c00:0x5d00]),tuple(bytes(b)for b in m.ram),tuple(m.rawtags))

    def observe(m,c):
        if m.rawtags[1]!=202 or not START<=c.pc<START+SIZE or c.pc in reached:
            return
        reached.add(c.pc)
        a,b=Clone.clone(m,c)
        irq.finish(a,b,STOP)
        for kind in ('NMI','IRQ'):
            q,d=Clone.clone(m,c)
            before=live(q,d)
            assert irq.isr(q,d,kind,STOP)=='returned'
            assert live(q,d)==before,(kind,hex(c.pc))
            irq.finish(q,d,STOP)
            assert live(q,d)==live(a,b),(kind,hex(c.pc),'continuation')
            stats[kind]+=1

    with patch.object(irq,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)), \
            patch.object(irq,'clone',side_effect=Clone.clone):
        for kind,vx,ex,ey,sx,sy in ((3,3,626,151,651,180),(3,-3,626,151,618,180),
                                   (2,3,626,169,634,180),(3,3,626,136,639,180),
                                   (3,3,626,205,639,180),(3,3,626,160,619,180)):
            m=N.fork(seed)
            set_box(m,3,ex,ey,sx,sy,vx,kind)
            N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255)
            Control.call(m,'KbShellEnemyContact',x=Control.SLOT,observe=observe)
        assert irq.DEEPEST is not None
        m,c,entry,stop=irq.DEEPEST
        q,d=Clone.clone(m,c)
        a,b=Clone.clone(m,c)
        before=live(q,d)
        assert irq.isr(q,d,'IRQ')=='returned' and live(q,d)==before
        for target in ((entry[0],entry[-1]),stop):
            irq.finish(a,b,target)
            irq.finish(q,d,target)
            assert live(q,d)==live(a,b)
    assert stats['NMI']==stats['IRQ']>=60
    assert all(p['symbols'][name] in reached for name in ('XStart','YBelow','CheckYWidth','No'))
    return dict(cuts=dict(stats),nested_IRQ=1,deepest_parent_SP=c.sp)


def main():
    seed,box=Control.prepare()
    image,p,receipt=proposal(seed.bundle['raw'],seed.bundle)
    trial=view(seed,image)
    print(json.dumps(dict(event='proposal',**receipt),sort_keys=True),flush=True)
    assert Control.turns(seed)==Control.turns(trial)
    print(json.dumps(dict(event='motion',baseline=Control.corners(seed,box),
        repaired=Control.corners(trial,box,swept=True),returns=return_contacts(seed,trial),
        unchanged_return_trajectory=True),sort_keys=True),flush=True)
    print(json.dumps(dict(event='boundaries',**native_boxes(seed,trial),**terrain_precedence(seed,trial),
                          **green_full_pairs(seed,trial)),sort_keys=True),flush=True)
    print(json.dumps(dict(event='vectors',**vectors(trial,p)),sort_keys=True),flush=True)
    print(json.dumps(dict(passed=True,output_files=0,natural_miss_claim=False)),flush=True)


if __name__=='__main__':
    main()
