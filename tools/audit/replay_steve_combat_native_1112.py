"""Bounded physical stage regression of the connected Steve combat candidate."""
import json
import argparse
import check_steve_throw_controls_live_1111 as Controls
import deliver_steve_lift_art_1111 as Previous


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--throw', action='store_true')
    args = parser.parse_args()
    output = Controls.H.ROOT / 'build/steve-combat-native-1112'
    raw = Previous.NIGHTLY.read_bytes()
    assert Previous.check(Previous.NIGHTLY)['ROM_sha256'] == Previous.PIN
    image, info = Controls.proposal(raw, combat_active=True)
    pin = Controls.C.digest(image)
    assert pin == '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
    groups = [tuple(map(int, group.split(':'))) for group in Previous.STAGE_GROUPS.split()]
    source = Previous.Replay.controller(groups, info, laser=True, laser_stage=not args.throw)
    if args.throw:
        fields = info['throw_control_fields']
        tail = '''
local throwStep,throwStamp,throwCount=0,-1,0
local launched,returned,sawRecovery,sawRobot=false,false,false,false
local function playThrow()
  assert(active() and read(0x75f)==2,'Throw keeps player alive in stage')
  if companionUpdates==throwStamp then return end
  throwStamp=companionUpdates
  throwCount=throwCount+1
  local lift,selector=work(2,LIFT),work(2,SELECTOR)
  local action=work(2,ACTION)
  sawRecovery=sawRecovery or action~=0
  if selector&128~=0 then launched=true end
  if launched then
    for at=0,252,4 do
      local tile=emu.read(at+1,emu.memType.nesSpriteRam)
      if emu.read(at,emu.memType.nesSpriteRam)<240 and (tile==0x6f or tile==0x73) then sawRobot=true end
    end
  end
  if throwStep==0 then
    pad=4
    if throwCount>=3 then throwStep=1;throwCount=0 end
  elseif throwStep==1 then
    pad=132
    assert(throwCount<110,'Robot reaches grounded lift latch')
    if lift==5 and work(2,DELAY)==255 then throwStep=2;throwCount=0 end
  elseif throwStep==2 then
    pad=196
    if throwCount>=3 then throwStep=3;throwCount=0 end
  else
    pad=0
    assert(throwCount<500,'Thrown robot returns')
    if launched and selector&128==0 and action==0 then
      assert(sawRecovery and sawRobot,'Recovery and thrown body reach physical gameplay')
      finish(true,'Earned Laserbot, threw from grounded latch, saw recovery and robot OAM, returned alive')
    end
  end
end
'''
        for token, name in {'LIFT':'SteveLiftState', 'SELECTOR':'SteveThrowSelector',
                            'ACTION':'SteveThrowPlayerAction', 'DELAY':'SteveLiftBotDelay'}.items():
            tail = tail.replace(token, str(fields[name]))
        marker = 'local function playCompanionRoute()'
        source = source.replace(marker, tail+'\n'+marker+"\n  if phase=='throw' then playThrow();return end")
        old = "finish(true,string.format('Earned Laserbot, body pairs %d, beam pairs %d',bodyPairs,shotPairs))"
        assert source.count(old) == 1
        source = source.replace(old, "phase='throw'")
        source = source.replace("assert(frame<=4200,'Bounded physical Steve replay')",
                                "assert(frame<=6500,'Bounded physical Steve replay')")
    output.mkdir(exist_ok=True)
    rom, script = output/'candidate.nes', output/'controller.lua'
    rom.write_bytes(image)
    script.write_text(source, encoding='utf-8')
    punch = info['punch']['symbols']
    environment = {'SMB_STEVE_COOKIE': info['cookie'].hex(),
                   'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
                   'SMB_STEVE_DRAW': str(punch['SteveDrawEmit'])}
    result = Previous.Replay.run(script, rom, output/'capture', pin, 120, extra_env=environment)
    # Images remain in memory; retain only the compact verification result.
    print(json.dumps({key:value for key,value in result.items() if key != 'images'}), flush=True)
    assert result['passed'], result['receipt']


if __name__ == '__main__':
    main()
