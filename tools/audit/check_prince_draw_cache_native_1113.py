"""Exact private-cache ROM native cases; root owns the single Mesen queue."""
import argparse
from hashlib import sha256
import json

import prince_draw_cache_1113 as Fix
import check_prince_earned_sword_combat_1113 as Fight
import replay_prince_native_flag_1111 as Stage
import steve_armor_idle_1113 as Idle
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Fix.Packet.R/'build/metal-flower-native-1112'
PINS={
    'combat':'848c67e399f5166ffea335d437a82a565885303a2753e5911e629d559b4aa0b3',
    'stage':'3dbbf79a4881fc9f6bf5c320b692c686231832a17c2899297af5df294000eedb',
    'steve_stage':'3c477bf925743d320a3e51e008f582708297a2b78f0ad19be5112bde6ba8144d',
}


def image():
    public=Fight.P.Base.C.ROM.read_bytes()
    parent=Fix.reverse(public) if sha256(public).hexdigest()==Fix.CANDIDATE else public
    assert sha256(parent).hexdigest()==Fix.PARENT
    candidate,info=Fix.proposal(parent)
    assert sha256(candidate).hexdigest()==Fix.CANDIDATE and Fix.reverse(candidate)==parent
    return candidate,info,parent


def controller(case,candidate,parent):
    assert sha256(candidate).hexdigest()==Fix.CANDIDATE and Fix.reverse(candidate)==parent
    if case=='combat':
        return Fight.controller(candidate)
    if case=='steve_stage':
        # Explicit frozen-parent recipe; the same Steve runtime and native
        # code are exercised against the actual new cartridge by the runner.
        public,info=Idle.proposal(Idle.reverse(parent))
        assert public==parent
        return Idle.Native.controller(public,info,mode='full_stage')
    assert case=='stage'
    cookie=candidate[Fix.Packet.COOKIE:Fix.Packet.COOKIE+16].hex()
    return stage_controller(cookie)


def stage_controller(cookie):
    text=Stage.controller(cookie,0xd746,3115,True)
    before="""    final=s
    finish(true,'Prince cleared authored 1-1 and entered underground 1-2')
    return true"""
    after="""    ending.undergroundStart=ending.undergroundStart or s
    assert(s.hp>0 and s.lives==2,'Living Prince underground entry')
    pad=0
    if frame-ending.undergroundStart.frame>=120 and s.y==176 and support(s) then
      ending.undergroundLanded=s
      final=s
      finish(true,'Prince cleared 1-1 and settled safely in underground 1-2')
    else
      assert(frame-ending.undergroundStart.frame<480,'Neutral underground landing bound')
    end
    return true"""
    assert text.count(before)==1
    return text.replace(before,after)


def validate(case,result):
    assert result['passed'],compact(case,result)
    q=result['receipt']
    assert q['ROM_SHA256']==Fix.CANDIDATE and q['controller_only']
    if case=='combat':
        assert q['reason']=='Naturally earned sword parry/attack and native Goomba defeat'
        combat=q['later_route']['swordCombat']
        assert combat['parried'] and combat['actions']['62'] and combat['actions']['58']
        assert combat['loss'] and combat['call'] and combat['kill']
        assert combat['post']['enemy_state']&32 and combat['post']['score']==1
        assert combat['terminal']['hp']==4 and combat['terminal']['lives']==2 and combat['terminal']['star']==0
    elif case=='stage':
        assert q['reason']=='Prince cleared 1-1 and settled safely in underground 1-2'
        stage=q['later_route']['finish'];terminal=q['terminal']
        assert stage['flag']['native_flag_write']==4 and stage['castle'] and stage['gap']
        assert stage['undergroundLanded']==terminal
        assert (terminal['world'],terminal['level'],terminal['engine'],terminal['lives'],terminal['y'])==(0,1,8,2,176)
        assert terminal['hp']>0 and not q['added_helpers']
    else:
        assert case=='steve_stage'
        assert q['flag'] and q['castle'] and len(q['route_crossings'])==8
        assert q['x']==40 and q['y']==176 and q['hp']>0 and q['lives']==2
    return q


def execute(case,rom,candidate,parent):
    assert rom.read_bytes()==candidate
    text=controller(case,candidate,parent)
    assert PINS[case] and sha256(text.encode()).hexdigest()==PINS[case]
    script=OUT/'controller.lua'
    script.write_text(text,encoding='utf-8',newline='\n')
    if case=='stage':
        result,_=Stage.replay(script,rom,OUT/'capture',Fix.CANDIDATE)
    else:
        result=run(script,rom,OUT/'capture',Fix.CANDIDATE,180,variant=3 if case=='combat' else 0)
    print(json.dumps(dict(event='native_observation',**compact(case,result)),sort_keys=True),flush=True)
    validate(case,result)
    return result


def compact(case,result):
    q=result['receipt']
    return dict(case=case,passed=result['passed'],ROM_SHA256=result['ROM_SHA256'],
        script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
        physical_frames=q['physical_frames'],reason=q['reason'],terminal=q.get('terminal'),
        x=q.get('x'),y=q.get('y'),hp=q.get('hp'),lives=q.get('lives'),
        source_updates=q.get('source_updates'),outputs_written=result['outputs_written'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=tuple(PINS),action='append')
    parser.add_argument('--downloads',action='store_true')
    parser.add_argument('--metadata',action='store_true')
    args=parser.parse_args()
    candidate,info,parent=image()
    rom=Fight.P.Base.C.ROM if args.downloads else OUT/'candidate.nes'
    if args.downloads:assert check(rom)['ROM_sha256']==Fix.CANDIDATE
    for case in args.case or list(PINS):
        if args.metadata:
            text=controller(case,candidate,parent)
            print(json.dumps(dict(case=case,script_SHA256=sha256(text.encode()).hexdigest(),
                native_run=False,outputs=0)),flush=True)
        else:
            execute(case,rom,candidate,parent)
    if args.downloads:assert check(rom)['ROM_sha256']==Fix.CANDIDATE
