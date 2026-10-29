"""Finite actual-ROM differential callers, strict RAM/SMC transport and IRQ/NMI.

Only genuine relocated PC/pointer/bank transport is translated. No blanket
stack, SMC, scratch, register or gameplay-memory exclusion is permitted.
"""
from pathlib import Path
import collections, hashlib, itertools, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_rygar_powerups_prepare_v1 import setup as scene
from current_roster_compact_11_v1 import BASE as IDENTITIES
import current_darkwing_roll_earned_cpu_v1 as Earned
import smb2_roster_audio_plan_v1 as Plan

OUT=ROOT/'build/smb2-roll-relocation-v1'
BASE=Plan.PARENT
CANDIDATE=OUT/'candidate.nes'
MOVE={119:(79,0xb00),120:(78,0x1000)}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bind=Plan.binding

def mapbank(bank):return MOVE.get(bank,(bank,0))[0]
def mapsite(pc,bank):return(pc+MOVE[bank][1],mapbank(bank))if bank in MOVE else(pc,bank)

class Pair:
    def __init__(self,bundles,char=9,variant=1,mode=1):
        self.q=[Arena(b,char)for b in bundles];self.tags={};self.sites=set();self.rows=[]
        for q in self.q:
            q.put(RlVariant=variant,CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaType=1)
            q.array('GameTimerDisplay',[3,9,9]);scene(q,dict(kind='idle',face=1,hit=False))
            q.m[0x5204]=128
        self.cur=address(bundles[0],'CurrentBank')
        self.smc=next(s for s in bundles[0]['segs'].values()if s['name']=='"SMCCODE"')
        self.smc_start=int(self.smc['start'],0);self.smc_n=int(self.smc['size'],0)
        self.bankfields={self.cur,0x5115,address(bundles[0],'NextBank_SMC')+1}
        self.pointerfields={address(bundles[0],'FarcallJmpTarget_SMC')+1,address(bundles[0],'FarcallJmpTarget_SMC')+2}
        self.smc_fields=self.pointerfields|{address(bundles[0],n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC']}
        self.stats=collections.Counter()

    def put(self,**kw):
        for q in self.q:q.put(**kw)
    def set(self,n,v,i=0):
        for q in self.q:q.set(n,v,i)
    def tag(self,p,kind):
        a,b=(q.m[p]for q in self.q)
        if a==b:self.tags.pop(p,None)
        else:self.tags[p]=(kind,a,b)

    def assert_RAM(self,context):
        a,b=(q.m for q in self.q)
        wrong=[]
        for p in range(0x8000):
            if a[p]!=b[p]:
                tag=self.tags.get(p)
                if not tag or(a[p],b[p])!=tag[1:]:wrong.append((hex(p),a[p],b[p],tag))
        assert not wrong,('fullRAM',context,wrong[:15])

    def call(self,name,a=0,x=0,y=0,p=0x30,start=None,stop=None,inject=None,limit=100000):
        cpus=[];entry=[]
        for j,q in enumerate(self.q):
            if start:
                bank,pc=start if j==0 else(mapbank(start[0]),mapsite(start[1],start[0])[0])
                window=(pc-0x8000)//8192;q.m.page(window,bank)
                if window in(1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
            else:
                sym=q.b['syms'][name];seg=q.b['segs'][sym['seg']]
                bank=(int(seg['ooffs'],0)-16)//8192;pc=address(q.b,name)
                window=(pc-0x8000)//8192;q.m.page(window,bank)
                if window in(1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
            c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xfd
            c.stPushWord(0x5aff);cpus.append(c);entry.append((pc,bank))
            q.m.writes=[]
        self.tag(self.cur,'bank')
        for at in [0x1fc,0x1fd]:self.tag(at,'outer-sentinel')
        # Explicit per-byte source provenance, including inactive stack slots.
        regtags={'a':None,'x':None,'y':None};cycles0=[c.processorCycles for c in cpus]
        visited=[];fired=False;low=255;events=0
        for count in range(limit):
            c,d=cpus;ms=[q.m for q in self.q]
            ends=[0x5b00,0x5b00]if stop is None else[stop,mapsite(stop,start[0])[0]]
            if c.pc==ends[0]:
                assert inject is None or fired,('requested interrupt site not reached',name,inject)
                assert d.pc==ends[1]and(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp),('returnedCPU',name)
                assert c.processorCycles-cycles0[0]==d.processorCycles-cycles0[1],('cycles',name,c.processorCycles,d.processorCycles)
                assert ms[1].banks==list(map(mapbank,ms[0].banks)),('return banks',name,ms[0].banks,ms[1].banks)
                self.assert_RAM(name)
                row=dict(name=name,instructions=count,cycles=c.processorCycles-cycles0[0],minimum_SP=low,
                    fullRAM=True,ordered_writes=events,interrupt=inject is not None)
                self.rows.append(row);return row,visited
            bank=ms[0].banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            nbank=ms[1].banks[(d.pc-0x8000)//8192]if d.pc>=0x8000 else -1
            assert mapsite(c.pc,bank)==(d.pc,nbank),('physicalPC',name,hex(c.pc),bank,hex(d.pc),nbank)
            self.sites.add((c.pc,bank));visited.append((c.pc,bank));low=min(low,c.sp,d.sp)
            assert(c.p,c.sp)==(d.p,d.sp),('P/SP',name,hex(c.pc),c.p,d.p,c.sp,d.sp)
            for reg in regtags:
                u,v=getattr(c,reg),getattr(d,reg)
                assert u==v or(regtags[reg]and regtags[reg][1:]==(u,v)),('register transport',name,hex(c.pc),reg,u,v,regtags[reg])
            if inject and not fired and(c.pc,bank)==inject[1]:
                self.interrupt(cpus,inject[0],regtags);fired=True
                # Interrupt leaves all caller CPU state unchanged, so live tags
                # remain genuine. Its precise dead return-PC bytes are tagged.
            op=c.memory[c.pc];nop=d.memory[d.pc]
            assert op==nop and op!=0,('opcode',name,hex(c.pc),op,nop)
            mn,mode=c.disassemble[op]
            pre=[(z.pc,z.a,z.x,z.y,z.p,z.sp)for z in cpus]
            # Determine the exact differing source read before executing it.
            incoming=None;destreg=None
            if mn in['LDA','LDX','LDY']:
                destreg={'LDA':'a','LDX':'x','LDY':'y'}[mn]
                if mode=='imm':
                    u,v=ms[0][c.pc+1],ms[1][d.pc+1]
                    if u!=v:
                        tag=self.tags.get(c.pc+1)if c.pc<0x8000 else None
                        if tag:incoming=tag
                        else:
                            assert mn=='LDA'and c.pc>=0x8000,'unqualified changed immediate'
                            # Only the independently exact18-byte farcall patch
                            # can have changed an instruction literal.
                            kind='bank'if(u&127)in MOVE and v==mapbank(u&127)|(u&128)else'pointer'
                            incoming=(kind,u,v)
                elif mode in['abs','zpg']:
                    addr=ms[0][c.pc+1]+(256*ms[0][c.pc+2]if mode=='abs'else 0)
                    naddr=ms[1][d.pc+1]+(256*ms[1][d.pc+2]if mode=='abs'else 0)
                    if addr==naddr:incoming=self.tags.get(addr)
            elif mn=='PLA':destreg='a';incoming=self.tags.get(0x100+((c.sp+1)&255))
            elif mn in['TAX','TAY','TXA','TYA']:
                src,destreg={'TAX':('a','x'),'TAY':('a','y'),'TXA':('x','a'),'TYA':('y','a')}[mn]
                incoming=regtags[src]
            starts=[len(m.writes)for m in ms]
            c.step();d.step()
            wa=ms[0].writes[starts[0]:];wb=ms[1].writes[starts[1]:]
            assert len(wa)==len(wb),('write count',name,hex(pre[0][0]))
            for i,((at,u),(nt,v))in enumerate(zip(wa,wb)):
                assert at==nt,('write address',name,hex(pre[0][0]),at,nt)
                events+=1
                if u==v:self.tags.pop(at,None);continue
                if 0x100<=at<0x200 and mn=='JSR':
                    shift=8 if i==0 else 0
                    assert(u,v)==(((pre[0][0]+2)>>shift)&255,((pre[1][0]+2)>>shift)&255)
                    tag=('returnPC',u,v)
                elif 0x100<=at<0x200 and mn=='PHA':tag=regtags['a']
                elif at in self.bankfields:tag=regtags['a']
                elif at in self.pointerfields:tag=regtags['a']
                else:raise AssertionError(('nontransport RAM differs',name,hex(pre[0][0]),hex(at),u,v))
                assert tag and tag[1:]==(u,v),('write provenance',name,hex(pre[0][0]),hex(at),u,v,tag)
                if at in self.bankfields:assert tag[0]=='bank'
                if at in self.pointerfields:assert tag[0]=='pointer'
                self.tags[at]=tag;self.stats[tag[0]]+=1
            if destreg:regtags[destreg]=incoming if getattr(c,destreg)!=getattr(d,destreg)else None
            # Any arithmetic mutation of a tagged value is a real mismatch,
            # rather than an invitation to normalize arbitrary game outputs.
            for reg in regtags:
                if getattr(c,reg)==getattr(d,reg):regtags[reg]=None
                elif regtags[reg]:assert regtags[reg][1:]==(getattr(c,reg),getattr(d,reg)),('modified transport value',name,mn,reg)
        raise AssertionError(('bounded return',name,hex(cpus[0].pc)))

    def interrupt(self,cpus,kind,regtags):
        snapshots=[];origins=[]
        for c,q in zip(cpus,self.q):
            m=q.m;smc=bytes(m[self.smc_start:self.smc_start+self.smc_n])
            snapshots.append(((c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,m.banks.copy()),smc))
            cause={p:('existing',tag)for p,tag in self.tags.items()if 0x100<=p<0x200}
            caller=snapshots[-1][0]
            cause[0x100+c.sp]=('hardware-returnPC',8)
            cause[0x100+((c.sp-1)&255)]=('hardware-returnPC',0)
            atag=('callerA',regtags['a'])if regtags['a']else None
            if kind=='IRQ':
                assert not c.p&4,'IRQ must actually enter';c.irq()
            else:c.nmi()
            for _ in range(30000):
                at=c.pc;op=m[at];mn,mode=c.disassemble[op];before=len(m.writes)
                newtag=None;changesA=False
                if mn=='LDA':
                    changesA=True
                    if mode in['abs','zpg']:
                        src=m[at+1]+(256*m[at+2]if mode=='abs'else 0)
                        if src in self.bankfields:newtag=('bank-read',src)
                        elif src in self.tags:newtag=('existing',self.tags[src])
                    elif mode=='imm'and at+1 in self.tags:newtag=('existing',self.tags[at+1])
                elif mn=='PLA':changesA=True;newtag=cause.get(0x100+((c.sp+1)&255))
                elif mn in['TXA','TYA','ADC','SBC','AND','ORA','EOR','ASL','LSR','ROL','ROR']:
                    changesA=mn in['TXA','TYA','ADC','SBC','AND','ORA','EOR']or mode=='acc'
                c.step()
                for i,(p,v)in enumerate(m.writes[before:]):
                    if p in self.bankfields or p in self.pointerfields:cause[p]=atag if mn=='STA'else None
                    if 0x100<=p<0x200:
                        if mn=='PHA':cause[p]=atag
                        elif mn=='JSR':cause[p]=('handler-returnPC',at,8 if i==0 else 0)
                        else:cause[p]=None
                if changesA:atag=newtag
                if c.pc==snapshots[-1][0][0]and c.sp==snapshots[-1][0][5]:break
            else:raise AssertionError(('interrupt did not return',kind,hex(c.pc)))
            old,smc=snapshots[-1]
            assert(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp)==old[:6],('interruptCPU',kind,old)
            assert m.banks==old[6],('interrupt bank restoration',kind,old,m.banks)
            assert smc==bytes(m[self.smc_start:self.smc_start+self.smc_n]),('interrupt SMC',kind)
            origins.append(cause)
        # Hardware stacked PCs are the ONLY differing interrupt-pushed values.
        for p in range(0x100,0x200):
            u,v=(q.m[p]for q in self.q)
            if u!=v:
                if p in self.tags and self.tags[p][1:]==(u,v):continue
                origin,norigin=origins[0].get(p),origins[1].get(p)
                assert origin and norigin,('interrupt stack lacks actual writer',hex(p),u,v)
                if origin[0]=='hardware-returnPC':
                    assert norigin==origin;shift=origin[1]
                    a,b=snapshots[0][0][0],snapshots[1][0][0]
                    assert(u,v)==((a>>shift)&255,(b>>shift)&255)
                elif origin[0]=='bank-read':
                    assert origin==norigin and v==mapbank(u&127)|(u&128)
                elif origin[0]in['existing','callerA']:
                    assert origin==norigin and origin[1]and origin[1][1:]==(u,v)
                else:raise AssertionError(('unqualified interrupted stack difference',hex(p),u,v,origin,norigin))
                self.tags[p]=('actual-interrupt-transport',u,v)
        for p in self.bankfields:
            u,v=(q.m[p]for q in self.q)
            if u==v:self.tags.pop(p,None);continue
            if p in self.tags and self.tags[p][1:]==(u,v):continue
            origin,norigin=origins[0].get(p),origins[1].get(p)
            assert origin and origin==norigin,('interrupt bank write provenance',hex(p),u,v,origin,norigin)
            assert origin[0]in['bank-read','existing','callerA']and v==mapbank(u&127)|(u&128)
            self.tags[p]=('actual-interrupt-bank-transport',u,v)
        self.assert_RAM(kind)


def main():
    build=json.loads((OUT/'build-proof.json').read_text());assert sha(CANDIDATE)==build['candidate']['sha256']
    bundles=list(map(scoped_load,[BASE,CANDIDATE]));rows=[];transport=collections.Counter();seams=[]
    def record(pair,*args,**kw):
        row,sites=pair.call(*args,**kw);rows.append(row);transport.update(pair.stats);pair.stats.clear();return sites
    # Complete actual Movement/Weapons/Graphics/Draw/HUD callers in both numeric
    # modes; source arena stages terrain only, real RlEnsure owns initialization.
    for mode in[0,1]:
        q=Pair(bundles,mode=mode)
        for bits in[0,1,65,128,129,0,2,66,0]:
            q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192)
            for name in['RlMovementDispatch','RlWeaponsDispatch','RlGraphicsDispatch','RlLegacyDrawDispatch','RlUiDispatch']:
                record(q,name,p=0x30)
        # Every incoming actual18-byte farcall stub is exercised in its real
        # caller bank, returning at its true continuation or outer tail return.
        plan=json.loads((ROOT/'build/smb2-roster-audio-plan-v1.json').read_text())
        for edge in plan['emitted_farcall_edges']:
            if edge['source_bank']in MOVE or edge['target_bank']not in MOVE:continue
            q=Pair(bundles,mode=mode);pc=int(edge['pc'],16)
            q.call('RlEnsure')
            q.put(SavedJoypadBits=0,A_B_Buttons=0)
            record(q,'incoming:'+','.join(edge['names']),start=(edge['source_bank'],pc),
                stop=pc+18 if edge['kind']=='JSR'else None,p=0x30)
    # All selector bytes and every nonzero variant are actual compiled guard
    # calls, including hostile values; no generic char-indexed consumer sees
    # an invalid identity in these guard-only controls.
    for mode in[0,1]:
        q=Pair(bundles,mode=mode)
        for char,variant in list(itertools.product(range(256),[1]))+list(itertools.product([9],range(256))):
            q.put(SelectedCharacter=char,RlVariant=variant)
            record(q,'RlIsActive',p=0x30)
        for bits in range(256):
            q=Pair(bundles,mode=mode);q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192)
            record(q,'RlMovementDispatch',p=0x79 if bits&1 else 0x30)
    # All actual37 inherited roster identities receive complete legal main
    # callers, not just a false branch in RlIsActive. Old helper seeds are
    # disclosed CPU arenas, not earned/native coverage.
    for identity,(_,char,variant_field,variant)in IDENTITIES.items():
        for mode in[0,1]:
            q=Pair(bundles,char=char,variant=variant if char==9 else 0,mode=mode)
            if variant_field:q.set(variant_field,variant)
            for bits in[0,65]:
                q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,FrameCounter=3)
                record(q,'GameLoop',p=0x30)
    # Additional currently linked expansion identities are cold-initialized
    # through the genuine new-roster reset before the same Main comparison.
    # Unlinked FF/Dragon/SMB2/Rogue components are deliberately not admitted.
    expansion=[('popo','CHARACTER_ICE_CLIMBERS','IcVariant',0),('nana','CHARACTER_ICE_CLIMBERS','IcVariant',1),
        ('alex','CHARACTER_RIVER_CITY','RcVariant',0),('ryan','CHARACTER_RIVER_CITY','RcVariant',1),
        ('sunny','CHARACTER_SUNNY',None,0),('celeste',None,'MarioVariant',4)]
    for identity,char_symbol,variant_field,variant in expansion:
        for mode in[0,1]:
            q=Pair(bundles,char=address(bundles[0],char_symbol)if char_symbol else 0,variant=0,mode=mode)
            if variant_field:q.set(variant_field,variant)
            record(q,'NrReset',p=0x30)
            for bits in[0,65]:
                q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,FrameCounter=3)
                record(q,'GameLoop',p=0x30)
    # Source-complete owned progression over genuine Main callbacks; NMI
    # scheduling is not invented. Clock is an explicit equal arena input.
    for mode in[0,1]:
        q=Pair(bundles,mode=mode)
        for tick in range(96):
            bits=65 if tick<32 else(129 if tick<48 else(2 if tick<72 else 0))
            q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,FrameCounter=tick&255)
            record(q,'GameLoop',p=0x30)
            for qq in q.q:qq.put(VRAM_Buffer1_Offset=0,VRAM_Buffer1=0)
    # Actual Parodius caller->moved fast helper paths, original authenticated
    # records and real C banks, rotated/full/edge/capacity outcomes unchanged.
    pn_paths=collections.Counter();interrupt_fixtures=[]
    for variant in[1,2,3]:
        names=[n for n in bundles[0]['syms']if n.startswith('PnRecordV'+str(variant)+'N')][:2]
        assert len(names)==2
        states=[(128,128,0,0),(32,96,0,252),(0,24,0,0),(255,239,0,252),
            (8,95,160,0),(224,176,240,252)]
        for name,(xpos,ypos,oam,rotation),flags in itertools.product(names,states,[0x30,0x79]):
            q=Pair(bundles,char=18,variant=0);q.put(VvVariant=variant)
            for qq in q.q:
                pc=address(qq.b,name);bank=(location(qq.b,name)-16)//8192
                qq.m.page(2,bank);qq.set('CurrentBankC',bank|128)
                qq.put(R0=pc&255,R1=pc>>8,SmPosePtr=pc&255,Player_X_Position=128,
                    R4=xpos,R5=0,R6=ypos,R7=1,CurrentOAMOffset=oam,
                    GuestOamRotationActive=bool(rotation),RgOamRotation=rotation,VvClock=7)
                qq.set('SmPosePtr',pc>>8,1)
            sites=record(q,'PnDrawRecord',p=flags)
            for label in['PnFastDrawRecord','PnFastDrawClippedRecord']:
                if(address(bundles[0],label),119)in sites:pn_paths[label]+=1
            if variant==1 and flags==0x30 and oam==0:interrupt_fixtures.append((name,xpos,ypos,rotation,sites))
    assert pn_paths['PnFastDrawRecord']and pn_paths['PnFastDrawClippedRecord'],pn_paths
    # Enabled actual IRQ at every distinct visited movement instruction in
    # both moved sections and its shared five-SMC mapper bridge. Actual lag
    # NMIs at bounded stable-owner call preparation/entry/return seams.
    probe=Pair(bundles);probe.call('RlEnsure');probe.put(SavedJoypadBits=129,A_B_Buttons=128)
    _,path=probe.call('RlMovementDispatch',p=0x30)
    irq_sites=sorted({s for s in path if s[1]in MOVE or 0x15a<=s[0]<0x17b})
    irq_sites += sorted({s for f in interrupt_fixtures for s in f[4]if s[1]==119 and
        address(bundles[0],'PnFastDrawRecord')<=s[0]<address(bundles[0],'RlEnsure')})
    irq_sites=sorted(set(irq_sites));irq_pass=0
    for at,bank in irq_sites:
        if bank==119 and at<address(bundles[0],'RlEnsure'):
            f=next(f for f in interrupt_fixtures if(at,bank)in f[4]);name,xpos,ypos,rotation,_=f
            q=Pair(bundles,char=18,variant=0);q.put(VvVariant=1)
            for qq in q.q:
                pc=address(qq.b,name);cb=(location(qq.b,name)-16)//8192;qq.m.page(2,cb);qq.set('CurrentBankC',cb|128)
                qq.put(R0=pc&255,R1=pc>>8,SmPosePtr=pc&255,R4=xpos,R5=0,R6=ypos,R7=1,
                    CurrentOAMOffset=0,GuestOamRotationActive=bool(rotation),RgOamRotation=rotation,VvClock=7);qq.set('SmPosePtr',pc>>8,1)
            record(q,'PnDrawRecord',p=0x30,inject=('IRQ',(at,bank)))
        else:
            q=Pair(bundles);q.call('RlEnsure');q.put(SavedJoypadBits=129,A_B_Buttons=128)
            record(q,'RlMovementDispatch',p=0x30,inject=('IRQ',(at,bank)))
        irq_pass+=1
    # NmiDisableFF exercises the authentic lag/audio path while preserving
    # current displayed CHR. It is not a PPU timing/render qualification.
    nmi_targets=[(address(bundles[0],n),(location(bundles[0],n)-16)//8192)
        for n in['RlMovementDispatch','RlMovement','RlSourceMovement']]
    own_edge=next(e for e in plan['emitted_farcall_edges']if e['source_bank']==120 and'RlMovement'in e['names'])
    nmi_targets += [(int(own_edge['pc'],16)+i,120)for i in[0,3,5,8,10,13,15]]
    for resident in[127,125]:
        for target in nmi_targets:
            q=Pair(bundles);q.call('RlEnsure');q.put(SavedJoypadBits=129,A_B_Buttons=128,
                NmiDisable=255,DisableScreenFlag=1)
            for qq in q.q:qq.m.page(3,resident)
            record(q,'RlMovementDispatch',p=0x30,inject=('NMI',target))
    # The existing genuine complete earned campaign is executed freshly on
    # BOTH actual binaries. Its historical constant is retained as provenance,
    # never used to retag this current result.
    earned=[]
    for b,rom in zip(bundles,[BASE,CANDIDATE]):
        z=Earned.campaign(b,'roll');z['historical_tool_constant']=z.pop('ROM_sha256');z['actual_ROM_sha256']=sha(rom);earned.append(z)
    def logical(v):
        if isinstance(v,dict):
            z={k:logical(x)for k,x in v.items()if k not in['actual_ROM_sha256']}
            if 'PC'in z and 'bank'in z:z['PC'],z['bank']=mapsite(z['PC'],z['bank'])
            return z
        if isinstance(v,list):return[logical(x)for x in v]
        return v
    assert logical(earned[0])==logical(earned[1])
    (OUT/'earned-controls.json').write_text(json.dumps(dict(passed=True,source_CPU_only=True,actual=earned),indent=2)+'\n')
    python_inputs=sorted({Path(m.__file__).resolve()for m in list(sys.modules.values())
        if getattr(m,'__file__',None)and Path(m.__file__).is_file()and
        Path(m.__file__).resolve().is_relative_to(ROOT)})
    proof=dict(passed=True,native_run=False,source_CPU_only=True,parent=bind(BASE),candidate=bind(CANDIDATE),
        build_proof=bind(OUT/'build-proof.json'),rows=rows,cases=len(rows),
        transport=dict(transport),Parodius_paths=dict(pn_paths),actual_IRQ_sites=irq_sites,IRQ_passes=irq_pass,
        NMI_passes=len(nmi_targets)*2,earned=bind(OUT/'earned-controls.json'),tool=bind(__file__),
        foreign_original_identities=list(IDENTITIES),foreign_expansion_identities=[x[0]for x in expansion],
        actual_loaded_workspace_python=[bind(p)for p in python_inputs],
        runtime=dict(version=sys.version,python=bind(sys.executable),MPU=bind(sys.modules[NesMPU.__base__.__module__].__file__)),
        limits='Finite actual CPU/mapper callers only; no PPU/native/audio scheduler claim.')
    (OUT/'caller-controls.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(rows),path=str(OUT/'caller-controls.json')),indent=2))

if __name__=='__main__':main()
