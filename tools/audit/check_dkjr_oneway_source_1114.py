"""Actual cold and ordinary controller source gate of exact one-way proposal."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys
from pathlib import Path

import compose_dkjr_oneway_support_1114 as S

F=S.Replay;G=F.Gate
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',action='store_true')
    ap.add_argument('--current-421',action='store_true');args=ap.parse_args()
    if args.current_421:
        import compose_dkjr_oneway_current_1114 as Current
        current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
        raw,info=Current.proposal(current);controller=Current.controller
    else:
        _,old=F.load_inputs();raw,info=S.proposal(old);controller=S.controller
    pin=sha256(raw).hexdigest();cookie=raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16]
    opening,seed=H.cold(raw,cookie);body=P.T.payload(raw)
    post_cold_code_differences=[dict(PC=0xa000+i,expected=b,actual=seed.ram[3][i])
        for i,b in enumerate(body[:0x1fe0])if seed.ram[3][i]!=b]
    assert bytes(seed.ram[2][0x900:0xd00])==body[8192:9216]
    assert bytes(seed.ram[2][0x1000:0x1800])==body[9216:]
    assert all(bytes(seed.ram[bank][0x1fe0:0x1ff0])==cookie for bank in(2,3))
    print('DKJR_ONEWAY_COLD '+json.dumps(dict(passed=True,candidate_SHA256=pin,
        complete_payload_checked_exact_at_actual_cold_return_by_H_probe=True,both_cookies_exact=True,
        post_cold_source_code_differences=post_cold_code_differences,opening=opening,
        conditional_C900_code_copied_by_actual_cold=True,outputs_written=0),separators=(',',':')),flush=True)
    if not args.route:return
    text=controller(raw);m=Q.mounted(seed,raw);ticks=0;counts=Counter();hits=set();output=sys.stdout
    ranges=((2,0xcbe0,0xcc20),(2,0xcc60,0xcc80),(3,0xbc74,0xbd3d),
        (2,0xd65e,0xd6a7),(3,0xb4b0,0xb54e))
    def watch(memory,cpu):
        tag=memory.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
        if any(tag==bank and lo<=cpu.pc<hi for bank,lo,hi in ranges):hits.add((tag,cpu.pc))
        if(tag,cpu.pc)==(2,0xcc14):counts['guard_calls']+=1
        if(tag,cpu.pc)==(2,0xd69e):
            assert memory.ram[2][0x6b]==3
            counts['source3_velocity_calls']+=1
        if(tag,cpu.pc)==(3,0xa8dd)and memory.ram[2][0x6b]==3:
            acc=int.from_bytes(memory.ram[2][0x82:0x84],'little');imp=int.from_bytes(memory.ram[2][0x86:0x88],'little')
            if(acc-imp)&0x8000:counts['rising_original_landings']+=1
    def after(memory):
        nonlocal ticks
        ticks+=1
        if ticks%1500==0:
            state=P.B.state(memory)
            print('DKJR_ONEWAY_ROUTE_PROGRESS '+json.dumps(dict(Main=ticks,x=state['x'],y=state['y'],lives=state['lives']),separators=(',',':')),file=output,flush=True)
    with redirect_stdout(io.StringIO()):
        result=P.B.route(m,raw,10000,controller_text=text,observe_extra=watch,after_frame=after)
    receipt=result['receipt']
    summary=dict(passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
        receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        reason=receipt.get('reason'),terminal=receipt.get('terminal'),flag=receipt.get('flag'),castle=receipt.get('castle'),
        final_helper_birth=receipt.get('births',{}).get('3040'),final_helper_carry=receipt.get('carries',{}).get('3040'),
        final_events=receipt.get('events',[])[-16:])
    print('DKJR_ONEWAY_SOURCE_ROUTE '+json.dumps(dict(candidate_SHA256=pin,current_421_preserved=args.current_421,
        controller_Lua_SHA256=sha256(text.encode()).hexdigest(),genuine_cold=True,
        controller_result=summary,observed_owned_PC_count=len(hits),query_counts=dict(counts),
        outputs_written=0,physical_cadence_claim=False,
        scope='Complete ordinary-controller scheduled source Main route with actual new cold payload. Native physical replay/ISR/current421 composition remain separate gates.'),separators=(',',':')),flush=True)
    assert result['passed'],result


if __name__=='__main__':main()
