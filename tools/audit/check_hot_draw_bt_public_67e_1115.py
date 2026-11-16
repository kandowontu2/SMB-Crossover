"""Reached actual Draw caller and full BT public transport over owning67."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_hot_draw_bt_67e_1115 as C
import hot_draw_bt_67e_model_1115 as Model

W,N,Frames=Model.W,Model.N,Model.Frames
Research=Model.Previous.Prior.Model.Previous.M.Research


def capture(raw,key):
    m=Model.cold(raw,key);base=N.NesMPU;captures=[]
    class Observe(base):
        def step(self):
            if not captures and self.pc==0xa122 and self.memory.rawtags[1]==132:
                assert bytes(self.memory[self.pc:self.pc+3])==bytes.fromhex('20ccbf')
                captures.append((N.fork(self.memory),dict(pc=self.pc,a=self.a,x=self.x,y=self.y,p=self.p,sp=self.sp)))
            return super().step()
    with patch.object(N,'NesMPU',Observe):
        m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(captures)==1
    seed,regs=captures[0]
    assert seed.bundle['raw']is raw and N.get(seed,'SelectedCharacter')==33
    return seed,regs


def execute(m,regs,p=None,a=None,x=None,y=None):
    c=N.NesMPU(memory=m,pc=regs['pc'])
    for name in('a','x','y','p','sp'):setattr(c,name,regs[name])
    for name,value in(('p',p),('a',a),('x',x),('y',y)):
        if value is not None:setattr(c,name,value)
    end=(regs['pc']+3,regs['sp']);minimum=c.sp;calls=Counter();new_steps=Counter();headers=[];pending=None
    context=dict(active=False,PC=0,tag=-1);reader=type(m).__getitem__
    def read(bus,at):
        value=reader(bus,at)
        if bus is m and context['active']and isinstance(at,int)and 0x8000<=at<0x10000:
            slot=(at-0x8000)//8192
            if m.rawtags[slot]==3 and 0x1fe0<=at&8191<0x1ff0:
                assert pending is not None,('Header outside acknowledged check',context,at)
                pending['header_reads'].append(dict(PC=context['PC'],address=at,physical_RAM=3,index=(at&8191)-0x1fe0,value=value))
        return value
    with patch.object(type(m),'__getitem__',read):
        for _ in range(30000):
            if pending is not None and(c.pc,c.sp)==tuple(pending['return']):
                pending['returned_P']=c.p;pending['accepted']=bool(c.p&1);pending=None
            if(c.pc,c.sp)==end:break
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            for name,point in(('HotNew',(194,0xb4a4)),('public_BtDraw',(215,0xb026)),('BtCheck',(221,0xadc0)),
                ('private_BtDraw',(3,W.address(m.bundle,'BtDraw'))),('NrDraw',(252,0xa1a2)),('HuDraw',(207,W.address(m.bundle,'HuDraw')))):
                if(tag,c.pc)==point:calls[name]+=1
            if(tag,c.pc)==(221,0xadc0):
                assert pending is None,('Unclosed BtCheck',pending)
                ret=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
                pending=dict(tag=tag,PC=c.pc,SP=c.sp,return_=(ret,(c.sp+2)&255),
                    published_target=[m[0x162],m[0x16c]+256*m[0x16d]],header_reads=[])
                pending['return']=pending.pop('return_');headers.append(pending)
            if(tag,c.pc)==(3,0xa006):
                assert headers and headers[-1].get('accepted'),('Private draw without accepted complete check',headers)
                calls['private_draw_veneer']+=1
            if tag==194 and C.BASE<=c.pc<C.BASE+89:new_steps[c.pc]+=1
            minimum=min(minimum,c.sp)
            assert m[c.pc],('Mapped public BRK',hex(c.pc),tag,c.sp,calls)
            context.update(active=tag==221 and 0xadc0<=c.pc<0xae01,PC=c.pc,tag=tag)
            try:c.step()
            finally:context['active']=False
        else:raise AssertionError(('Actual Draw caller bound',c.pc,c.sp,calls))
    assert pending is None and headers
    return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,CPU=c.processorCycles,
        minimum_SP=minimum,calls=dict(calls),header_checks=headers,mapped_Hot_instruction_PCs=sorted(new_steps))


def compare(pair,out,label):
    assert out[0]['PC']==out[1]['PC'],(label,out)
    delta=Research.compare(pair,out,label)
    assert not delta,('New draw SMC difference',label,delta,out)
    assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
    assert bytes(pair[0][0x101+out[0]['SP']:0x200])==bytes(pair[1][0x101+out[1]['SP']:0x200]),('Live outer caller stack',label)
    return delta


def run(parent,image):
    savings=Counter();checks=Counter();minimum=255;rows=[];cases=0
    for key in('rash','zitz'):
        seed,regs=capture(parent,key)
        header=bytes(seed.ram[3][0x1fe0:0x1ff0])
        vectors=[('valid',-1,p,None,None,None)for p in range(256)if p&32]
        vectors += [('fault',bad,p,None,None,None)for bad in range(17)for p in(0x20,0x31,0x69,0xe5)]
        vectors += [('register',-1,0xe9,a,x,y)for a,x,y in((0,0,0),(255,255,255),(85,7,91),(1,109,71))]
        for kind,bad,p,a,x,y in vectors:
            pair=[Model.reimage(seed,raw)for raw in(parent,image)]
            if bad>=0:
                for m in pair:
                    m.ram[3][0x1fe0:0x1ff0]=header
                    if bad<16:m.ram[3][0x1fe0+bad]^=1
                    else:m.ram[3][0x1fe0]=0
            out=[execute(m,regs,p,a,x,y)for m in pair]
            compare(pair,out,(key,kind,bad,p,a,x,y))
            assert out[0]['calls'].get('HotNew')==out[1]['calls'].get('HotNew')==1
            if cases==0:print('FIRST_ACTUAL_COUNTS '+json.dumps(out),flush=True)
            assert out[0]['calls'].get('BtCheck')==out[1]['calls'].get('BtCheck')and out[1]['calls']['BtCheck']>=1,(key,kind,bad,out)
            for row in out:
                assert len(row['header_checks'])==row['calls']['BtCheck']
                for h in row['header_checks']:
                    assert bool(h['accepted'])==(bad<0),(key,kind,bad,h)
                    indices=[r['index']for r in h['header_reads']]
                    if bad<0:assert set(indices)==set(range(16)),('Incomplete valid header',h)
                    else:assert not row['calls'].get('private_draw_veneer')and not row['calls'].get('private_BtDraw'),row
            assert out[1]['calls'].get('public_BtDraw')==1 and not out[1]['calls'].get('NrDraw')
            minimum=min(minimum,*(r['minimum_SP']for r in out));cases+=1
            savings[key,kind,out[0]['CPU']-out[1]['CPU']]+=1
            checks[key,kind,out[0]['calls']['BtCheck'],out[1]['calls']['BtCheck']]+=1
            if len(rows)<8:rows.append(dict(identity=key,fixture=kind,bad=bad,status=p,returns=out))
        print('PROGRESS '+json.dumps(dict(identity=key,actual_public_cases=cases)),flush=True)
    return dict(cases=cases,all128_hardware_statuses_both_variants=True,
        every_cookie_byte_corrupt_and_retired_header=True,reached_caller=dict(tag=132,PC=0xa122,opcode='20ccbf'),
        true_return_PC=0xa125,minimum_SP=minimum,
        exact_AXYP_SP_CVID_SafeA_SMC_native_private_RAM_OAM_VRAM_maps_live_caller_stack=True,
        full_BtCheck_and_real_BtDraw_code_unchanged=True,all_actual_valid_checks_read_every_header_byte=True,
        mapped_check_entry_return_PC_SP_and_header_readers_recorded=True,
        explicit_component_cookie_faults_only_no_gameplay_seeds=True,
        cycle_savings=[dict(identity=k,fixture=f,cycles=d,cases=n)for(k,f,d),n in sorted(savings.items())],
        header_check_counts=[dict(identity=k,fixture=f,old=a,new=b,cases=n)for(k,f,a,b),n in sorted(checks.items())],
        sparse_examples=rows,actual_mounted_opcodes=True,no_read_overlay_or_PC_redirect=True)


def main():
    raw=C.load_current_image();parent=Model.F.parent(raw);image,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Public source check attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(parent,image)
    q.update(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
