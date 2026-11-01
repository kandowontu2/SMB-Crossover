"""Assemble an isolated same-PC menu proposal and execute real native consumers.

No shared/root edits, ROM publication, Mesen or candidate/code-cache admission.
Only this task's compact assembly products and aggregate receipt are written.
"""
from pathlib import Path
import copy,hashlib,itertools,json,re,subprocess,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from verify_native_relocation import NesMPU
from prepare_menu_input_1101_v3 import proposal
OUT=ROOT/'build/karnov-menu-input-component-1101-v3'
BASE=ROOT/'build/karnov-host-resource-base-1101-v1'
SRC=ROOT/'tools/reference/menu_input_1101_v3.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]

def asm(b):
    bank=(location(b,'CrossoverMenuInput')-16)//8192
    assert bank==0x42
    edge=address(b,'CrossoverMenuInput')+13
    retain=address(b,'CrossoverMenuInput::BuildScreen')+9
    cold=address(b,'CrossoverInit')
    helper,coldhelper=0xb0c0,0xbeb5
    def pos(pc,bk=bank):return 16+bk*8192+(pc&8191)
    own=next(s for s in b['segs'].values()if s['name']=='"PROTO_MENU"')
    assert int(own['start'],0)+int(own['size'],0)==0xb134
    assert b['raw'][pos(helper):pos(0xb134)]==bytes([255])*116
    gaps=[]
    for s in b['segs'].values():
        if 'ooffs'not in s or int(s.get('size','0'),0)==0:continue
        lo,sz=int(s['ooffs'],0),int(s['size'],0)
        if max(lo,pos(coldhelper))<min(lo+sz,pos(0xbf00)):gaps.append(s['name'])
    assert not gaps,('Cold wrapper gap has physical segment owners',gaps)
    assert b['raw'][pos(coldhelper):pos(0xbf00)]==bytes([255])*75
    nextseg=next(s for s in b['segs'].values()if s['name']=='"ROGUE_RELOC_PAGE_7"')
    ack=next(s for s in b['segs'].values()if s['name']=='"PROTO_PALETTE_ACK"')
    assert int(ack['start'],0)+int(ack['size'],0)==coldhelper and int(nextseg['start'],0)==0xbf00
    names=['SavedJoypad1Bits','SavedJoypad2Bits','CrossoverMenuPressed','CrossoverMenuButtons','CrossoverMenuState','CrossoverContinue','FmAlts','FmGroups','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','NrGlobalInit']
    nrbank=(location(b,'NrGlobalInit')-16)//8192
    defs=''.join(f'{n}=${address(b,n):04x}\n'for n in names)
    defs+=f'.scope CrossoverMenuInput\nCheckDirection=${address(b,"CrossoverMenuInput::CheckDirection"):04x}\n.endscope\n'
    # The component-only macro emits the same native18-byte farcall recipe.
    # Root integration uses src/mmc5.s's real macro and real bank attributes.
    far=f'''.macro farcall target,tail
 sta SafecallA_SMC+1
 lda #<target
 sta FarcallJmpTarget_SMC+1
 lda #>target
 sta FarcallJmpTarget_SMC+2
 .if .xmatch({{target}},{{NrGlobalInit}})
  lda #${nrbank|128:02x}
 .else
  lda #${bank|128:02x}
 .endif
 .ifblank tail
  jsr FarCallCommon
 .else
  jmp FarCallCommon
 .endif
.endmacro
'''
    (OUT/'component.s').write_text('.setcpu "6502"\n'+defs+far+'.include "menu_input_1101_v3.inc"\n.segment "EDGE"\nMnMenuInputHook\n.segment "RETAIN"\nMnMenuRetainHook\n.segment "COLDHOOK"\nMnMenuColdHook\n.segment "HELPER"\nMnMenuEmitEdges\n.segment "COLD"\nMnMenuEmitColdInit\n')
    specs=[('EDGE',edge,20,'edge.bin'),('RETAIN',retain,6,'retain.bin'),('COLDHOOK',cold,18,'coldhook.bin'),('HELPER',helper,107,'helper.bin'),('COLD',coldhelper,26,'cold.bin')]
    cfg='MEMORY{\n'+''.join(f'{n}:start=${pc:04x},size=${sz:x},file="{(OUT/f).as_posix()}";\n'for n,pc,sz,f in specs)+'}\nSEGMENTS{\n'+''.join(f'{n}:load={n},type=ro;\n'for n,pc,sz,f in specs)+'}\n'
    (OUT/'component.cfg').write_text(cfg)
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    for cmd in [[cc/'ca65.exe','-g','-I',ROOT/'tools/reference',OUT/'component.s','-o',OUT/'component.o'],[cc/'ld65.exe','-C',OUT/'component.cfg',OUT/'component.o','-o',OUT/'unused.bin','--dbgfile',OUT/'component.dbg','-Ln',OUT/'component.lbl']]:
        cmd=list(map(str,cmd));guard=validate(cmd,OUT,cwd=ROOT);r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        commands.append(dict(command=cmd,guard=guard,returncode=r.returncode,stderr=r.stderr));assert r.returncode==0,r.stderr
    labels={}
    for line in(OUT/'component.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
        if m:labels[m[2]]=int(m[1],16)
    # Verify every displaced byte is precisely the claimed source consumer.
    expected=bytes([0xa5,address(b,'SavedJoypad1Bits'),0x05,address(b,'SavedJoypad2Bits'),0xaa,0x8e,address(b,'CrossoverMenuPressed')&255,address(b,'CrossoverMenuPressed')>>8,0x4d,address(b,'CrossoverMenuButtons')&255,address(b,'CrossoverMenuButtons')>>8,0x2d,address(b,'CrossoverMenuPressed')&255,address(b,'CrossoverMenuPressed')>>8,0x8d,address(b,'CrossoverMenuPressed')&255,address(b,'CrossoverMenuPressed')>>8,0x8e,address(b,'CrossoverMenuButtons')&255,address(b,'CrossoverMenuButtons')>>8])
    assert b['raw'][pos(edge):pos(edge)+20]==expected
    assert b['raw'][pos(retain):pos(retain)+6]==bytes([0x8d,address(b,'FmAlts')&255,address(b,'FmAlts')>>8,0x8d,address(b,'FmGroups')&255,address(b,'FmGroups')>>8])
    nr=address(b,'NrGlobalInit');raw=b['raw'];at=location(b,'CrossoverInit');old=raw[at:at+18]
    assert old[3:5]==bytes([0xa9,nr&255])and old[8:10]==bytes([0xa9,nr>>8])and old[13:15]==bytes([0xa9,nrbank|128])and old[-3:]==bytes([0x20,address(b,'FarCallCommon')&255,address(b,'FarCallCommon')>>8])
    new=copy.deepcopy(b);r=bytearray(raw);patches=[]
    for n,pc,sz,f in specs:
        data=(OUT/f).read_bytes();assert len(data)==sz
        at=location(b,'CrossoverInit')if n=='COLDHOOK'else pos(pc)
        patches.append(dict(segment=n,bank=(at-16)//8192,PC=pc,bytes=sz,file_offset=at,before_sha256=hashlib.sha256(raw[at:at+sz]).hexdigest(),after_sha256=hashlib.sha256(data).hexdigest()))
        r[at:at+sz]=data
    new['raw']=bytes(r)
    for n in ['MnMenuEdges','MnMenuColdInit']:
        new['syms'][n]=dict(val=hex(labels[n]),seg=own['id'])
    return new,dict(menu_bank=bank,helper_bytes=107,cold_helper_bytes=26,new_ROM29_bytes=0,patched_bytes=sum(p['bytes']for p in patches),padding_remaining=dict(PROTO_MENU=9,bank42_unclaimed_BECF_BEFF=49),public_PCs_unchanged=True,patches=patches,commands=commands,labels=labels,cold_gap_physical_owners=gaps)

def main():
    OUT.mkdir(exist_ok=True);q=dict(passed=False,source_CPU=True,native=False,installed=False,shared_host_modified=False)
    bound=[Path(__file__),SRC,ROOT/'tools/audit/prepare_menu_input_1101_v3.py',BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'character_select.s',BASE/'entrypoint.s',BASE/'candidate.cfg',ROOT/'src/characters.s',ROOT/'tools/audit/check_hogan_current_bounded_v1.py',ROOT/'tools/audit/ff_wram_host_controls_v7.py',ROOT/'tools/audit/arthur_cache_host_controls_v1.py',ROOT/'src/mmc5.s']
    before={str(p.resolve()):sha(p)for p in bound}
    try:
        texts=[p.read_text()for p in[BASE/'character_select.s',ROOT/'src/characters.s',BASE/'entrypoint.s',BASE/'candidate.cfg']]
        proposed=proposal(*texts)
        q['pure_source_proposal_sha256']={n:hashlib.sha256(s.encode()).hexdigest()for n,s in zip(['character_select.s','characters.s','entrypoint.s','candidate.cfg'],proposed)}
        old=H.C.qualified(BASE/'candidate.nes');new,layout=asm(old);q['layout']=layout
        calls=0;minimum=224;digest=hashlib.sha256()
        def invoke(m,name,**kw):
            nonlocal calls,minimum
            oldA=m.rawtags[1];c=H.start(m,name,**kw);live=bytes(m[0x101+c.sp+2:0x200])
            c,low=H.finish(m,c);calls+=1;minimum=min(minimum,low)
            assert c.sp==kw.get('sp',224)and bytes(m[0x101+c.sp:0x200])==live
            assert m.rawtags[1]==oldA and H.get(m,'CurrentBank')==oldA
            return c
        def fresh(bundle=new):
            m=C.fresh(bundle);H.put(m,CrossoverMenuState=0,CrossoverMenuButtons=0,CrossoverTitleDrawn=0,CrossoverOptionsFocus=0,CrossoverMenuIndex=0);return m
        def tick(m,p1=0,p2=0,mask=None,**kw):
            state=H.get(m,'CrossoverMenuState')
            H.put(m,SavedJoypad1Bits=p1,SavedJoypad2Bits=p2,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Mirror_PPUMASK=(0 if state in [1,3,5,7]else 24)if mask is None else mask)
            return invoke(m,'CrossoverMenuInput',**kw)
        def tap(m,key,pad=1):
            z=tick(m,key if pad==1 else 0,key if pad==2 else 0);tick(m);return z
        def roster(m):
            tick(m);tick(m,16);assert H.get(m,'CrossoverMenuState')==1
            tick(m);tick(m);assert H.get(m,'CrossoverMenuState')==2
        def snap(m):
            return tuple(H.get(m,n)for n in ['CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','FmAlts','FmGroups','MarioVariant','CrossoverContinue'])
        variant_names=['MarioVariant','BillVariant','ProtoVariant','Z2Variant','Cv3Variant','DarkwingVariant','CdVariant','M3Variant','VvVariant','KbVariant','TnVariant','RlVariant','RcVariant','MacVariant','IcVariant']
        variant_names=[n for n in variant_names if n in new['syms']]
        def variants(m):
            # Original new-family variants also use these explicit EXRAM
            # bytes (SMB2/Doki, Rogue Dawn and Final Fantasy respectively).
            return tuple(H.get(m,n)for n in variant_names)+tuple(m[a]for a in[0x5fe3,0x5fee,0x5fef])
        # Poison EXRAM before the genuine global initializer: cold default is
        # explicit, and only B/re-entry retains alternates.
        init=fresh();H.put(init,FmAlts=255,FmGroups=255);invoke(init,'CrossoverInit');assert(H.get(init,'FmAlts'),H.get(init,'FmGroups'))==(0,0)
        normal=simultaneous=build_edges=reentry=0
        for pad,hard,outlines,continued,confirm in itertools.product([1,2],[0,1],[0,1],[0,128],[16,128]):
            m=fresh();H.put(m,CrossoverBehaviorVersion=hard,PlayerOutlinesOff=outlines);roster(m);H.put(m,CrossoverContinue=continued)
            tap(m,2,pad);assert H.get(m,'CrossoverMenuIndex')==7
            for combined in [False,True]:
                n=C.fork(m)
                if not combined:tap(n,32,pad)
                c=tick(n,(32 if combined else 0)|confirm if pad==1 else 0,(32 if combined else 0)|confirm if pad==2 else 0)
                assert H.get(n,'CrossoverMenuState')==0 and H.get(n,'SelectedCharacter')==34 and H.get(n,'FmAlts')&1 and H.get(n,'CrossoverContinue')==continued
                assert c.a==continued|16,(combined,c.a,continued)
                if combined:simultaneous+=1
                else:normal+=1
            # Return to title with selected Karnov, re-enter while pressing
            # Select during one or several waiting BuildScreen frames.
            tap(m,32,pad);assert H.get(m,'SelectedCharacter')==34
            tap(m,64,pad);tick(m,16 if pad==1 else 0,16 if pad==2 else 0);assert H.get(m,'CrossoverMenuState')==1
            tick(m);tick(m);assert H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1;reentry+=1
            for held,waits in itertools.product([False,True],[0,3]):
                n=C.fork(m);tap(n,64,pad);tick(n,16 if pad==1 else 0,16 if pad==2 else 0)
                for i in range(waits):tick(n,32 if pad==1 else 0,32 if pad==2 else 0,mask=24)
                tick(n,32 if pad==1 else 0,32 if pad==2 else 0)
                assert H.get(n,'CrossoverMenuState')==2
                tick(n,((32 if held else 0)|confirm)if pad==1 else 0,((32 if held else 0)|confirm)if pad==2 else 0)
                # Deferred Select toggles retained Karnov BACK to Rygar.
                assert H.get(n,'CrossoverMenuState')==0 and H.get(n,'SelectedCharacter')==7 and not H.get(n,'FmAlts')&1
                assert H.get(n,'CrossoverContinue')==0;build_edges+=1
        # Every90 identity's normal confirm agrees with baseline. A combined
        # Select+confirm agrees with separate Select, then confirm, including
        # pending alternates. Full actual family logic supplies all IDs.
        profiles=ordinary_pairs=combined_pairs=0
        fields=['CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','FmAlts','FmGroups','MarioVariant','CrossoverContinue']
        for slot,total in enumerate(COUNTS):
            a=fresh(old);b=fresh(new)
            for z in [a,b]:H.put(z,CrossoverMenuState=2,CrossoverMenuIndex=slot);invoke(z,'MenuResolveCharacter');invoke(z,'QueueSelection')
            for variant in range(total):
                if variant:
                    for z in [a,b]:tap(z,32)
                assert snap(a)==snap(b)and variants(a)==variants(b),(slot,variant,snap(a),snap(b))
                for key in [16,128]:
                    left,right=[C.fork(z)for z in[a,b]]
                    ca,cb=tick(left,key),tick(right,key)
                    assert snap(left)==snap(right)and variants(left)==variants(right)and(ca.a,ca.x,ca.y,ca.p)==(cb.a,cb.x,cb.y,cb.p)and left.rawtags==right.rawtags,(slot,variant,key)
                    ordinary_pairs+=1
                    separate,combined=C.fork(b),C.fork(b)
                    tap(separate,32);tick(separate,key);tick(combined,32|key)
                    assert snap(separate)==snap(combined)and variants(separate)==variants(combined),(slot,variant,key,snap(separate),snap(combined))
                    digest.update(bytes(snap(combined)));combined_pairs+=1
                # B/Start preserves the exact highlighted profile, including
                # folded WWF/ContraForce groups and unrelated legacy alts.
                n=C.fork(b);beforeprofile=snap(n)[1:6];beforevariants=variants(n);tap(n,64);tick(n,16);tick(n);tick(n)
                assert snap(n)[1:6]==beforeprofile and variants(n)==beforevariants,(slot,variant,beforeprofile,snap(n))
                profiles+=1
        assert profiles==90
        # Prefix contract: every input combination in all9states. Skip the
        # actual dispatcher after the helper so no GUI action is invented.
        edgecases=0
        for state,held,previous,flags in itertools.product(range(9),[0,1,16,32,48,64,128,160,255],[0,32,255],[0x30,0x31,0x71,0xf1]):
            if state in [1,2]:continue # covered behaviorfully above
            m=fresh();H.put(m,CrossoverMenuState=state,CrossoverMenuButtons=previous,SavedJoypad1Bits=held,SavedJoypad2Bits=0)
            at=address(new,'CrossoverMenuInput')+13;m[0x5115]=0xc2;H.put(m,CurrentBank=0xc2)
            c=NesMPU(memory=m,pc=at);c.p=flags;c.y=91;c.sp=224;c.stPushWord(0x5aff)
            for i in range(200):
                if c.pc==at+20:break
                c.step()
            else:raise AssertionError('Menu edge hook did not restore dispatcher')
            assert c.sp==222 # hook restoredP/Y; outer sentinel remains
            assert(c.a,c.x,c.y)==(held&(~previous&255),held,91)and c.p&0x4d==flags&0x4d,(state,held,previous,flags,c.a,c.x,c.y,c.p)
            edgecases+=1
        assert all(sha(p)==h for p,h in before.items()),'Read-only base/input changed during proof'
        q.update(passed=True,base_ROM_sha256=before[str((BASE/'candidate.nes').resolve())],cold_global_defaults=True,normal_Karnov_contexts=normal,simultaneous_Karnov_contexts=simultaneous,BuildScreen_edge_contexts=build_edges,Karnov_B_title_reentry_contexts=reentry,all_roster_identities=profiles,baseline_normal_confirm_pairs=ordinary_pairs,combined_equals_separate_confirm_pairs=combined_pairs,nonroster_prefix_contract_cases=edgecases,cold_menu_calls=calls,minimum_standalone_SP=minimum,trace_sha256=digest.hexdigest(),contracts=dict(input='Same native edge algorithm; hook restores callerY/CVDI and returns X=held/A=pressed/NZ. Original dispatcher immediately loads state. Hook savesP/Y onstack and tail-jumps helper/resume; nested CheckDirection only for simultaneous Select+confirm. B priority retained.',scratch='No new SRAM; only bit0 of existing CrossoverContinue during state1, normalized backto00/80 before state2 confirm. R0..R7 not borrowed by helper; authentic CheckDirection retains existing native scratch effects.',cold='CrossoverInit equal18-byte farcall replacement initializes FmAlts/groups via26Bwrapper then tail-calls actual NrGlobalInit. BuildScreen sixSTAbytes becomeNOPs; B/title rebuild preserves selected profile.',funding='107B of116B exact PROTO_MENU padding plus26B unclaimed bank$42gap;0ROM29/0RAMkernel bytes. Every preexisting source/public PC remains unchanged.'),scope='Isolated assembled source macros overlaid IN MEMORY into actual stable native menu; real family/navigation/confirmation/init consumers execute. No shared O edits, new ROM/authenticated code cache, Mesen/raster/Main-stack/ISR qualification, installation or nightly admission. Root must integrate named optional segment, exact source callsites and requalify composed candidate before delivery.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']=before
    (OUT/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','layout','contracts']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
