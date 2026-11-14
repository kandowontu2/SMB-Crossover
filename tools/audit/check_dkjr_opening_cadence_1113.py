"""Exercise cadence factory callbacks/ordinary phases in untimed CPU models."""
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json

import replay_dkjr_opening_cadence_1113 as F
import check_dkjr_direct_platform_1113 as Gate
from check_ff_stdout_controller_source_1110 import LuaRuntime


def original(text):
    cpu,_=F.Donor.active();m=cpu.memory
    lua=LuaRuntime(unpack_returned_tuples=True);events={};callbacks={};reads={};receipt=None;exit_code=None;pad=0
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesPrgRom=1,nesWorkRam=2))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0,read=1))
    emu.read=lambda at,kind=0:m[at]if kind==0 else F.Donor.donor()[16+at]
    emu.convertAddress=lambda pc:lua.table_from(dict(memType=1,address=pc&16383))
    emu.getState=lambda:lua.table_from({f'cpu.{name}':getattr(cpu,name)for name in('pc','sp','a','x','y')})
    def inputs(keys,port):
        nonlocal pad
        assert port==0;pad=sum(bit for name,bit in(('right',1),('left',2),('down',4),('start',16),('select',32))if keys[name])
    emu.setInput=inputs
    def output(line):
        nonlocal receipt
        if line.startswith('SMB_NATIVE_RECEIPT '):receipt=json.loads(line[19:])
    def stop(code):
        nonlocal exit_code
        exit_code=code
    emu.stop=stop;emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    def callback(fn,kind,lo,hi=None):
        for pc in range(lo,(hi if hi is not None else lo)+1):(callbacks if kind==0 else reads).setdefault(pc,[]).append(fn)
    emu.addMemoryCallback=callback
    Base=type(m)
    class ReadHooks(Base):
        def __getitem__(self,at):
            if isinstance(at,int):
                for fn in reads.get(at,()):fn()
            return super().__getitem__(at)
    m.__class__=ReadHooks
    lua.globals().emu=emu;lua.globals().print=output;lua.globals().CPU_CONTROLLER_OPENING=True;lua.execute(text)
    def observe(c):
        for fn in callbacks.get(c.pc,()):fn()
    for epoch in range(500):
        events[0]();F.Donor.frame(cpu,pad,observe);events[1]()
        if exit_code is not None:break
    assert exit_code==0 and receipt and receipt['passed'],(exit_code,receipt)
    assert len(receipt['rows'])==3 and all(r['controller_reads']>0 for r in receipt['rows'])
    return dict(scheduled_NMI_epochs=epoch+1,receipt=receipt)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--donor-ground',action='store_true');args=ap.parse_args()
    parent,raw=F.T.load_inputs();text=(F.donor_ground_controller if args.donor_ground else F.controller)(raw);donor_text=F.original_controller(F.Donor.donor())
    Q,P,H=Gate.Q,Gate.P,Gate.H;e73=F.T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
    for _ in range(160):
        if P.B.state(m)['y']==176 and m.ram[2][0x6b]==1:break
        Q.frame(m,0)
    with redirect_stdout(io.StringIO()):current=P.B.route(m,raw,500,controller_text=text)
    assert current['passed'] and len(current['receipt']['rows'])==3,current
    donor=original(donor_text)
    print('DKJR_OPENING_CADENCE_CPU '+json.dumps(dict(
        Lua_SHA256=dict(current=sha256(text.encode()).hexdigest(),original=sha256(donor_text.encode()).hexdigest()),
        current=current,original=donor,outputs_written=0,acknowledged_donor_ground=args.donor_ground,
        scope='Factory callback/phase tests only. Current harness does not dispatch CPU read hooks; original does. Untimed scheduled model epochs are not native physical frames.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
