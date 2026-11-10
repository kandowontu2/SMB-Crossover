"""Independent observer of the genuine FF 1-2 intro; no product changes.

Reuses the frozen controller prefix with only its cartridge read facade
changed before cold startup. All later RAM changes come from actual CPU,
controller peripheral or normal-NMI execution. No ROM/artifact is written.
"""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_full_stage_current_1110 as Stage
import check_ff_head_corner_1110 as Fix

R,W,N=Fix.R,Stage.W,Stage.N
STAGE_PIN='4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439'
FIELDS=('Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State '
        'Player_X_Speed Player_Y_Speed PlayerFacingDir Player_MovingDir PlayerSize PlayerStatus '
        'Player_SprAttrib Player_CollisionBits SideCollisionTimer ChangeAreaTimer '
        'GameEngineSubroutine PlayerEntranceCtrl AltEntranceControl DisableCollisionDet '
        'SavedJoypadBits Left_Right_Buttons Up_Down_Buttons AreaType '
        'ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc').split()
NAMES=('PlayerEntrance AutoControlPlayer PlayerCtrlRoutine PlayerMovementSubr '
       'EnterSidePipe PlayerBGCollision DoPlayerSideCheck SideCheckLoop CheckSideMTiles '
       'StopPlayerMove ImpedePlayerMove PlyrPipe PipeDwnS ContSChk InitSteP '
       'BlockBufferCollision BlockBufferColli_Side FfHostMovement FfHostFeet FfHostSide '
       'FfHostWall FfHostAfterTerrain ScrollHandler').split()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--prefix-only',action='store_true')
    parser.add_argument('--candidate',choices=('v1','v2'),default='v1')
    args=parser.parse_args();assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    assert sha256(Path(Stage.__file__).read_bytes()).hexdigest()==STAGE_PIN
    proposal=Fix.proposal
    if args.candidate=='v2':
        import check_ff_head_corner_1110_v2 as Fix2
        proposal=Fix2.proposal
    image,_,cookie,_,_,_=proposal(W.ROM.read_bytes())
    assert sha256(image).hexdigest()==dict(
        v1='db20d5a53259b90b0c0892b416e8da78aab1815a1c68fb99c4a1974ad5326069',
        v2='96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd')[args.candidate]
    class MemoryImage:
        def read_bytes(self):return image
    with patch.object(W,'ROM',MemoryImage()),patch.object(W,'PIN',sha256(image).hexdigest()):
        priority_events=[];entrance_reads=[];timer_writes=[];holder={}
        original_fixture=Stage.fixture;original_cpu=N.NesMPU
        def observed_fixture(variant):
            result,model=original_fixture(variant)
            fields={name:W.address(model.bundle,name)for name in FIELDS if name in model.bundle['syms']}
            level=W.address(model.bundle,'LevelNumber');engine=fields['GameEngineSubroutine']
            attribute=fields['Player_SprAttrib']
            entrance=W.address(model.bundle,'PlayerEntrance')
            timer=fields['ChangeAreaTimer']
            class PriorityObserver(type(model)):
                intro_priority=True
                intro_cpu=None
                def __getitem__(self,at):
                    value=super().__getitem__(at)
                    cpu=self.intro_cpu
                    if isinstance(at,int)and at==attribute and cpu is not None:
                        if entrance<=cpu.pc<entrance+40 and self.rawtags[(cpu.pc-0x8000)//8192]==129:
                            if super().__getitem__(level)==1 and super().__getitem__(engine)==7 and len(entrance_reads)<256:
                                entrance_reads.append(dict(operand_PC=cpu.pc,value=value,
                                    x=super().__getitem__(fields['Player_X_Position']),
                                    y=super().__getitem__(fields['Player_Y_Position']),
                                    timer=super().__getitem__(timer)))
                    return value
                def __setitem__(self,at,value):
                    if isinstance(at,int)and at==timer and self[level]==1 and self[engine]==7:
                        cpu=self.intro_cpu
                        if len(timer_writes)<384:
                            timer_writes.append(dict(old=self[at],new=value&255,operand_PC=None if cpu is None else cpu.pc,
                                bank=None if cpu is None else self.rawtags[(cpu.pc-0x8000)//8192],
                                x=self[fields['Player_X_Position']]))
                    if isinstance(at,int)and at==attribute and self[level]==1 and self[engine]==7:
                        previous=self[at]
                        if(previous^value)&0x20 and len(priority_events)<128:
                            cpu=self.intro_cpu;stores=[]
                            if cpu is not None:
                                # py65 exposes the operand PC while STA writes;
                                # resolve its actual target rather than guess
                                # a store instruction's length/PC convention.
                                for pc in range(cpu.pc-3,cpu.pc+1):
                                    opcode=self[pc];target=None
                                    if opcode in(0x8d,0x9d,0x99):
                                        target=self[pc+1]|self[pc+2]<<8
                                        if opcode==0x9d:target=(target+cpu.x)&65535
                                        if opcode==0x99:target=(target+cpu.y)&65535
                                    if target==at:
                                        bank=self.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else 0
                                        stores.append(dict(bank=bank,pc=pc,opcode=bytes(self[pc:pc+3]).hex()))
                            priority_events.append(dict(old=previous,new=value&255,CPU_PC=None if cpu is None else cpu.pc,
                                stores=stores,state={name:N.get(self,name)for name in fields},
                                registers=None if cpu is None else[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],
                                stack=None if cpu is None else bytes(self[0x101+cpu.sp:min(0x10d+cpu.sp,0x200)]).hex()))
                    return super().__setitem__(at,value)
            model.__class__=PriorityObserver
            holder['model']=model
            return result,model
        def observed_cpu(*pos,**kwargs):
            cpu=original_cpu(*pos,**kwargs)
            if getattr(cpu.memory,'intro_priority',False):cpu.memory.intro_cpu=cpu
            return cpu
        # Capture only the existing genuine controller result. Its whole
        # cold/pickup/attack/1-1 prefix executes without memory injection.
        with redirect_stdout(io.StringIO()),patch.object(Stage,'fixture',observed_fixture),patch.object(N,'NesMPU',observed_cpu):
            result=Stage.route(0,stop_at_intro=True)
        if isinstance(result,tuple):receipt,m=result
        else:receipt,m=result,holder['model']
        if args.prefix_only or args.candidate=='v2':
            cells=[]
            for x in range(0,384,16):
                for y in range(32,240,16):
                    at=0x300+((x>>8)&1)*208+((y-32)//16)*16+((x>>4)&15)
                    if m[at]in(*range(0x10,0x16),*range(0x1c,0x22),0x6b,0x6c):cells.append(dict(x=x,y=y,tile=m[at]))
            assert sha256(Path(Stage.__file__).read_bytes()).hexdigest()==STAGE_PIN
            print(json.dumps(dict(diagnostic=True,product_edits=False,outputs_written=0,ROM_written=False,
                candidate_SHA256=W.PIN,candidate=args.candidate,
                prefix=receipt.get('terminal',receipt.get('active_1_2')),priority_events=priority_events,
                native_entrance_attribute_reads=entrance_reads,native_timer_writes=timer_writes,
                active_1_2=receipt.get('active_1_2'),full_1_1=receipt.get('full_1_1',receipt.get('full_1_1_flag_and_level_transition')),
                native_flag=receipt['native_flag'],injuries=receipt['injuries'],
                actual_pipe_cells=cells,source_only=True),sort_keys=True),flush=True)
            assert not args.output.exists()
            return
        b=m.bundle;addresses={name:W.address(b,name)for name in FIELDS if name in b['syms']}
        points={}
        for name in NAMES:
            if name in b['syms']:
                pc= W.address(b,name);bank=(W.location(b,name)-16)//8192|128
                points[bank,pc]=name
        watched={at:name for name,at in addresses.items()}
        writes=[];reads=[];calls=[];counts=Counter();frames=[];frame=-1
        class Observe(type(m)):
            active=False
            instruction=None
            def __setitem__(self,at,value):
                if self.active and isinstance(at,int)and at in watched:
                    previous=super().__getitem__(at)
                    if len(writes)<12000:
                        writes.append(dict(frame=frame,name=watched[at],at=at,old=previous,new=value&255,
                                           instruction=self.instruction))
                return super().__setitem__(at,value)
            def __getitem__(self,at):
                value=super().__getitem__(at)
                if self.active and isinstance(at,int)and 0x300<=at<0x4a0 and len(reads)<12000:
                    reads.append(dict(frame=frame,at=at,value=value,instruction=self.instruction))
                return value
        m.__class__=Observe
        def state():
            return {name:N.get(m,name)for name in addresses}
        def stack(c):
            return bytes(m[0x101+c.sp:min(0x109+c.sp,0x200)]).hex()
        idle=W.address(b,'IdleLoop')
        for frame in range(80):
            before=state();frames.append(dict(frame=frame,before=before))
            m.controller_pad=0;W.clear_logs(m);N.consume(m)
            c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
            m.active=True
            try:
                for _ in range(250000):
                    if(c.pc,c.sp)==(idle+12,252):break
                    bank=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else 0
                    m.instruction=dict(bank=bank,pc=c.pc,registers=[c.a,c.x,c.y,c.p,c.sp])
                    name=points.get((bank,c.pc))
                    if name:
                        counts[name]+=1
                        if len(calls)<6000:
                            calls.append(dict(frame=frame,name=name,point=m.instruction,state=state(),
                                              scratch=bytes(m[3:11]).hex(),stack=stack(c),
                                              opcode=bytes(m[c.pc:c.pc+6]).hex()))
                    assert m[c.pc],('Intro BRK',frame,hex(c.pc),bank)
                    c.step()
                else:raise AssertionError(('Intro frame bound',frame,hex(c.pc)))
            finally:m.active=False
            frames[-1]['after']=state()
            if frame>24 and all(row['after']['Player_X_Position']==239 for row in frames[-8:]):break
        first_back=next((row for row in writes if row['name']=='Player_X_Position'and row['new']<row['old']),None)
        interesting={0,1,2,frame}
        if first_back:interesting.update((first_back['frame']-1,first_back['frame'],first_back['frame']+1))
        focus=[row for row in calls if row['frame']in interesting and row['name']in
               ('PlayerEntrance','PlayerCtrlRoutine','DoPlayerSideCheck','CheckSideMTiles','ContSChk',
                'StopPlayerMove','ImpedePlayerMove','PlyrPipe','PipeDwnS','InitSteP','EnterSidePipe')]
        focus_writes=[row for row in writes if row['frame']in interesting and row['name']in
                      ('Player_X_Position','Player_X_Speed','Player_State','Player_SprAttrib',
                       'Player_MovingDir','PlayerFacingDir','Player_CollisionBits','GameEngineSubroutine')]
        focus_reads=[row for row in reads if row['frame']in interesting]
        assert receipt['full_1_1_flag_and_level_transition']and not receipt['active_1_2']
        assert sha256(Path(Stage.__file__).read_bytes()).hexdigest()==STAGE_PIN
        print(json.dumps(dict(diagnostic=True,product_edits=False,outputs_written=0,ROM_written=False,
                              candidate_SHA256=W.PIN,cookie=cookie.hex(),prefix=receipt['terminal'],
                              priority_events=priority_events,
                              terminal=state(),calls=dict(counts),first_backward_X_write=first_back,
                              frame_samples=[row for row in frames if row['frame']in interesting],
                              focus_calls=focus,focus_writes=focus_writes,focus_buffer_reads=focus_reads),sort_keys=True),flush=True)
    assert not args.output.exists()


if __name__=='__main__':main()
