"""Finite static UI consumers and real native interrupt cuts; no ROM output."""
from pathlib import Path
import sys,json,collections
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import propose_bub_menu_controls_1102_v1 as C
A=C.A;F=C.F;M=F.M;O=F.O;address=F.address;location=F.location

def isr(c,kind,native,allow_native_publication=False):
    m=c.memory;regs=(c.pc,c.a,c.x,c.y,c.p,c.sp)
    scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);maps=list(m.rawtags)
    ppustate=(m.ppu_addr,m.toggle,m.buffer,m.ppuctrl,m.ppu_reads)
    chrstate=(list(m.chr_latches),m.upper,m.lastset);ram=[bytes(z)for z in m.ram]
    if kind=='NMI'and allow_native_publication and M.get(m,'SelectedCharacter')==0 and M.get(m,'MarioVariant')!=2:
        # Native Mario's established busy guard intentionally republishes
        # logical CHR. Bind the exact actual publisher result, not an invented
        # "busy means no CHR writes" contract that the native code never had.
        n=M.fork(m);F.invoke(n,'X5PublishChr');chrstate=(list(n.chr_latches),n.upper,n.lastset)
    if kind=='IRQ':c.irq()
    else:c.nmi()
    accepted=c.pc!=regs[0]
    for _ in range(200000):
        if c.pc==regs[0]and c.sp==regs[5]:break
        assert m[c.pc]!=0,('ISR BRK',kind,hex(c.pc),m.rawtags)
        native.step(c)
    else:raise AssertionError(('ISR bound',kind,hex(c.pc)))
    assert regs==(c.pc,c.a,c.x,c.y,c.p,c.sp),('ISR AXYP/SP',kind,regs)
    assert scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])and maps==m.rawtags
    assert ram==[bytes(z)for z in m.ram]
    if kind=='NMI':
        assert ppustate==(m.ppu_addr,m.toggle,m.buffer,m.ppuctrl,m.ppu_reads),'Busy NMI changed foreground PPU transaction'
        assert chrstate==(list(m.chr_latches),m.upper,m.lastset),'Busy NMI changed already-published CHR state'
    return accepted

def interrupt_controls(old,new):
    native=M.NesMPU;counts=collections.Counter();seen=set();negative={}
    # Capture the original actual IRQ hazard, not an invented corruption.
    class OldIRQ(native):
        def step(self):
            if self.pc==0xa5b0 and self.memory.rawtags[1]==194 and not negative:
                before=self.memory.ppu_addr;assert isr(self,'IRQ',native)
                negative.update(cut_PC=self.pc,PPU_address_before=before,PPU_address_after=self.memory.ppu_addr)
            return native.step(self)
    M.NesMPU=OldIRQ
    try:m,z=A.run_decoder(old,0xa588)
    finally:M.NesMPU=native
    assert bytes(m.vram[0x2000:0x2400])!=A.run_decoder(old,0xa588)[0].vram[0x2000:0x2400]
    negative['actual_original_copy_corrupted']=True
    # Every actual executed new instruction/data-loop state gets the real
    # busy native NMI and attempted IRQ. The latter must remain masked after
    # the initializer's SEI, including all literal/repeat PPUDATA writes.
    class Probe(native):
        def step(self):
            m=self.memory;key=(self.pc,self.sp,m[4],self.y)
            if m.rawtags[1]!=194 or not(self.pc==0xa588 or 0xafb5<=self.pc<0xb010):return native.step(self)
            if key not in seen:
                seen.add(key)
                for kind in ['NMI','IRQ']:
                    n=M.fork(m);c=native(memory=n,pc=self.pc)
                    for attr in ['a','x','y','p','sp']:setattr(c,attr,getattr(self,attr))
                    accepted=isr(c,kind,native);counts[kind+('_accepted'if accepted else'_masked')]+=1
                    if kind=='IRQ'and accepted:
                        # Before SEI all source-byte/PPU initialization is
                        # still ahead of us, so the final complete copy wins.
                        while c.pc!=0xa5b9:
                            assert n[c.pc]!=0;native.step(c)
                        assert bytes(n.vram[0x2000:0x2400])==expected
            return native.step(self)
    expected=A.run_decoder(new,0xa588)[0].vram[0x2000:0x2400]
    # Hardware begins with the complete existing logical mapping. This also
    # makes the native-Mario lag republisher an idempotent write sequence.
    original_fresh=M.fresh
    def fresh(b):
        m=original_fresh(b);F.invoke(m,'X5PublishChr');M.put(m,SelectedCharacter=39)
        return m
    M.fresh=fresh;M.NesMPU=Probe
    try:m,z=A.run_decoder(new,0xa588)
    finally:M.fresh=original_fresh;M.NesMPU=native
    assert bytes(m.vram[0x2000:0x2400])==expected and counts['IRQ_accepted']==5,dict(counts)
    return dict(passed=True,original_unmasked_IRQ_negative=negative,actual_new_copy_instruction_state_cuts=len(seen),actual_ISR_counts=dict(counts),accepted_IRQ_boundaries='Three cuts before SEI/PPU initialization; two cuts after complete copy and PLP. All PPUDATA writes remain masked.')

def consumers(old,new):
    oldseed=M.fresh(old);rows=[];used=set();names=set();draws=set()
    nname=address(old,'FmQueueName')+3;ndraw=address(old,'FmDrawPreviewSelected')
    def watch(c):
        if c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==204:
            if c.pc==nname:names.add(c.a)
            if c.pc==ndraw:draws.add(c.a)
    for slot,count in enumerate(F.COUNTS):
        m=M.fork(oldseed);M.put(m,CrossoverMenuIndex=slot)
        F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection',watch=watch)
        for variant in range(count):
            if variant:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                F.invoke(m,'CrossoverMenuInput',watch=watch)
            F.invoke(m,'X5PublishChr')
            hits=[]
            for i in range(0,M.get(m,'CurrentOAMOffset'),4):
                y,t,attr,x=m[0x200+i:0x204+i]
                if y>=239:continue
                pos=(t&1)*4096+(t&254)*16;page=m.chr_latches[pos//1024];off=pos%1024
                if 700<=page<=703:
                    assert page!=700 or off>=96,('Live old body touches leased prefix',slot,variant,i,t,page,off)
                    used.add((page,off));hits.append((page,off))
            rows.append(dict(slot=slot,variant=variant,raw=M.get(m,'SelectedCharacter'),visible_preview_pairs=hits))
    assert len(rows)==91 and not names&{0,1,9,14}and not draws&{9,14}
    # Construct the complete source/table union independently of whether a
    # proposed page happens to be blank. Upper0/1/3 cannot name700; each
    # upper2 caller is bounded by these actual metadata/table/source domains.
    dp=R/'build/bubble-bobble-source-1101-v1/current3-domain-rebind.json'
    sp=R/'build/bubble-bobble-source-1101-v1/current3-closure-supplement.json'
    domains=json.loads(dp.read_text());supp=json.loads(sp.read_text());assert supp['passed']and supp['remaining_existing_finite_publishers']==0
    tables=[]
    for t in domains['current_table_bindings']:
        at=location(old,t['name']);data=old['raw'][at:at+t['bytes']]
        assert __import__('hashlib').sha256(data).hexdigest()==t['SHA256'],t['name'];tables.append(t['name'])
    assert not any(700 in pages for pages in domains['finite_domains'].values())
    # Positive current menu selectors: two actual loops over Y0..3 map the
    # literal lowBC with upper2. The DK special is inside the first worker.
    fm=old['raw'][location(old,'FmDrawPreviewSelected'):location(old,'FmDrawPreviewSelected')+0xc1]
    cf=old['raw'][location(old,'FmDrawCfPreview'):location(old,'FmDrawCfPreview')+0x9b]
    selector=bytes.fromhex('98 18 69bc a202 8d6a01 a975 8d6c01 a9a2 8d6d01 a9be 205a01 c8 c004 90')
    assert selector in fm and selector in cf
    # All old static-table rows remain byte-identical except the two proven
    # unused rows; CF has separate literal OAM and DK owns its six-sprite row.
    bg=old['raw'][1048592+4096:1048592+8192];mapat=location(old,'ChrPhysicalMap');cmap=old['raw'][mapat:mapat+256]
    reverse={p:[i for i,v in enumerate(cmap)if v==p]for p in range(4,8)}
    assert reverse=={4:[60],5:[61],6:[62],7:[63]}
    screens=[]
    for state in [1,3,5,7]:
        m=M.fork(oldseed);M.put(m,CrossoverMenuState=state,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,CrossoverMenuButtons=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0)
        F.invoke(m,'CrossoverMenuInput');tiles=set(m.vram[0x2000:0x23c0]);assert not tiles&{245,246,247,248},('Existing screen tile collision',state)
        commands=F.commands(m)
        for packet in commands:
            if 0x2000<=packet['address']<0x3000:assert not set(packet['bytes'])&{245,246,247,248}
        screens.append(dict(build_state=state,result_state=M.get(m,'CrossoverMenuState'),background_tiles=sorted(tiles),queue_commands=len(commands)))
    # The pending data source has one names reader and one portrait reader;
    # enumerate and bind the declared source references instead of searching
    # raw data bytes for accidental instruction-like substrings.
    refs=[]
    for path in (R/'src').rglob('*'):
        if path.suffix not in['.s','.inc']:continue
        for lineno,line in enumerate(path.read_text(errors='replace').splitlines(),1):
            if any(n in line for n in ['FmNames','FmPreviewTiles','FmPreviewColors']):refs.append(dict(file=path.relative_to(R).as_posix(),line=lineno,text=line.strip()))
    assert {x['file']for x in refs}=={'src/full_roster_menu.s'}
    return dict(passed=True,actual_existing_profiles=len(rows),name_rows=sorted(names),portrait_rows=sorted(draws),actual_visible_pending_pairs=sorted(used),source_references=refs,
        inherited_finite_table_rebinds=len(tables),source_family_page_domains=len(domains['finite_domains']),nonmenu_upper2_domains_exclude700=True,
        positive700_menu_publishers=['FmDrawPreviewSelected incl DKspecial row17','FmDrawCfPreview'],
        BG_reverse_legacy_selectors=reverse,existing_screen_builds=screens,profiles=rows,
        scope='Actual existing menu profile/name/OAM consumers plus source-typed upper2 family domains, current tables and positive menu selector constructors. Source-valid states only; arbitrary forged CHR modes/pointers are outside the ABI.',
        inherited_bindings={p.relative_to(R).as_posix():F.sha(p)for p in[dp,sp,R/'build/metal-storm-chr-closure-1101-v10/source-domains.json']})

def ingress_interrupts(new):
    native=M.NesMPU;old_F_CPU=F.NesMPU;seen=set();counts=collections.Counter()
    class Probe(native):
        def step(self):
            m=self.memory;pc=self.pc
            tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
            changed=(tag==194 and(0xad39<=pc<0xad78))or(tag==204 and(0xbced<=pc<0xbd04 or pc==0xb979))or(tag==157 and(0xb5ab<=pc<0xb5ba or 0xb5e6<=pc<0xb630))
            key=(tag,pc,self.sp,M.get(m,'SelectedCharacter'),M.get(m,'FmGroups'))
            if changed and key not in seen:
                seen.add(key)
                for kind in ['NMI','IRQ']:
                    n=M.fork(m);c=native(memory=n,pc=pc)
                    for attr in ['a','x','y','p','sp']:setattr(c,attr,getattr(self,attr))
                    accepted=isr(c,kind,native,allow_native_publication=True);counts[kind+('_accepted'if accepted else'_masked')]+=1
            return native.step(self)
    seed=M.fresh(new);F.invoke(seed,'X5PublishChr')
    M.NesMPU=F.NesMPU=Probe
    try:
        # Both new variants and all accepted old family marker states. These
        # are actual complete menu entry calls, with no private cold execution.
        for slot,groups,alts in [(32,0,0),(32,128,0),(23,0,0),(23,32,0),(30,0,0),(30,8,0),(30,16,0),(30,24,0),(0,0,0),(29,0,0)]:
            m=M.fork(seed);M.put(m,CrossoverMenuIndex=slot,FmGroups=groups,FmAlts=alts,DisableScreenFlag=1,NmiDisable=255)
            F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
            for key in [32,16,128,48,160]:
                n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0)
                F.invoke(n,'CrossoverMenuInput')
    finally:M.NesMPU=native;F.NesMPU=old_F_CPU
    return dict(actual_changed_instruction_identity_states=len(seen),actual_ISR_counts=dict(counts),scope='Actual new pending/Select/confirm and shared P1/Start instructions in complete menu calls; real IRQ and busy NMI preserve AXYP/SP/R0..7/SMC/maps/conditional RAM. Unloaded static menu path only; new authenticated backend is separately qualified.')

def main():
    old,new,patches=C.bundle();q=dict(passed=False,proposal_only=True,ROM_written=False,native=False,menu_admitted=False,base_ROM_SHA256=F.PIN)
    q['consumers']=consumers(old,new);print('consumer domains passed',flush=True)
    q['interrupts']=interrupt_controls(old,new);print('copy interrupts passed',flush=True)
    q['ingress_interrupts']=ingress_interrupts(new);q['passed']=True
    q['bindings']={p.relative_to(R).as_posix():F.sha(p)for p in[Path(__file__),Path(C.__file__),Path(A.__file__),F.BASE,O/'art-proposal.json',O/'menu-stream.bin',O/'menu-controls.bin']}
    (O/'art-CPU-closure.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(existing_profiles=q['consumers']['actual_existing_profiles'],**q['interrupts'])))
if __name__=='__main__':main()
