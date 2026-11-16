"""Execute new6d7 probe registration and all existing observer-only mocks."""
from collections import Counter
import json
import replay_dkjr_carry_camera_probe_1116 as F
import check_dkjr_fourth_first_loss_registration_v2_1115 as Old

def runtime(raw):
    lua=F.Frozen.V1.LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ROM_PIN=F.C.CANDIDATE;lua.execute(Old.MOCK)
    for at in range(534485-16,534500-16+1):lua.globals().host.rom[at]=raw[at+16]
    return lua

if __name__=='__main__':
    parent=F.C.Bowser.ROM.read_bytes();raw,_=F.C.proposal(parent);text,q=F.controller(raw)
    lua=runtime(raw);lua.execute(text);h=lua.globals().host
    expected=Counter({'grounded1-2 motor entry':1,'first-loss actual944position':1,'first-loss nextD65Eentry':1,
        'first-loss support entry':1,'first-loss wall entry':1,'first-loss plane entry':1,
        'first-loss source4writer':len(q['state_writers_new']),'first-loss originwriter':len(q['origin_writers_exact']),
        'first-loss nativeXwrite':1,'main':1,'birth':1,'gap constructor':1,'gap constructor return':1,
        'gap top ingress':1,'gap top reject':3,'gap top append':1,'original gap landing':1,'carry':1,'injury':1})
    assert Old.labels(lua)==expected and len(h.events)==2 and lua.globals().guarded is None
    count=len(h.callbacks)
    for r in list(h.callbacks.values()):
        if r['kind']==1:lua.execute(f'host.exec({r["first"]},220,0)')
        else:r['fn'](r['first'],0)
    h.events[1]['fn']();h.events[2]['fn']()
    assert h.status is None and len(h.prints)==0 and len(h.callbacks)==count
    pair=runtime(raw);pair.execute(text+Old.EXPOSE);pair.execute('host.armObserver()')
    reference=F.C.reference(parent);config,_=F.Frozen.V1.bindings(reference)
    for name in ('support','wall','plane'):
        pc={'support':0xb065,'wall':0xb061,'plane':0xb5c8}[name]
        for i,v in enumerate(config[name]):pair.globals().host.mem[pc+i]=v
        pair.execute(f'host.stack(0x9afa,220);host.exec({pc},220,139)')
        row=pair.globals().host.observerPair(name);assert row is not None and row['returned'] is None
        pair.execute('host.exec(0x9afb,222);host.exec(0x9afa,223)');assert row['returned'] is None
        pair.execute('host.exec(0x9afa,222,1)');assert row['returned']['pc']==0x9afa and row['returned']['sp']==222
    assert pair.globals().host.status is None and len(pair.globals().host.prints)==0
    result=dict(passed=True,ROM_SHA256=F.C.CANDIDATE,Lua_SHA256=q['Lua_SHA256'],
        static_callbacks=count,events=2,all_inactive_callbacks_and_events_executed=True,
        dynamic_matching_pairs=3,wrong_PC_SP_rejected=True,metadata_only_original_v2_restoration=True,
        scope='Executed Lua registration/observer mocks only; no game CPU/native',outputs=0)
    encoded=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+encoded,flush=True);print('RECEIPT_SHA256 '+F.C.H(encoded.encode()),flush=True)
