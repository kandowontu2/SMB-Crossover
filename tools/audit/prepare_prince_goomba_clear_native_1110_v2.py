"""Stage the same Prince controls with separate camera and ledge budgets."""

import argparse
import csv
import json
from pathlib import Path
import sys

from check_prince_goomba_recovery_1110 import Route
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, Current = Route.R, Route.Current
V1 = R/'build/prince-goomba-clear-native-1110'
EARLIER = Route.ROOT/'native/capture'
PINS = {
    V1/'ready.json':'609e91b782fa5c5b71b18474d19b1a983f6914f53df514b798db316632169020',
    V1/'controller.lua':'db4ae5bd510a3eb3d74a3d35814f56310e603898827cd5501d06752b592345b0',
    V1/'capture/binding.json':'674551973d49d99d9c393fc2eb479ec4e81843e8aba06a4ba28d38d8d35d3e56',
    V1/'capture/third-goombas.json':'ba82a7d21b6cdf9db856a37e965ec3ffeb228ce9894c4e49ab1cd6b30811dad9',
    V1/'capture/full11.json':'6d779934e09f78937e010f2953e16b2ae31a44b2ce3ff19d41b73e6f4702962e',
    V1/'capture/full11-route.csv':'4124a2bacdb3f8f9b68d3c7c57b35b65077c2244ea2d7602b3196187f122d529',
    V1/'capture/source-phases.csv':'1124af375aeccaad89578e89cd291ea30585fbe60f705dc842a2f1dc2aff5332',
    EARLIER/'source-phases.csv':'003e1d3da59b43f1b5e80e7c2bf964896eab654b7d4b11712020091d74d328dc',
    EARLIER/'third-pipe.json':'9ec9472d480b21c6fd421b09f90b7f52033936fe688e5d8f6c36c73141a1cd7b',
    R/'build/prince-goomba-recovery-1110/handoff.json':'28651e37f3f3927cd4d57a2d9d2b47cffa143fbd46ae5c51bb1cd6e8e9137cd8',
}


FIELDS = ('wrappers','world_x','native_y','source_action','source_frame','source_mode','source_facing','pad','physical_foot')
OLD_LEDGE = "  change('third-cam-ledge',{'up'})"
NEW_LEDGE = "  c.ledge_Main=admitted\n" + OLD_LEDGE
OLD_LIMIT = " if admitted-c.Main>600 or admitted-route.changed>150 then\n  routeFail('Original camera and Up handoff exceeded its finite bound')\n end"
NEW_LIMIT = """ if not c.ledge_Main and admitted-c.Main>600 then
  routeFail('Original camera travel exceeded its finite bound')
 end
 if admitted-route.changed>150 then
  routeFail('Original camera, Up or climb phase exceeded its finite bound')
 end"""


def rows(path,start,end):
    with path.open(newline='') as file:
        return [{k:int(row[k]) for k in FIELDS} for row in csv.DictReader(file)
                if row['part']=='full11' and row['event']=='original-advance-return'
                and start<=int(row['wrappers'])<=end]


def evidence():
    ready,bound,group,full,earlier=(Current.read(p) for p in (V1/'ready.json',V1/'capture/binding.json',
        V1/'capture/third-goombas.json',V1/'capture/full11.json',EARLIER/'third-pipe.json'))
    assert ready['ROM_sha256']==bound['ROM_sha256']==group['ROM_sha256']==full['ROM_sha256']==earlier['ROM_sha256']==Route.PIN
    assert bound['ready_sha256']==PINS[V1/'ready.json'] and bound['exit_code']!=0 and earlier['passed']
    assert not ready['emulated_writes'] and not group['passed'] and not full['passed']
    assert full['reason']=="Original camera and Up handoff exceeded its finite bound"
    assert full['HP']==5 and full['initial_lives']==full['final_lives']==2
    c=group['camera_route']
    nudge,settle,ledge=c['events'][-3:]
    assert [r['to'] for r in (nudge,settle,ledge)]==['third-cam-nudge','third-cam-settle','third-cam-ledge']
    assert [r['player']['world_x'] for r in (nudge,settle,ledge)]==[699,715,705]
    assert [r['right'] for r in (nudge,settle,ledge)]==[809,814,819]
    age,up=full['admitted']-c['Main'],full['admitted']-ledge['Main']
    assert (c['Main'],ledge['Main'],full['admitted'],age,up)==(969,1537,1570,601,33)
    live=rows(V1/'capture/source-phases.csv',1541,1569)
    completed=rows(EARLIER/'source-phases.csv',1081,1137)
    assert len(live)==8 and [r['source_frame'] for r in live]==list(range(67,75))
    assert live==[dict(r,wrappers=r['wrappers']+460) for r in completed[:len(live)]]
    hang=completed[-1]
    assert (hang['wrappers'],hang['world_x'],hang['source_action'],hang['source_frame'],hang['source_mode'],hang['pad'])==(1137,713,24,91,2,8)
    assert (group['terminal']['source_action'],group['terminal']['source_frame'],group['terminal']['source_mode'])==(24,74,1)
    assert group['group']['begin']['camera_right']==819 and len(group['group']['births'])==2
    cpu=Current.read(R/'build/prince-goomba-recovery-1110/handoff.json')
    positive,=[r for r in cpu['results'] if r['terminal']=='cleared' and r['nudge']==713]
    old_entry,=[r['row'] for r in positive['events'] if r['transition']=='settle to ledge']
    assert (old_entry['x'],old_entry['source_x'],old_entry['action'],old_entry['frame'],old_entry['mode'],old_entry['phase'])==(705,713,47,15,0,1)
    assert (ledge['player']['world_x'],ledge['player']['source_x'],ledge['player']['source_action'],
            ledge['player']['source_frame'],ledge['player']['source_mode'],ledge['player']['phase']&3)==(705,713,47,15,0,1)
    assert positive['end']['x']==891 and positive['end']['hp']==5 and positive['end']['lives']==2
    return ready,dict(passed=True,ROM_SHA256=Route.PIN,controller_only=True,emulated_writes=False,
                      native_pending=True,failed_total_Main=age,failed_Up_Main=up,
                      exact_native_Up_prefix=live,earlier_native_hang=hang,
                      earlier_native_continuation=completed[len(live):],
                      projected_hang_Main=hang['wrappers']+460,
                      grounded_nudge=nudge,grounded_settle=settle,actual_Up_entry=ledge,
                      scope='V1 and the completed native ledge matched eight donor advances. '
                            'The former ran out of its shared camera budget while Up was still progressing. '
                            'The successor gives the unchanged Up and climb inputs their existing per-phase bounds.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    for path,pin in PINS.items():
        assert sha(path)==pin,path
    assert sha(Route.ROM)==Route.PIN
    ready,receipt=evidence()
    bindings(ready['bindings'])
    prior=(V1/'controller.lua').read_text(encoding='utf-8')
    source=once(once(prior,OLD_LEDGE,NEW_LEDGE),OLD_LIMIT,NEW_LIMIT)
    assert once(once(source,NEW_LIMIT,OLD_LIMIT),NEW_LEDGE,OLD_LEDGE)==prior
    assert 'emu.write(' not in source
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    refs={Path(__file__),*PINS,*map(Path,ready['bindings'])}
    receipt['bindings']={str(p.resolve()):sha(p) for p in sorted(refs)}
    out.mkdir()
    proof=out/'handoff-evidence.json'
    proof.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    prepare(out/'native',Route.ROM,source,refs|{proof},expected=Route.PIN,timeout=ready['timeout'],
            scope='Exact V1 inputs, real camera and ledge progress budgets separated. '
                  'Keeps native group, third-pipe ground and full-stage witnesses.',
            allow_interactive=ready['allow_interactive'])
    assert sum(p.is_file() for p in out.rglob('*'))==4


if __name__=='__main__':
    main()
