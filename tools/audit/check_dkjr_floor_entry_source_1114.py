"""Granted current floor/entry cold and ordinary full controller source gate."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
import sys

import compose_dkjr_floor_entry_current_1114 as Current
import replay_dkjr_floor_entry_1114 as Replay

Floor=Current.Floor;F,G=Floor.F,Floor.G
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def run(*,route=False,private_only=False,projection=False,flag_window=False):
    if private_only:
        _,legacy=F.load_inputs();parent=Floor.S.proposal(legacy)[0]
        raw,composition=Floor.proposal(parent);private=raw
        text=Replay.private_controller(raw)
    elif projection:
        import project_dkjr_floor_entry_current_1114 as Project
        parent=Current.Delivered.NIGHTLY.read_bytes()
        raw,private,composition=Project.source_projection(parent,kind=Current.Delivered.KIND)
        text=Replay.current_controller(raw,private=private)
    else:
        parent=Current.Delivered.NIGHTLY.read_bytes();raw,composition=Current.proposal(parent)
        private=Current.private_image(raw);text=Replay.current_controller(raw,private=private)
    pin=sha256(raw).hexdigest();cookie=raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16];labels=Replay.symbols(private)
    opening,seed=H.cold(raw,cookie);body=P.T.payload(raw)
    assert bytes(seed.ram[2][0x900:0xd00])==body[8192:9216]
    assert bytes(seed.ram[2][0x1000:0x1800])==body[9216:]
    assert all(bytes(seed.ram[b][0x1fe0:0x1ff0])==cookie for b in (2,3))
    smc_cells={labels['StoreCell']+off for off in (1,2)}
    shared=labels['CurrentRectReadCell']
    smc_cells.update((shared+1,shared+2))
    # Existing WorldBuild selects its output list by patching only the low
    # byte of the two STA C800,Y operands. These are outside the new spans.
    world_smc=[]
    for name in ('StoreRect','StoreEnd'):
        pc=labels[name];assert body[pc-0xa000:pc-0xa000+3]==bytes.fromhex('9900c8')
        target=pc+1;writers=[0xa000+i for i in range(0x1fde)
            if body[i]==0x8d and int.from_bytes(body[i+1:i+3],'little')==target]
        assert len(writers)==1
        actual=seed.ram[3][target-0xa000];assert actual in (0,0x40,0x80)
        smc_cells.add(target);world_smc.append(dict(operand_PC=target,sole_writer=writers[0],value=actual))
    deltas=[dict(PC=0xa000+i,expected=b,actual=seed.ram[3][i])for i,b in enumerate(body[:0x1fe0])if seed.ram[3][i]!=b]
    assert all(r['PC']in smc_cells for r in deltas),deltas
    print('DKJR_FLOOR_ENTRY_COLD '+json.dumps(dict(passed=True,candidate_SHA256=pin,
        exact_source_readback_before_constructor=True,both_cookies_exact=True,
        post_constructor_only_known_shared_SMC_differences=deltas,opening=opening,
        existing_WorldBuild_output_list_SMC=world_smc,
        controller_Lua_SHA256=sha256(text.encode()).hexdigest(),outputs_written=0),separators=(',',':')),flush=True)
    if not route:return dict(passed=True,composition=composition)
    m=Q.mounted(seed,raw);ticks=0;counts=Counter();floor_pending=None;entry_rows=[];admissions=[];pending_draw=[]
    flag_rows=[];flag_writers=[];flag_start=None;first_flag_abort=None
    body_bytes=body[0xbc74-0xa000:0xbd3d-0xa000]
    body_y_writes=[0xbc74+i for i in range(len(body_bytes)-2)if body_bytes[i:i+3]==bytes.fromhex('990002')]
    assert len(body_y_writes)==1
    def snapshot(memory):
        r=memory.ram[2]
        return dict(Main=ticks,x=N.get(memory,'Player_X_Position')+256*N.get(memory,'Player_PageLoc'),
            y=N.get(memory,'Player_Y_Position'),high=N.get(memory,'Player_Y_HighPos'),
            state=N.get(memory,'Player_State'),source=r[0x6b],prior=r[0x6c],source_y=r[0x210],
            origin=r[0x76],limit=r[0x7b],ready=r[0x8fe],engine=N.get(memory,'GameEngineSubroutine'),
            lives=N.get(memory,'NumberofLives'),area=N.get(memory,'AreaPointer'))
    def token(memory,c):return ((memory[0x100+((c.sp+1)&255)]+256*memory[0x100+((c.sp+2)&255)]+1)&65535,(c.sp+2)&255)
    def bounded(rows,row):
        if len(rows)>=32:del rows[8]
        rows.append(row)
    def flag_state(memory):
        r=memory.ram[2]
        return dict(**snapshot(memory),held=r[0x14],sample=r[0x15],direction=r[0x54],facing=r[0x6d],
            age=r[0x7e],fraction=r[0x7f],acc=int.from_bytes(r[0x82:0x84],'little'),
            impulse=int.from_bytes(r[0x86:0x88],'little'),native_vy=N.get(memory,'Player_Y_Speed'),
            controller_bits=memory.controller_pad,native_held=N.get(memory,'SavedJoypadBits'),
            AB=N.get(memory,'A_B_Buttons'),query_kind=r[0x8db],query=list(r[0x3e:0x42]),
            support=list(r[0x840:0x84c]),walls=list(r[0x880:0x88c]))
    def flag_cells(memory):
        at=W.location(memory.bundle,'MTileAttribute');attrs=raw[at:at+256];cells=[]
        for wx in (3152,3168):
            base=W.address(memory.bundle,'Block_Buffer_2'if wx>>8&1 else'Block_Buffer_1')
            for wy in (176,192,208):
                tile=memory[base+((wy-32)&240)+((wx>>4)&15)]
                cells.append(dict(x=wx,y=wy,tile=tile,attr=attrs[tile]))
        return cells
    def observe(memory,c):
        nonlocal floor_pending,first_flag_abort
        tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if floor_pending==(c.pc,c.sp):floor_pending=None
        if tag==3:
            if c.pc==labels['MeasuredAfterEffects']:
                floor_pending=token(memory,c);counts['service34_calls']+=1
            if floor_pending and c.pc==labels['CarryAccepted']+7:
                counts['qualified_static_floor_admissions']+=1;bounded(admissions,snapshot(memory))
            if c.pc==labels['DkjrNativeSourcePhase']:
                assert memory.ram[2][0x8fe]==2,'Source phase advanced during pending entry'
            if c.pc==labels['MeasuredAnchorReady']and memory.ram[2][0x8fe]==1:
                counts['pending_entry_motor_calls']+=1
                if N.get(memory,'LevelNumber')==1:bounded(entry_rows,snapshot(memory))
            if c.pc==body_y_writes[0]and memory.ram[2][0x8fe]==1:
                assert N.get(memory,'Player_State')==2
                expected=N.get(memory,'Player_Y_Position')+15
                assert c.a in (expected,(expected+8)&255),(snapshot(memory),c.a)
                counts['pending_entry_body_pairs']+=1
                if N.get(memory,'LevelNumber')==1:bounded(pending_draw,dict(**snapshot(memory),OAM_Y=c.a))
            if flag_start is not None and ticks-flag_start<120 and bytes(memory[c.pc:c.pc+3])==bytes.fromhex('8d6bc0'):
                row=dict(PC=c.pc,pending_A=c.a,**flag_state(memory));bounded(flag_writers,row)
                if memory.ram[2][0x6b]==3 and c.a in (1,4,5)and first_flag_abort is None:
                    first_flag_abort=dict(**row,authored_cells=flag_cells(memory))
                    print('DKJR_FIRST_FLAG_ABORT '+json.dumps(first_flag_abort,separators=(',',':')),file=output,flush=True)
    output=sys.stdout
    class FlagWindowComplete(Exception):pass
    def after(memory):
        nonlocal ticks,flag_start
        ticks+=1
        if N.get(memory,'LevelNumber')==0 and snapshot(memory)['x']>=3148:
            if flag_start is None:flag_start=ticks
            if ticks-flag_start<120:bounded(flag_rows,flag_state(memory))
            elif flag_window:raise FlagWindowComplete()
        if ticks%1000==0:print('DKJR_FLOOR_ENTRY_SOURCE_PROGRESS '+json.dumps(snapshot(memory)),file=output,flush=True)
    try:
        with redirect_stdout(io.StringIO()):
            result=P.B.route(m,raw,12000,controller_text=text,observe_extra=observe,after_frame=after)
    except FlagWindowComplete:
        report=dict(diagnostic_window_complete=True,full_route_passed=False,candidate_SHA256=pin,
            controller_Lua_SHA256=sha256(text.encode()).hexdigest(),Main=ticks,
            first_flag_abort=first_flag_abort,flag_rows=flag_rows[:8]+flag_rows[-8:],
            flag_writers=flag_writers[:4]+flag_writers[-4:],cells=flag_cells(m),
            source_projection=projection,inputs_and_game_bytes_unchanged=True,outputs_written=0)
        print('DKJR_FLAG_WINDOW '+json.dumps(report,separators=(',',':')),file=output,flush=True)
        return report
    receipt=result['receipt']
    summary={key:receipt.get(key)for key in ('passed','reason','terminal','flag','castle',
        'grounded_12_return_count','actual_12_returns','first_grounded_12_return','last_grounded_12_return')}
    summary.update(receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        final_helper_birth=receipt.get('births',{}).get('3040'),final_helper_carry=receipt.get('carries',{}).get('3040'),
        final_events=receipt.get('events',[])[-10:])
    report=dict(passed=result['passed'],candidate_SHA256=pin,private_SHA256=Floor.PIN,
        controller_Lua_SHA256=sha256(text.encode()).hexdigest(),logical_updates=result['logical_updates'],
        result=summary,counts=dict(counts),floor_admissions=admissions[:2]+admissions[-2:],pending_entry_rows=entry_rows[:4]+entry_rows[-4:],
        pending_entry_render=pending_draw[:4]+pending_draw[-4:],
        flag_first_abort=first_flag_abort,flag_rows=flag_rows[:8]+flag_rows[-8:],flag_writers=flag_writers[:4]+flag_writers[-4:],
        all_current32B_and176_preserved=not private_only,
        no_actor_position_state_or_input_seeds=True,outputs_written=0,physical_cadence_claim=False,native_claim=False)
    print('DKJR_FLOOR_ENTRY_SOURCE_ROUTE '+json.dumps(report,separators=(',',':')),flush=True)
    assert result['passed'],(summary['receipt_SHA256'],summary['reason'],summary['terminal'])
    assert receipt['grounded_12_return_count']>=25 and pending_draw
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--route',action='store_true');p.add_argument('--private',action='store_true')
    p.add_argument('--qualified-projection',action='store_true');p.add_argument('--flag-window',action='store_true')
    a=p.parse_args();run(route=a.route,private_only=a.private,projection=a.qualified_projection,flag_window=a.flag_window)
