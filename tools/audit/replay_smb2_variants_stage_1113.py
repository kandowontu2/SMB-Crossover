"""Ordinary SMB2/Doki terrain/flag CPU routes; frozen ROM, zero outputs.

Castle setup is an explicitly partial endpoint: the frozen 2c62 image still
has the independently diagnosed pipe-priority seam. Existing full-stage
factories and assertions are not modified.
"""
from collections import defaultdict
from hashlib import sha256
import argparse
import json
import time
from unittest.mock import patch
from zipfile import ZipFile

import check_bub_current_budget_1113 as Frames
import replay_smb2_foot_mirror_1113 as Frozen

Flag=Frozen.C.Flag.Check
W=Flag.W
N=W.N
PIN='2c62e1a0de1b732cfa57af59e71c0775396e067bf04aa101e78f644c3e4c9c4b'
FULL_PIN='dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be'
NAMES=Frozen.Flag.Root.NAMES
PROFILES={v:dict(jump_hold=60 if v in(1,5,6,7)else 24,
                 charged_pipes=v in(2,3,5,6))for v in range(8)}
PARTIAL_SHA={
    0:'03f90738f2ea053be483b0773e5bde4592afa05df2c160f340e1e28efc2c66a9',
    1:'46a07bf584998ae3603a31a2a03b26ca25f66aa85d9e8bdab7c835b5e5c11295',
    2:'047791f1542b329c44e74745979fed0219d280d8761e03c48d6b80cf01026891',
    3:'89013637c21136f726a4930da90fa4177726c8bdf0a59507c468071b71a2843e',
    4:'35ce452a938d14a318d41539892cdfd2f4463bef53a206ee1b6360d7ad47c301',
    5:'695f087482e4fba98cd49700550ff3251a003f83edfbeccdbb4bc2dad07793b6',
    6:'bb5828bd9d5b643a2777d8d51d00770695c3cda5ab0a4dbf4d9291140fe45f74',
    7:'712e593335fe56999b779e95245522955df675c4b333c39f028b778a0f6b9e19',
}
FULL_SHA={
    0:'8be09da7f57b54fa938b5e69d1a67945500bd64617b4a595f9388da3e6ced6c1',
    1:'50f01bb6df2ed330055782041210ff4c521c3f98f7821b490c5b5d66eb3fa70e',
    2:'ada18c2496c2f63513bf03bb231fb9bf3c1b52f2548f9079a489d08b03c6c9dc',
    3:'cb51906ade80f9df1140a9afcaecf11ea3873991b2e8d0c81bc167ba35c96c1a',
    4:'f7f16dd05ccf03c07598555e212de2b7121f07e6505d9e35f2b787a15f8ef931',
    5:'d8cb2fc7015f1d0c48fec849adf180bd33e92f84400fa2915d3691d175e94149',
    6:'09092856114a8a74822324682efa4d1675e1e62d560cfbb734708255cc2f2227',
    7:'bfe7c1114cd559bc7cf622b901f43856fd5880b6bee3f74fa032dc9a218b729e',
}


def image():
    parent=Flag.load_input()
    assert sha256(parent).hexdigest()==Flag.PIN
    flagged,_=Frozen.C.Flag.proposal(parent)
    assert sha256(flagged).hexdigest()==Frozen.Flag.CANDIDATE
    candidate,_=Frozen.C.all_mirrors_proposal(flagged)
    assert sha256(candidate).hexdigest()==PIN
    assert Frozen.C.Flag.inverse(Frozen.C.all_mirrors_inverse(candidate))==parent
    return candidate


def charge_source(raw):
    """Bind real Down60 charge and original charged-jump selection."""
    archive=Flag.R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
    member='build/doki-current-component-1101-v1/src/smb2_roster_native.inc'
    with ZipFile(archive)as z:data=z.read(member)
    assert sha256(data).hexdigest()=='c929f894f8d6f4723e6371d140c85fef76de47eb9f53bff0af6b544325f80cb0'
    source=data.decode()
    for text in ('S2N8C57: lda S2Charge','S2N8C5A: cmp #$3c',
                 'S2N8C5E: inc S2Charge','S2N8CB8: ldy S2Charge',
                 'S2N8CBB: cpy #$3c'):
        assert text in source
    b=dict(W.Symbols.bundle(),raw=raw)
    windows=[]
    for name,expected in (
        ('S2N8C57',b'\xad'+W.address(b,'S2Charge').to_bytes(2,'little')+b'\xc9\x3c\xb0'),
        ('S2N8C5E',b'\xee'+W.address(b,'S2Charge').to_bytes(2,'little')),
        ('S2N8CB8',b'\xac'+W.address(b,'S2Charge').to_bytes(2,'little')+b'\xc0\x3c\x90')):
        at=W.location(b,name)
        assert raw[at:at+len(expected)]==expected,(name,'Current actual charge instruction')
        windows.append(dict(name=name,pc=W.address(b,name),bytes=expected.hex()))
    return dict(original_member_SHA256=sha256(data).hexdigest(),charge_threshold=60,
                current_instruction_windows=windows,new_game_bytes=0)


def controller(raw,variant=0,*,jump_hold=24,enemy_gap=48,charged_pipes=False):
    assert sha256(raw).hexdigest()==PIN and 0<=variant<8
    assert 4<=jump_hold<=60 and 16<=enemy_gap<=96
    text=Frozen.controller(raw,variant)
    once=Frozen.Flag.Root.once
    if jump_hold!=24:
        text=once(text,"string.format('%q',k)","string.format('%q',tostring(k))")
        text=once(text,'if jump then hold=23;a=true end',f'if jump then hold={jump_hold-1};a=true end')
        text=once(text,' if hold>0 then hold=hold-1;a=true',
            " if hold>0 and grounded and read(0x5c3f)==0 and read(0x5c4f)&128~=0 then hold=0;a=false\n elseif hold>0 then hold=hold-1;a=true")
        text=once(text,'local smb2Idle={}',"local smb2Idle={}\nlocal wallRunup={stage='normal',age=0,records={}}")
        text=once(text,'idle=smb2Idle','idle=smb2Idle,wall_runups=wallRunup')
        point=" assert(still<240,'No240-update active horizontal softlock')"
        text=once(text,point,point+'''
 if wallRunup.stage=='normal'and still>=50 and read(0x5c3f)==0 then
  assert(#wallRunup.records<16,'Bounded ordinary source wall runups')
  wallRunup.stage='back';wallRunup.target=s.x-12;wallRunup.age=0;wallRunup.records[#wallRunup.records+1]=s
  hold=0;lastA=false
 end
 if wallRunup.stage~='normal'then
  wallRunup.age=wallRunup.age+1;assert(wallRunup.age<220,'Bounded ordinary wall runup')
  if wallRunup.stage=='back'then
   assert(solid(s.x-1,s.y+32)or solid(s.x+14,s.y+32),'Real support during twelve-pixel retreat')
   pad=2
   if s.x<=wallRunup.target and read(0x5c3f)==0 then wallRunup.stage='forward';pad=1 end
  elseif wallRunup.stage=='forward'then
   pad=1
   if read(0x5c3f)==0 and read(0x5c20)>=8 and read(0x5c20)<128 and read(0x5c4f)&128==0 then
    wallRunup.stage='jump';wallRunup.age=0;pad=129
   end
  elseif wallRunup.stage=='jump'then
   pad=wallRunup.age<60 and 129 or 1
   if wallRunup.age>3 and read(0x5c3f)==0 then wallRunup.stage='normal';hold=0;lastA=false;pad=1 end
  end
  return
 end''')
    if enemy_gap!=48:
        text=once(text,'if gap>0 and gap<48 then jump=true end',f'if gap>0 and gap<{enemy_gap} then jump=true end')
    if charged_pipes:
        charge_source(raw)
        text=once(text,'local smb2Idle={}',"local smb2Idle={}\nlocal chargeRoute={index=1,stage='approach',age=0,records={}}")
        text=once(text,'idle=smb2Idle','idle=smb2Idle,charged_pipes=chargeRoute')
        point=" assert(s.world==0 and s.level==0,'Expected ordinary1-1 before flagpole')"
        text=once(text,point,point+'''
 local chargeLeft=({736,912})[chargeRoute.index]
 local target=chargeRoute.index==1 and 630 or 876
 local chargeAdmission=chargeRoute.index==1 and s.x>=592 and s.x<=640
  or chargeRoute.index==2 and s.x>=832 and s.x<912
 if chargeLeft and(chargeRoute.stage~='approach'or chargeAdmission)then
  local vx=read(0x5c20);if vx>=128 then vx=vx-256 end
  if chargeRoute.stage=='approach'then chargeRoute.stage='align';chargeRoute.age=0;hold=0;lastA=false end
  chargeRoute.age=chargeRoute.age+1;assert(chargeRoute.age<260,'Bounded original charged pipe jump')
  if chargeRoute.stage=='align'then
   local stopping=math.abs(vx)*(math.abs(vx)+1)//32+1
   if vx>0 and s.x+stopping>=target then pad=2 elseif vx<0 and s.x-stopping<=target then pad=1
   elseif s.x<target then pad=1 elseif s.x>target then pad=2 else pad=0 end
   if read(0x5c3f)~=0 and read(0x5c2a)>=128 then pad=pad|128 end
   if read(0x5c3f)==0 and vx==0 and math.abs(s.x-target)<=1 and(chargeRoute.index~=1 or s.y<=144)then
    assert(solid(s.x+1,s.y+32)or solid(s.x+14,s.y+32),'Real native foot support before original Down charge')
    chargeRoute.stage='charge';chargeRoute.age=0;pad=4
   end
  elseif chargeRoute.stage=='charge'then
   assert(read(0x5c3f)==0,'Charge remains genuinely grounded')
   pad=4
   if read(0x5c6c)>=60 and read(0x5c4f)&128==0 then
    chargeRoute.records[tostring(chargeRoute.index)]={left=chargeLeft,charge=read(0x5c6c),launch=s}
    chargeRoute.stage='jump';chargeRoute.age=0;pad=128
   end
  elseif chargeRoute.stage=='jump'then
   pad=chargeRoute.age<=72 and 193 or 65
   if s.x>=chargeLeft+8 and read(0x5c3f)==0 then
    chargeRoute.records[tostring(chargeRoute.index)].landing=s
    chargeRoute.index=chargeRoute.index+1;chargeRoute.stage='approach';chargeRoute.age=0;hold=0;lastA=false
   end
  end
  return
 end''')
        if variant==6:
            trigger=f'if jump then hold={jump_hold-1};a=true end'
            text=once(text,trigger,"if s.x>=1454 and s.x<=1472 then jump=true end\n  "+trigger)
            text=once(text,"local target=chargeRoute.index==1 and 630 or 876",
                "local target=chargeRoute.index==1 and(chargeRoute.floor and 700 or 630)or 876")
            if jump_hold!=24:
                text=once(text,"wallRunup.stage='back';wallRunup.target=s.x-12;wallRunup.age=0;",
                    "wallRunup.stage=s.x>=2100 and s.x<2320 and 'charge' or 'back';wallRunup.target=s.x-12;wallRunup.age=0;")
                text=once(text,"  elseif wallRunup.stage=='jump'then",'''
  elseif wallRunup.stage=='charge'then
   assert(read(0x5c3f)==0,'Real supported staircase charge')
   pad=4
   if read(0x5c6c)>=60 and read(0x5c4f)&128==0 then
    wallRunup.records[#wallRunup.records].charge=read(0x5c6c)
    wallRunup.stage='jump';wallRunup.age=0;pad=128
   end
  elseif wallRunup.stage=='jump'then''')
            text=once(text,'(chargeRoute.index~=1 or s.y<=144)',
                '(chargeRoute.index~=1 or chargeRoute.floor or s.y<=144)')
            point="  elseif chargeRoute.stage=='jump'then\n   pad=chargeRoute.age<=72 and 193 or 65"
            text=once(text,point,point+'''
   if chargeRoute.age>12 and read(0x5c3f)==0 and s.x<chargeLeft+8 then
    assert(not chargeRoute.floor,'Bounded one authentic ground-charge retry')
    chargeRoute.floor=true;chargeRoute.stage='align';chargeRoute.age=0;pad=0
    chargeRoute.records[tostring(chargeRoute.index)].landed_short=s
   end''')
            text=once(text,"chargeRoute.records[tostring(chargeRoute.index)]={left=chargeLeft,charge=read(0x5c6c),launch=s}",
                "local prior=chargeRoute.records[tostring(chargeRoute.index)]\n    chargeRoute.records[tostring(chargeRoute.index)]={left=chargeLeft,charge=read(0x5c6c),launch=s,prior_attempt=prior}")
    text=once(text,"local phase='menu';local records={};local pipes={};local seenPipes={}",
        "local phase='menu';local records={};local pipes={};local seenPipes={}\nlocal terrain={};local terrainMaximum=40\nlocal authored={{448,480},{608,640},{736,768},{912,944},{1104,1136},{1376,1424},{2448,2480}}")
    text=once(text,'new_helpers=0,capture_files=0,runtime_state_writes=0',
        'new_helpers=0,capture_files=0,runtime_state_writes=0,partial_endpoint=true,full_stage=false,terrain=terrain')
    point=" if s.world==0 and s.level==0 and s.engine==5 and s.x>=3160 then castle=true end"
    text=once(text,point,point+'''
 if s.world==0 and s.level==0 then
  terrainMaximum=math.max(terrainMaximum,s.x)
  for i,span in ipairs(authored)do
   if not terrain[tostring(i)]and s.x>=span[2]+16 then
    terrain[tostring(i)]={left=span[1],right_exclusive=span[2],x=s.x,y=s.y,Main=updates}
   end
  end
 end
 if flag and castle and s.world==0 and s.level==0 and s.engine==5 and s.x>=3264 then
  for i=1,7 do assert(terrain[tostring(i)],'All seven authored obstacles before actual castle setup')end
  finish(true,'PARTIAL: ordinary 1-1 terrain, native flag/castle and next-area setup; settled 1-2 NOT qualified');return
 end''')
    text=once(text,'local task=coroutine.create(function()',
        "local task=coroutine.create(function()\n if CPU_CONTROLLER_OPENING then assert(r('SelectedCharacter')==25 and read(0x5fe3)==identity,'Actual CPU SMB2/Doki menu');game=true;phase='game';pad=0;return end")
    text=once(text,"assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,",
        "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,")
    Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def full_controller(raw,variant=0,**controls):
    """Explicit dadb successor; restore original complete entrance assertions."""
    import compose_smb2_pipe_priority_1113 as Priority
    assert sha256(raw).hexdigest()==Priority.CANDIDATE==FULL_PIN
    parent=Priority.inverse(raw)
    assert sha256(parent).hexdigest()==PIN
    text=controller(parent,variant,**controls)
    return _full_text(text)


def _full_text(text):
    """Pure endpoint/label formatting after the caller's exact ROM check."""
    stop=""" if flag and castle and s.world==0 and s.level==0 and s.engine==5 and s.x>=3264 then
  for i=1,7 do assert(terrain[tostring(i)],'All seven authored obstacles before actual castle setup')end
  finish(true,'PARTIAL: ordinary 1-1 terrain, native flag/castle and next-area setup; settled 1-2 NOT qualified');return
 end"""
    text=Frozen.Flag.Root.once(text,stop,'')
    text=Frozen.Flag.Root.once(text,'partial_endpoint=true,full_stage=false','partial_endpoint=false,full_stage=ok')
    assert text.count(PIN)==1
    text=text.replace(PIN,FULL_PIN)
    assert "nextUpdates>=25"in text and "assert(flag and castle and entrance"in text
    assert "SMB2/Doki clears non-shortcut1-1 then25 grounded quiet underground1-2 updates"in text
    Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    return text


def profile_controller(raw,variant=0,*,full=False):
    """Named intended-ability policy; raw generic baseline remains separate."""
    text=(full_controller if full else controller)(raw,variant,**PROFILES[variant])
    assert sha256(text.encode()).hexdigest()==(FULL_SHA if full else PARTIAL_SHA)[variant]
    return text


def bindings():
    import compose_smb2_pipe_priority_1113 as Priority
    parent=image();full=Priority.proposal(parent)[0]
    assert sha256(full).hexdigest()==FULL_PIN and Priority.inverse(full)==parent
    rows=[]
    for variant in range(8):
        partial=profile_controller(parent,variant)
        # All rows use this same authenticated full image. Runtime/public
        # full_controller still performs its complete inverse on every call.
        complete=_full_text(partial)
        rows.append(dict(variant=variant,name=NAMES[variant],controls=PROFILES[variant],
                         partial_Lua_SHA256=sha256(partial.encode()).hexdigest(),
                         full_Lua_SHA256=sha256(complete.encode()).hexdigest()))
    assert rows[0]['partial_Lua_SHA256']=='03f90738f2ea053be483b0773e5bde4592afa05df2c160f340e1e28efc2c66a9'
    assert rows[1]['full_Lua_SHA256']=='50f01bb6df2ed330055782041210ff4c521c3f98f7821b490c5b5d66eb3fa70e'
    assert sha256(full_controller(full,1,**PROFILES[1]).encode()).hexdigest()==rows[1]['full_Lua_SHA256']
    return dict(partial_ROM_SHA256=PIN,full_ROM_SHA256=FULL_PIN,controllers=rows,
                original_full_assertions_retained=True,
                shared_full_image_verified_in_metadata_batch=True,outputs=0,Mesen_run=False)


def state(m):
    names=('S2Variant','S2NativeCharacter','S2Health','S2Air','S2VX','S2VY','S2Held','S2Fresh',
           'GameEngineSubroutine','Player_State','NumberofLives','WorldNumber','LevelNumber','AreaType')
    row={name:N.get(m,name)for name in names}
    row.update(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'))
    return row


def run(raw,variant=0,*,limit=7200,jump_hold=24,enemy_gap=48,charged_pipes=False,full=False):
    began=time.perf_counter()
    text=(full_controller if full else controller)(raw,variant,jump_hold=jump_hold,enemy_gap=enemy_gap,charged_pipes=charged_pipes)
    m=Flag.cold(raw,variant)
    lua=Frozen.Flag.Root.Base.LuaRuntime(unpack_returned_tuples=True)
    callbacks=defaultdict(list);events={};ctx=dict(cpu=None,status=None,receipt=None,cap_trace=[],fault=None)
    original_stats=[N.get(m,'S2Stats',i)for i in range(23)]
    api=lua.table()
    api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0))
    api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        return m.ram[at//8192][at%8192]if kind==1 else raw[16+at]if kind==2 else m[at]
    def convert(at):
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def cpu_state():
        c=ctx['cpu']
        return lua.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in ('pc','sp','a','x','y','p')})
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in (('right',1),('left',2),('down',4),('up',8),
            ('start',16),('select',32),('b',64),('a',128))if pad[name])
    def memory(fn,kind,lo,hi=None):
        assert kind==0
        for at in range(lo,lo+1 if hi is None else hi+1):callbacks[at].append(fn)
    def emit(line):
        if line.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(line.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read,api.convertAddress,api.getState,api.setInput=read,convert,cpu_state,set_input
    api.addMemoryCallback=memory
    api.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu=api;lua.globals().print=emit;lua.globals().CPU_CONTROLLER_OPENING=True
    lua.execute(text)
    Native=N.NesMPU
    class Observed(Native):
        def step(self):
            ctx['cpu']=self
            for fn in tuple(callbacks.get(self.pc,())):fn()
            if self.pc in (0x82be,0x82d0)and self.sp==252:
                xx=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if 600<=xx<=650 and len(ctx['cap_trace'])<64:
                    ctx['cap_trace'].append([xx]+[N.get(m,k)for k in ('Player_Y_Position',
                        'S2Y','S2Air','S2VX','S2VY','Player_State','S2Held')])
            opcode_pc=self.pc
            try:return super().step()
            except AssertionError as error:
                ctx['fault']=dict(error=str(error),instruction_PC=opcode_pc,
                    current_PC=self.pc,opcode_bytes=bytes(m[(opcode_pc+i)&65535]for i in range(3)).hex(),
                    A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp,maps=m.rawtags[:],
                    bankA=N.get(m,'CurrentBank'),bankC=N.get(m,'CurrentBankC'),
                    NmiDisable=N.get(m,'NmiDisable'),stack_above_SP=bytes(m[0x100+((self.sp+i)&255)]for i in range(1,17)).hex())
                raise
    with patch.object(N,'NesMPU',Observed):
        for epoch in range(limit):
            try:
                events[0]();Frames.frame(m,whole_pass=True);events[1]()
            except AssertionError:
                if ctx['fault']is None:raise
                break
            if ctx['status']is not None:break
            if epoch%750==749:print(json.dumps(dict(event='terrain_progress',variant=variant,epoch=epoch+1,state=state(m))),flush=True)
    return dict(passed=ctx['status']==0,variant=variant,name=NAMES[variant],ROM_SHA256=sha256(raw).hexdigest(),
        controller_SHA256=sha256(text.encode()).hexdigest(),jump_hold=jump_hold,enemy_gap=enemy_gap,
        charged_pipes=charged_pipes,
        actual_constructor_stats=original_stats,second_cap_trace=ctx['cap_trace'],
        CPU_model_fault=ctx['fault'],
        scheduler_passes=epoch+1,seconds=round(time.perf_counter()-began,2),terminal=state(m),receipt=ctx['receipt'],
        full_stage_qualified=full and ctx['status']==0,partial_endpoint=None if full else 'actual native castle/next-setup',
        genuine_cold_menu_and_controls=True,state_or_actor_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',type=int,choices=range(8),default=0)
    p.add_argument('--variants',help='Comma-separated ordinary routes, e.g.0,1,2,3,5,6,7')
    p.add_argument('--limit',type=int,default=7200)
    p.add_argument('--jump-hold',type=int,default=24)
    p.add_argument('--enemy-gap',type=int,default=48)
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--compact',action='store_true',help='Print bounded terrain/injury/last-pit aggregates only.')
    p.add_argument('--charged-pipes',action='store_true',help='Use actual supported Down60 charged jumps at authored obstacles.')
    p.add_argument('--full',action='store_true',help='Explicit dadb successor with original25-grounded1-2 assertions.')
    p.add_argument('--bindings',action='store_true')
    p.add_argument('--profile',action='store_true',help='Use this variant\'s measured intended-ability control policy.')
    args=p.parse_args();raw=image()
    if args.bindings:
        print(json.dumps(bindings(),separators=(',',':')),flush=True)
        raise SystemExit(0)
    if args.full:
        import compose_smb2_pipe_priority_1113 as Priority
        raw=Priority.proposal(raw)[0]
    failed=False
    for v in map(int,args.variants.split(','))if args.variants else(args.variant,):
        controls=PROFILES[v]if args.profile else dict(jump_hold=args.jump_hold,enemy_gap=args.enemy_gap,charged_pipes=args.charged_pipes)
        if args.metadata:
            text=(full_controller if args.full else controller)(raw,v,**controls)
            row=dict(ROM_SHA256=sha256(raw).hexdigest(),variant=v,controller_SHA256=sha256(text.encode()).hexdigest(),outputs=0)
        else:
            row=run(raw,v,limit=args.limit,full=args.full,**controls)
            failed=failed or not row['passed']
            if args.compact and row['receipt']:
                row['receipt'].pop('recent',None)
                row['receipt']['pipe_columns_seen']=len(row['receipt'].pop('pipes',{}))
        print(json.dumps(row,separators=(',',':')),flush=True)
    if failed:raise SystemExit(1)
