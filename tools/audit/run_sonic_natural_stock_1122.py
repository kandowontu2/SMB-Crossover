"""Replay natural Sonic and Super Sonic item pickups on the Downloads nightly."""

import argparse
from hashlib import sha256
import json

from capture_budget import preflight
from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_sonic_stock_binding_1122 import bindings
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from replay_sonic_hidden_life_f7c9_1116 import BODY, value
from run_stdout_mesen_1110 import R, run
import sonic_natural_stock_policy_1327_1116 as Stock


ROM = Stock.F.ROM
OUT = R / 'build/smb2-flag-native-1113'
TAIL = R / 'tools/playthroughs/sonic_natural_stock_1122.lua'


def controller(raw, form, item):
    config = bindings(raw, form, item)
    hook_names = ('GameLoop', 'SonicHostMain', 'OriginalFrame', 'PlayerHeadCollision',
                  'HandlePowerUpCollision')
    config = dict(config, hooks={name: config['hooks'][name] for name in hook_names})
    text = BODY

    def replace(before, after):
        nonlocal text
        assert text.count(before) == 1, before
        text = text.replace(before, after, 1)

    stock = Stock.text()
    sensors = stock[stock.index('local function read('):stock.index('function P.new(')]
    replace("local P=(function()\nPOLICY_TEXT\nend)();local policy=P.new('life')", sensors)
    replace("'Exact owningf7c9'", "'Exact Downloads ROM'")
    replace("ready=w(0xc119)", "star=r('StarInvincibleTimer'),ready=w(0xc119)")
    replace("local target,credit,lifePending=nil,nil,nil;local lastphase=nil", 'local lastphase=nil')
    replace('collected=collections,credit=credit,sounds=sounds', 'collected=collections,sounds=sounds')
    replace('controller_only=true,original_emergence_state6_allowed=true,no_fully_mature128_claim=true,',
            'controller_only=true,')
    begin = text.index('local function afterMain()')
    end = text.index('local function settle()', begin)
    route = TAIL.read_text(encoding='utf-8')
    config['source_policy_SHA256'] = sha256((sensors + route).encode()).hexdigest()
    text = text[:begin] + route + '''
local function returned(p,c)
 count(p.name..'_returns')
 if p.name=='GameLoop'then main=main+1;afterMain()
 elseif p.name=='OriginalFrame'then
  if c['cpu.ps']&1~=0 then motor=motor+1 else count('OriginalFrame_C0') end
 elseif p.name=='HandlePowerUpCollision'and p.actor and r('Enemy_Flag',p.actor.slot)==0 then
  stockCollected(p)
 end
end
''' + text[end:]
    begin = text.index(' if lifePending and pc==lifePending.pc')
    end = text.index(' while #pending>0', begin)
    text = text[:begin] + text[end:]
    begin = text.index(" if name=='PlayerHeadCollision'then")
    end = text.index(" count(name..'_entries')", begin)
    text = text[:begin] + '''
 if name=='PlayerHeadCollision'then
  local s=state()
  local i=items[index]
  if math.abs(s.x+8-i.x)<=12 and not births[index] then
   bounded(heads,{kind=i.kind,player=s,tile=c['cpu.a']},6)
  end
  return
 end
''' + text[end:]
    replace('a.kind==3 then\n  p.actor=a;', 'a.kind==items[index].kind and births[index] then\n  p.actor=a;')
    replace("assert(frame<8000,'Bounded physical frames')", "assert(frame<10000,'Bounded physical frames')")
    result = 'local SONIC_CONFIG='+value(config)+'\n'+text
    LuaRuntime().compile(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('items', nargs='+', choices=('star', 'flower'))
    parser.add_argument('--form', choices=('sonic', 'super', 'both'), default='both')
    args = parser.parse_args()
    guard = check(ROM)
    raw = ROM.read_bytes()
    target, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {entry.name for entry in OUT.iterdir()} == {target.name, script.name}
    assert target.read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    forms = ('sonic', 'super') if args.form == 'both' else (args.form,)
    try:
        for item in args.items:
            for form in forms:
                script.write_bytes(controller(raw, form, item).encode())
                q = run(script, ROM, OUT / 'capture', guard['ROM_sha256'], 150)
                receipt = q['receipt']
                summary = {k: receipt[k] for k in ('passed', 'reason', 'form', 'physical_frames',
                           'terminal', 'head', 'births', 'collected', 'phase_changes', 'tail')}
                summary.update(item=item, receipt=q['receipt_SHA256'], script=q['script_SHA256'])
                print('SONIC STOCK '+json.dumps(summary, separators=(',', ':')), flush=True)
                assert q['passed'] and q['outputs_written'] == 0 and not q['images']
    finally:
        script.write_bytes(previous)
        assert ROM.read_bytes() == raw and check(ROM) == guard


if __name__ == '__main__':
    main()
