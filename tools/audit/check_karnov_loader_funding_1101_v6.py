"""Source-assembled loader/dispatch differential; no root ROM/source writes."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_karnov_loader_funding_1101_v6 import transform_sources
from private_build_outputs_v1 import validate
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
import check_karnov_pickup_composed_1101_v4 as P
from check_tmnt_render_oa import address,location
O=R/'build/karnov-loader-funding-1101-v6';B=R/'build/karnov-host-resource-base-1101-v1'
HELP=R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc'
PIN='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def flatten(text,fragments,inputs):
    def include(m):
        name=m[1]
        if name in fragments:part=fragments[name]
        else:
            p=B/name;inputs.add(p);part=p.read_text()
        return flatten(part,fragments,inputs)
    text=re.sub(r'(?m)^\s*\.include "([^"]+)"\s*$',include,text)
    def binary(m):
        p=B/m[1];inputs.add(p);return '.byte '+','.join(str(v)for v in p.read_bytes())
    return re.sub(r'\.incbin "([^"]+)"',binary,text)


def assemble(b,name,resident,fragments,inputs):
    text=flatten(resident,fragments,inputs)
    text=re.sub(r'(?m)^\s*\.(?:import|importzp|export|exportzp)\b[^\n]*\n','',text)
    labels=set(re.findall(r'(?m)^([A-Za-z_]\w*):',text))
    assigned=set(re.findall(r'(?m)^([A-Za-z_]\w*)\s*=',text))
    native={n:address(b,n)for n in set(re.findall(r'\b[A-Za-z_]\w*\b',text))
            if n in b['syms']and n not in labels|assigned}
    def bank(n):return ((location(b,n)-16)//8192)&127
    text=re.sub(r'\.bank\((\w+)\)',lambda m:str(bank(m[1]))if m[1]in native else m[0],text)
    def far(m):
        n=m[1];jump='jmp'if m[2]else'jsr'
        return f''' sta SafecallA_SMC+1
 lda #<{n}
 sta FarcallJmpTarget_SMC+1
 lda #>{n}
 sta FarcallJmpTarget_SMC+2
 lda #{bank(n)|128}
 {jump} FarCallCommon'''
    text=re.sub(r'(?m)^\s*farcall (\w+)(,jmp)?\s*$',far,text)
    seg=b['segs'][b['syms']['KrResidentBegin']['seg']];start=int(seg['start'],0)
    pre=address(b,'KrResidentBegin')-start
    charmap=R/'inc/charmap.inc';inputs.add(charmap)
    source='.setcpu "6502"\n.macpack longbranch\n'+charmap.read_text()+'\n'+''.join(f'{n}=${v:04x}\n'for n,v in sorted(native.items()))
    source+='\n.segment "RESIDENT"\n.res '+str(pre)+',$ff\nKrResidentBegin:\n'+text
    source+='\n.res 2432-(*-KrResidentBegin),$ff\nKrResidentLimit:\n.export '+','.join(sorted(labels|{'KrResidentBegin','KrResidentLimit'}))+'\n'
    (O/(name+'.s')).write_text(source)
    cfg=f'MEMORY{{P:start=${start:04x},size=${pre+2432:04x},bank=29,file=%O;}}SEGMENTS{{RESIDENT:load=P,type=ro;}}\n'
    (O/(name+'.cfg')).write_text(cfg)
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for cmd in [[cc/'ca65.exe','-g',O/(name+'.s'),'-o',O/(name+'.o')],
                [cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl'),'--dbgfile',O/(name+'.dbg')]]:
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True)
        commands.append(dict(command=cmd,guard=guard,returncode=z.returncode,stderr=z.stderr));assert z.returncode==0,z.stderr
    labs={m[2]:int(m[1],16)for m in re.finditer(r'(?m)^al ([0-9A-Fa-f]+) \.(\S+)$',(O/(name+'.lbl')).read_text())}
    raw=(O/(name+'.bin')).read_bytes()[pre:];assert len(raw)==2432
    assert labs['KrMarioWaterProductHi']==0xbb8e and labs['KrResidentEnd']<=0xbfb0
    q=dict(b,raw=b['raw'],syms=dict(b['syms']))
    for n,v in labs.items():
        q['syms'][n]=dict(b['syms'].get(n,b['syms']['KrResidentBegin']),val=hex(v),seg=b['syms']['KrResidentBegin']['seg'])
    image=bytearray(b['raw']);pos=location(b,'KrResidentBegin');image[pos:pos+2432]=raw;q['raw']=bytes(image)
    return q,dict(name=name,resident_bytes=labs['KrResidentEnd']-labs['KrResidentBegin'],water=labs['KrMarioWaterProductHi'],tail_free=0xbfb0-labs['KrResidentEnd'],labels=labs,commands=commands)


def call(m,name,row=None,observer=None,**kw):
    c=H.start(m,name,**kw)
    if row is not None:
        at=address(m.bundle,'KrServiceVeneers')+3*row
        m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=at&255;m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=at>>8
    return H.finish(m,c,observer)


def state(m,c,callee=None):
    # Dead stack bytes have no native ownership.  The complete live frame and
    # caller registers/maps/33SMC/ZP and all native state remain compared.
    smc=bytearray(m[0x15a:0x17b])
    if callee is not None:
        offset=address(m.bundle,'FarcallJmpTarget_SMC')+1-0x15a
        assert int.from_bytes(smc[offset:offset+2],'little')==address(m.bundle,callee)
        smc[offset:offset+2]=b'\0\0' # only the proved relocated caller target
    return ((c.a,c.x,c.y,c.p,c.sp),bytes(m[:256]),bytes(m[0x200:0x2000]),
            bytes(m[0x5c00:0x8000]),[bytes(z)for z in m.ram],m.rawtags[:],
            m.chr_latches[:],m.upper,m.ppuctrl,m.toggle,bytes(smc))


def loader_checks(old,new,carrier=False):
    rows=[];seed=None;options=list(itertools.product([0,1],[0,1],[128,160,164]))
    for wide,reload,ctrl in options:
        pair=[]
        for b in [old,new]:
            m=L.make(b,SelectedCharacter=34,FmAlts=1,X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl)
            m.ppuctrl=ctrl;H.invoke(m,'X5PublishChr');latches=m.chr_latches[:]
            initial=bytes(m[3:11]);smc=[];ret=[]
            def hook(mem,c,i):
                if c.pc==address(b,'KrLoad'):smc.append(bytes(mem[0x15a:0x17b]))
                if c.pc==address(b,'KrLoadReturn'):ret.append(bytes(mem[0x15a:0x17b]))
            c,low=call(m,'KrLoad',observer=hook)
            assert c.p&1 and c.sp==224 and(c.a,c.x,c.y)==(85,7,91)
            assert smc==ret and len(smc)==1 and bytes(m[3:11])==initial
            assert m.chr_latches==latches and m.ppuctrl==ctrl and m.toggle==0
            assert m.ram_writes[:2]==[(3,0x1fe0,0),(2,0x1fe0,0)]and m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            reads=m.ppu_reads;writes=len(m.ram_writes);warm,wl=call(m,'KrLoad')
            assert warm.p&1 and reads==m.ppu_reads and writes==len(m.ram_writes)
            pair.append((m,c,low,reads))
        if not carrier:
            aa,zz=[state(m,c,'KrLoad')for m,c,_,_ in pair]
            delta=[(i,[(j,x,y)for j,(x,y)in enumerate(zip(aa[i],zz[i]))if x!=y][:6])for i in range(len(aa))if aa[i]!=zz[i]]
            assert not delta,('Actual full loader differential',wide,reload,ctrl,delta)
        rows.append(dict(wide=wide,reload=reload,ctrl=ctrl,old_cycles=pair[0][1].processorCycles,new_cycles=pair[1][1].processorCycles,minimum_SP=pair[1][2],PPU_reads=pair[1][3]))
        if seed is None:seed=L.fork(pair[1][0])
    return dict(passed=True,complete_cold_and_warm_cases=len(rows),rows=rows),seed


def model_link(old,new):
    """Model only source-declared native relocation sites, entirely in memory.

    This is not a full owning-object link or a publishable candidate ROM.
    """
    raw=bytearray(new['raw']);updates=[]
    for caller,target,offsets in [('InitScreen','KrSceneInit',[12,17,22]),
        ('FmResolve::Native','KrMenuResolve',[4,9,14]),('FmStartFlags','KrStartFlags',[4,9,14])]:
        p=location(old,caller);a=address(old,target);z=address(new,target)
        for offset,value,was in zip(offsets,[z&255,z>>8,157],[a&255,a>>8,157]):
            assert raw[p+offset-1]==0xa9 and raw[p+offset]==was
            raw[p+offset]=value
        updates.append(dict(caller=caller,callee=target,old=a,new=z))
    p=location(old,'KrServiceVeneers');a=address(old,'KrDispatch');z=address(new,'KrDispatch')
    for row in range(37):
        at=p+3*row;assert raw[at:at+3]==bytes([0x4c,a&255,a>>8])
        raw[at+1:at+3]=z.to_bytes(2,'little')
    new=dict(new,raw=bytes(raw));return new,dict(farcall_targets=updates,auth_veneer_JMP_relocations=37,scope='Exact source-declared native call sites model-rebound in memory only; root must perform its complete owning-object link.')


def negative_checks(old,new):
    rows=[]
    cases=[('foreign',dict(SelectedCharacter=0)),('legacy-Rygar',dict(SelectedCharacter=7,FmAlts=0)),
        ('title',dict(OperMode=0)),('other-mode',dict(OperMode=2)),('visible',dict(DisableScreenFlag=0)),
        ('mask',dict(Mirror_PPUMASK=24)),('NMI',dict(NmiDisable=0)),('not-commit',dict(FamilyMainCommit=0))]
    for name,values in cases:
        pair=[]
        for b in [old,new]:
            m=L.make(b,SelectedCharacter=34,FmAlts=1,**values)if'SelectedCharacter'not in values else L.make(b,FmAlts=values.get('FmAlts',1),**{k:v for k,v in values.items()if k!='FmAlts'})
            before=[bytes(z)for z in m.ram];c,_=call(m,'KrLoad')
            assert not c.p&1 and before==[bytes(z)for z in m.ram]and not m.ppu_reads
            pair.append(state(m,c,'KrLoad'))
        assert pair[0]==pair[1],name;rows.append(name)
    for name,protection,corrupt in [('locked',[0,0],None),('state',[2,1],(2,23)),
        ('code',[2,1],(3,17)),('last-code',[2,1],(3,7268))]:
        pair=[]
        for b in [old,new]:
            m=L.make(b,SelectedCharacter=34,FmAlts=1);m.protection=protection;m.corrupt_at=corrupt
            before=[bytes(z)for z in m.ram];c,_=call(m,'KrLoad');assert not c.p&1
            if protection==[2,1]:assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
            else:assert before==[bytes(z)for z in m.ram]and all(m.ram[i][0x1fe0]!=167 for i in [2,3])
            pair.append(state(m,c,'KrLoad'))
        assert pair[0]==pair[1],name;rows.append(name)
    return dict(passed=True,complete_failure_differential=rows)


def dispatch_checks(old,new):
    seeds=[P.cold(b)for b in [old,new]];cases=0;digest=hashlib.sha256()
    class Entered(Exception):pass
    for row,y,f in itertools.product([n for n in range(37)if n!=20],[0,1,91,255],[0,63]):
        pair=[]
        for b,seed in zip([old,new],seeds):
            m=L.fork(seed);pending=[None];result=[]
            c=H.start(m,'KrServiceVeneers',a=85,x=5,y=y,p=L.flags(f));pc=address(b,'KrServiceVeneers')+3*row
            m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
            def hook(mem,c,i):
                if c.pc==address(b,'FarCallCommon')and i>0:
                    target=mem[address(b,'FarcallJmpTarget_SMC')+1]|mem[address(b,'FarcallJmpTarget_SMC')+2]<<8
                    pending[0]=(target,c.a)
                if pending[0]and(c.pc,mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else 0)==pending[0]:
                    result.append((c.a,c.x,c.y,c.p&0xcf,bytes(mem[3:11])));raise Entered
            try:H.finish(m,c,hook)
            except Entered:pass
            assert len(result)==1,('Missing actual typed child',row,y,f)
            assert result[0][2]==y,('Genuine child Y lost',row,y,f,result)
            pair.append(result[0])
        assert pair[0]==pair[1],('Actual typed child ABI differential',row,y,f,pair)
        digest.update(bytes(pair[1][:4])+pair[1][4]);cases+=1
    # Execute real movement, probes, item maturity/collection and their native
    # effects using complete declared fixtures, in addition to the child seam.
    contact=0
    for kind,health,weapon,cycle,y in itertools.product([0,1],[0,128],[0,1,2],[0,9],[0,255]):
        pair=[]
        for b,seed in zip([old,new],seeds):
            m=L.fork(seed);P.object_fields(m,kind=kind)
            P.source_fixture(m,{0x68:health,0x65:weapon,0x860:cycle,0xba:0x49,0x40b:0x99})
            c,_=call(m,'KrServiceVeneers',row=24,x=5,y=y)
            pair.append(state(m,c))
        # The active farcall's target caller differs only when its callee has
        # relocated.  Here the veneer address itself is fixedB400 in both.
        assert pair[0]==pair[1],('Complete pickup consumer differential',kind,health,weapon,cycle,y)
        contact+=1
    return dict(passed=True,genuine_typed_child_AXYP_R0_R7_cases=cases,full_pickup_consumer_cases=contact,trace_sha256=digest.hexdigest())


def header_checks(old,new):
    seeds=[P.cold(b)for b in [old,new]];count=0
    for corrupt,f in itertools.product([None]+list(itertools.product([2,3],range(16))),[0,63]):
        pair=[]
        for b,seed in zip([old,new],seeds):
            m=L.fork(seed)
            if corrupt is not None:m.ram[corrupt[0]][0x1fe0+corrupt[1]]^=1
            before=[bytes(z)for z in m.ram];c,_=call(m,'KrCheckCode',p=L.flags(f))
            assert bool(c.p&1)==(corrupt is None)and before==[bytes(z)for z in m.ram]
            pair.append(state(m,c,'KrCheckCode'))
        assert pair[0]==pair[1],('Full public header differential',corrupt,f);count+=1
    return dict(passed=True,complete_public_check_cases=count,all32_cookie_bytes_independently_rejected=True)


def carrier_checks(b):
    payload=R/'build/karnov-combat-component-1101-v2/resident.bin';code=payload.read_bytes();assert len(code)==1040
    image=bytearray(b['raw']);carrier=code+bytes(1280-len(code));at=1048592+1019*1024
    assert image[at:at+1280]==bytes(1280),'Proposed test carrier must begin unoccupied in pinned image'
    image[at:at+1280]=carrier;test=dict(b,raw=bytes(image));rows=[]
    for failure in [None,'carrier-row8','carrier-row9']:
        m=L.make(test,SelectedCharacter=34,FmAlts=1);seen=[]
        def hook(mem,c,i):
            if c.pc==address(test,'KrCopyRow'):
                row=mem[address(test,'R2')];seen.append(row)
                if failure=='carrier-row8'and row==8:mem.corrupt_at=(2,0x900)
                if failure=='carrier-row9'and row==9:mem.corrupt_at=(2,0xd00)
        c,low=call(m,'KrLoad',observer=hook)
        if failure is None:
            assert c.p&1 and seen==list(range(10))and m.ppu_reads==18964
            assert m.ram[2][0x900:0xe00]==carrier and m.ram[3]==test['raw'][1048592+399*1024:1048592+407*1024]
            assert m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            nr=m.ppu_reads;nw=len(m.ram_writes);warm,_=call(m,'KrLoad');assert warm.p&1 and nr==m.ppu_reads and nw==len(m.ram_writes)
        else:assert not c.p&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        rows.append(dict(failure=failure,copied_rows=seen,success=bool(c.p&1),PPU_reads=m.ppu_reads,minimum_SP=low))
    return test,dict(passed=True,actual_complete_KrLoad_cases=rows,payload_SHA256=sha(payload),payload_bytes=len(code),padded_carrier_bytes=len(carrier),carrier_ownership_granted=False,executed_carrier_code=False)


def cold_Main_ISR(b):
    m=P.C.fresh(b);H.put(m,CrossoverMenuIndex=7)
    for name in ['MenuResolveCharacter','QueueSelection']:P.C.invoke(m,name)
    H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
    P.C.invoke(m,'CrossoverMenuInput');P.C.invoke(m,'DrawSelectionPreview')
    H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);P.C.invoke(m,'GameMenuRoutine');P.C.invoke(m,'PauseRoutine',a=0)
    points={address(b,n):n for n in ['KrLoad','KrLoadSaveZp','KrLoadSaveSmc','KrLoadRestoreSmc','KrLoadRestoreZp',
        'KrInvalidateBoth','KrInvalidateBank','KrCopyRow','KrMapRow','KrCarrierRowSetup','KrCarrierMap']if n in b['syms']}
    captured=None
    for frame in range(180):
        H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        origin=P.C.fork(m);cuts={};seen=set();minimum=[255,0]
        def observe(mem,c,i):
            if c.sp<minimum[0]:minimum[:]=[c.sp,i]
            if c.pc in points and c.pc>=0x8000 and mem.rawtags[(c.pc-0x8000)//8192]==157:
                n=points[c.pc];row=mem[address(b,'R2')]if n in ['KrCopyRow','KrMapRow','KrCarrierRowSetup','KrCarrierMap']else None
                key=(n,row if row in [0,8,9]else None)
                if key not in seen:cuts[i]=dict(label=n,row=row);seen.add(key)
            if c.pc>=0x8000 and mem.rawtags[(c.pc-0x8000)//8192]==157 and mem[c.pc]in[0x8d,0x8e]and bytes(mem[c.pc+1:c.pc+3])==b'\x16\x51':
                if mem.rawtags[2]!=H.get(mem,'CurrentBankC'):
                    key=('Cmap-seam',c.pc,mem.rawtags[2],H.get(mem,'CurrentBankC'))
                    if key not in seen:cuts[i]=dict(label='Cmap-seam',PC=c.pc);seen.add(key)
        c,_=call(m,'GameLoop',observer=observe)
        if any(z['label']=='KrCopyRow'for z in cuts.values()):
            cuts[minimum[1]]=dict(label='ActualMainMinimum',SP=minimum[0])
            captured=(origin,P.C.fork(m),(c.a,c.x,c.y,c.p,c.sp),frame,cuts);break
        P.C.consume(m)
    assert captured,'Actual native cold-loader Main not reached'
    origin,expected,regs,frame,cuts=captured
    def foreground(mem):
        fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','FrameCounter','CurrentBank','CurrentBankC','ReloadCHRBank']
        return([bytes(z)for z in mem.ram],bytes(mem[0x200:0x300]),bytes(mem[3:11]),bytes(mem[0x15a:0x17b]),mem.rawtags[:],
               [H.get(mem,n)for n in fields],mem.chr_latches[:],mem.upper,mem.ppuctrl,mem.toggle)
    previous=V.pending_store
    def pending(mem,c,slot,op):
        if previous(mem,c,slot,op):return True
        reg=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
        return value is not None and bytes(mem[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
    V.pending_store=pending;rows=[]
    try:
        for cut,kind in itertools.product(sorted(cuts),['IRQ','NMI']):
            z=P.C.fork(origin);events=[]
            def inject(mem,c,i):
                if i==cut:
                    if kind=='IRQ'and c.p&4:events.append(dict(masked=True));return
                    events.append(dict(foreground_PC=c.pc,foreground_SP=c.sp,**V.interrupt(mem,c,kind)))
            c,_=call(z,'GameLoop',observer=inject)
            assert len(events)==1
            if events[0].get('masked'):continue
            assert(c.a,c.x,c.y,c.p,c.sp)==regs and foreground(z)==foreground(expected),('Cold Main ISR resumption',frame,cut,kind,cuts[cut],events)
            rows.append(dict(cut=cut,**cuts[cut],**events[0]))
    finally:V.pending_store=previous
    low=min(z['minimum_SP']for z in rows);assert low-0x7b>=12,('Cold Main ISR12-byte reserve',low)
    return dict(passed=True,actual_Main=frame,unmasked_ISR_cases=len(rows),minimum_ISR_SP=low,reserve_above_SMC=low-0x7b,interrupts=rows,
        scope='Actual Select/Start and native Main reach the full source-assembled cold loader. Indexed saves/restores, shared invalidation, full copy/verify and mapper seams resume under real unmasked IRQ/lagNMI. IRQ remains masked after the original SEI. Full owning-object relink/native emulator qualification is separate.')


def main():
    a=argparse.ArgumentParser();a.add_argument('--assemble-only',action='store_true');args=a.parse_args()
    O.mkdir(exist_ok=True);q=dict(passed=False,component_only=True,root_modified=False,native=False,installed=False,carrier_ownership_granted=False)
    inputs={Path(__file__),R/'tools/audit/prepare_karnov_loader_funding_1101_v6.py',HELP,B/'candidate.nes',B/'candidate.dbg',B/'kr-resident.inc',
        Path(L.__file__),Path(H.__file__),Path(V.__file__),Path(P.__file__),R/'build/karnov-combat-component-1101-v2/resident.bin',
        R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe'}
    try:
        assert sha(B/'candidate.nes')==PIN
        b=H.C.qualified(B/'candidate.nes');source=(B/'kr-resident.inc').read_text();helper=HELP.read_text()
        o,ao=assemble(b,'original',source,{},inputs)
        assert o['raw']==b['raw'],'Isolated original assembly must exactly reproduce the full current ROM'
        optimized=transform_sources(resident=source,helper_source=helper,carrier=False)
        extended=transform_sources(resident=source,helper_source=helper,carrier=True)
        n,an=assemble(b,'optimized',optimized['resident'],optimized['fragments'],inputs)
        e,ae=assemble(b,'extended',extended['resident'],extended['fragments'],inputs)
        # A direct source dataflow check complements the complete byte/CPU
        # comparison: R0 is written once before all32 zero pages. Only declared
        # mapper helpers are called until the full copy/verify loop finishes.
        ext=extended['resident'];zero=' lda #0\n sta R0\n lda #$c0\n sta R1\n'
        assert ext.count(zero)==1
        region=ext[ext.index(zero)+len(zero):ext.index(' ; Image header is not an early validity publication.')]
        assert not re.search(r'(?mi)^\s*(?:sta|stx|sty|inc|dec)\s+R0\b',region)
        assert set(re.findall(r'\bjsr (\w+)',region))=={'KrMapRow','KrCarrierRowSetup'}
        for name in ['kr-loader-carrier-v6.inc','kr-loader-invalidate-v6.inc']:
            assert not re.search(r'(?mi)^\s*(?:sta|stx|sty|inc|dec)\s+R0\b',extended['fragments'][name])
        assert address(b,'R0')==3 and all(address(b,'R'+str(i))==3+i for i in range(8))
        offsets=[(address(b,n)+delta)&255 for n,delta in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
        assert e['raw'][location(e,'KrSavedSmcOffsets'):location(e,'KrSavedSmcOffsets')+5]==bytes(offsets)
        q['source_invariants']=dict(hot_dispatch_source_unchanged=True,R0_zero_reaches_all_copy_verify_rows=True,source_pointer=[3,4],same_five_SMC_push_offsets=offsets,new_scratch=[],cold_invalidate_extra_stack_bytes=2)
        for name,t in [('optimized',optimized),('extended',extended)]:
            (O/(name+'-resident.inc')).write_text(t['resident'])
            for filename,text in t['fragments'].items():(O/filename).write_text(text)
        q.update(assembly=dict(original=ao,optimized=an,extended=ae),expected_base=PIN)
        if not args.assemble_only:
            n,q['optimized_model_relocations']=model_link(b,n)
            e,q['extended_model_relocations']=model_link(b,e)
            q['loader'],seed=loader_checks(b,n)
            q['negative']=negative_checks(b,n)
            q['headers']=header_checks(b,n)
            q['dispatch']=dispatch_checks(b,n)
            e,q['carrier']=carrier_checks(e)
            q['cold_Main_ISR']=cold_Main_ISR(e)
            q['optimized_Main']=P.main_checks(n)
            assert q['optimized_Main']['passed'],'Unextended optimized Main ISR12-byte reserve'
            q['extended_Main']=P.main_checks(e)
            assert q['extended_Main']['passed'],'Extended source-model Main ISR12-byte reserve'
        q['passed']=True
    except Exception as exc:q.update(error=repr(exc),traceback=traceback.format_exc())
    inputs.update(p for p in O.iterdir()if p.is_file()and p.name!='funding.json'and p.suffix not in ['.o'])
    q['bindings']={str(p.resolve()):sha(p)for p in sorted(inputs)}
    (O/'funding.json').write_text(json.dumps(q,indent=2)+'\n')
    shown={k:v for k,v in q.items()if k not in ['bindings','assembly','traceback']}
    for name in ['optimized_Main','extended_Main','cold_Main_ISR']:
        if name in shown:shown[name]={k:v for k,v in shown[name].items()if k not in ['Main_events','interrupts']}
    print(json.dumps(shown));assert q['passed'],q.get('error')
if __name__=='__main__':main()
