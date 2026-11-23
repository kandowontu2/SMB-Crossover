"""Exact bcc DK Jr ordinary life/Star access; bounded, memory-only source trial.

No emulator launcher, gameplay-memory writer, asset copy or retained output.
Arthur recovery temporarily assembles its five original cache files only.
"""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from unittest.mock import patch

import run_arthur_restored_cache_native_1123 as Arthur
import run_dkjr_flower_draw_native_1123 as Joined

S, H = Joined.S, Joined.H
Check, Head = S.Check, S.Check.Head
N, W = Check.N, Check.W
PIN = Arthur.CANDIDATE
OUT = Joined.Native.R / 'build/dkjr-life-star-source-1123'
PINS = {
    'run_arthur_restored_cache_native_1123.py': 'ed2f37ed59a7070b73beb665ebda843673c046000120ebbc16b79990fc45dd90',
    'run_dkjr_flower_draw_native_1123.py': 'a0e2a61a2945ff2acc39a09a4be89cb44fa48a16aab509302f7656aed31a32f1',
}

POLICY = r'''
local lifeProbe={phase='edge'}
local function lifePolicy()
 if not lifeProbe.started then
  if index~=4 or phase~='lower' or x()<940 then return nil end
  lifeProbe.started=updates;remember('life-existing944-entry',currentTop(944))
 end
 assert(updates-lifeProbe.started<700,'Finite existing944 hidden life approach')
 local p,y=x(),read(0xbd);local top=currentTop(944)
 local ride=top and ram(2,0x6b)==1 and ram(2,0x6c)==1 and y+32==top and ram(2,0x210)==y+15
 if lifeProbe.phase=='edge'then
  if p<EDGE then return 1 end
  assert(p<=EDGE+1 and ride,'Actual supported rightmost944 edge')
  lifeProbe.phase='wait';remember('life-right-edge',top)
 end
 if lifeProbe.phase=='wait'then
  assert(ride,'Existing944 carries the whole wait')
  if top>=TOP and top<=TOP+1 and (ram(2,0x14)&128)==0 then
   lifeProbe.phase='jump';lifeProbe.takeoff=updates
   remember('life-fresh-right-launch',top);return 129
  end
  return 0
 end
 if lifeProbe.phase=='jump'then
  assert(updates-lifeProbe.takeoff<160,'Finite original right jump')
  return 1|(updates-lifeProbe.takeoff<8 and 128 or 0)
 end
 error('Unknown life probe phase')
end
'''


def block(m, x, y):
    assert x % 16 == y % 16 == 0 and 32 <= y <= 224
    return m[0x300 + ((x // 256) & 1) * 0xd0 + ((x // 16) & 15) + y - 32]


def authenticate(raw):
    assert H(raw) == PIN
    for name, digest in PINS.items():
        assert H((Joined.Native.R / 'tools/audit' / name).read_bytes()) == digest, name
    parent = Arthur.recover_parent(raw, OUT)
    assert H(parent) == Joined.CANDIDATE
    payload = S.C.Old.Head.payload
    assert payload(raw) == payload(parent)
    at = S.C.Old.Head.COOKIE_AT
    assert raw[at:at+16] == parent[at:at+16]
    changed = {i for i, (a, b) in enumerate(zip(raw, parent, strict=True)) if a != b}
    loader = 16 + 70 * 8192 + (0xd9b8 & 8191)
    atlas = 1048592 + 868 * 1024
    assert changed <= set(range(loader, loader+733)) | set(range(atlas, atlas+13*1024))
    flower = Joined.without_draw(parent)
    bindings = Joined.Native.bindings(flower)
    for name, hook in bindings['hooks'].items():
        lo = 16 + hook['offset']; pre = bytes.fromhex(hook['preimage16'])
        assert raw[lo:lo+len(pre)] == parent[lo:lo+len(pre)] == pre, name
    return parent, dict(ROM_SHA256=PIN, recovered_d1_SHA256=H(parent),
        DK_payload_and_cookie_identical=True, unaffected_native_hook_preimages=True,
        only_Arthur_loader_and_atlas_changes=True, changed_bytes=len(changed))


def controller(raw, parent, *, kind='life', edge=976, top=174):
    text = Joined.controllers(parent)['full'].decode()
    assert H(text.encode()) == Joined.SCRIPTS['full'] and text.count(Joined.CANDIDATE) == 2
    old = text
    text = text.replace(Joined.CANDIDATE, PIN)
    assert text.replace(PIN, Joined.CANDIDATE) == old
    if kind == 'life':
        policy = POLICY.replace('EDGE', str(edge)).replace('TOP', str(top))
        text = Check.Replay.one(text, 'local function drive()\n', policy+'\nlocal function drive()\n')
        text = Check.Replay.one(text, ' lastUpdate=updates\n',
            ' lastUpdate=updates\n local lp=lifePolicy();if lp~=nil then bits=lp;return end\n')
    assert not any(v in text for v in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    return text


class Finished(Exception):
    pass


def run(raw, text, *, kind, limit):
    m, opening = Head.cold(raw)
    steps, previous, jump_start, work, pending = 0, None, None, None, None
    returns = post = grounded = 0
    events, curve, geometry, recent, heads, pickups = [], [], {}, [], [], []
    birth = mature = collection = None
    target, target_y, item_kind = (1024, 128, 3) if kind == 'life' else (1616, 144, 2)
    hook_names = ('NativeRarePlayerHeadCollisionCore','HandlePowerUpCollision')
    hooks = {(((W.location(m.bundle,n)-16)//8192)|128, W.address(m.bundle,n)): n for n in hook_names}
    watched = {pc for _,pc in hooks} | {0xb8f0,0xa2e8,0xaf2d}
    def token(c):
        return ((m[0x101+c.sp]+256*m[0x102+c.sp]+1)&65535, c.sp+2)
    def snap():
        return dict(step=steps, hero=Head.state(m), native=N.get(m,'Player_State'),
            source_y=m.ram[2][0x210], sample=m.ram[2][0x15], pad=m.controller_pad,
            origin=m.ram[2][0x76], fall_limit=m.ram[2][0x7b],
            source_box=list(m.ram[2][0x42:0x46]), actors=Head.actors(m))
    def observe(memory, c):
        nonlocal work, returns, post, grounded, pending, collection
        if (c.pc not in watched and (not work or c.pc!=work['token'][0])
                and (not pending or c.pc!=pending['token'][0])):return
        point = Head.point(c)
        if point == (3, 0xb8f0):
            assert work is None; work = dict(token=token(c), move=False, clock=False)
        if work and point == (3, 0xa2e8): work['move'] = True
        if work and point == (3, 0xaf2d): work['clock'] = True
        if work and (c.pc,c.sp) == work['token']:
            assert work['move'] and work['clock']; returns += 1
            if collection:
                post += 1;s=Head.state(m)
                ground = s['source']==s['prior']==1 and N.get(m,'Player_State')==0 and m.ram[2][0x210]==s['y']+15
                grounded = grounded+1 if ground else 0
            work = None
        name = hooks.get(point)
        if name == 'NativeRarePlayerHeadCollisionCore' and target-64 <= Head.state(m)['x'] <= target+32:
            heads.append(dict(snap(), tile=c.a, cell=m[9]+256*m[10]+m[5]))
        if name == 'HandlePowerUpCollision' and c.x < 6 and N.get(m,'Enemy_ID',c.x)==46 and N.get(m,'PowerUpType',c.x)==item_kind:
            a=Head.actor(m,c.x)
            assert birth and mature and a['state']&128 and N.get(m,'InvPickupOwner',c.x)==40 and N.get(m,'InvPickup',c.x)==252
            pending=dict(token=token(c), before=snap(), actor=a, score=Check.score(m),
                lives=N.get(m,'NumberofLives'), star=N.get(m,'StarInvincibleTimer'))
        if pending and (c.pc,c.sp)==pending['token']:
            assert not N.get(m,'Enemy_Flag',pending['actor']['slot'])
            collection=dict(pending,after=snap(),after_score=Check.score(m),after_star=N.get(m,'StarInvincibleTimer'))
            pickups.append(collection);pending=None
    def after(memory):
        nonlocal steps, previous, jump_start, birth, mature
        steps+=1;s=Head.state(m);cam=s['camera']
        for x in range(target-96,target+65,16):
            if str(x) not in geometry and cam<=x<cam+208:
                geometry[str(x)]={str(y):block(m,x,y) for y in range(48,225,16) if block(m,x,y)}
        if (s['x']>=900 if kind=='life' else s['x']>=1536):
            row=snap();recent.append(row)
            if len(recent)>12:recent.pop(0)
            if s['source']==3 and previous!=3 and jump_start is None:
                jump_start=steps;events.append(dict(event='actual-original-jump',**row))
            if jump_start is not None and steps-jump_start<=100:
                curve.append(dict(step=steps,x=s['x'],y=s['y'],source=s['source'],
                    source_y=m.ram[2][0x210],box=list(m.ram[2][0x42:0x46]),pad=m.controller_pad))
        previous=s['source']
        for i in range(6):
            if N.get(m,'Enemy_Flag',i) and N.get(m,'Enemy_ID',i)==46 and N.get(m,'PowerUpType',i)==item_kind:
                a=dict(Head.actor(m,i),owner=N.get(m,'InvPickupOwner',i),stamp=N.get(m,'InvPickup',i))
                if birth is None:birth=a
                if a['state']&128 and mature is None:mature=a
        if collection and post>=25 and grounded>=25:
            assert s['lives']==(3 if kind=='life' else 2) and s['hurt']==0
            if kind=='star':assert collection['after_star'] and Check.score(m)==collection['score']+1000
            raise Finished
        if kind=='star' and s['x']>=1610 and s['source']==s['prior']==1:
            events.append(dict(event='ordinary-floor-star-position',**snap()));raise Finished
    try:
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame),redirect_stdout(io.StringIO()):
            result=Check.Route.route(m,raw,limit,controller_text=text,observe_extra=observe,after_frame=after)
    except Finished: result=None
    except Exception as error:
        result={'receipt':{'reason':type(error).__name__+': '+str(error)}}
    star_trial=None
    if kind=='star' and collection is None and any(e['event']=='ordinary-floor-star-position' for e in events):
        # This suffix continues the reached ordinary state. Only the pad is
        # changed; no position, terrain, powerup, physics or source RAM seed.
        before=Head.state(m);before_tile=block(m,target,target_y);motion=[];settled=0
        try:
            for tick in range(160):
                m.controller_pad=128 if tick<8 else 0
                Check.normal_frame(m,observe);steps+=1;v=Head.state(m)
                motion.append(dict(tick=tick,hero=v,source_y=m.ram[2][0x210],pad=m.controller_pad))
                assert v['lives']==2 and v['hurt']==0 and v['source']!=5,('Healthy ordinary Star jump',tick,v)
                ground=v['source']==v['prior']==1 and N.get(m,'Player_State')==0 and m.ram[2][0x210]==v['y']+15
                settled=settled+1 if ground and tick>=8 else 0
                if settled>=25:break
            assert settled>=25,'Twenty-five actual grounded movement returns after Star reach attempt'
            star_trial=dict(completed_jump=True,initial=before,minimum_y=min(v['hero']['y'] for v in motion),
                minimum_source_y=min(v['source_y'] for v in motion),actual_updates=len(motion),grounded_returns=settled,
                tile_before=before_tile,tile_after=block(m,target,target_y),item_birth=birth,
                head_effects=heads,final=Head.state(m),tail=motion[-3:],pad_A_updates=8)
        except Exception as error:
            star_trial=dict(completed_jump=False,reason=str(error),initial=before,final=Head.state(m),tail=motion[-6:])
    receipt=(result or {}).get('receipt')or{}
    return dict(passed=collection is not None and post>=25 and grounded>=25,
        kind=kind,ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),opening_Main=opening,
        steps=steps,source_returns=returns,post_returns=post,grounded_returns=grounded,
        birth=birth,mature=mature,collection=collection,heads=heads,events=events,curve=curve,star_trial=star_trial,
        geometry=geometry,recent=recent,final=Head.state(m),reason=receipt.get('reason'),
        policy_events=[e for e in receipt.get('events',[])if e.get('event','').startswith('life-')],
        controller_only=True,gameplay_seeds=False,outputs=0)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=('life','star'),default='life')
    ap.add_argument('--edge',type=int,choices=(976,977),default=976)
    ap.add_argument('--top',type=int,default=174);ap.add_argument('--limit',type=int,default=4200)
    ap.add_argument('--compile-only',action='store_true');args=ap.parse_args()
    assert 144<=args.top<=192 and 1<=args.limit<=8000
    raw=Joined.Native.ROM.read_bytes()
    try:
        with Joined.cache():
            parent,binding=authenticate(raw)
            text=controller(raw,parent,kind=args.kind,edge=args.edge,top=args.top)
            print('DK LIFE STAR BINDING '+json.dumps(dict(binding,controller_SHA256=H(text.encode()),source_SHA256=H(Path(__file__).read_bytes())),separators=(',',':')),flush=True)
            if args.compile_only:return
            q=run(raw,text,kind=args.kind,limit=args.limit)
            print('DK LIFE STAR '+json.dumps(q,separators=(',',':')),flush=True)
            print('RECEIPT '+H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),flush=True)
    finally:
        if OUT.exists():
            assert not any(OUT.iterdir()),'No retained files allowed'
            OUT.rmdir()


if __name__=='__main__':main()
