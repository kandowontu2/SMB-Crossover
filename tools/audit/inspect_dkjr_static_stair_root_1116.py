"""Read-only first static-stair source/native handoff after a natural prefix."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import diagnose_dkjr_ledge_controls_root_1116 as D
import replay_dkjr_clear_stair_head_root_1116 as F

H=lambda value:sha256(value).hexdigest()


def main():
    public,binding=D.Input.normalize(D.ROM.read_bytes(),kind='bt91dc-reference-only')
    parent,_=D.F.C.Camera.proposal(public);raw,_=D.F.C.proposal(parent)
    text=F.controller(raw,source=True);opening,m=D.R.cold(raw)
    tick=0;rows=[];last=None;previous=None
    class Enough(Exception):pass
    def watch(memory,cpu):
        nonlocal previous,last
        if 5335<=tick<=5430:
            r=memory.ram[2]
            current=(memory[0xbd],memory[0x1e],r[0x210],r[0x6b])
            if current!=last and len(rows)<96:
                rows.append(dict(tick=tick,writer=previous,nativeY=current[0],nativeState=current[1],
                    sourceY=current[2],sourceState=current[3],x=memory[0x75]+256*memory[0x5c],
                    sourceX=r[0x213],nativeBox=list(memory[0x658:0x65c]),
                    sourceRect=list(r[0x3e:0x46]),age=r[0x7e],origin=r[0x76],limit=r[0x7b],
                    pad=memory.controller_pad,currentPC=cpu.pc))
            last=current
            tag=memory.rawtags[(cpu.pc-32768)//8192]if cpu.pc>=32768 else-1
            previous=dict(PC=cpu.pc,tag=tag,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,SP=cpu.sp,
                bytes=bytes(memory[(cpu.pc+i)&65535]for i in range(3)).hex())
    def after(memory):
        nonlocal tick
        tick+=1
        if tick>=5430:raise Enough()
    with redirect_stdout(io.StringIO()):
        try:D.R.B.route(m,raw,5500,controller_text=text,observe_extra=watch,after_frame=after)
        except Enough:pass
    q=dict(binding=binding,opening=opening,source_ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),
        rows=rows,terminal=D.R.B.state(m),source_updates=tick,game_state_seeds=0,outputs=0,
        scope='Natural menu and unchanged clear-head input prefix; instruction-after-write witnesses around the first static step. No full clear, native cadence or new game fix claim.')
    encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_STATIC_STAIR '+encoded,flush=True)
    print('DKJR_STATIC_STAIR_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
