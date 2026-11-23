"""Read-only exactffd708 organic Flower access investigation.

Normal menu/cold, the frozen earned-Mushroom pads, then the proven full-route
prefix. No actor/terrain/resource/state writes, emulator or output files.
"""
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import io,json
import compose_dkjr_mushroom_slot_order_1123 as C

Check,Head,H=C.Check,C.Check.Head,C.H
N,W,B=Check.N,Check.W,Check.B
SOURCE_SHA='45bea71d531c5bf4197b9ab6f5b1156ef86c128fd6014e48fe05c66ca1fe1003'


def controller(raw):
    assert H(Path(C.__file__).read_bytes())==SOURCE_SHA and H(raw)==C.CANDIDATE
    mushroom=C.controller(raw,route=True)
    lo=mushroom.index('local slotAdmissionWait,slotAdmissionReady')
    hi=mushroom.index('local function drive()\n',lo)
    adapter=mushroom[lo:hi]
    text=C.full_controller(raw)
    once=Check.Replay.one
    text=once(text,'local function drive()\n',adapter+'local function drive()\n')
    text=once(text,' lastUpdate=updates\n', ''' lastUpdate=updates
 local firstBits=mushroomPolicy()
 if firstBits~=nil then bits=firstBits;return end
''')
    assert not any(q in text for q in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    return text


def block(m,x,y):
    assert x%16==y%16==0 and 32<=y<=224
    return m[0x300+((x//256)&1)*0xd0+((x//16)&15)+y-32]


class Arrived(Exception):pass


def prefix(raw):
    text=controller(raw);m,opening=Head.cold(raw)
    ticks=0;geometry={};items=[];last_status=0;arrival=None
    def after(memory):
        nonlocal ticks,last_status,arrival
        ticks+=1;s=Head.state(m)
        if last_status==1:
            assert s['status']==1 and s['hurt']==0 and s['lives']==2,('Earned Mushroom retained',ticks,s,Head.actors(m))
        if s['status']==1 and not last_status:
            items.append(dict(event='natural_M_complete',step=ticks,hero=s,score=Check.score(m)))
            assert block(m,336,144)==196
            last_status=1
        cam=s['camera']
        for x in range(944,1361,16):
            if str(x) not in geometry and cam<=x<cam+224:
                geometry[str(x)]={str(y):block(m,x,y) for y in range(48,225,16) if block(m,x,y)}
        if s['x']>=1256 and s['source']==s['prior']==1 and s['y']==176 and N.get(m,'Player_State')==0:
            assert s['status']==1 and N.get(m,'GuestPowerupActive')==0
            arrival=dict(step=ticks,hero=s,actors=Head.actors(m),block=block(m,1248,144),score=Check.score(m))
            raise Arrived
    try:
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame):
            with redirect_stdout(io.StringIO()):
                result=Check.Route.route(m,raw,5200,controller_text=text,after_frame=after)
    except Arrived:result=None
    assert arrival is not None,dict(result=result,final=Head.state(m),items=items)
    return m,dict(controller_SHA256=H(text.encode()),opening_Main=opening,
        approach=arrival,natural_M=items,authored_geometry=geometry,
        actual_helpers=[a for a in Head.actors(m) if a['id'] in (37,40)],outputs=0)


def jump(m):
    hooks={(((W.location(m.bundle,n)-16)//8192)|128,W.address(m.bundle,n)):n
        for n in ('NativeRarePlayerHeadCollisionCore','HandlePowerUpCollision')}
    events=[];positions=[];before=block(m,1248,144)
    def observe(memory,cpu):
        name=hooks.get(Head.point(cpu))
        if name:
            events.append(dict(event=name,hero=Head.state(m),A=cpu.a,X=cpu.x,
                actors=Head.actors(m)))
    for _ in range(8):
        Check.normal_frame(m,observe)
    stand=Head.state(m)
    assert stand['source']==1 and stand['y']==176 and stand['status']==1 and not stand['held']&128,stand
    for step in range(120):
        m.controller_pad=128 if step<8 else 0
        Check.normal_frame(m,observe)
        s=Head.state(m);positions.append(dict(step=step,pad=m.controller_pad,hero=s))
        assert s['lives']==2 and s['hurt']==0 and s['source']!=5 and s['status']==1,(step,s,Head.actors(m))
        if step>=8 and s['source']==s['prior']==1 and s['y']==176 and not s['held']&128:break
    else:raise AssertionError(('Finite ordinary ground jump',Head.state(m)))
    return dict(stand=stand,peak=min(p['hero']['y'] for p in positions),
        min_sourceY=min(p['hero']['y']+15 for p in positions),updates=len(positions),
        block_before=before,block_after=block(m,1248,144),events=events,
        actual_powerup_actors=[a for a in Head.actors(m) if a['id']==46],
        final=Head.state(m),tail=positions[-4:],ordinary_A_hold=8,outputs=0)


def main():
    raw=C.Old.M.ROM.read_bytes();assert H(raw)==C.CANDIDATE
    C.inverse(raw)
    m,q=prefix(raw)
    print('DK FLOWER PREFIX '+json.dumps(q,separators=(',',':')),flush=True)
    q.update(ROM_SHA256=H(raw),jump=jump(m),probe_SHA256=H(Path(__file__).read_bytes()))
    receipt=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('DK FLOWER PROBE '+json.dumps(q,separators=(',',':')),flush=True)
    print('RECEIPT '+receipt,flush=True)


if __name__=='__main__':main()
