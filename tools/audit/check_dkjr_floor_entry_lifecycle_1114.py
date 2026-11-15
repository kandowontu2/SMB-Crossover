"""Exact-current DK floor/entry cold/header/retire/foreign/death research."""
from hashlib import sha256
import argparse
import json

import compose_dkjr_floor_entry_current_1114 as Current
import check_dkjr_retire_lease_1113 as Lease
import replay_dkjr_floor_entry_1114 as Replay

Floor=Current.Floor;G=Floor.G
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def death(seed):
    m=L.clone(seed);initial_lives=N.get(m,'NumberofLives')
    # Actual native injury ingress is the declared event, not a source5 seed.
    N.invoke(m,'InjurePlayer',a=85,x=0,y=0,p=0x61)
    assert m.ram[2][0x6b]==5 and N.get(m,'NumberofLives')==initial_lives
    first=dict(source=5,engine=N.get(m,'GameEngineSubroutine'),lives=initial_lives)
    end_death=None;life_lost=None;healthy=0
    for epoch in range(900):
        Q.frame(m,0)
        engine=N.get(m,'GameEngineSubroutine');lives=N.get(m,'NumberofLives')
        if engine==6 and end_death is None:end_death=epoch+1
        if lives==initial_lives-1 and life_lost is None:life_lost=epoch+1
        assert lives in (initial_lives,initial_lives-1)
        ready=m.ram[2][0x8fe]
        good=life_lost is not None and engine==8 and ready==2 and m.ram[2][0x6b]!=5
        healthy=healthy+1 if good else 0
        if healthy>=25:break
    assert end_death is not None and life_lost is not None and healthy>=25
    return dict(declared_native_InjurePlayer=True,source5_written_by_actual_ingress=True,
        initial=first,original_terminal_to_engine6_epoch=end_death,one_native_life_loss_epoch=life_lost,
        updates=epoch+1,consecutive_healthy_respawn_updates=healthy,
        final_lives=N.get(m,'NumberofLives'),source_final=m.ram[2][0x6b],
        no_source_or_final_player_state_seeds=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cold-vectors',action='store_true');args=ap.parse_args()
    parent=Current.Delivered.NIGHTLY.read_bytes();raw,info=Current.proposal(parent)
    previous,_,_=Floor.replace_component(raw,reverse=True)
    assert sha256(previous).hexdigest()==Current.PREVIOUS_DELIVERED_PIN
    cookie=raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16];legacy_cookie=previous[P.B.COOKIE_AT:P.B.COOKIE_AT+16]
    _,seed=H.cold(raw,cookie);_,before=H.cold(previous,legacy_cookie)
    details=dict(cookie=cookie.hex())
    result=dict(passed=True,candidate_SHA256=Current.PIN,source_private_SHA256=Floor.PIN,
        exact_current1daca_parent=True,cold=Lease.cold_cases(seed,raw,details),
        headers=Lease.header_guards(seed,details),retire=Lease.retirement_lifecycle(seed,raw,details),
        foreign=H.foreign(before,seed),death=death(seed),outputs_written=0,ROM_written=False,native_claim=False)
    if args.cold_vectors:result['cold_vectors']=Lease.cold_interrupts(seed,raw,details)
    print('DKJR_FLOOR_ENTRY_LIFECYCLE '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
