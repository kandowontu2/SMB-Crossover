"""Exercise read-only trace callbacks on a genuine32-Main prefix; no files."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import dkjr_contact_observer_1113 as O

P,H=O.P,O.H


def snapshot(m):
    return tuple(bytes(bank)for bank in m.ram),bytes(m[:0x800]),tuple(m.rawtags),bytes(m.vram),tuple(m.chr_latches)


def main():
    raw=(P.B.R/'build/metal-flower-native-1112/candidate.nes').read_bytes()
    assert sha256(raw).hexdigest()==P.PRINCE_PROPOSAL
    observed=O.controller(raw)
    assert sha256(observed.encode()).hexdigest()=='d46b3350c2a23dcc9c2ec5dc4323411c9cc4e114305c995b4e8ec2702067d13b'
    plain=P.fourth_contact_ride_controller(raw)
    # Only the observation window and prefix stop differ in this smoke check.
    # The native factory retains its exact3338..3385 window and no such stop.
    observed=P.once(observed,'updates<3338 or updates>3385','updates<0 or updates>40')
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    outcomes=[];memories=[]
    for text in(plain,observed):
        text=P.once(text,'if playing then',
            "if playing and updates>=32 then finish(true,'read-only-observer-prefix');return end\n if playing then")
        m=H.L.clone(seed)
        with redirect_stdout(io.StringIO()):result=P.B.route(m,raw,80,controller_text=text)
        assert result['passed']and result['receipt']['reason']=='read-only-observer-prefix'
        outcomes.append(result);memories.append(snapshot(m))
    assert memories[0]==memories[1]
    trace=outcomes[1]['receipt']['fourth_contact_trace']
    assert trace['rows']and all(len(row)==len(trace['columns'])for row in trace['rows'])
    assert not trace['dropped']
    assert outcomes[0]['final']==outcomes[1]['final']
    print(json.dumps(dict(passed=True,ROM_SHA256=P.PRINCE_PROPOSAL,
        native_observer_controller_SHA256=sha256(O.controller(raw).encode()).hexdigest(),
        validation_window_Main=[0,40],prefix_Main_updates=32,trace_rows=len(trace['rows']),
        complete_WRAM_native_RAM_maps_VRAM_CHR_equal=True,controller_policy_unchanged=True,
        final=outcomes[1]['final'],output_files=0,
        scope='Model runtime smoke of the observer on a genuine menu/stage prefix. Not the native3338..3385 contact result or a full-stage pass.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
