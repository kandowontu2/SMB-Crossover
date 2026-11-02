"""Source-funded marker and same-footprint Start-mask proposal; no ROM output."""
from pathlib import Path
import sys,json,copy,subprocess,itertools,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import audit_bub_menu_frontend_1102_v1 as F
M=F.M;address=F.address;location=F.location;O=F.O

def state(m):
    r=bytearray(m[:256])+bytearray(m[0x200:0x800])+bytearray(m[0x5c00:0x8000])
    # Variant/lease encoding is checked separately at its authoritative address.
    r[256+1536+0x5fe8-0x5c00]=0
    return bytes(r),tuple(bytes(q)for q in m.ram),tuple(m.rawtags),tuple(m.chr_latches),m.upper,m.lastset

def main():
    b=F.scoped_load(F.BASE);assert F.sha(F.BASE)==F.PIN
    source='''.setcpu "6502"
.segment "START"
.export BubStartFlags,BubStartFlagsEnd
BubStartFlags:
 php
 txa
 pha
 tya
 pha
 jsr $b599
 ; Original savedX is two bytes above currentSP. Keep savedY on stack
 ; until the end so Y can index the immutable masks without extra saves.
 tsx
 lda $0102,x
 ldy #8
Search:
 cmp Slots,y
 beq Found
 dey
 bpl Search
 ldy #4
Found:
 lda Alts,y
 and $5fe5
 sta $5fe5
 lda Groups,y
 and $5fe8
 sta $5fe8
 pla
 tay
 pla
 tax
 plp
 lda #0
 rts
Slots:.byte 10,31,9,26,255,23,30,28,32
Alts:.byte $44,$80,$20,$08,0,0,0,0,0
Groups=Alts+4
 .byte $20,$18,7,$80
BubStartFlagsEnd:
 .res $4a-(*-BubStartFlags),$ea
'''
    (O/'start-flags.s').write_text(source)
    (O/'start-flags.cfg').write_text('MEMORY{P:start=$b5e6,size=$4a,file=%O;}SEGMENTS{START:load=P,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'start-flags.s','-o',O/'start-flags.o'],
                [cc/'ld65.exe','-C',O/'start-flags.cfg',O/'start-flags.o','-o',O/'start-flags.bin','-Ln',O/'start-flags.lbl']]:
        q=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert not q.returncode,q.stderr
    body=(O/'start-flags.bin').read_bytes();assert len(body)==74
    nr=bytearray(b['raw']);patches=[]
    def patch(at,old,new,role):
        assert len(old)==len(new)and nr[at:at+len(old)]==old,role
        nr[at:at+len(new)]=new;patches.append(dict(offset=at,old=old.hex(),new=new.hex(),role=role))
    for pc,old,new,role in [(0xb4a0,0x80,0x40,'CF uses same P1 lease marker as BT'),
        (0xb5af,0xc0,0x40,'Only shared P1 lease triggers restoration'),
        (0xb5b6,0x3f,0xbf,'Restore clears lease and preserves new Bob selector')]:
        patch(16+29*8192+pc-0xa000,bytes([old]),bytes([new]),role)
    at=location(b,'FmStartRetireFlags');patch(at,nr[at:at+74],body,'Same74B Start masks, newslot32 retains80')
    nb=dict(b);nb['raw']=bytes(nr);seeds=[M.fresh(q)for q in [b,nb]]
    mask_cases=0;allflags_cases=0
    # All byte domains independently, all33 actual/public slot arguments.
    # Original high-bit palette markers normalize to the shared new bit6;
    # bit7 in the successor is independent Bob identity.
    for slot in range(33):
        for groups,alts,bob in itertools.chain(((g,255,bb)for g in range(256)for bb in [0,128]),
                                            ((0,a,bb)for a in range(256)for bb in [0,128])):
            pair=[]
            oldgroups=groups;newgroups=(groups&63)|(64 if groups&192 else 0)|bob
            for i,seed in enumerate(seeds):
                m=M.fork(seed);M.put(m,FmGroups=oldgroups if i==0 else newgroups,FmAlts=alts,VRAM_Buffer1_Offset=0)
                z=F.invoke(m,'FmStartRetireFlags',x=slot,a=173,y=99,p=0xf1);pair.append((m,z))
            old,zold=pair[0];new,znew=pair[1]
            expected_alts=alts&{9:32,10:68,26:8,31:128}.get(slot,0)
            expected_groups=(groups&{23:32,28:7,30:24}.get(slot,0))if slot!=32 else bob
            assert M.get(new,'FmAlts')==expected_alts and M.get(new,'FmGroups')==expected_groups,(slot,groups,alts,bob)
            assert state(old)==state(new),(slot,groups,alts,bob,'Start state')
            assert all(zold[k]==znew[k]for k in ['A','X','Y','P']),('Start AXYP',slot,zold,znew)
            mask_cases+=1
        for flags in range(256):
            # D and internal B flags are retained by native PHP/PLP; all bits.
            pair=[]
            for seed in seeds:
                m=M.fork(seed);M.put(m,FmGroups=63,FmAlts=255,VRAM_Buffer1_Offset=0)
                pair.append(F.invoke(m,'FmStartRetireFlags',x=slot,a=173,y=99,p=flags))
            assert all(pair[0][k]==pair[1][k]for k in ['A','X','Y','P'])
            allflags_cases+=1
        if slot%8==0:print('mask slots',slot,mask_cases,flush=True)
    # Entire real cold preview->menu-resolution restoration->Start paths.
    transitions=0;actual_rows=[]
    for slot,variants in [(23,2),(30,4)]:
        oldbase=M.fresh(b);newbase=M.fresh(nb)
        for variant in range(variants):
            if variant:
                for m in [oldbase,newbase]:
                    M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                    F.invoke(m,'CrossoverMenuInput')
            else:
                for m in [oldbase,newbase]:
                    M.put(m,CrossoverMenuIndex=slot)
                    F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
            for bob in [0,128]:
                for offset in range(77):
                    pair=[]
                    for i,base in enumerate([oldbase,newbase]):
                        m=M.fork(base)
                        if i:M.put(m,FmGroups=(M.get(m,'FmGroups')&127)|bob)
                        M.put(m,VRAM_Buffer1_Offset=offset)
                        # Re-execute the actual owner portrait, including its
                        # palette marker, before genuine resolver retirement.
                        if slot==30:F.invoke(m,'FmDrawCfPreview',a=26+variant)
                        else:F.invoke(m,'BtColdPortrait')
                        F.invoke(m,'MenuResolveCharacter')
                        F.invoke(m,'FmStartFlags',x=slot)
                        pair.append(m)
                    assert state(pair[0])==state(pair[1]),('preview restore Start',slot,variant,bob,offset)
                    assert M.get(pair[0],'FmGroups')==M.get(pair[1],'FmGroups')
                    transitions+=1
            actual_rows.append(dict(slot=slot,variant=variant,all_offsets=list(range(77)),Bub_Bob_markers=[0,128]))
    result=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,base_ROM_SHA256=F.PIN,
                marker_operand_bytes=3,Start_allocated_bytes=74,Start_used_bytes=72,Start_spare_bytes=2,
                mask_pairs=mask_cases,all_input_flag_pairs=allflags_cases,whole_preview_restore_Start_cases=transitions,
                previews=actual_rows,patches=patches,
                source_funding='Existing74B FmStartRetireFlags, overlapping zero masks and delayed register restoration. Retirement stays first.',
                caller_contract='All33 X slots; old Alts/Groups effective masks retained for0..31; only32 retains new bit7. Original AXYP/SP/maps/state exact except declared bit encoding.',
                bindings={p.relative_to(R).as_posix():F.sha(p)for p in [Path(__file__),Path(F.__file__),F.BASE,O/'start-flags.s',O/'start-flags.bin']})
    (O/'flag-proposal.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['bindings','patches','previews']}))
if __name__=='__main__':main()
