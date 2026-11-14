"""Private82ec composition/portability and actual source caller observations."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_shared_world_chr_reset_1114 as C
import replay_shared_world_chr_reset_1114 as Replay
import check_shared_world_sprite_images_1114 as Source
import run_stdout_mesen_1110 as Native


def strict(parent):
    original=Path.read_bytes
    def read(p):
        assert p.resolve()!=Replay.ROM.resolve(),'Mutable Downloads read after initial input load'
        return original(p)
    def forbid(*a,**kw):raise RuntimeError('Source-only proposal attempted file output/Mesen')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid):
        candidate,info=C.proposal(parent)
        assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
        rejects=[]
        for name,raw in(('truncated',candidate[:-1]),('parent421',parent)):
            try:C.inverse(raw)
            except AssertionError:rejects.append(name)
            else:raise AssertionError(('Wrong inverse input accepted',name))
        for name,at in(('dirty_owned',1034868),('dirty_unowned',16+8192),('dirty_hidden',971064),('dirty_cheat',0x1e037)):
            raw=bytearray(candidate);raw[at]^=1
            try:C.inverse(bytes(raw))
            except AssertionError:rejects.append(name)
            else:raise AssertionError(('Dirty inverse input accepted',name))
        for name,raw in(('candidate_as_forward_parent',candidate),('truncated_forward',parent[:-1]),
            ('dirty_forward',parent[:16+8192]+bytes((parent[16+8192]^1,))+parent[17+8192:])):
            try:C.proposal(raw)
            except AssertionError:rejects.append(name)
            else:raise AssertionError(('Wrong forward input accepted',name))
        protected=C.Current.protected_envelopes()
        assert all(candidate[at:at+size]==parent[at:at+size]for at,size in protected)
        assert sum(a!=b for a,b in zip(candidate,parent,strict=True))==28
        loader_cases=[]
        for label,boundary_image in(('delivered421',parent),('postdelivery82ec',candidate)):
            reads=[]
            def boundary(p):
                if p.resolve()==Replay.ROM.resolve():
                    reads.append(str(p));assert len(reads)==1,'Only explicit loader boundary may read nightly'
                    return boundary_image
                return read(p)
            with patch.object(Path,'read_bytes',boundary):assert C.load_current_image()==candidate
            assert len(reads)==1;loader_cases.append(label)
        return candidate,dict(info,strict_rejections=rejects,mutable_Downloads_reads=0,
            file_and_Mesen_traps=True,protected_envelope_bytes=sum(size for _,size in protected),
            protected_hidden_and_cheat_fix_bytes=176,exact_portable_inverse_and_roundtrip=True,
            explicit_loader_boundary_cases=loader_cases,loader_boundary_fixture_files=0)


def cold_interrupts(parent,key='hogan'):
    """Capture the real contaminated-preview Start call, then replay ISR cuts."""
    raw,composition=strict(parent)
    native_zero=key in('toad','mario')
    if native_zero:Replay.stage_bindings(raw,'toad')
    else:Replay.bindings(raw,key)
    W,N=Replay.W,Replay.N;base=N.NesMPU;captured=[]
    class Capture(base):
        def step(self):
            m=self.memory
            if not captured and self.pc==C.Measure.START and m.rawtags[0]==254 and m.bundle['raw']==raw:
                captured.append((N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')}))
            return super().step()
    with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
        if native_zero:
            import check_smb1_alts_full11_1114 as Stage
            class StageFactory:
                @staticmethod
                def bindings(image,identity):
                    c=deepcopy(Replay.stage_bindings(image,'toad'))
                    if identity=='mario':c.update(key='mario',name='MARIO',cycle=0,variant=0)
                    return c
            with patch.object(Stage,'Factory',StageFactory):Stage.cold(raw,key)
        else:
            with patch.object(Source,'Factory',Replay):Source.cold(raw,key)
    assert len(captured)==1,'Actual current Start must enter the granted macro'
    arena,registers=captured[0]
    sp=registers['sp'];ret=(arena[256+((sp+1)&255)]+256*arena[256+((sp+2)&255)]+1)&65535
    caller=ret-3;assert caller==0xbc1d and bytes(arena[caller:caller+3])==bytes.fromhex('20308a')
    assert arena.rawtags[(caller-0x8000)//8192]==137,'Actual PRG9 Start caller'
    baseline_cuts=[];minimum=255;irq_masked=0
    def execute(cut=None,kind=None):
        nonlocal minimum,irq_masked
        m=N.fork(arena);cpu=base(memory=m,pc=registers['pc'])
        for n,v in registers.items():setattr(cpu,n,v)
        index=0;injected=False;checks={}
        for _ in range(1000):
            if(cpu.pc,cpu.sp)==(ret,(sp+2)&255):break
            minimum=min(minimum,cpu.sp)
            if C.Measure.START<=cpu.pc<C.Measure.END:
                if cut is None:baseline_cuts.append((index,cpu.pc,cpu.x,cpu.y,cpu.p))
                if cut==index:
                    regs=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                    private=tuple(map(bytes,m.ram));maps=m.rawtags[:];smc=bytes(m[0x15a:0x17b])
                    modes=bytes(m[0x73e0:0x73ef]);banks=m.chr_latches[:]
                    scratch=bytes(m[W.address(m.bundle,'R0'):W.address(m.bundle,'R0')+8])
                    skipped=N.get(m,'NmiSkipped');writes=len(m.ram_writes)
                    reload=N.get(m,'ReloadCHRBank')
                    if kind=='IRQ'and cpu.p&4:
                        irq_masked+=1;checks=dict(masked_by_actual_I=True)
                    else:
                        calls={'BankSwitchCHR':0,'X5PublishChr':0}
                        targets={name:(W.address(m.bundle,name),((W.location(m.bundle,name)-16)//8192)|128)for name in calls}
                        nmi_before=N.get(m,'NmiDisable')
                        cpu.irq()if kind=='IRQ'else cpu.nmi()
                        for _ in range(200000):
                            minimum=min(minimum,cpu.sp)
                            if(cpu.pc,cpu.sp)==regs[:2]:break
                            assert m[cpu.pc],('Actual ISR BRK',kind,hex(cpu.pc))
                            if cpu.pc>=0x8000:
                                tag=m.rawtags[(cpu.pc-0x8000)//8192]
                                for name,target in targets.items():calls[name]+=(cpu.pc,tag)==target
                            base.step(cpu)
                        else:raise AssertionError(('Actual ISR return bound',kind,cut))
                        actual=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                        assert actual[:5]==regs[:5]and actual[5]&0xef==regs[5]&0xef
                        assert tuple(map(bytes,m.ram))==private and not m.ram_writes[writes:]
                        assert m.rawtags==maps and bytes(m[0x15a:0x17b])==smc
                        assert bytes(m[0x73e0:0x73ef])==modes
                        assert N.get(m,'NmiDisable')==nmi_before
                        if native_zero and kind=='NMI'and reload and calls['X5PublishChr']:
                            assert list(modes[1:12])==[0]*11,'Actual native0 fixture has clean logical windows'
                            assert N.get(m,'SsChrActive')==N.get(m,'InvHudActive')==0
                            at=W.location(m.bundle,'ChrPhysicalMap');mapping=raw[at:at+256]
                            expected_banks=[]
                            for i in range(12):
                                value=N.get(m,'CurrentCHRBank',i);mode=modes[i]
                                expected_banks.append((mode&3)*256+value if mode&128 else mapping[value])
                            assert m.chr_latches==expected_banks,dict(reason='Native0 CHR publication expectation',cut=cut,PC=regs[0],
                                actual=m.chr_latches,expected=expected_banks,modes=list(modes),
                                logical=[N.get(m,'CurrentCHRBank',i)for i in range(12)],wide=N.get(m,'X5WideChrActive'))
                            assert N.get(m,'ReloadCHRBank')==0
                        else:assert m.chr_latches==banks
                        assert bytes(m[W.address(m.bundle,'R0'):W.address(m.bundle,'R0')+8])==scratch
                        checks=dict(registers_private_cache_maps_SMC_scratch_modes_and_chr_latches_exact=True,
                            actual_NmiDisable=N.get(m,'NmiDisable'),actual_FamilyMainCommit=N.get(m,'FamilyMainCommit'),
                            NmiSkipped_delta=(N.get(m,'NmiSkipped')-skipped)&255,actual_publication_calls=calls)
                        assert checks['NmiSkipped_delta']==(kind=='NMI')
                    injected=True
                index+=1
            assert m[cpu.pc],('Foreground BRK',hex(cpu.pc));base.step(cpu)
        else:raise AssertionError('Macro continuation bound')
        assert cut is None or injected
        return m,tuple(getattr(cpu,n)for n in('a','x','y','p','sp')),checks
    baseline,expected,_=execute()
    counts={'IRQ':0,'NMI':0};publication_totals={'BankSwitchCHR':0,'X5PublishChr':0};examples=[]
    for index,pc,x,y,p in baseline_cuts:
        for kind in('IRQ','NMI'):
            m,regs,check=execute(index,kind)
            assert regs[:3]==expected[:3]and regs[3]&0xef==expected[3]&0xef and regs[4]==expected[4]
            assert bytes(m[0x73e0:0x73ef])==bytes(baseline[0x73e0:0x73ef])
            counts[kind]+=1
            for name,value in check.get('actual_publication_calls',{}).items():publication_totals[name]+=value
            if len(examples)<4:examples.append(dict(kind=kind,index=index,PC=pc,X=x,Y=y,P=p,check=check))
    return dict(composition=composition,actual_caller=dict(PRG=9,CPU=caller,JSR_hex='20308a',
        macro_entry=registers,modes=list(arena[0x73e0:0x73ef]),
        NmiDisable=N.get(arena,'NmiDisable'),FamilyMainCommit=N.get(arena,'FamilyMainCommit')),
        new_dynamic_instruction_boundaries=len(baseline_cuts),genuine_ISR_cuts=counts,actual_IRQ_masked_cases=irq_masked,
        every_new_PC_covered=sorted({pc for _,pc,*_ in baseline_cuts}),minimum_SP=minimum,examples=examples,
        private0_wide_special_HUD_exact=True,busy_NMI_no_partial_CHR_publication=True,
        native0_lag_NMI_variant_tested=native_zero,actual_publication_totals=publication_totals,
        original_negative_NMI_branch=True,pipe_nextlevel_samepose_gates='PENDING',outputs=0,Mesen_run=False)


def image_routes(parent,key):
    candidate,info=strict(parent)
    with patch.object(Source,'Factory',Replay):q=Source.run(candidate,key)
    assert q['passed'],q
    by_tag={s['tag']:s for s in q['shots']}
    goomba=by_tag['first-live-Goomba'];mush=by_tag['first-natural-mature-Mushroom']
    assert goomba['actual_sprite_banks'][2]==17 and goomba['actual_sprite_banks'][3]==18
    assert mush['actual_sprite_banks'][2]==17 and mush['actual_sprite_banks'][3]==18
    assert key!='hogan'or goomba['actual_sprite_banks'][1]==mush['actual_sprite_banks'][1]==16
    assert key!='prince'or mush['actual_sprite_banks'][1]==383
    assert key!='donkey_kong'or mush['actual_sprite_banks'][1]==823
    return dict(composition=info,route=q,correct_native_Goomba_window=True,
        native_Mushroom_window=key=='hogan',private_Prince_DK_window1_conflicts_still_open=key!='hogan')


def full_transition(parent,secret_pipe=False):
    """Original normal-control Toad1-1→1-2, observing real area-call snapshots."""
    import check_smb1_alts_full11_1114 as Stage
    B=Replay.Previous.Frozen;W,N=Replay.W,Replay.N
    raw,composition=strict(parent);rows=[];pending=[];base=N.NesMPU
    class Factory:
        ROM=Replay.ROM
        IDENTITIES={'toad':B.IDENTITIES['toad']}
        @staticmethod
        def normalize(image):return B.normalize(C.inverse(image))
        @staticmethod
        def bindings(image,key):
            return Replay.stage_bindings(image,key)
        @staticmethod
        def controller(image,key):
            text=Replay.stage_controller(image,key)
            if secret_pipe:
                marker='local nextUpdates,maxX=0,0'
                assert text.count(marker)==1;text=text.replace(marker,marker+'\nlocal pipeRoomUpdates,pipeEntered=0,false',1)
                old="local ok=reason=='full-1-1-and25grounded-1-2'and first and flag and castle and entrance and nextUpdates==25 and identity()and r('NumberofLives')==2"
                new="local ok=reason=='same-level-secret-pipe25grounded'and first and pipeEntered and pipeRoomUpdates>=25 and identity()and r('NumberofLives')==2 and r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==2"
                assert text.count(old)==1;text=text.replace(old,new,1)
                marker='emu.addEventCallback(guard(function()\n polls=polls+1'
                wrapper=r'''
local ordinaryControls=controls
controls=function(c)
 if c.world==0 and c.level==0 and c.areaType==2 then pipeEntered=true;return{}end
 if c.world==0 and c.level==0 and c.areaType==1 and c.r('AreaAddrsLOffset')==5 and c.x>=864 and c.x<992 then
  if c.grounded and c.y>113 and c.x<896 then return c.lastA and{}or{right=true,a=true}end
  if c.grounded and c.y>=110 and c.y<=113 and c.x>=896 and c.x<=920 then return{down=true}end
  local velocity=c.vx<128 and c.vx or c.vx-256
  local stopping=c.x+velocity*math.abs(velocity)/32
  return{right=stopping<910,left=stopping>914,a=c.lastA and c.y>104}
 end
 return ordinaryControls(c)
end
'''
                assert text.count(marker)==1;text=text.replace(marker,wrapper+'\n'+marker,1)
                marker='  local s=state();maxX=math.max(maxX,s.x)'
                observer="""  if active()and r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==2 then
   pipeEntered=true
   if r('Player_State')==0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<224 then pipeRoomUpdates=pipeRoomUpdates+1 else pipeRoomUpdates=0 end
   if pipeRoomUpdates==25 then finish('same-level-secret-pipe25grounded');return end
  end
"""
                assert text.count(marker)==1;text=text.replace(marker,observer+marker,1)
            return text
        @staticmethod
        def metadata(image,key):
            c=Factory.bindings(image,key)
            return dict(ROM_SHA256=C.CANDIDATE,controller_SHA256=sha256(Factory.controller(image,key).encode()).hexdigest(),
                original421_controller_SHA256=sha256(B.controller(C.inverse(image),key).encode()).hexdigest(),
                only_granted29B_native_bank_delta=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
    def snapshot(m,c):
        return dict(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,
            selected=N.get(m,'SelectedCharacter'),variant=N.get(m,'MarioVariant'),
            world=N.get(m,'WorldNumber'),level=N.get(m,'LevelNumber'),area=N.get(m,'AreaType'),
            AreaChrBank=N.get(m,'AreaChrBank'),modes=list(m[0x73e0:0x73ef]),
            banks=[N.get(m,'CurrentCHRBank',i)for i in range(12)],
            private_cache_SHA256=[sha256(bytes(m.ram[i])).hexdigest()for i in(2,3)],
            NmiDisable=N.get(m,'NmiDisable'),FamilyMainCommit=N.get(m,'FamilyMainCommit'))
    class Trace(base):
        def step(self):
            m=self.memory
            if m.bundle.get('raw')==raw:
                for p in list(pending):
                    if(self.pc,self.sp)==p['return']:
                        p['row']['returned']=snapshot(m,self);p['row']['macro_taken']=p['macro_taken']
                        pending.remove(p)
                area_entry=self.pc==W.address(m.bundle,'GetAreaType')and not pending
                if(self.pc==0x8a30 or area_entry)and m.rawtags[0]==254:
                    assert len(rows)<16,'Bounded actual area-call census'
                    ret=(m[256+((self.sp+1)&255)]+256*m[256+((self.sp+2)&255)]+1)&65535
                    row=dict(entry_name='GetAreaType'if area_entry else'LoadAreaPointer',entry=snapshot(m,self),caller=ret-3,caller_tag=m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1)
                    rows.append(row);pending.append(dict(row=row,return_ignored=False,**{'return':(ret,(self.sp+2)&255)},macro_taken=False))
                if self.pc==C.Measure.START and m.rawtags[0]==254:
                    assert pending;pending[-1]['macro_taken']=True
            return super().step()
    # The existing source runner supplies genuine compiled Select/Start and
    # original controller decisions. Only its explicit new factory is replaced.
    with patch.object(Stage,'Factory',Factory),patch.object(N,'NesMPU',Trace),patch.object(W.UI.F,'NesMPU',Trace):
        q=Stage.run(raw,'toad',limit=2200 if secret_pipe else 8500)
    assert q['passed']and not pending,dict(reason=q.get('receipt',{}).get('reason'),terminal=q.get('receipt',{}).get('terminal'),rows=rows)
    assert any(row.get('macro_taken')for row in rows)
    assert any(row.get('returned',{}).get('level')==(0 if secret_pipe else 1)and row.get('returned',{}).get('area')==2 for row in rows),'Actual underground area call'
    for row in rows:
        a,z=row['entry'],row['returned']
        assert z['modes'][0]==a['modes'][0]and z['modes'][12:]==a['modes'][12:]
        assert z['private_cache_SHA256']==a['private_cache_SHA256']
        if row['macro_taken']:assert z['modes'][1:12]==[0]*11
        else:assert z['modes']==a['modes']
    return dict(composition=composition,source_full11_passed=not secret_pipe,source_receipt_SHA256=q['source_receipt_SHA256'],
        source_Main_passes=q['source_scheduler_passes'],controller_metadata=q['metadata'],
        actual_area_callers=rows,terminal=q['receipt']['terminal'],outputs=0,Mesen_run=False,
        scope='Actual normal-controller same-level secret-pipe area transition to25grounded'if secret_pipe else'Actual normal-controller full1-1/next-level/pipe entrance to25grounded1-2; source clock only',
        shortcut_pipe_case=secret_pipe)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=('prince','hogan','donkey_kong','toad','mario'))
    p.add_argument('--interrupts',action='store_true')
    p.add_argument('--full-transition',action='store_true')
    p.add_argument('--secret-pipe',action='store_true')
    a=p.parse_args();parent=Replay.ROM.read_bytes()
    q=full_transition(parent,a.secret_pipe)if a.full_transition or a.secret_pipe else cold_interrupts(parent,a.identity or'hogan')if a.interrupts else image_routes(parent,a.identity)if a.identity else strict(parent)[1]
    print(json.dumps(q,separators=(',',':')),flush=True)
