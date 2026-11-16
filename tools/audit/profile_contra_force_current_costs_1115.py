"""Read-only exactbc5 Burns normal/catch-up attribution; no image/overlay."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import argparse,json,re
import compose_hot_draw_bt_67e_1115 as C
import hot_draw_bt_67e_model_1115 as Model

W,N,Frames=Model.W,Model.N,Model.Frames
KERNEL=C.R/'build/contra-force-projectile-contact-1031-v3/kernel'
PINS={'runtime.dbg':'d98abb1cc9701fb2b4674c99cbeef7fe03411a8d00cefd0752522af06aad4f82',
    'runtime.lbl':'8944961064964d2bac2d7b2ebca31fbb4ac4c2d9b555af032f7477ee16414ab2',
    'ram1.bin':'aee82a91f7f4396105f66286aab9630cb65f7cdbb365a0da07fd0cf7f16c8624',
    'ram2.bin':'8d37a18c459df07976adab3f1f815272a342f3a482c4c0894293762a33b38d50',
    'ram3.bin':'0ad7bb16f75acc550db46f63e9466a370b6370d247b7e3d3ad3be6db86901795'}
CHR=1048592
PRIVATE=('CfA2Router','CfCallA','CfNativeClear','CfHostMovement','CfHostAfterBG','CfHostEnsure',
    'CfHostSceneEnsure','CfHostImport','CfHostExport','CfHostCallInput','CfHostCallBody',
    'CfNativeInput','CfNativeBody','CfHostGraphics','CfHostDraw','CfHostRenderAll','CfHostShots',
    'CfHostScrollPublish','CfHostPaletteTick','CfP1LateEntry','CfP1Acquire','CfP1Heartbeat')
GLOBAL=('GameLoop','DrawAllMetasprites','MetaspriteRenderLoop','AudioUpdate','ExpandedAudioUpdate','VgAudioDispatch',
    'CfOrBtCheck','CfLoaderProposal','CfLoaderCoreProposal','HuMovement','HuDraw','NrMovement','NrDraw',
    'HotNewCharacterDraw','ThSharedDrawHot','KbDrawDispatch','RlSpecialDrawDispatch','JnSpecialDrawDispatch',
    'BlockBufferColli_Head','BlockBufferColli_Side','TerrainCatchupPending')


def fields(line):
    return {k:v.strip('"')for k,v in re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1])}


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and C.H(raw)==C.CANDIDATE,'Exact currentbc5 required'
    parent=C.inverse(raw);assert C.H(parent)==C.PIN
    b=Model.symbols(raw);assert b['raw']is raw
    inputs={name:(KERNEL/name).read_bytes()for name in PINS}
    for name,pin in PINS.items():
        assert len(pin)==64,('Malformed local source pin',name,pin)
        assert C.H(inputs[name])==pin,(name,'Changed retained input')
    carrier=raw[CHR+935*1024:CHR+959*1024]
    assert carrier==parent[CHR+935*1024:CHR+959*1024]and len(carrier)==24576
    for tag in(1,2,3):
        expected=bytearray(inputs[f'ram{tag}.bin']);expected.extend(bytes(8192-len(expected)))
        if tag in(2,3):expected[-32:]=bytes(32)
        assert carrier[(tag-1)*8192:tag*8192]==expected,('Actual CF carrier changed',tag)
    segments={};symbols=[]
    for line in inputs['runtime.dbg'].decode().splitlines():
        if line.startswith('seg\t'):
            row=fields(line);segments[int(row['id'])]=row
        elif line.startswith('sym\t'):
            row=fields(line)
            if row.get('name')in PRIVATE and'val'in row and'seg'in row:symbols.append(row)
    points={};missing=[]
    for name in PRIVATE:
        candidates=[]
        for sym in symbols:
            if sym['name']!=name:continue
            seg=segments[int(sym['seg'])];file=seg.get('oname','')
            if file not in('ram1.bin','ram2.bin','ram3.bin'):continue
            tag=int(file[3]);pc=int(sym['val'],0);offset=int(seg['ooffs'])+pc-int(seg['start'],0)
            assert offset==pc&8191
            data=carrier[(tag-1)*8192+offset:(tag-1)*8192+offset+8]
            candidates.append((tag,pc,data,seg['name']))
        unique={(t,p,data,seg)for t,p,data,seg in candidates}
        if not unique:missing.append(name);continue
        assert len(unique)==1,(name,unique)
        tag,pc,data,segment=unique.pop()
        if(tag,pc)in points:
            points[tag,pc].setdefault('aliases',[]).append(name)
        else:points[tag,pc]=dict(name=name,tag=tag,PC=pc,bytes=list(data),segment=segment,source='current kernel DBG/oname + authenticated carrier')
    assert all(any(q['name']==name for q in points.values())for name in('CfA2Router','CfCallA','CfHostMovement','CfNativeInput','CfNativeBody'))
    for name in GLOBAL:
        try:pc=W.address(b,name);at=W.location(b,name)
        except(KeyError,AssertionError):missing.append(name);continue
        assert 16<=at<CHR
        tag=((at-16)//8192)|128
        assert(tag,pc)not in points,('Duplicate active name',name,points.get((tag,pc)))
        points[tag,pc]=dict(name=name,tag=tag,PC=pc,bytes=list(raw[at:at+8]),source_file=at,source='actual bc5 compiled symbol/preimage')
    return dict(bundle=b,points=points,missing=missing,carrier=carrier,
        reference67_SHA256=C.H(parent),CF_carrier_SHA256=C.H(carrier),retained_CF_inputs=PINS)


def cold(raw):
    q=bindings(raw);b=q['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in([4]*3+[1]*6):W.UI.key(m,pad)
    assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),(N.get(m,'FmGroups')>>3)&3)==('BURNS',30,31,0)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError('Actual current Burns constructor bound')
    empty(m);assert m.bundle['raw']is raw
    at=W.location(b,'CfExternalCookie');assert bytes(m.ram[2][-32:-16])==raw[at:at+16]
    assert bytes(m.ram[3][-32:])==bytes(32)
    return m


def empty(m):
    assert N.get(m,'SelectedCharacter')==31 and(N.get(m,'FmGroups')>>3)&3==0
    assert N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==N.get(m,'StarInvincibleTimer')==0
    assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
    assert not any(m.ram[2][0x382+i]for i in range(10,22))


def inspect(raw):
    q=bindings(raw);m=cold(raw)
    return dict(ROM_SHA256=C.H(raw),reference67_SHA256=q['reference67_SHA256'],
        actual_cpu_bytes_retained=True,CF_carrier_SHA256=q['CF_carrier_SHA256'],
        retained_CF_inputs=q['retained_CF_inputs'],points=list(q['points'].values()),unavailable_named_points=q['missing'],
        genuine_compiled_name='BURNS',slot=30,Select_cycles=0,variant=0,
        native_actors=0,source_shots=0,lives=2,power=0,star=0,
        x=N.get(m,'Player_X_Position'),y=N.get(m,'Player_Y_Position'),
        no_output_or_overlay_or_gameplay_seeds=True)


def profile(raw,injected=False):
    q=bindings(raw);m=cold(raw);b=m.bundle;base=N.NesMPU;points=q['points'];all_rows=[]
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    movement=next((tag,pc)for(tag,pc),p in points.items()if p['name']=='CfHostMovement')
    for phase,pad,count in(('idle',0,8),('Right',1,8)):
        inclusive=Counter();exclusive=Counter();calls=Counter();returns=Counter();unwinds=Counter();banks=Counter();pcs=Counter()
        categories=Counter();service_rows=Counter();isr_costs=Counter();main_classes=Counter();instances=[];sparse=[];minimum=255
        class Probe(base):
            def __init__(self,*args,**kw):
                super().__init__(*args,**kw);self.pending=[];self.interrupts=[];self.completed_ISR=0;self.injected=False;instances.append(self)
            def interrupt(self,kind):
                ret=(self.pc,self.sp);start=self.processorCycles;busy=bool(N.get(m,'NmiDisable')&128)
                result=(super().nmi()if kind=='NMI'else super().irq())
                if(self.pc,self.sp)!=ret:self.interrupts.append(dict(kind=kind,return_=ret,start=start,child=0,busy=busy))
                return result
            def nmi(self):return self.interrupt('NMI')
            def irq(self):return self.interrupt('IRQ')
            def settle(self):
                while self.interrupts and(self.pc,self.sp)==self.interrupts[-1]['return_']:
                    done=self.interrupts.pop();wall=self.processorCycles-done['start'];label='busy'if done['busy']else'regular'
                    isr_costs[done['kind'],label,'wall']+=wall;isr_costs[done['kind'],label,'exclusive']+=wall-done['child'];isr_costs[done['kind'],label,'calls']+=1
                    self.completed_ISR+=wall
                    if self.interrupts:self.interrupts[-1]['child']+=wall
                context=id(self.interrupts[-1])if self.interrupts else 0
                while self.pending and self.pending[-1]['context']==context:
                    done=self.pending[-1]
                    tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                    if(self.pc,self.sp,tag)==done['return_']:
                        self.pending.pop();wall=self.processorCycles-done['start']
                        child=(self.completed_ISR-done['ISR'])if context==0 else self.interrupts[-1]['child']-done['child']
                        inclusive[done['name']]+=wall-child;returns[done['name']]+=1
                        if done['name']=='GameLoop':
                            key=('render'if done['render']else'no-render',done['checks']);main_classes[key]+=1
                            if len(sparse)<8:sparse.append(dict(kind='Main',wall=wall,ISR=child,exclusive=wall-child,render_calls=done['render'],external_checks=done['checks'],entry_SP=done['entry_SP'],return_PC=self.pc,return_SP=self.sp,VRAM_AddrCtrl=N.get(m,'VRAM_Buffer_AddrCtrl')))
                    elif self.sp>done['return_'][1]:
                        self.pending.pop();unwinds[done['name']]+=1
                    else:break
                return context
            def step(self):
                nonlocal minimum
                context=self.settle();tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if injected and not self.injected and context==0 and(tag,self.pc)==movement:
                    assert N.get(m,'NmiDisable')&128;self.injected=True;self.nmi();return
                point=points.get((tag,self.pc))
                if point:
                    assert bytes(m[self.pc:self.pc+8])==bytes(point['bytes']),('Changed actual profile point',point,bytes(m[self.pc:self.pc+8]).hex())
                    name=point['name'];sp=self.sp;ret=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                    rt=m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                    self.pending.append(dict(name=name,return_=(ret,(sp+2)&255,rt),start=self.processorCycles,ISR=self.completed_ISR,
                        child=self.interrupts[-1]['child']if context else 0,context=context,entry_SP=sp,render=0,checks=0))
                    calls[name]+=1
                    for scope in self.pending:
                        if scope['name']=='GameLoop'and scope['context']==context:
                            if name=='DrawAllMetasprites':scope['render']+=1
                            if name=='CfOrBtCheck':scope['checks']+=1
                    if name in('CfOrBtCheck','CfA2Router'):service_rows[name,m[0x16c]]+=1
                pc=self.pc;start=self.processorCycles;minimum=min(minimum,self.sp);result=super().step();delta=self.processorCycles-start
                banks[tag]+=delta;pcs[tag,pc]+=delta
                active=next((s for s in reversed(self.pending)if s['context']==context),None)
                if active:exclusive[active['name']]+=delta
                categories['ISR'if context else'Main_or_idle']+=delta
                return result
        with patch.object(N,'NesMPU',Probe):
            for _ in range(count):
                m.controller_pad=pad;Frames.frame(m,whole_pass=True);empty(m)
        for c in instances:c.settle()
        pending=[dict(name=p['name'],PC=c.pc,SP=c.sp,expected=p['return_'])for c in instances for p in c.pending]
        open_ISR=[dict(PC=c.pc,SP=c.sp,kind=p['kind'])for c in instances for p in c.interrupts]
        assert not open_ISR,open_ISR
        row=dict(phase=phase,scheduler_iterations=count,diagnostic_busy_NMI_injected=injected,
            calls=dict(calls),returns=dict(returns),nonlocal_unwinds=dict(unwinds),unclosed_scopes=pending,
            inclusive_excluding_ISR=dict(inclusive),innermost_exclusive=dict(exclusive),
            main_classes=[dict(class_=kind,external_checks=n,calls=k)for(kind,n),k in sorted(main_classes.items())],
            service_frequencies=[dict(name=name,target_low=low,calls=n)for(name,low),n in sorted(service_rows.items())],
            ISR=[dict(kind=k,state=s,metric=t,total=v)for(k,s,t),v in sorted(isr_costs.items())],
            CPU_instruction_categories=dict(categories),mapped_cycles=dict(banks),
            hot_instruction_totals=[dict(tag=t,PC=p,cycles=n)for(t,p),n in pcs.most_common(12)],
            sparse_rows=sparse,minimum_SP=minimum,final_x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),final_y=N.get(m,'Player_Y_Position'))
        all_rows.append(row);print('PROGRESS '+json.dumps(dict(phase=phase,Main=calls['GameLoop'],draw=calls['DrawAllMetasprites'],unclosed=len(pending),unwinds=dict(unwinds))),flush=True)
    return dict(ROM_SHA256=C.H(raw),reference67_SHA256=q['reference67_SHA256'],actual_bc5_CPU_and_private_carrier=True,
        phases=all_rows,nested_scopes_overlap_do_not_sum=True,native30Hz_is_prior_separate_evidence=True,
        source_only_no_physical_video_or_cadence_claim=True,controls_idle_Right_only=True,
        no_actor_shot_health_position_terrain_or_ability_seeds=True,actual_hardware_NMI_component_if_requested=injected,
        no_game_bytes_or_allocations_or_read_overlay=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('inspect','normal','busy'));args=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.CANDIDATE
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Current source profile reread mutable Nightly'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only CF profile attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        result=inspect(raw)if args.mode=='inspect'else profile(raw,args.mode=='busy')
    result.update(mode=args.mode,outputs=0,Mesen_run=False)
    result['source_receipt_SHA256']=C.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
