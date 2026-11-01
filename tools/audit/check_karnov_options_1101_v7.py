"""Original/native relocation differential plus explicit SMB control tests."""
from pathlib import Path
import hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
O=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Proof:
    def __init__(self,assembly):
        self.a=assembly;self.labels=assembly['labels'];self.raw=ROM.read_bytes();self.binary=(O/'component.bin').read_bytes()
        self.count=0;self.normalizations=0;self.minimum=224;self.trace=hashlib.sha256();self.events={}
    def make(self,port,values=None):
        m=Memory()
        if port:
            m[0x7000:0x7000+len(self.binary)]=self.binary
            m[:256]=bytes((i*37+19)&255 for i in range(256))
        else:m[0xc000:]=self.raw[16+14*8192:16+16*8192]
        fields={0x62:0,0x63:128,0x64:144,0x65:2,0x66:0,0x68:0,0x69:128,
            0x8b:2,0x8d:0x1c,0x8e:0,0x8f:255,0x90:1,0x94:0xa4,0x61:7,
            0xbb:2,0xbc:2,0xbd:2,0xbe:2,0xbf:2}
        fields.update(values or{})
        for addr,value in fields.items():m[(0xc000 if port else 0)+addr]=value
        m.writes=[];return m
    def get(self,m,p,a):return m[(0xc000 if p else 0)+a]
    def put(self,m,p,values):
        for a,v in values.items():m[(0xc000 if p else 0)+a]=v
    def run(self,m,p,kind,flags=0x71,ceiling=0):
        native={'options':0xeaa7,'timers':0xada8,'actor':0xf28d,'weapons':0xaab2}
        portable={'options':'KrOptionsNative','timers':'KrOptionsNativeTimers','actor':'KrOptionActor','weapons':'KrOptionWeapons','controls':'KrOptionsControls','tick':'KrOptionsTick'}
        if p:pc=self.labels[portable[kind]]
        else:
            pc=native[kind]
            if kind in['timers','weapons']:
                bank=12 if kind=='timers'else 11;m[0xa000:0xc000]=self.raw[16+bank*8192:16+(bank+1)*8192]
        c=NesMPU(memory=m,pc=pc);c.a=85;c.x=7;c.y=91;c.p=flags;c.sp=224;c.stPushWord(0x5aff)
        before=bytes(m[:256])if p else None;events=[];last=[None,None,None];result=None;low=c.sp
        aset={'LDA','PLA','TXA','TYA','ADC','SBC','AND','ORA','EOR'};xset={'LDX','TAX','TSX','INX','DEX'};yset={'LDY','TAY','INY','DEY'}
        returns={self.labels[n]+13 for n in ['KrOptionsNative','KrOptionsNativeTimers','KrOptionActor','KrOptionWeapons']}
        traps={0xff10:'sound',0xff20:'scene',0xff30:'actor-scene',0xff40:'terrain'}if p else{0xc81d:'sound',0xc6fc:'scene',0xc1c7:'actor-scene',0xc3d8:'terrain'}
        for step in range(12000):
            if c.pc==0x5b00:break
            low=min(low,c.sp)
            if p and c.pc in returns:result=(c.a,c.x,c.y,c.p,last[:],m[3]|m[4]<<8)
            if c.pc in traps:
                name=traps[c.pc];events.append((name,c.a,c.x,c.y,last[:],(m[3]|m[4]<<8)if p else(m[0x58]|m[0x59]<<8)))
                if name=='terrain':c.a=int(c.y<ceiling);c.FlagsNZ(c.a)
                c.pc=(c.stPopWord()+1)&65535;continue
            mnemonic,mode=c.disassemble[m[c.pc]]
            if mnemonic in aset or(mnemonic in['ASL','LSR','ROL','ROR']and mode=='acc'):last[0]=c.pc
            if mnemonic in xset:last[1]=c.pc
            if mnemonic in yset:last[2]=c.pc
            assert m[c.pc]!=0,('Source BRK',p,kind,hex(c.pc));c.step()
        else:raise AssertionError(('Source bound',p,kind,hex(c.pc)))
        assert c.sp==224
        if p:
            assert bytes(m[:256])==before,'Actual borrowed3/4 not restored'
            assert all(0xc000<=a<0xc800 or a==0xc865 or 0x100<=a<0x200 or a in[3,4]for a in m.writes),('Undeclared private write',[hex(a)for a in m.writes if not(0xc000<=a<0xc800 or a==0xc865 or 0x100<=a<0x200 or a in[3,4])][:10])
        return c,events,result,last,low
    def pointer_register(self,old,new,old_writer,new_writer,index,old_pointer,new_pointer):
        source=0xc83e if index==0 else 0xc83c
        assert old_writer==source and new_writer==self.labels['KrDispatch']+source-0xc831,('Unproved register change',index,old,new,old_writer,new_writer)
        assert self.labels[f'Kr_{old_pointer:04X}']==new_pointer
        assert old==(old_pointer>>8 if index==0 else old_pointer&255)and new==(new_pointer>>8 if index==0 else new_pointer&255)
        self.normalizations+=1
    def pair(self,mems,kind,flags=0x71,ceiling=0,port_kind=None):
        values=[self.run(m,p,port_kind if p and port_kind else kind,flags,ceiling)for p,m in enumerate(mems)]
        (a,ea,_,la,al),(z,ez,result,lz,zl)=values
        assert result and(a.y,a.p&0x4d)==(z.y,z.p&0x4d),('Source Y/P',kind,a.y,z.y,a.p,z.p)
        native_pointer=mems[0][0x58]|mems[0][0x59]<<8
        for i,(x,y)in enumerate([(a.a,z.a),(a.x,z.x)]):
            if x!=y:self.pointer_register(x,y,la[i],result[4][i],i,native_pointer,result[5])
        if a.p&0x82!=z.p&0x82:
            self.pointer_register(a.a,z.a,la[0],result[4][0],0,native_pointer,result[5])
            nz=lambda value:(128 if value&128 else 0)|(2 if not value else 0)
            assert a.p&0x82==nz(a.a)and z.p&0x82==nz(z.a),'Only the proved relocated pointer LDA may change NZ'
        assert len(ea)==len(ez),('Source callback count',kind,ea,ez)
        for e,f in zip(ea,ez):
            assert e[0]==f[0]and e[3]==f[3],('Source callback type/Y',kind,e,f)
            for i in [0,1]:
                if e[i+1]!=f[i+1]:self.pointer_register(e[i+1],f[i+1],e[4][i],f[4][i],i,e[5],f[5])
            self.events[e[0]]=self.events.get(e[0],0)+1
        skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}
        delta=[i for i in range(2048)if i not in skip and mems[0][i]!=mems[1][0xc000+i]]
        assert not delta,('Source state',kind,[(hex(i),mems[0][i],mems[1][0xc000+i])for i in delta[:10]])
        self.minimum=min(self.minimum,zl);self.trace.update(bytes(mems[0][0x5e:0xc0]));self.count+=1
        return ea


def native_pairs(p):
    activation=selection=timers=0
    for item,stock,state,weapon,flags in itertools.product(range(9),[0,1,9,0x10,0x99],[0,6,15,16,24,25],[0,2,8,128],[0x31,0xf1]):
        fields={0x8e:item,0x21:4,0x62:state,0x65:weapon,0xbb:stock,0xbc:stock,0xbd:stock,0xbe:stock,0xbf:stock}
        p.pair([p.make(i,fields)for i in range(2)],'options',flags);activation+=1
    for item,pressed,owned,flags in itertools.product(range(9),[0,64,128,192],[0,1,8,128,137,255],[0x31,0xf1]):
        fields={0x8e:item,0x21:pressed,0x8f:owned,0x90:0}
        p.pair([p.make(i,fields)for i in range(2)],'options',flags);selection+=1
    for job,phase,remaining,state in itertools.product(range(1,8),[0,1,63,64,255],[0,1,7,255],[0,15,16,17]):
        fields={0x63f:job,0x640:remaining,0x0f:phase,0x62:state,0x65:128}
        p.pair([p.make(i,fields)for i in range(2)],'timers');timers+=1
    return dict(passed=True,full_original_activation_pairs=activation,full_original_selection_pairs=selection,timed_effect_pairs=timers)


def controls(p):
    cycles=0;activations=0
    for owners,start in itertools.product(range(256),[0,3,7,255,1]):
        m=p.make(True,{0x8f:owners,0x8e:start,0x21:4});before=[m[0xc000+n]for n in[0xbb,0xbc,0xbd,0xbe,0xbf]]
        ids=[0,3,7,255];index=ids.index(start)if start in ids else 3
        for advance in range(1,5):
            chosen=ids[(index+advance)%4]
            if chosen==255 or owners&{0:1,3:8,7:128}[chosen]:break
        c,_,_,_,_=p.run(m,True,'controls')
        assert c.p&1 and m[0xc08e]==chosen and m[0xc021]==0
        assert before==[m[0xc000+n]for n in[0xbb,0xbc,0xbd,0xbe,0xbf]];cycles+=1
    for item,stock in itertools.product([0,3,7],[1,9,0x10,0x99]):
        fields={0x8e:item,0x1b:0x22,0x21:2,0xbb:stock,0xbc:stock,0xbd:stock,0xbe:stock,0xbf:stock}
        m=p.make(True,fields);c,events,_,_,_=p.run(m,True,'controls')
        ref=p.make(False,dict(fields,**{}));ref[0x21]=4
        rc,re,_,_,_=p.run(ref,False,'options')
        skip=set(range(0x100,0x200))|{0x21,0x58,0x59,0x7fe,0x7ff}
        assert c.p&1 and m[0xc021]==0
        assert all(ref[i]==m[0xc000+i]for i in range(2048)if i not in skip),('Mapped exact activation',item,stock)
        assert [e[:2]for e in events]==[e[:2]for e in re];activations+=1
    unhandled=0
    for item,owners,held,pressed in itertools.product([0,3,7,255,1,2,4,5,6,8],[0,255],[0,2,32,34],[0,2,3,128]):
        valid=item in[0,3,7]and owners&{0:1,3:8,7:128}[item]and held&32 and pressed&2
        if valid:continue
        m=p.make(True,{0x8e:item,0x8f:owners,0x1b:held,0x21:pressed});before=bytes(m[0xc000:0xc800])
        c,events,_,_,_=p.run(m,True,'controls');assert not c.p&1 and not events
        assert bytes(m[0xc000:0xc800])==before,'Ordinary input was altered';unhandled+=1
    return dict(passed=True,earned_inventory_cycle_cases=cycles,exact_native_mapped_activations=activations,ordinary_or_unsupported_input_cases=unhandled,new_private_scratch=[0xc865])


def input_edges():
    count=0
    for name,mask in [('input-original',3),('input-full',255)]:
        m=Memory();data=(O/(name+'.bin')).read_bytes();m[0x6000:0x6000+len(data)]=data
        for current,previous in itertools.product(range(256),repeat=2):
            m[16]=current;m[0xc81c]=previous;m.writes.clear()
            c=NesMPU(memory=m,pc=0x6000);c.sp=224;c.stPushWord(0x5aff)
            for step in range(100):
                if c.pc==0x5b00:break
                assert m[c.pc]!=0;c.step()
            else:raise AssertionError('Input converter bound')
            held=int(f'{current:08b}'[::-1],2);pressed=((held^previous)&held)&mask
            assert c.sp==224 and(m[0xc01b],m[0xc021],m[0xc81c])==(held,pressed,held),(name,current,previous)
            count+=1
    return dict(passed=True,actual_assembled_previous_current_cases=count,full_edge_cases=count//2,source_Select_bit=4,source_B_bit=2,source_Down_bit=32,
        scope='Actual frozen converter and proposed full-edge converter, all256 prior source-held bytes by all256 current native inputs. Original converter masks toA/B; proposed converter preserves all source edges.')


def tick_mapping(p):
    count=0
    for phase,job in itertools.product([0,1,63,64,127,255],[1,4,5]):
        fields={0x0f:phase,0xe8:phase,0x63f:job,0x640:1,0x62:15,0x65:128}
        mems=[p.make(i,fields)for i in range(2)];mems[1][0xc00f]=phase^7
        p.pair(mems,'timers',port_kind='tick');count+=1
    return dict(passed=True,clock_mapping_pairs=count,source_divider=64,clock='Accepted sourceE8 epoch, explicit wall-clock adaptation')


def sequences(p):
    rows=[]
    for item in[0,3,7]:
        fields={0x8e:item,0x21:4,0x8f:{0:1,3:8,7:128}[item],0x90:0}
        mems=[p.make(i,fields)for i in range(2)];p.pair(mems,'options');warning=[];expiry=None;peak=144;prev=0
        for tick in range(1,1101):
            held=1 if 20<=tick<35 else 2 if 40<=tick<42 else 128 if 100<=tick<120 else 0
            if item==7:held=16 if 20<=tick<40 else 32 if 80<=tick<100 else held
            for port,m in enumerate(mems):
                y=p.get(m,port,0x64);state=p.get(m,port,0x62)&31
                if y>=144 and state not in[15,16]:p.put(m,port,{0x64:144})
                p.put(m,port,{0x1b:held,0x21:held&~prev,0x0f:tick&255,0xe8:tick&255,0x8b:2 if p.get(m,port,0x64)>=144 else 0})
            p.pair(mems,'actor');p.pair(mems,'weapons');events=p.pair(mems,'timers')
            if any(e[0]=='sound'and e[1]==24 for e in events):warning.append(tick)
            if expiry is None:
                if item==0 and not mems[0][0x65]&128:expiry=tick
                if item==7 and not any(mems[0][0x63f+j]==4 for j in range(0,16,2)):expiry=tick
                if item==3 and tick>42 and not mems[0][0x65]&8:expiry=tick
            peak=min(peak,mems[0][0x64]);prev=held
        if item==0:assert expiry==640 and warning==[448],('Original boots duration',expiry,warning)
        if item==7:
            assert expiry==960 and warning==[768],('Original wings duration',expiry,warning)
            assert 144-peak>=15,('Real original upward flight not exercised',peak)
        if item==3:assert expiry is not None and expiry<300,('Original boomerang return',expiry)
        rows.append(dict(option=item,accepted_updates=1100,expiry_or_return=expiry,warning_updates=warning,maximum_rise=144-peak,remaining_stock=mems[0][{0:0xbd,3:0xbe,7:0xbf}[item]]))
    return dict(passed=True,original_actor_weapon_timer_sequences=rows,total_sequence_updates=3300)


def main():
    q=dict(passed=False,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False)
    try:
        a=json.loads((O/'assembly.json').read_text());assert a['passed']and sha(ROM)==EXPECTED
        for path,value in a['bindings'].items():assert sha(path)==value,path
        p=Proof(a);q['original_source']=native_pairs(p);q['controls']=controls(p);q['input_edges']=input_edges();q['tick_mapping']=tick_mapping(p);q['sequences']=sequences(p)
        q.update(passed=True,source_pairs=p.count,engine_executions=2*p.count,pointer_only_register_normalizations=p.normalizations,
            source_trace_sha256=p.trace.hexdigest(),minimum_component_SP=p.minimum,callback_counts=p.events,
            source_globals_preserved=True,limits=['Source sound/scene/terrain callbacks are isolated identically; no native audio/graphics/terrain claim.',
                'Host whitelist is Boots0/Boomerang3/Wings7 only. Full original9-option controller is recovered/proved but other equipment is not integrated.',
                'Production clock uses accepted source updates rather than original NMI wall-clock during lag. No code/SRAM/CHR lease is granted.',
                'Full host link, actual Main interrupt stack, native controller/graphics/audio and campaign qualification remain required.'])
    except Exception as exc:q.update(error=repr(exc),traceback=traceback.format_exc())
    q['bindings']={str(path.resolve()):sha(path)for path in[Path(__file__),R/'tools/reference/karnov_options_1101_v7.inc',O/'assembly.json',O/'component.bin',O/'component.dbg',ROM]}
    (O/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
