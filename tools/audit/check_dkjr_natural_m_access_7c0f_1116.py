"""One actual7c0f ordinary M access run and compact first-writer causality."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import replay_dkjr_natural_m_access_7c0f_1116 as F
import check_dkjr_carry_camera_route_1116 as Route
from check_ff_stdout_controller_source_1110 import LuaRuntime

H=lambda b:sha256(b).hexdigest()


def main():
    raw=F.ROM.read_bytes();binding=F.bindings(raw);text=F.controller(raw)
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    # Exact whole image, packet, cookie and leaf preimages were checked before
    # cold. The supported cold path authenticates every admitted page before
    # the real original constructor. No private fixture inverse or mount.
    opening,m=Route.cold(raw)
    assert H(m.bundle['raw'])==F.PIN and opening['opening_updates']==0
    assert all(bytes(m.ram[b][0x1fe0:0x1ff0]).hex()==F.COOKIE for b in(2,3))
    packet=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in F.PAGES)
    writes={0xa000+i for i in range(8158)if packet[i:i+3]==bytes.fromhex('8d6bc0')}
    counts=Counter();first_stop=None;first5=None;tick=0
    out=__import__('sys').stdout
    def snapshot(memory,c):
        return dict(Route.B.state(memory),tick=tick,PC=c.pc,SP=c.sp,A=c.a,P=c.p,
            source=memory.ram[2][0x6b],prior=memory.ram[2][0x6c],
            source_x=memory.ram[2][0x213],source_y=memory.ram[2][0x210],
            facing=memory.ram[2][0x6d],held=memory.ram[2][0x14],sample=memory.ram[2][0x15],
            origin=memory.ram[2][0x76],limit=memory.ram[2][0x7b],
            source_body=list(memory.ram[2][0x5fc:0x600]))
    def observe(memory,c):
        nonlocal first_stop,first5
        if c.pc not in writes:return
        if memory.rawtags[1]!=3:return
        before=memory.ram[2][0x6b];counts[f'{before}->{c.a}']+=1
        if before==3 and c.a==4 and first_stop is None:first_stop=snapshot(memory,c)
        if c.a==5 and first5 is None:first5=snapshot(memory,c)
    def after(memory):
        nonlocal tick
        tick+=1
        if tick%250==0:
            print('DKJR_M_ACCESS_PROGRESS '+json.dumps(dict(tick=tick,**Route.B.state(memory)),separators=(',',':')),file=out,flush=True)
    print('DKJR_M_ACCESS_BINDING '+json.dumps(dict(ROM=H(raw),factory_SHA256=H(Path(F.__file__).read_bytes()),
        Lua_SHA256=H(text.encode()),packet=H(packet),cookie=F.COOKIE,opening=opening),separators=(',',':')),flush=True)
    with redirect_stdout(io.StringIO()):
        result=Route.B.route(m,raw,1200,controller_text=text,observe_extra=observe,after_frame=after)
    receipt=result.get('receipt')or{}
    assert result['stopped'],'Controller receipt must precede harness bound'
    report=dict(passed=result['passed'],diagnostic_complete=True,actual_CPU_ROM_SHA256=H(raw),
        factory_SHA256=H(Path(F.__file__).read_bytes()),checker_SHA256=H(Path(__file__).read_bytes()),
        Lua_SHA256=H(text.encode()),logical_updates=result['logical_updates'],terminal=result['final'],
        receipt=receipt,first_original_rising_to_fall_writer=first_stop,first_source5_writer=first5,
        source_phase_writes=dict(counts),actual_original_ownership=True,private336_helper_or_head_bridge=False,
        ordinary_inputs_only=True,gameplay_outcome_seeds=False,modified_ROM=False,native_Mesen=False,outputs=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_M_ACCESS '+encoded,flush=True)
    print('DKJR_M_ACCESS_SHA256 '+H(encoded.encode()),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
