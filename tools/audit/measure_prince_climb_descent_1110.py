"""Rebind the funded Prince and isolate the first pipe's actual CPU paths."""

import argparse
import json
from pathlib import Path

import prepare_prince_climb_funded_1109_v1 as P


R, N, I, E = P.R, P.N, P.I, P.EDGE
BASE = R/'build/mini-box-terrain-visible-1110/candidate.nes'
BASE_PIN = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
PRIVATE_PIN = '9110fc24d627dfa3a73160b40706dcd2767eb97c9a4111d58f114f3125ec935b'
FUNDED = R/'build/prince-climb-funded-1109-v1/result.json'
FOOT_TRACE = R/'build/prince-climb-current-1109/native/capture/source-phases.csv'
LEVEL_SOURCE = R/'src/level_tiles.s'


def image():
    raw = BASE.read_bytes()
    proof = json.loads(FUNDED.read_text())
    assert P.sha(raw) == BASE_PIN and proof['passed'] and len(proof['patches']) == 24
    for path,digest in proof['bindings'].items():
        assert P.sha((R/path).read_bytes()) == digest,path
    out = bytearray(raw)
    for row in proof['patches']:
        at = row['offset']
        old,new = (bytes.fromhex(row[n]) for n in ('preimage','replacement'))
        assert len(old) == len(new) and out[at:at+len(old)] == old,hex(at)
        out[at:at+len(new)] = new
    assert P.sha(out) == PRIVATE_PIN
    mini = slice(1048592+962*1024,1048592+969*1024)
    assert out[mini] == raw[mini]
    template,_ = P.Q.M.OLD.image()
    return dict(template,raw=bytes(out))


def geometry(m, *, x, foot, old, facing):
    # Natural decorative pipe and ground from the retained native columns.
    # This is an explicit CPU terrain/phase fixture, not a controller replay.
    for sx in range(0,512,16):
        for y in (208,224):
            m[E.block(sx,y)] = 0x54
    for sx,top,shaft in ((448,0x12,0x14),(464,0x13,0x15)):
        m[E.block(sx,176)] = top
        m[E.block(sx,192)] = shaft
    N.put(m,SelectedCharacter=38,GameEngineSubroutine=8,OperMode=1,TimerControl=0,
          DisableCollisionDet=0,SwimmingFlag=0,PlayerSize=1,PlayerStatus=0,
          PlayerFacingDir=1 if facing else 2,Player_MovingDir=1 if facing else 2,
          Player_X_Position=x&255,Player_PageLoc=x>>8,
          Player_Y_Position=foot-32,Player_Y_HighPos=1,Player_State=2,
          Player_Y_Speed=foot-old,ScreenLeft_PageLoc=1,ScreenLeft_X_Pos=128)
    m.raw_page(2,2)
    N.put(m,CurrentBankC=2)
    m[0xc615] = facing
    m[0xc616] = 7
    m[0xc617] = 106
    m[0xc618] = 4
    m[0xc6d1] = 5
    E.put(m,0xc60f,x+8)
    E.put(m,0xc089,77)
    I.invoke(m,3,0xbd06,(83,71,109,0x21))  # PpHostProject, source pose 106
    delta = m[0xc088]
    delta -= 256 if delta >= 128 else 0
    source_y = foot-77-delta
    assert 0 <= source_y < 256
    m[0xc611] = m[0xc08b] = source_y
    E.put(m,0xc084,foot)
    E.put(m,0xc086,old)


def observe(m, operation):
    def values():
        s = m.ram[2]
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),dy=N.get(m,'Player_Y_Speed'),
            native_state=N.get(m,'Player_State'),source_x=s[0x60f]+256*s[0x610],
            source_y=s[0x611],action=s[0x616],pose=s[0x617],mode=s[0x618],
            foot=s[0x84]+256*s[0x85],old_foot=s[0x86]+256*s[0x87],
            surface=s[0x7f]+256*s[0x80])
    watches = ('GuestLandingWindow','GuestFootContactSide','RosterGuestFootContactSide',
               'StopPlayerMove','LandPlyr','SamusStopAtWallBanked')
    points = {(((I.location(m.bundle,name)-16)//8192)|128,I.address(m.bundle,name)):name
              for name in watches}
    points[138,0xa2dc] = 'right clamp write'
    points[3,0xb310] = 'source typed point'
    points[2,0xc362] = 'source landing align'
    native = N.NesMPU
    events = []

    class Trace(native):
        def step(self):
            tag = m.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
            watch = points.get((tag,self.pc))
            if watch:
                detail = dict(event=watch,PC=hex(self.pc),tag=tag,A=self.a,X=self.x,Y=self.y,P=self.p,
                              scratch=list(m[3:11]),**values())
                if watch == 'source typed point':
                    detail.update(query_x=E.word(m,0xb369),query_y=E.word(m,0xb36b))
                events.append(detail)
            return super().step()

    initial = values()
    N.NesMPU = Trace
    try:
        operation()
    finally:
        N.NesMPU = native
    return dict(before=initial,after=values(),events=events)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    current = image()
    seed,_ = P.Q.C.C.cold(current,38)
    _,seed,lab = P.Q.loaded(current,seed)
    assert lab['PpHostProject'] == 0xbd06
    assert (bytes(seed.ram[2][0x1fe0:0x1ff0]) ==
            bytes(seed.ram[3][0x1fe0:0x1ff0]) ==
            bytes.fromhex(json.loads(FUNDED.read_text())['Prince_cookie']))
    native = []
    source = []
    for x,foot,old,facing in [(449,193,175,255),(449,176,175,255),
                               (449,175,175,255),(433,193,175,255),(465,193,175,0)]:
        m = N.fork(seed)
        geometry(m,x=x,foot=foot,old=old,facing=facing)
        native.append(observe(m,lambda:N.invoke(m,'PlayerBGCollision',a=0,x=0,y=0,p=0x21)))
        m = N.fork(seed)
        geometry(m,x=x,foot=foot,old=old,facing=facing)
        source.append(observe(m,lambda:I.invoke(m,3,0xa5d9,(0,0,0,0x21))))
    refs = [Path(__file__),BASE,FUNDED,FOOT_TRACE,LEVEL_SOURCE,R/'src/collision.s',
            R/'tools/reference/prince_host_world_1102_v8.s']
    result = dict(passed=True,CPU_fixture_only=True,ROM_written=False,Mesen_run=False,
                  parent_SHA256=BASE_PIN,current_private_SHA256=PRIVATE_PIN,native_foot_paths=native,
                  source_terrain_paths=source,bindings={str(p):P.sha(p.read_bytes()) for p in refs})
    args.output.mkdir(exist_ok=True)
    (args.output/'geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:[(row['before'],row['after']) for row in result[key]]
                      for key in ('native_foot_paths','source_terrain_paths')}))


if __name__ == '__main__':
    main()
