"""Strict769 full route with an ordinary immediate third-riser takeoff."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE_LUA='6c6aac8a3d0fdfe334beebcf62b4514014e45d9e044f43926b3ee38e261c8d73'
LUA_PIN='bfa40d77d1e0f7d6b45621589e9e49a2b24ef49fbb702011691de199fa25524f'
ACTIVE_LUA_PIN='78215151aee3a4bb4309c26b31d18cf50dae9b95a9fd9a2772e7e45b4d8a729d'
ACTIVE_TRACE_LUA_PIN='52792e0ce5141270c96ec7a40491f29ee9384787705d28dfbe00f34295538963'


def controller(raw):
    assert sha256(raw).hexdigest()==T.PIN
    text=T.controller(raw,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    assert sha256(text.encode()).hexdigest()==BASE_LUA
    # The genuine Main7499 fork reaches2944 while walking. A neutral delay
    # projects it back to2942; a premature2939 jump also meets the side lip.
    # Keep the existing original A8/rearm47/retry/landing assertions intact.
    text=T.P.once(text,'{2939,2944,2941},','{2944,2944,2944},')
    assert sha256(text.encode()).hexdigest()==LUA_PIN
    LuaRuntime().compile(text)
    return text


def active_controller(raw):
    """Require anchor2944 in the executed fast path; no neutral delay."""
    assert sha256(raw).hexdigest()==T.PIN
    text=T.controller(raw,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    assert sha256(text.encode()).hexdigest()==BASE_LUA
    text=T.P.once(text,
        'if (fast or finalRiser==1) and player>=takeoff-2',
        'if ((fast and finalRiser~=3)or finalRiser==1) and player>=takeoff-2')
    assert sha256(text.encode()).hexdigest()==ACTIVE_LUA_PIN
    LuaRuntime().compile(text)
    return text


def active_trace_controller(raw):
    """Same active inputs plus the frozen bounded991 causal observer."""
    import replay_dkjr_final_stair_trace_1113 as Trace
    text=Trace.controller(raw)
    assert sha256(text.encode()).hexdigest()=='99119500edddae146c71a8c9986c37f68cce27e69a0e7399426596c2e1679f6d'
    text=T.P.once(text,
        'if (fast or finalRiser==1) and player>=takeoff-2',
        'if ((fast and finalRiser~=3)or finalRiser==1) and player>=takeoff-2')
    assert sha256(text.encode()).hexdigest()==ACTIVE_TRACE_LUA_PIN
    LuaRuntime().compile(text)
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--route',action='store_true')
    ap.add_argument('--active',action='store_true')
    ap.add_argument('--trace',action='store_true',help='Use active controls with the frozen bounded causal observer.')
    a=ap.parse_args()
    assert not a.trace or a.active
    parent,candidate=T.load_inputs()
    text=active_trace_controller(candidate)if a.trace else active_controller(candidate)if a.active else controller(candidate)
    row=dict(candidate_SHA256=T.PIN,base_controller_SHA256=BASE_LUA,
        Lua_SHA256=sha256(text.encode()).hexdigest(),Lua_compiled=True,
        proposal='active-fast-fallback'if a.active else'inactive-table-only',
        bounded_causal_observer=a.trace,
        third_riser_takeoffs=[2944,2944,2944]if not a.active else[2944],ordinary_inputs_only=True,
        source_physics_and_native_geometry_unchanged=True,outputs_written=0)
    if a.route:
        Q,P,H=Gate.Q,Gate.P,Gate.H
        e73=T.Old.reverse(parent)
        _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
        m=Q.mounted(seed,candidate);updates=0;output=sys.stdout
        def after(mem):
            nonlocal updates
            updates+=1
            if updates%1500==0:
                print('DKJR_FINAL_TAKEOFF_PROGRESS '+json.dumps(dict(Main=updates,
                    final=P.B.state(mem)),separators=(',',':')),file=output,flush=True)
        with redirect_stdout(io.StringIO()):
            result=P.B.route(m,candidate,12000,controller_text=text,after_frame=after)
        receipt=result.get('receipt')or{}
        row.update(passed=result['passed'],logical_updates=result['logical_updates'],
            final=result['final'],reason=receipt.get('reason'),
            receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            crossings=receipt.get('crossings'),last_events=receipt.get('events',[])[-20:],
            birth_lefts=sorted(receipt.get('births',{})),
            endpoint='Existing active falling1-2 endpoint; not25 grounded updates.',
            physical_cadence_claim=False)
    print('DKJR_FINAL_TAKEOFF '+json.dumps(row,separators=(',',':')),flush=True)
    if a.route:assert row['passed'],row


if __name__=='__main__':main()
