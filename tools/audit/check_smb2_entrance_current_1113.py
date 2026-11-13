"""Unseeded private flag-route CPU entrance trace, bounded stdout only."""
from collections import deque
from hashlib import sha256
import argparse
import json
from unittest.mock import patch

import check_smb2_natural_powerups_1113 as Source
import replay_smb2_natural_powerups_1113 as Factory
import replay_smb2_flag_handoff_1113 as Flag


def run(parent,limit=4300):
    image,info=Flag.C.proposal(parent);text=Flag.controller(image,4)
    assert sha256(text.encode()).hexdigest()=='09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453'
    # Source CPU already executes the real menu/Start/constructor. The shim
    # skips only Lua's duplicate menu coroutine; post-menu decisions are exact.
    before='local task=coroutine.create(function()'
    assert text.count(before)==1
    text=text.replace(before,before+"\n if CPU_CONTROLLER_OPENING then assert(r('SelectedCharacter')==25 and read(0x5fe3)==4,'Actual CPU Imajin menu');game=true;phase='game';pad=0;return end")
    before="assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,"
    assert text.count(before)==1
    text=text.replace(before,"assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,")
    text=text.replace("string.format('%q',k)","string.format('%q',tostring(k))")
    N=Source.N;native=N.NesMPU;last=deque(maxlen=80);maps=deque(maxlen=30)
    farcalls=deque(maxlen=30);holder={};previous=None;entry=None
    class Trace(native):
        def step(self):
            nonlocal previous,entry
            m=self.memory
            if N.get(m,'WorldNumber')==0 and N.get(m,'LevelNumber')==1:
                holder['m']=m;holder['cpu']=self
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
                row=dict(pc=hex(self.pc),tag=tag,sp=self.sp,a=self.a,x=self.x,y=self.y,
                    p=self.p,code=bytes(m[self.pc:self.pc+3]).hex())
                last.append(row)
                current=tuple(m.rawtags)
                if current!=previous:maps.append(dict(**row,maps=current));previous=current
                if self.pc==0x16b:
                    farcalls.append(dict(**row,SMC=bytes(m[0x15a:0x17b]).hex()))
                if entry is None and N.get(m,'GameEngineSubroutine')==7:
                    entry=dict(s=Source.state(m),maps=current,at=row)
                if(tag,self.pc)==(176,0xb144):
                    raise AssertionError('reached actual native mapped-data halt PC')
            return native.step(self)
    try:
        with patch.object(N,'NesMPU',Trace),patch.object(Factory,'controller',lambda *a,**k:text):
            q=Source.run_controller(image,4,'entrance-followup',limit)
        q.update(ROM_SHA256=info['ROM_SHA256'],frozen_native_controller='09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453',
            source_menu_only_shim=True,first_next_entrance=entry,last_instructions=list(last),map_changes=list(maps),farcall_targets=list(farcalls))
        return q
    except Exception as error:
        m=holder.get('m');c=holder.get('cpu')
        return dict(passed=False,ROM_SHA256=info['ROM_SHA256'],error=repr(error),
            scope='actual original-menu unbroken ordinary-controller/Main/NMI route; CPU-model evidence',
            first_next_entrance=entry,last_instructions=list(last),map_changes=list(maps),
            farcall_targets=list(farcalls),terminal=Source.state(m)if m else None,
            stack=bytes(m[0x100+c.sp+1:0x200]).hex()if c else None,
            source_menu_only_shim=True,gameplay_state_or_scene_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=4300);args=p.parse_args()
    print(json.dumps(run(Source.Flag.load_input(),args.limit),separators=(',',':')),flush=True)
