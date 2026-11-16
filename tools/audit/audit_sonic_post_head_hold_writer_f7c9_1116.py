"""Read-only real held-jump writer after f7 native ceiling; no successor CPU."""
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_sonic_hidden_native_callback_f7c9_1116 as Source

F=Source.F


def run(raw):
    assert F.H(Path(Source.__file__).read_bytes())=='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'
    q=F.bindings(raw);N=F.N;base=N.NesMPU;active={'head':False,'frame':False,'first':False,'ctx':None}
    writes=[];returns=[];begins=[];rt=None;m=None;first_negative=None;stack=ExitStack()
    held=bytes.fromhex('ad59c08d50c0ad5ac08d51c0a9ff8d52c0a9008d53c08d54c08d55c0ce58c0ad56c009048d56c060')
    off=q['kernel'].find(held);assert off>=0 and q['kernel'].count(held)==1
    def snapshot(mem):
        return dict(nativeY=N.get(mem,'Player_Y_Position'),sourceY=list(mem.ram[2][0x73:0x76]),VY=list(mem.ram[2][0x60:0x63]),
            flags=mem.ram[2][0x30],scratch_flags=mem.ram[2][0x56],JumpTimer=mem.ram[2][0x58],JumpVelocity=list(mem.ram[2][0x59:0x5b]),
            requested=mem.controller_pad,saved=N.get(mem,'SavedJoypadBits'),sourceInput=mem.ram[2][0xa8],HeadPending=mem.ram[2][0x122],
            policy=list(rt.globals().SONIC_SOURCE_POLICY())if rt else None)
    def capture(runtime,memory):
        nonlocal rt,m
        rt,m=runtime,memory;old=type(m).__setitem__
        def writer(mem,at,value):
            nonlocal first_negative
            if mem is m and active['first']and isinstance(at,int)and at>=0x8000 and mem.rawtags[(at-0x8000)//8192]==2:
                pos=at&8191
                if pos in(0x50,0x51,0x52,0x58,0x60,0x61,0x62)and mem.ram[2][pos]!=(value&255):
                    assert len(writes)<16;ctx=dict(active['ctx']);ctx.update(address=at,physical_offset=pos,before=mem.ram[2][pos],after=value&255,state=snapshot(mem));writes.append(ctx)
                    vy=bytearray(mem.ram[2][0x60:0x63])
                    if 0x60<=pos<=0x62:vy[pos-0x60]=value&255
                    if first_negative is None and 0x60<=pos<=0x62 and vy[2]&128:
                        first_negative=dict(ctx,complete_VY_after=list(vy))
            return old(mem,at,value)
        stack.enter_context(patch.object(type(m),'__setitem__',writer))
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.audit_return=None
        def step(self):
            mem=self.memory;t=mem.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if mem is m:
                if(t,self.pc)==(q['hooks']['PlayerHeadCollision']['tag'],q['hooks']['PlayerHeadCollision']['PC'])and self.a==96:active['head']=True
                if(t,self.pc)==(3,0xbbb0):
                    sp=self.sp;pc=(mem[0x100+((sp+1)&255)]+256*mem[0x100+((sp+2)&255)]+1)&65535
                    self.audit_return=(pc,(sp+2)&255,mem.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1)
                    if active['head']and len(returns)<8:
                        active['frame']=True;active['first']=not returns;begins.append(snapshot(mem))
                if self.audit_return==(self.pc,self.sp,t):
                    self.audit_return=None
                    if active['frame']and len(returns)<8:
                        returns.append(dict(PC=self.pc,SP=self.sp,C=self.p&1,state=snapshot(mem)));active['frame']=False;active['first']=False
                active['ctx']=dict(PC=self.pc,tag=t,SP=self.sp,opcode=bytes(mem[self.pc:self.pc+3]).hex(),A=self.a,X=self.x,Y=self.y,P=self.p)
            return super().step()
    code=inspect.getsource(Source.run)
    a="rt.execute(fixture);rt.execute('SONIC_SOURCE_START()')"
    b="fixture=fixture.replace('SONIC_SOURCE_START=function()', 'SONIC_SOURCE_POLICY=function()return policy.lastJump,policy.hold,policy.clock,policy.phase,pad end;SONIC_SOURCE_START=function()');rt.execute(fixture);rt.execute('SONIC_SOURCE_START()');_capture(rt,m)"
    assert code.count(a)==1;code=code.replace(a,b);ns=dict(Source.__dict__,_capture=capture)
    exec(compile(code,'<same production observer plus read-only held-jump writer>','exec'),ns)
    try:
        with patch.object(N,'NesMPU',CPU):result=ns['run'](raw,'sonic',900)
    finally:stack.close()
    assert result['passed']and len(returns)==8 and first_negative
    assert first_negative['tag']==3 and first_negative['opcode']=='8d62c0'and first_negative['complete_VY_after']==[128,252,255]
    assert begins[0]['JumpTimer']>0 and returns[0]['state']['JumpTimer']==begins[0]['JumpTimer']-1
    assert all(x['state']['policy'][0]==479 for x in returns)
    kernel=q['kernel'];pending=[]
    for bank,start,data in((3,0xa000,kernel),(2,0xd000,q['metadata'])):
        at=0
        while True:
            at=data.find(bytes.fromhex('a9018d22c1'),at)
            if at<0:break
            pending.append(dict(tag=bank,PC=start+at+2,store=data[at+2:at+5].hex(),context=data[max(0,at-8):at+12].hex()));at+=1
    assert len(pending)==1
    out=dict(passed=True,ROM_SHA256=F.PIN,source_SHA256=F.H(Path(__file__).read_bytes()),unchanged_production_natural_receipt=result['receipt_SHA256'],
        active_held_impulse_entry=0xa000+off,active_held_impulse_hex=held.hex(),first_post_head_VY_writes=writes,
        first_complete_negative_VY_writer=first_negative,post_head_frame_begins=begins,first8_original_returns=returns,
        existing_ceiling_pending_store=pending,
        conclusion='Nonzero original JumpTimer bypasses eligibility and reapplies stored JumpVelocity under the same heldA; this is continuation of the same held impulse, not a new policy jump. Original ContactYVelocity zeroedVY but did not cancel JumpTimer. No successor response executed.',
        new_variant_CPU=False,ROM_written=False,Mesen=False,outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Read-only held-jump audit attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
