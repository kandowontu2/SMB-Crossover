"""Root's bounded physical qualification of the granted DK Jr. successor."""
import argparse
from hashlib import sha256
import json

import compose_dkjr_helper_retire_1113 as P
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PARENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
CANDIDATE='e73b66263a8e150d3d21b801e5a55be1817f86d09639fc428ab809b2518842d9'
ROOT=P.B.R/'build/metal-flower-native-1112'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata',action='store_true')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--full-frozen',action='store_true',help='Observe the frozen terrain-positive CPU controller on actual native timing.')
    modes.add_argument('--fourth-board',action='store_true',help='Only add ordinary stationary enemy hops at the fourth boarding wait.')
    modes.add_argument('--contact-ride',action='store_true',help='Ride the fourth descent after actual source-supported contact.')
    modes.add_argument('--contact-trace',action='store_true',help='Observe the first fourth-platform contact and its immediate loss.')
    parser.add_argument('--require-pass',action='store_true')
    args=parser.parse_args()
    nightly=P.B.C.ROM
    raw=nightly.read_bytes()
    assert check(nightly)['ROM_sha256']==PARENT==sha256(raw).hexdigest()
    full=args.full_frozen or args.fourth_board or args.contact_ride or args.contact_trace
    if full:
        # Reuse the exact candidate already composed and physically qualified
        # for its first mushroom. No repeated source tree or candidate copy.
        image=(ROOT/'candidate.nes').read_bytes()
        assert sha256(image).hexdigest()==CANDIDATE
        if args.contact_trace:
            import dkjr_contact_observer_1113 as Observer
            text=Observer.controller(image)
            assert sha256(text.encode()).hexdigest()=='d46b3350c2a23dcc9c2ec5dc4323411c9cc4e114305c995b4e8ec2702067d13b'
            before='updates<3338 or updates>3385'
            assert text.count(before)==1
            text=text.replace(before,'updates<3343 or updates>3351')
        elif args.contact_ride:
            text=P.fourth_contact_ride_controller(image)
            assert sha256(text.encode()).hexdigest()=='9f943b1b45c6c829b732b3bc76dc9cf3496e5918fede7816d97d0fd53da93547'
        elif args.fourth_board:
            text=P.fourth_board_guard_controller(image)
            assert sha256(text.encode()).hexdigest()=='4302a3494ef9db39764d53d6cb8f1c4af8a4731207d9a7f5c836406b036ab08e'
        else:
            text=P.controller(image,full=True,ride_fourth=False,fourth_window=True,
                ledge_wait=True,stationary_wait=True,early_stairs=True,
                riser_retreat=True,landing_prep=False)
            assert sha256(text.encode()).hexdigest()=='bd4bacd76d2584eccc1f745c6abd27c48ab39afe04764d6254438da0f4e11464'
    else:
        image,info=P.proposal_current(raw)
        assert sha256(image).hexdigest()==CANDIDATE
        assert info['all_unrelated_bytes_retained'] and info['identical_owned_byte_edits']==708
        text=P.controller(image,full=False)
    LuaRuntime().compile(text)
    summary=dict(parent_SHA256=PARENT,ROM_SHA256=CANDIDATE,
        script_SHA256=sha256(text.encode()).hexdigest(),
        actual_native_run=not args.metadata,scope=('Read-only fourth contact causal trace'if args.contact_trace else 'Fourth contact ride experiment'if args.contact_ride else 'Fourth boarding hop experiment'if args.fourth_board else 'Frozen full-stage controller observation')if full else 'First natural mushroom; full stage is separate')
    if args.metadata:
        print(json.dumps(summary,separators=(',',':')),flush=True)
        return
    rom,script=ROOT/'candidate.nes',ROOT/'controller.lua'
    if not full:
        rom.write_bytes(image)
    script.write_text(text,encoding='utf-8',newline='\n')
    result=run(script,rom,ROOT/'capture',CANDIDATE,240 if full else 180)
    receipt=result['receipt']
    if full:
        receipt={key:value for key,value in receipt.items() if key!='events'}
        receipt['last_events']=result['receipt'].get('events',[])[-12:]
    if args.contact_trace:
        trace=result['receipt'].get('fourth_contact_trace',{})
        names=('Main','event','phase','nativeX','nativeY','nativeDY','sourceY',
            'sourceState','sourcePriorState','fallStart','fallLimit','jumpProgress',
            'carryTop','carryPhase','carryReason','worldKind','worldTop','worldBottom',
            'worldCount','sourceRect','playerBox','playerBoxCtrl','slot944','flag944',
            'top944','box944','DY944','force944','PC','SP','ObjectOffset')
        columns=trace.get('columns',[])
        indices=[columns.index(name)for name in names]
        event_index=columns.index('event')
        events={'source-before','source-after','source-carry-before','state-store',
            'native-position-entry','native-before-Y-store','native-after-Y-before-source',
            'native-position-after','foot-plane-appended','fall-before','fall-after'}
        events.update(('support-before','support-after'))
        rows=[row for row in trace.get('rows',[])if row[event_index]in events]
        receipt={key:result['receipt'].get(key) for key in('passed','reason','terminal','injury')}
        receipt['fourth_contact_trace']=dict(columns=names,rows=[[row[i]for i in indices]for row in rows],
            full_row_count=len(trace.get('rows',[])),dropped=trace.get('dropped'),
            full_trace_SHA256=sha256(json.dumps(trace,sort_keys=True).encode()).hexdigest())
    summary.update(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        receipt=receipt,outputs_written=result['outputs_written'])
    print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(nightly)['ROM_sha256']==PARENT
    if not full or args.require_pass:
        assert result['passed'],'DK Jr. native qualification failed'


if __name__=='__main__':
    main()
