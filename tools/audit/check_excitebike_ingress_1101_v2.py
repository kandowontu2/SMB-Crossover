"""Current shot/bbox one-byte shift and actual native UI ingress equivalence."""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_excitebike_dispatch_1101_v1 import O,save,sha,labels
from prepare_excitebike_host_1101_v1 import BASE,PIN
from compose_excitebike_current_1101_v2 import bundle


def state(m,z):
    return (tuple(z[n]for n in ['A','X','Y','P']),bytes(m[:256]),bytes(m[0x200:0x800]),
            bytes(m[0x5c00:0x8000]),[bytes(x)for x in m.ram],list(m.rawtags),
            bytes(m[0x15a:0x17b]),list(m.chr_latches),m.upper,m.lastset)


def profiles(b):
    counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    seed=M.fresh(b);rows=[]
    for slot,count in enumerate(counts):
        m=M.fork(seed);M.put(m,CrossoverMenuIndex=slot)
        M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
        for v in range(count):
            if v:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                M.invoke(m,'CrossoverMenuInput')
            rows.append((slot,v,M.fork(m)))
    assert len(rows)==90
    return rows


def ui():
    new=bundle();old=copy.deepcopy(new);raw=bytearray(old['raw']);base=BASE.read_bytes()
    for name in ['GetPlayerColors','CrossoverPatchStatusName']:
        at=location(old,name);raw[at:at+18]=base[at:at+18]
    old['raw']=bytes(raw);cases=0;owners=set();pending=0
    rows=profiles(new)
    extra=M.fork(rows[0][2]);M.put(extra,SelectedCharacter=30);rows.append((32,0,extra))
    for slot,v,seed in rows:
        char=M.get(seed,'SelectedCharacter');owners.add(char)
        if char==37:pending+=1;continue
        for name,variants in [('GetPlayerColors',range(8)),('CrossoverPatchStatusName',range(5))]:
          for variation in variants:
           for flags in [0x30,0x31,0x70,0xf1]:
            pair=[]
            for b in [old,new]:
                m=M.fork(seed);m.bundle=b
                # Re-map the same current windows from the selected image.
                for win,tag in enumerate(list(m.rawtags)):
                    if tag&128:m.raw_page(win,tag)
                M.put(m,VRAM_Buffer1_Offset=0,BackgroundColorCtrl=variation&7,AreaType=1,
                      CurrentPlayer=variation&1,PlayerStatus=variation%3)
                at=address(b,'VRAM_Buffer1');m[at:at+84]=bytes([0xa5])*84
                z=M.invoke(m,name,a=variation if name=='CrossoverPatchStatusName'else 0x55,p=flags)
                pair.append(state(m,z))
            assert pair[0]==pair[1],('Foreign actual native UI ABI',slot,v,char,name,variation,flags,
                                        pair[0][0],pair[1][0],[i for i,(a,z)in enumerate(zip(pair[0],pair[1]))if a!=z])
            cases+=1
    assert pending==1 and set(range(37))<=owners,(pending,sorted(owners))
    # Loaded own UI: every native backdrop branch, full84-byte queue bounds,
    # fixed native status message0 only, and no source actor mutation.
    m=M.fresh(new);M.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
        Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
    assert M.invoke(m,'ExScene')['P']&1;own=0
    bg=[34,34,15,15,15,34,15,15]
    for control in range(8):
      for offset in [0,12,76,77,83]:
        n=M.fork(m);M.put(n,BackgroundColorCtrl=control,AreaType=1,VRAM_Buffer1_Offset=offset)
        at=address(new,'VRAM_Buffer1');n[at:at+85]=bytes([0xa5])*85;source=bytes(n.ram[2])
        z=M.invoke(n,'GetPlayerColors',a=0x55,x=7,y=91,p=0xf1)
        assert z['P']&1 and source==bytes(n.ram[2])
        if offset<77:
            assert bytes(n[at+offset:at+offset+8])==bytes([63,16,4,bg[control or 1],32,22,15,0])
            assert M.get(n,'VRAM_Buffer1_Offset')==offset+7
        else:assert bytes(n[at:at+85])==bytes([0xa5])*85 and M.get(n,'VRAM_Buffer1_Offset')==offset
        assert n[at+84]==0xa5;own+=1
    for message in range(5):
      for flags in [0x30,0x31,0x70,0xf1]:
        n=M.fork(m);at=address(new,'VRAM_Buffer1');n[at:at+84]=bytes([0xa5])*84
        z=M.invoke(n,'CrossoverPatchStatusName',a=message,x=7,y=91,p=flags)
        assert [z[k]for k in ['A','X','Y']]==[message,7,91]and z['P']&1
        expected=bytearray([0xa5]*84)
        if message==0:expected[11:18]=bytes([14,33,11,18,20,14,36])
        assert bytes(n[at:at+84])==expected;own+=1
    save('UI-ingress-CPU.json',dict(passed=True,base_ROM_SHA256=PIN,actual_profiles=90,
         all_raw0_36_and_alternates=True,foreign_full_ABI_cases=cases,own_queue_status_cases=own,
         all_AXYP_SP_SMC_R0_7_RAM_maps_exact=True,native=False,installed=False,
         bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,O/'host-assembly.json',O/'shot-owner-assembly.json']}))
    return new,m,cases,own


def shots(new):
    old=scoped_load(BASE);before=M.fresh(old);after=M.fresh(new);count=0;skips=0;bboxes=0
    for char in list(range(39))+[127,255]:
      for flags in [0x30,0x31,0x70,0xf1]:
       for variant in [0,1]:
        pair=[]
        for seed in [before,after]:
            m=M.fork(seed);M.put(m,SelectedCharacter=char,ProtoVariant=variant,SavedJoypadBits=65)
            z=M.invoke(m,'MegaManFullShotBank',p=flags);pair.append(state(m,z))
        if char!=37:
            assert pair[0]==pair[1],('Shot foreign ABI',char,flags,variant,pair[0][0],pair[1][0]);count+=1
        else:
            assert pair[1][0]==(0x55,7,91,(flags&0x7d)|0x20),pair[1][0]
            assert list(after.chr_latches)==pair[1][-3];skips+=1
    # The shifted entry uses the byte-identical40B native gate; raw36 must
    # still reach the same cached source body while every other owner returns
    # the same native fallback effects. Warm both matching Sh caches.
    labs=[labels(R/'build/shinobi-bbox-design-1101-v29/resident-design.lbl'),labels(O/'shot-owner.lbl')]
    seeds=[]
    for b,lab in zip([old,new],labs):
        b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
        for n,a in lab.items():b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
        m=M.fresh(b);M.put(m,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
        M.invoke(m,'ShScene');assert m.ram[2][0x800]==167;seeds.append(m)
    for char in range(39):
      for x,y in [(3,16),(120,176),(250,239)]:
       for flags in [0x30,0xf1]:
        pair=[]
        for seed in seeds:
            m=M.fork(seed);M.put(m,SelectedCharacter=char,Player_X_Position=x,Player_Y_Position=y,
                Player_Y_HighPos=1,Player_Rel_XPos=x,Player_Rel_YPos=y,Player_PageLoc=0,
                ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,Player_BoundBoxCtrl=1)
            z=M.invoke(m,'LmBoundingBoxGate',a=0x55,x=0,y=0,p=flags);pair.append(state(m,z))
        assert pair[0]==pair[1],('Shifted bbox ABI',char,x,y,flags,pair[0][0],pair[1][0]);bboxes+=1
    return count,skips,bboxes,seeds[1]


def interrupts(new,ex,sh):
    native=M.NesMPU;seen=set();counts={'IRQ':0,'lagNMI':0}
    starts=[(ex,'GetPlayerColors'),(ex,'CrossoverPatchStatusName'),(ex,'MegaManFullShotBank'),(sh,'LmBoundingBoxGate')]
    points={address(new,n)for n in ['GetPlayerColors','CrossoverPatchStatusName']}
    class Probe(native):
      def step(self):
        mem=self.memory;pc=self.pc;tag=mem.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
        inrange=(tag==193 and 0xadb6<=pc<0xadff)or(tag==3 and 0xae50<=pc<0xafa0)or any(p<=pc<p+18 for p in points)
        key=(pc,self.sp,tag,M.get(mem,'SelectedCharacter'))
        if inrange and key not in seen:
          seen.add(key)
          for kind in counts:
            if kind=='IRQ'and self.p&4:continue
            n=M.fork(mem);c=native(memory=n,pc=pc)
            for attr in ['a','x','y','p','sp','pc']:setattr(c,attr,getattr(self,attr))
            regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);scratch=bytes(n[3:11]);smc=bytes(n[0x15a:0x17b]);ram=[bytes(z)for z in n.ram]
            maps=list(n.rawtags);maps[2]=M.get(n,'CurrentBankC')
            if kind=='IRQ':c.irq()
            else:c.nmi()
            for _ in range(200000):
                if (c.a,c.x,c.y,c.p,c.sp,c.pc)==regs:break
                assert n[c.pc]!=0,('ISR BRK',kind,key,hex(c.pc));c.step()
            else:raise AssertionError(('ISR continuation',kind,key))
            assert scratch==bytes(n[3:11])and smc==bytes(n[0x15a:0x17b])and ram==[bytes(z)for z in n.ram]and maps==n.rawtags,('ISR ABI',kind,key)
            counts[kind]+=1
        return native.step(self)
    M.NesMPU=Probe
    try:
        for seed,name in starts:
            m=M.fork(seed);M.put(m,NmiDisable=255,DisableScreenFlag=1,VRAM_Buffer1_Offset=0)
            M.invoke(m,name,a=0 if name=='CrossoverPatchStatusName'else 0x55,x=0 if name=='LmBoundingBoxGate'else 7,p=0x31)
        for char in [0,35,36,37,38,255]:
            m=M.fork(ex);M.put(m,SelectedCharacter=char,NmiDisable=255,DisableScreenFlag=1)
            M.invoke(m,'MegaManFullShotBank',p=0x31)
    finally:M.NesMPU=native
    return counts


def main():
    new,ex,foreign,own=ui();count,skips,bboxes,sh=shots(new);cuts=interrupts(new,ex,sh)
    q=dict(passed=True,base_ROM_SHA256=PIN,foreign_shot_cases=count,raw37_preserving_skips=skips,
           actual_bbox_shift_cases=bboxes,actual_ISR_cuts=cuts,Sh_cookie_current_and_unchanged=True,
           native=False,installed=False,source_funded_growth=1,
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,O/'shot-owner-assembly.json',O/'host-assembly.json']})
    save('shot-owner-CPU.json',q);print(json.dumps(dict(UI_foreign=foreign,UI_own=own,**q)))

if __name__=='__main__':main()
