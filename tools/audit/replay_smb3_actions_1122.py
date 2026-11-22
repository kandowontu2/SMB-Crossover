"""Exact59 controller-only natural suit acquisition followed by native actions.

Default validation creates no files and never starts Mesen. --run is reserved
for root's existing shared sequential native queue. Linked CPU checks are
explicit typed components, separate from natural native replay evidence.
"""

import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_smb3_upgrades_1122 as Acquire
import prepare_kirby_contacts_current_1108_v1 as Authority
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

R, ROM, N, W = Acquire.R, Acquire.ROM, Acquire.Current.N, Acquire.Current.W
PIN = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
FORMS = {'mario3': (0, 'SMB3 MARIO'), 'luigi3': (1, 'SMB3 LUIGI'),
         'toad3': (2, 'SMB3 TOAD'), 'peach3': (3, 'SMB3 PEACH')}
ACTIONS = {'Fire': 2, 'Raccoon': 3, 'Frog': 4, 'Tanooki': 5, 'Hammer': 6}
NATIVE_BANKS = {90: 'abc53520a1d833c4a120c7399c022b2cb6885a4709edf9008ba8af654c814d49',
                91: '175d7f632d0acbf0a61f08132456bf80473e546d4fe7621fb925d0bbf8e83751',
                92: 'bf2dcd6ebcd1accd0f7e64b0c90bfdfc965068ab4f7d820fc7c3f2a44ca78cd3'}
POLICY = R / 'tools/playthroughs/smb3_actions_1122.lua'
OUT = R / 'build/smb2-flag-native-1113'
H = lambda raw: sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def authority():
    assert Authority.sha(Authority.AUTHORITY) == Authority.AUTHORITY_ROM
    assert Authority.sha(Authority.AUTHORITY.with_suffix('.dbg')) == Authority.AUTHORITY_DBG
    return Authority.scoped_load(Authority.AUTHORITY)


def bindings(raw, form, action):
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN, 'Exact installed59e1a591 only'
    assert form in FORMS and action in ACTIONS
    b = authority()
    fields = set(Acquire.Current.Stock.Shared.RAM_FIELDS) - {
        n for n in Acquire.Current.Stock.Shared.RAM_FIELDS if n.startswith('Ic')}
    fields.update(Acquire.Current.Stock.EXTRA_FIELDS)
    fields.update(('PseudoRandomBitReg', 'GamePauseStatus', 'GamePauseTimer', 'FrameCounter',
                   'M3Native::Player_YVelFrac', 'M3Native::Player_YVel',
                   'M3Native::Player_Statue', 'M3Native::Player_QueueSuit',
                   'M3Native::Player_TailAttack', 'M3Native::Player_FrogHopCnt',
                   'M3Native::Player_Frame', 'M3Native::Player_FlashInv',
                   'M3ShotKind', 'M3ShotX', 'M3ShotPage', 'M3ShotY', 'M3ShotYHi',
                   'M3ShotVX', 'M3ShotVY', 'M3ShotAge', 'M3SavedSlot',
                   'InjuryTimer', 'GuestInvulTicks', 'GuestHurtTicks'))
    ram = {name: W.address(b, name) for name in sorted(fields)}
    assert (ram['M3Variant'], ram['M3Form'], ram['M3Ready']) == (0x5fe4, 0x5f40, 0x5c80)
    hooks = {}
    names = dict(GameLoop='GameLoop', M3Movement='M3Movement', M3Step='M3Step',
                 M3PreparePickup='M3PreparePickup', M3CollectPickup='M3CollectPickup',
                 HandlePowerUpCollision='HandlePowerUpCollision', PlayerHeadCollision='PlayerHeadCollision',
                 M3RisePickup='M3RisePickup', M3Graphics='M3Graphics', M3DrawWorld='M3DrawWorld',
                 TargetPauseInput='HpPauseCold', ActionThrow='M3Throw', ActionAdvance='M3AdvanceShot',
                 ActionDamage='M3ProjectileDamage', ActionDefeat='M3DefeatEnemy',
                 ActionBody='M3BodyDispatch', ActionInjury='M3Injury', ActionTail='M3TailEnemies')
    for name, symbol in names.items():
        pc, at = W.address(b, symbol), W.location(b, symbol)
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191), symbol
        code = raw[at:at+16]
        if symbol != 'GameLoop':
            assert code == b['raw'][at:at+16], ('Scoped native entry preimage changed', symbol)
        hooks[name] = dict(pc=pc, tag=bank|128, offset=at-16, hex=code.hex(), bytes=list(code))
    at, pc = W.location(b, 'M3PreparePickup'), W.address(b, 'M3PreparePickup')
    needle = b'\xad'+(ram['PseudoRandomBitReg']+2).to_bytes(2, 'little')
    hits = [i for i in range(125) if raw[at+i:at+i+3] == needle]
    assert len(hits) == 1
    i = hits[0]
    hooks['M3RNGRead'] = dict(pc=pc+i, tag=((at-16)//8192)|128, offset=at+i-16,
                              hex=needle.hex(), bytes=list(needle))
    domains = []
    for bank, expected in NATIVE_BANKS.items():
        lo = 16+bank*8192
        assert H(raw[lo:lo+8192]) == expected, ('Actual59 SMB3 domain changed', bank)
        domains.append(dict(bank=bank, SHA256=expected,
                            equals_symbol_authority=raw[lo:lo+8192] == b['raw'][lo:lo+8192]))
    menu = 16+124*8192
    left = bytes.fromhex('088a2907d0058a0907d003ca8ae828090060')
    assert raw[menu:menu+len(left)] == left
    ids = list(raw[menu+0x40:menu+0x60]);assert ids[16] == 17
    edges = {'left': [(i&24)|((i-1)&7) for i in range(32)],
             'right': [(i&24)|((i+1)&7) for i in range(32)],
             'up': [(i-8)&31 for i in range(32)], 'down': [(i+8)&31 for i in range(32)]}
    paths = []
    for start in range(32):
        queue, seen = [(start, [])], {start}
        for node, path in queue:
            if node == 16:
                paths.append(path);break
            for key, edge in edges.items():
                if edge[node] not in seen:
                    seen.add(edge[node]);queue.append((edge[node], path+[key]))
        else:
            raise AssertionError('Compiled SMB3 menu slot unreachable')
    variant, name = FORMS[form]
    target = ACTIONS[action]
    return dict(sha=PIN, key=form, form=form, name=name, character=17, slot=16,
                variant=variant, select=variant, mode='easy', mode_value=0,
                route='mushroom-suit', item='mushroom-suit', stockKind=1, blockX=1248, blockY=144,
                bits=dict(a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1),
                navigation=[p[0] if p else '' for p in paths], ram=ram, hooks=hooks,
                smc_return_pc=0x016e, suit_names=Acquire.Current.SUITS,
                target_suit=target, target_suit_name=action, target_stamp=0xd0+target, action=action,
                logical_item_classifier='owner17/D1=Mushroom; owner17/D2..D6=actual suit',
                scoped_symbol_ROM=Authority.AUTHORITY_ROM, actual_input_CPU_SHA256=PIN,
                pinned_native_SMB3=domains, symbol_authority_only=True)


ACTION_OBSERVER = r'''
local A=assert(SMB3_ACTION_STATE)
local function actionState()
 local s=state();s.statue=r('M3Native::Player_Statue');s.queue=r('M3Native::Player_QueueSuit')
 s.tail=r('M3Native::Player_TailAttack');s.frog=r('M3Native::Player_FrogHopCnt')
 s.native_frame=r('M3Native::Player_Frame');s.previous=r('M3Previous');return s
end
local function shot(i)
 return {slot=i,kind=r('M3ShotKind',i),x=pos('M3ShotX','M3ShotPage',i),
  y=r('M3ShotY',i),y_high=r('M3ShotYHi',i),vx=r('M3ShotVX',i),vy=r('M3ShotVY',i),age=r('M3ShotAge',i)}
end
local function actionEntry(name,p,cpu)
 if not A.acquired then return end
 if name=='ActionThrow'then
  assert(r('M3Fresh')&64~=0 and r('SavedJoypadBits')&64~=0,'Actual fresh B reaches native throw')
  p.action={kind='throw',before=actionState()}
 elseif name=='ActionAdvance'and A.throw then
  local s=shot(cpu['cpu.x']);if s.kind~=0 then p.action={kind='advance',before=s}end
 elseif name=='ActionDamage'or name=='ActionDefeat'then
  local a=actor(cpu['cpu.x'])
  if a.flag>0 and a.flag<128 and a.state&32==0 then
   p.action={kind=name=='ActionDamage'and'projectile-contact'or'body-or-tail-contact',
    before=actionState(),target=a,projectile=shot(r('M3SavedSlot'))}
  end
 elseif name=='ActionBody'and r('M3Native::Player_Statue')~=0 then
  p.action={kind='stone-body',before=actionState(),target=actor(cpu['cpu.x']),
   injury=r('InjuryTimer'),invul=r('GuestInvulTicks')}
 elseif name=='ActionInjury'then
  A.injury={player=actionState(),target=actor(cpu['cpu.x'])}
 elseif name=='ActionTail'then
  A.tail_probes=A.tail_probes or {};A.tail_probes[tostring(r('M3Native::Player_TailAttack'))]=actionState()
 elseif name=='M3DrawWorld'and r('M3Poof')>0 then
  p.action_poof=r('M3Poof')
 end
end
local function actionReturned(p)
 local a=p.action
 if a.kind=='throw'then
  local wanted=C.action=='Fire'and 1 or 2
  local found
  for i=0,1 do local s=shot(i);if s.kind==wanted then found=s;break end end
  assert(found and r('M3Form')==C.target_suit,'Native fresh-B throw creates the actual requested projectile')
  A.throw=A.throw or {before=a.before,after=actionState(),shot=found};A.motion=A.motion or 0
 elseif a.kind=='advance'then
  local s=shot(a.before.slot)
  if s.kind==a.before.kind and(s.x~=a.before.x or s.y~=a.before.y)then
   A.motion=A.motion+1;A.last_motion={before=a.before,after=s,player=actionState()}
  end
 elseif a.kind=='stone-body'then
  local cpu=emu.getState();local carry=(cpu['cpu.ps']or cpu['cpu.p'])&1
  if carry~=0 then
   assert(r('M3Form')==5 and r('InjuryTimer')==a.injury and r('GuestInvulTicks')==a.invul,
    'Actual native stone contact is protected without new injury/invulnerability')
   A.protected={before=a.before,after=actionState(),target_before=a.target,target_after=actor(a.target.slot),carry=true}
  end
 else
  local target=actor(a.target.slot)
  if target.flag==0 or target.state&32~=0 then
   A.contact={kind=a.kind,before=a.before,after=actionState(),target_before=a.target,
    target_after=target,projectile=a.projectile}
  end
 end
end
local function actionTick()
 local s=actionState()
 assert(s.power==C.target_suit and not A.injury,'Action retains its naturally earned suit without injury')
 assert(updates-A.acquired.update<500,'Bounded real suit-action window')
 if(C.action=='Fire'or C.action=='Hammer')and A.throw and(A.motion or 0)>=2 then
  A.activation=A.activation or s
 elseif C.action=='Tanooki'then
  if s.queue>=15 and not A.queue then A.queue=s end
  if s.statue>0 and s.poof==0 then A.stone=A.stone or s end
  if A.stone and A.exit_input and s.statue==0 and s.queue==0 and s.poof==0 then
   assert((A.poof_ticks or 0)==48,'Actual entry and exit poof clocks both completed')
   A.activation=A.activation or s
  end
 elseif C.action=='Raccoon'then
  if s.tail>0 then A.tail=A.tail or s end
  if A.tail and s.tail==0 and A.tail_probes and A.tail_probes['9']and A.tail_probes['12']then A.activation=A.activation or s end
 elseif C.action=='Frog'then
  if s.frog>0 then A.hop=A.hop or s end
  if A.hop and s.x>=A.input.x+4 and A.phase=='observe-action'then A.activation=A.activation or s end
 end
 if A.activation and s.motor-A.activation.motor>=25 and s.growth==0 and s.poof==0 then
  A.after=s;A.complete=true
 end
end
'''


def controller(raw, form='peach3', action='Fire'):
    config = bindings(raw, form, action)
    observer = Acquire.body(targeted=True)
    observer = Acquire.once(observer, 'local function afterMain()', ACTION_OBSERVER+'\nlocal function afterMain()')
    observer = Acquire.once(observer, "  finish(true,'Natural Mushroom/suit, actual effects and25 resumed original steps per checkpoint');return",
        """  A.acquired=A.acquired or actionState()
  actionTick()
  if A.complete then finish(true,'Naturally acquired suit, real native action and25 resumed source steps');return end""")
    # p is constructed after the special nonreturning observers, so insert the
    # action witnesses beside the established native collector entry.
    observer = Acquire.once(observer, " if name=='HandlePowerUpCollision' then",
                            " actionEntry(name,p,cpu)\n if name=='HandlePowerUpCollision' then")
    observer = Acquire.once(observer, 'elseif p.prepare then prepared(p)',
        "elseif p.action_poof then\n   assert(r('M3Poof')==p.action_poof-1,'Actual action poof decrement');A.poof_ticks=(A.poof_ticks or 0)+1\n  elseif p.action then actionReturned(p)\n  elseif p.prepare then prepared(p)")
    observer = Acquire.once(observer, 'requested_stamp=C.target_stamp', 'requested_stamp=C.target_stamp,actions=SMB3_ACTION_STATE')
    navigation = Acquire.Stock.Navigation.policy()
    acquisition = Acquire.POLICY.read_text(encoding='utf-8')
    action_policy = POLICY.read_text(encoding='utf-8')
    text = '\n'.join(('local C='+value(config), "local ROSTER_CONFIG={name='smb3'}",
        'local SMB3_UPGRADE_PROGRESS={}', 'local SMB3_UPGRADE_MODE=C.route',
        'local SMB3_UPGRADE_TARGET=C.target_suit',
        'local SMB3_UPGRADE_BASE=(function()\n'+navigation+'\nend)()',
        'local SMB3_ACTION_ACQUIRE=(function()\n'+acquisition+'\nend)()',
        'local choose=(function()\n'+action_policy+'\nend)()', observer))
    LuaRuntime().compile(text)
    assert not any(word in text for word in ('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState','dofile'))
    return text


def cpu_checks(raw):
    b = dict(authority(), raw=raw)
    m = N.fresh(b)
    N.put(m,SelectedCharacter=17,M3Variant=2,M3Marker=0xb3,NumberofLives=2,
          AreaType=1,AreaNumber=0,LevelNumber=0,PlayerFacingDir=1,OperMode=1,
          OperMode_Task=3,GameEngineSubroutine=8,Player_Y_HighPos=1)
    N.invoke(m,'M3Reset')
    rows=[]
    for form in (2,6):
        q=N.fork(m)
        N.put(q,M3Form=form,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
              Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,SavedJoypadBits=64,FrameCounter=1)
        N.invoke(q,'M3Movement');N.invoke(q,'M3Weapons')
        slot=next(i for i in range(2)if N.get(q,'M3ShotKind',i))
        wanted=1 if form==2 else 2
        assert N.get(q,'M3ShotKind',slot)==wanted
        before=(N.get(q,'M3ShotX',slot),N.get(q,'M3ShotY',slot))
        for tick in range(2,5):
            N.put(q,FrameCounter=tick);N.invoke(q,'M3Movement');N.invoke(q,'M3Weapons')
        after=(N.get(q,'M3ShotX',slot),N.get(q,'M3ShotY',slot))
        assert after!=before
        N.put(q,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,
              Enemy_X_Position=after[0]+4,Enemy_PageLoc=0,Enemy_Y_Position=after[1],M3SavedSlot=slot)
        N.invoke(q,'M3ShotEnemies')
        assert N.get(q,'Enemy_State')&32 and N.get(q,'M3Form')==form
        assert N.get(q,'M3ShotKind',slot)==(0 if form==2 else 2)
        rows.append(dict(form=form,kind=wanted,before=before,after=after,native_Goomba_defeated=True,
                         projectile_after_contact=N.get(q,'M3ShotKind',slot)))
    q=N.fork(m)
    N.put(q,M3Form=5,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
          Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,SavedJoypadBits=68,FrameCounter=1)
    N.invoke(q,'M3Movement')
    assert N.get(q,'M3Poof')==24 and N.get(q,'M3Native::Player_QueueSuit')==32
    for _ in range(24):N.invoke(q,'M3DrawWorld')
    N.put(q,FrameCounter=2);N.invoke(q,'M3Movement')
    stone=N.get(q,'M3Native::Player_Statue');assert stone>0 and N.get(q,'M3Poof')==0
    N.put(q,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,
          Enemy_X_Position=118,Enemy_PageLoc=0,Enemy_Y_Position=184,
          Player_Y_Speed=1,InjuryTimer=0,GuestInvulTicks=0)
    result=N.invoke(q,'M3BodyDispatch',x=0,p=48)
    assert result['P']&1 and N.get(q,'M3Form')==5 and N.get(q,'Enemy_State')&32
    assert N.get(q,'InjuryTimer')==N.get(q,'GuestInvulTicks')==0
    N.put(q,SavedJoypadBits=0,FrameCounter=3);N.invoke(q,'M3Movement')
    assert N.get(q,'M3Native::Player_Statue')==0 and N.get(q,'M3Poof')==24
    for _ in range(24):N.invoke(q,'M3DrawWorld')
    assert N.get(q,'M3Poof')==0 and N.get(q,'M3Form')==5
    rows.append(dict(form=5,statue=stone,entry_poof_returns=24,exit_poof_returns=24,
                     protected_carry=True,native_Goomba_defeated=True,new_invulnerability=0))
    q=N.fork(m)
    N.put(q,M3Form=3,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
          Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,SavedJoypadBits=64)
    phases=[]
    for tick in range(1,26):
        N.put(q,FrameCounter=tick);N.invoke(q,'M3Movement');N.invoke(q,'M3Weapons')
        phases.append(N.get(q,'M3Native::Player_TailAttack'))
    assert max(phases)>0 and 9 in phases and 12 in phases and phases[-1]==0
    rows.append(dict(form=3,tail_phases=phases))
    q=N.fork(m)
    N.put(q,M3Form=4,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
          Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,SavedJoypadBits=1)
    hops=[]
    for tick in range(1,14):
        N.put(q,FrameCounter=tick);N.invoke(q,'M3Movement')
        hops.append(dict(counter=N.get(q,'M3Native::Player_FrogHopCnt'),
                         x=N.get(q,'Player_X_Position'),frame=N.get(q,'M3Native::Player_Frame')))
    assert max(p['counter']for p in hops)>0 and hops[-1]['x']>=hops[0]['x']+4
    rows.append(dict(form=4,directional_hop=hops,
                     counter_changes=len({p['counter']for p in hops})))
    return dict(scope='Typed linked CPU action components only; natural Mesen actions remain unqualified',cases=rows,files=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Root only: use existing sequential Mesen slot')
    parser.add_argument('--form',choices=(*FORMS,'both'),default='peach3')
    parser.add_argument('--action',choices=tuple(ACTIONS),action='append')
    args=parser.parse_args()
    raw=ROM.read_bytes();assert H(raw)==PIN
    forms=('toad3','peach3')if args.form=='both'else(args.form,)
    actions=args.action or ('Fire',)
    if not args.run:
        cases=[dict(form=form,action=action,script_SHA256=H(controller(raw,form,action).encode()))
               for form in forms for action in actions]
        print('SMB3 ACTION SOURCE '+json.dumps(dict(passed=True,ROM_SHA256=PIN,cases=cases,
              cpu=cpu_checks(raw),files=0,Mesen=False)),flush=True);return
    from capture_budget import preflight
    from mesen_session_guard_v1 import require_free_workspace
    from nightly_patch_guard_v1 import check
    from run_stdout_mesen_1110 import run
    initial=check(ROM);assert initial['ROM_sha256']==PIN and not initial['matching_patch_files']
    assert {p.name for p in OUT.iterdir()}=={'candidate.nes','controller.lua'}
    assert (OUT/'candidate.nes').read_bytes()==raw
    preflight(OUT/'capture',reserved_files=0);require_free_workspace(R,ROM,allow_interactive=True)
    script=OUT/'controller.lua';previous=script.read_bytes()
    try:
        for form in forms:
            for action in actions:
                script.write_bytes(controller(raw,form,action).encode())
                result=run(script,ROM,OUT/'capture',PIN,180)
                assert not result['images'] and result['outputs_written']==0
                print('SMB3 ACTION '+json.dumps(dict(form=form,action=action,**result),separators=(',',':')),flush=True)
                assert ROM.read_bytes()==raw and check(ROM)==initial
                if not result['passed']:return 1
    finally:
        script.write_bytes(previous);assert ROM.read_bytes()==raw and check(ROM)==initial
    return 0


if __name__=='__main__':
    raise SystemExit(main())
