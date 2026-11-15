"""Exact granted Gimmick7 source qualification, in memory and stdout only."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import compose_gimmick_private_window7_1114 as C
import replay_gimmick_private_window7_1114 as F
import check_mr_gimmick_full11_current_1114 as Stage
import check_gimmick_private7_callers_1114 as Owners
import check_shared_world_sprite_images_1114 as Images
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=F.W,F.N


def strict(parent):
    raw,info=C.proposal(parent);assert C.inverse(raw)==parent and C.proposal(C.inverse(raw))[0]==raw
    rejects=[]
    for label,image,method in(('parent_as_inverse',parent,C.inverse),('candidate_as_forward',raw,C.proposal),
        ('truncated',raw[:-1],C.inverse),('old82',C.Parent.inverse(parent),C.proposal)):
        try:method(image)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Wrong image accepted',label))
    for label,at in(('dirty_publisher',622194),('dirty_metadata',604999),('dirty_unowned',90000),('dirty_DK',105706),('dirty_common',1034868)):
        changed=bytearray(raw);changed[at]^=1
        try:C.inverse(bytes(changed))
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Dirty inverse accepted',label))
    original=Path.read_bytes
    def read(path):
        assert path.resolve()!=F.ROM.resolve(),'No mutable Nightly inverse/proposal dependency'
        return original(path)
    with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent and C.proposal(parent)[0]==raw
    boundary_cases=[]
    for name,image in(('parent1daca',parent),('postdelivery_cf7b',raw)):
        calls=[]
        def boundary(path):
            if path.resolve()==F.ROM.resolve():calls.append(1);assert len(calls)==1;return image
            return read(path)
        with patch.object(Path,'read_bytes',boundary):assert C.load_current_image()==raw
        assert len(calls)==1;boundary_cases.append(name)
    return raw,dict(info,strict_rejections=rejects,portable_inverse_roundtrip=True,
        mutable_Nightly_rereads=0,explicit_single_read_loader_cases=boundary_cases)


def cold(raw):
    with patch.object(Stage,'Factory',F):return Stage.cold(raw)


def emitter_units(parent):
    raw,info=strict(parent);old=Stage.cold(parent);new=cold(raw);b=new.bundle
    cases=0;parts=0
    for name,count in(('GmHeroTable',22),('GmStarTable',66),('GmEffectTable',4)):
        table=W.location(b,name);bank=(table-16)//8192
        for index in range(count):
            ptr=int.from_bytes(parent[table+2*index:table+2*index+2],'little')
            for facing in(0,1):
                for attr in(0,1,64,65,128,129,192,193):
                    for flags in(0x20,0x21,0x60,0xe1):
                        pair=[N.fork(old),N.fork(new)];returns=[]
                        for m in pair:
                            m.raw_page(2,bank|128);N.put(m,CurrentBankC=bank|128)
                            N.put(m,R0=ptr&255,R1=ptr>>8,R3=attr,R4=96,R5=0,R6=120,R7=1,
                                GmTemp2=facing,CurrentOAMOffset=0,GuestOamRotationActive=0)
                            returns.append(N.invoke(m,'GmEmitRecord',a=83,x=71,y=109,p=flags))
                        assert all(returns[0][k]==returns[1][k]for k in('A','X','Y','P','CPU','minimum_SP'))
                        assert N.get(pair[0],'CurrentOAMOffset')==N.get(pair[1],'CurrentOAMOffset')
                        for i in range(N.get(pair[0],'CurrentOAMOffset')):
                            a,z=pair[0][512+i],pair[1][512+i]
                            if i%4==1 and a>=64:assert z==(a&63)|193 and z&62==a&62
                            else:assert a==z,(name,index,facing,attr,flags,i,a,z)
                        parts+=N.get(pair[1],'CurrentOAMOffset')//4;cases+=1
    return dict(composition=info,actual_emitter_pose_facing_attribute_flags_cases=cases,actual_parts=parts,
        geometry_attributes_order_pair_offsets_and_complete_ABI_exact=True,CPU_cycles_and_stack_exact=True,
        outputs=0,Mesen_run=False)


def public_units(parent):
    raw,info=strict(parent);old=Stage.cold(parent);new=cold(raw);b=new.bundle;cases=0
    def compare(name,pair):
        nonlocal cases
        results=[N.invoke(m,name,a=83,x=71,y=109,p=0xe1)for m in pair]
        assert all(results[0][k]==results[1][k]for k in('A','X','Y','P','CPU','minimum_SP')),(name,results)
        for i in range(256):
            a,z=pair[0][512+i],pair[1][512+i]
            if i%4==1 and 64<=a<128:assert z==(a&63)|193
            else:assert a==z,(name,i,a,z)
        assert bytes(pair[0][0x5c00:0x5c80])==bytes(pair[1][0x5c00:0x5c80]),name
        assert bytes(pair[0][0:256])==bytes(pair[1][0:256]),('Live zero page',name)
        assert bytes(pair[0][0x15a:0x17b])==bytes(pair[1][0x15a:0x17b]),('Farcall SMC',name)
        cases+=1
    for pose in range(22):
        pair=[N.fork(old),N.fork(new)]
        for m in pair:N.put(m,GmRam0300=pose,GmRam036E=128,GmRam038C=0)
        compare('GmGraphics',pair)
        for facing in(0,1):
            draw=[N.fork(m)for m in pair]
            for m in draw:N.put(m,GmRam030A=facing,CurrentOAMOffset=0,GuestOamRotationActive=0)
            compare('GmDraw',draw)
    for facing in(0,1):
        pair=[N.fork(old),N.fork(new)]
        for m in pair:N.put(m,R4=96,R5=0,R6=120,CurrentOAMOffset=0,GuestOamRotationActive=0)
        results=[N.invoke(m,'GmPortrait',a=facing,x=71,y=109,p=0xe1)for m in pair]
        assert all(results[0][k]==results[1][k]for k in('A','X','Y','P','CPU','minimum_SP'))
        assert bytes(pair[0][512:768])==bytes(pair[1][512:768]);cases+=1
    for frame in range(66):
        pair=[N.fork(old),N.fork(new)]
        for m in pair:
            N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,GmRam0091=1,GmRam0301=frame,
                GmRam00AF=128,GmRam00B9=8,GmRam009B=128,GmRam00A5=7,GmVisible=1)
            history=W.address(b,'GmHistory');effects=W.address(b,'GmEffects')
            m[history:history+20]=bytes(20);m[effects:effects+28]=bytes(28)
        compare('GmDraw',pair)
    for effect in range(4):
        pair=[N.fork(old),N.fork(new)]
        for m in pair:
            N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,GmRam0091=0,GmVisible=1)
            at=W.address(b,'GmEffects');m[at:at+28]=bytes(28);m[at:at+4]=bytes((128,8,128,((1 if effect==0 else effect*4)<<4)|7))
        compare('GmDraw',pair)
    return dict(composition=info,public_graphics_portrait_all_star_and_effect_cases=cases,complete_ABI_CPU_stack_private_state_exact=True,
        outputs=0,Mesen_run=False)


def image_route(parent):
    raw,info=strict(parent)
    with patch.object(Images,'Factory',F.ImageFactory):q=Images.run(raw,'mr_gimmick',1800)
    assert q['passed'],q
    assert all(s['actual_sprite_banks'][1:4]==[16,17,18]and s['actual_sprite_banks'][7]==818 for s in q['shots'])
    return dict(composition=info,route=q,correct_world1_and_private7=True,outputs=0,Mesen_run=False)


def stage_route(parent):
    raw,info=strict(parent)
    with patch.object(Runner,'Factory',F),patch.object(Runner,'cold',lambda image,key:cold(image)):
        q=Runner.run(raw,'mr_gimmick',9000)
    assert q['passed'],q
    return dict(composition=info,route=q,outputs=0,Mesen_run=False)


def owners(parent):
    raw,info=strict(parent)
    with patch.object(Owners,'F',F),patch.object(Stage,'Factory',F):q=Owners.run(raw)
    q.update(candidate_not_composed=False,allocation_granted=True,composition=info)
    return q


def capture_renderers(raw):
    """Snapshot only calls reached by genuine UI/Start and ordinary B input."""
    b=dict(W.Symbols.bundle(),raw=raw);base=N.NesMPU;captures={};calls={}
    entries={(((W.location(b,n)-16)//8192)|128,W.address(b,n)):n
        for n in('GmGraphics','GmPortrait','GmDraw')}
    class Trace(base):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            name=entries.get((tag,self.pc))
            if name and N.get(m,'SelectedCharacter')==26:
                mode=N.get(m,'OperMode');star=N.get(m,'GmRam0091')
                suffix=('menu'if mode==0 else'lives'if N.get(m,'OperMode_Task')!=3 else
                    'star'if star==1 else'charge'if star>=128 else'body')
                key=name+'_'+suffix;calls[key]=calls.get(key,0)+1
                if key not in captures:
                    captures[key]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')})
            return super().step()
    with patch.object(N,'NesMPU',Trace),patch.object(W.UI.F,'NesMPU',Trace):
        m=cold(raw)
        for tick in range(72):
            m.controller_pad=64 if tick<48 else 0;Frames.frame(m,whole_pass=True)
    assert any(n.startswith('GmPortrait_')for n in captures)
    assert 'GmGraphics_body'in captures and 'GmDraw_star'in captures,(list(captures),calls)
    return captures,calls


def interrupts(parent):
    raw,info=strict(parent);captures,calls=capture_renderers(raw);base=N.NesMPU;rows=[];minimum=255
    # The exact executed publisher LDY instructions and metadata LDA/STA/INY
    # sequence are unchanged in size. These are reached boundaries, not newly
    # allocated executable PCs or an invented regular-NMI arm inside Main.
    b=dict(W.Symbols.bundle(),raw=raw);begin=W.location(b,'GmEmitRecord');code=raw[begin:begin+200]
    marker=bytes((0xb1,W.address(b,'R0'),0x9d))+W.address(b,'Sprite_Tilenumber').to_bytes(2,'little')+b'\xc8'
    assert code.count(marker)==1
    tilepc=W.address(b,'GmEmitRecord')+code.index(marker)
    tiletag=((begin-16)//8192)|128
    pubs={(203,48737),(203,48739),(203,48956),(203,48958)}
    # Cold GmGraphics/Portrait are physical PRG75 (raw203).
    for name,(arena,registers)in captures.items():
        sp=registers['sp'];ret=(arena[256+((sp+1)&255)]+256*arena[256+((sp+2)&255)]+1)&65535
        boundaries=[]
        def execute(cut=None,kind=None):
            nonlocal minimum
            m=N.fork(arena);cpu=base(memory=m,pc=registers['pc'])
            for key,value in registers.items():setattr(cpu,key,value)
            index=0;injected=False;masked=False
            for _ in range(20000):
                if(cpu.pc,cpu.sp)==(ret,(sp+2)&255):break
                minimum=min(minimum,cpu.sp)
                tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                owned=(tag,cpu.pc)in pubs or(tag==tiletag and cpu.pc in(tilepc,tilepc+2,tilepc+5,tilepc+6))
                setter=tag==190 and 0xa275<=cpu.pc<0xa289 and cpu.y==7
                if owned or setter:
                    if cut is None:boundaries.append((index,cpu.pc,tag))
                    if cut==index:
                        regs=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                        before=dict(private=tuple(map(bytes,m.ram)),maps=m.rawtags[:],smc=bytes(m[0x15a:0x17b]),
                            modes=bytes(m[0x73e0:0x73ef]),latches=m.chr_latches[:],upper=m.upper,
                            skipped=N.get(m,'NmiSkipped'),disable=N.get(m,'NmiDisable'))
                        # Menu calls do not have Main's busy arm and are kept
                        # separately; regular-NMI assertions require a genuine
                        # scheduler state rather than leaf-fixture injection.
                        if not before['disable']&128:
                            raise AssertionError(('Reached non-busy context needs separate ISR contract',name,before['disable']))
                        if kind=='IRQ'and cpu.p&4:masked=True
                        else:
                            cpu.irq()if kind=='IRQ'else cpu.nmi()
                            for _ in range(200000):
                                minimum=min(minimum,cpu.sp)
                                if(cpu.pc,cpu.sp)==regs[:2]:break
                                assert m[cpu.pc],('ISR BRK',name,kind,hex(cpu.pc));base.step(cpu)
                            else:raise AssertionError('ISR return bound')
                            actual=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                            assert actual[:5]==regs[:5]and actual[5]&0xef==regs[5]&0xef
                            assert tuple(map(bytes,m.ram))==before['private']and m.rawtags==before['maps']
                            assert bytes(m[0x15a:0x17b])==before['smc']and bytes(m[0x73e0:0x73ef])==before['modes']
                            assert m.chr_latches==before['latches']and m.upper==before['upper']
                            assert N.get(m,'NmiDisable')==before['disable']
                            assert(N.get(m,'NmiSkipped')-before['skipped'])&255==(kind=='NMI')
                        injected=True
                    index+=1
                assert m[cpu.pc],('Renderer continuation BRK',name,hex(cpu.pc));base.step(cpu)
            else:raise AssertionError(('Captured actual renderer return bound',name))
            assert cut is None or injected
            return m,tuple(getattr(cpu,n)for n in('a','x','y','p','sp')),masked
        baseline,regs,_=execute();counts={'IRQ':0,'NMI':0};masked=0
        for index,pc,tag in boundaries:
            for kind in('IRQ','NMI'):
                m,returned,was_masked=execute(index,kind)
                assert returned[:3]==regs[:3]and returned[3]&0xef==regs[3]&0xef and returned[4]==regs[4]
                assert bytes(m[512:768])==bytes(baseline[512:768])
                assert bytes(m[0x73e0:0x73ef])==bytes(baseline[0x73e0:0x73ef])
                counts[kind]+=1;masked+=was_masked
        rows.append(dict(context=name,actual_entry=registers,actual_return_PC=ret,actual_return_SP=(sp+2)&255,
            instruction_boundaries=len(boundaries),PCs=sorted({pc for _,pc,_ in boundaries}),cuts=counts,IRQ_masked_by_actual_I=masked))
    return dict(composition=info,actual_reached_renderer_calls=calls,actual_instruction_cut_contexts=rows,
        minimum_SP=minimum,regular_NMI_inside_busy_unreachable=True,
        regular_post_update_NMI='Naturally exercised by ordinary source frame scheduler and source image/full-stage routes',
        outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emitters',action='store_true');p.add_argument('--public',action='store_true');p.add_argument('--images',action='store_true');p.add_argument('--stage',action='store_true');p.add_argument('--owners',action='store_true');p.add_argument('--interrupts',action='store_true');a=p.parse_args()
    raw=C.load_current_image();parent=C.inverse(raw)
    def forbid(*args,**kwargs):raise RuntimeError('Memory-only Gimmick7 checker attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=interrupts(parent)if a.interrupts else owners(parent)if a.owners else stage_route(parent)if a.stage else image_route(parent)if a.images else public_units(parent)if a.public else emitter_units(parent)if a.emitters else strict(parent)[1]
    q['file_and_Mesen_traps']=True;print(json.dumps(q,separators=(',',':')),flush=True)
