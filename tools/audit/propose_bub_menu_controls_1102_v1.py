"""Prove granted66B Select/confirmation glue with static UI in memory only."""
from pathlib import Path
import sys,json,hashlib,collections
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import propose_bub_menu_art_1102_v1 as A
F=A.F;M=F.M;O=F.O;address=F.address;location=F.location

def bundle():
    b=F.scoped_load(F.BASE);assert F.sha(F.BASE)==F.PIN
    art=json.loads((O/'art-proposal.json').read_text());flags=json.loads((R/'docs/qa/allocations/bub-menu-flags-1102-v2.json').read_text())
    nr=bytearray(b['raw']);patches=[]
    def apply(z):
        at=z['offset'];old=bytes.fromhex(z['old']);new=bytes.fromhex(z['new'])
        assert nr[at:at+len(old)]==old;nr[at:at+len(new)]=new;patches.append(z)
    for z in art['requested_patches']+flags['patches']:apply(z)
    navroot=R/'build/bub-menu-navigation-1102-v1';nav=json.loads((navroot/'proposal.json').read_text())
    at=16+124*8192;body=(navroot/'navigation.bin').read_bytes();assert len(body)==224
    apply(dict(offset=at,old=bytes(nr[at:at+224]).hex(),new=body.hex(),role='Granted33slot navigation'))
    for z in nav['patches']:apply(z)
    body=A.assemble('menu-controls','''.setcpu "6502"
.segment "CODE"
.export BubMenuToggle,BubMenuConfirmGate
BubMenuToggle:
 lda $7308
 and #$20
 beq ForeignToggle
 cmp $7309
 bne ForeignToggle
 lda $5fe8
 eor #$80
 sta $5fe8
 ; Equality CMP above supplies native handledC; no extra byte required.
 rts
ForeignToggle:
 lda #$8a
 sta $016c
 lda #$ba
 sta $016d
 lda #$cc
 jmp $015a
BubMenuConfirmGate:
 ldx $7309
 cpx #32
 bne ForeignConfirm
 sec
 rts
ForeignConfirm:
 sta $016a
 lda #$f3
 sta $016c
 lda #$bf
 sta $016d
 lda #$cc
 jmp $015a
''',0xad39,66)
    assert len(body)==63
    at=16+66*8192+0xd39
    apply(dict(offset=at,old=bytes(nr[at:at+66]).hex(),new=(body+bytes([0xea])*3).hex(),role='Granted66B dead cursor fallback: Select36B + blocked confirmation27B'))
    # Exact actual operand sites, not stale assembler-source patterns.
    for pc,old,new,role in [(0xa7ee,0xf3,0x5d,'Confirm gate low'),(0xa7f3,0xbf,0xad,'Confirm gate high'),(0xa7f8,0xcc,0xc2,'Confirm gate bank'),
        (0xa860,0x8a,0x39,'Select wrapper low'),(0xa865,0xba,0xad,'Select wrapper high'),(0xa86a,0xcc,0xc2,'Select wrapper bank')]:
        at=16+66*8192+pc-0xa000;apply(dict(offset=at,old=bytes([old]).hex(),new=bytes([new]).hex(),role=role))
    nb=dict(b);nb['raw']=bytes(nr);return b,nb,patches

def state(m):
    # Ignore stack and deliberate normalized palette lease/retained Bob bit.
    out=bytearray(m[:256])+bytearray(m[0x200:0x800])+bytearray(m[0x5c00:0x8000])
    out[256+1536+0x5fe8-0x5c00]&=63
    return bytes(out),tuple(bytes(x)for x in m.ram),tuple(m.rawtags),tuple(m.chr_latches),m.upper,m.lastset

def main():
    old,new,patches=bundle();oldseed=M.fresh(old);newseed=M.fresh(new)
    cases=0;profiles=0;names=collections.Counter();portraits=collections.Counter()
    pcname=address(old,'FmQueueName')+3;pcportrait=address(old,'FmDrawPreviewSelected')
    def trace(c):
        if c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==204:
            if c.pc==pcname:names[c.a]+=1
            if c.pc==pcportrait:portraits[c.a]+=1
    # Real oldprofile lifecycle, each Select increments the actual source
    # selector. Keep all fixture states in memory and aggregate only counters.
    for slot,count in enumerate(F.COUNTS):
        pair=[M.fork(oldseed),M.fork(newseed)]
        for m in pair:
            M.put(m,CrossoverMenuIndex=slot)
            F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                for m in pair:
                    M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                    F.invoke(m,'CrossoverMenuInput')
            for bob in [0,128]:
                for keys in [0,32,16,128,48,160,176]:
                    results=[]
                    for i,base in enumerate(pair):
                        m=M.fork(base)
                        if i:M.put(m,FmGroups=(M.get(m,'FmGroups')&127)|bob)
                        M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
                        z=F.invoke(m,'CrossoverMenuInput',watch=trace if i else None)
                        results.append((m,z))
                    assert state(results[0][0])==state(results[1][0]),('foreign lifecycle state',slot,variant,bob,keys)
                    assert all(results[0][1][k]==results[1][1][k]for k in ['A','X','Y','P']),('foreign AXYP',slot,variant,bob,keys,results[0][1],results[1][1])
                    cases+=1
            profiles+=1
        print('oldslot',slot,profiles,flush=True)
    own=[]
    m=M.fork(newseed);M.put(m,CrossoverMenuIndex=32,FmGroups=0,VRAM_Buffer1_Offset=0)
    F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection',watch=trace)
    for variant in range(4):
        if variant:
            M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
            F.invoke(m,'CrossoverMenuInput',watch=trace)
        assert M.get(m,'SelectedCharacter')==39 and bool(M.get(m,'FmGroups')&128)==bool(variant&1)
        commands=F.commands(m);name=[q['bytes']for q in commands if q['address']==0x2328][-1]
        expected=[36]*16;expected[6:9]=[11,24 if variant&1 else 30,11]
        assert name==expected,('source name',variant,name)
        pal=[q['bytes']for q in commands if q['address']==0x3f11][-1]
        assert pal==([44,35,48]if variant&1 else[42,38,48])
        assert list(m[0x200:0x210])==[159,0,0,120,159,0,0,128,175,2,0,120,175,4,0,128]
        for key in [16,128,48,160,176]:
            n=M.fork(m);M.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
            F.invoke(n,'CrossoverMenuInput');assert M.get(n,'CrossoverMenuState')==2,'Unqualified gameplay admitted'
        own.append(dict(variant=variant,raw=39,Bob=bool(variant&1),name=name,source_palette=pal,confirmation_blocked=True))
    # The source art reads exactly the blank pair and genuine two source pairs;
    # palette and ordered OAM are checked through actual menu code above.
    q=dict(passed=True,proposal_only=True,ROM_written=False,native=False,menu_admitted=False,base_ROM_SHA256=F.PIN,
        granted_frontend_used_bytes=63,allocated_bytes=66,spare_bytes=3,Select_bytes=36,confirmation_gate_bytes=27,
        old_profiles=profiles,foreign_actual_input_cases=cases,own_static_UI_cases=own,
        observed_name_rows=dict(sorted(names.items())),observed_portrait_rows=dict(sorted(portraits.items())),
        required_operand_patches=patches[-6:],all_patches=patches,
        remaining=['Formal static-art/data grants.','Actual source reader and ISR closure.','Root native menu/backend pass, then replace only owning gate SEC with CLC after readiness approval.'],
        bindings={p.relative_to(R).as_posix():F.sha(p)for p in [Path(__file__),Path(A.__file__),F.BASE,O/'art-proposal.json',O/'flag-proposal.json',O/'menu-controls.bin',O/'menu-controls.s',R/'docs/qa/allocations/bub-menu-1102-v1.json',R/'docs/qa/allocations/bub-menu-flags-1102-v2.json']})
    (O/'controls-proposal.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<16000000 and len(files)<=128
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','all_patches']}))
if __name__=='__main__':main()
