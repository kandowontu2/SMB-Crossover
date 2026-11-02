"""Source-reproduce the current helper span, propose a bit8 WWF record in RAM only."""
from pathlib import Path
import ast,copy,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/bub-menu-candidate-1102-v2/wwf-helper-proposal'
BASE=R/'build/wwf-death-1102-v2/candidate.nes'
PIN='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def dragon_source():
    p=R/'tools/prepare_dragon_power_platform_v1.py';tree=ast.parse(p.read_text())
    text=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ASM'for t in n.targets))
    f=next(n for n in ast.parse((R/'tools/prepare_dragon_power_two_platforms_v1.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='main')
    pairs=[]
    for n in f.body:
        if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant)and isinstance(n.value.value,str):
            for t in n.targets:
                if isinstance(t,ast.Name)and t.id in['before','after']:pairs.append((t.id,n.value.value))
    for i in range(0,len(pairs),2):
        old,new=pairs[i:i+2];assert old[0]=='before'and new[0]=='after'and text.count(old[1])==1
        text=text.replace(old[1],new[1])
    start=text.index('.proc DpPlatformTick');end=text.index('.endproc',start)+len('.endproc')
    replacement=(R/'build/karnov-native-platform-1101-v1/shared-tick.s').read_text()
    replacement='KarnovTickStart:\n'+replacement[replacement.index('.proc DpPlatformTick'):replacement.index('.endproc')+len('.endproc')]+'\n.res 217-(*-KarnovTickStart),$ea'
    text=text[:start]+replacement+text[end:]
    text=text.replace('.assert *=$b134,lderror,"Original helper end must remain B134"','')
    text=text.replace('.res 12,$ff','KrPlatformDispatch:\nlda SelectedCharacter\ncmp #34\nbeq DpPlatformTick\njmp HpSpawnAndTrack\n.res 2,$ea',1)
    return text.replace(' phx\n',' txa\n pha\n').replace(' plx\n',' pla\n tax\n').replace(' phy\n',' tya\n pha\n').replace(' ply\n',' pla\n tay\n')

def expanded_source():
    p=R/'src/crossover_helpers.s';text=p.read_text()
    for name in['crossover_helper_data.inc','native_platform16.s','native_platform16_v2.s','native_helper_pause.s']:
        clause='.include "'+name+'"';assert text.count(clause)==1;text=text.replace(clause,(R/'src'/name).read_text())
    return text+'\n'+dragon_source()

def qualify(text,b):
    # Expand only the existing source farcall ABI, using actual physical-bank
    # symbols. Constants are not guessed from blank ROM contents.
    def far(m):
        target,tail=m.group(1),m.group(2);bank=(location(b,target)-16)//8192
        return 'sta SafecallA_SMC+1\nlda #<'+target+'\nsta FarcallJmpTarget_SMC+1\nlda #>'+target+'\nsta FarcallJmpTarget_SMC+2\nlda #$%02x\n%s FarCallCommon'%(bank|128,'jmp'if tail else'jsr')
    text=re.sub(r'farcall\s+(\w+)(,jmp)?',far,text)
    def dp(m):
        target=m.group(1);return far(type('Match',(),{'group':lambda self,i:target if i==1 else None})())
    text=re.sub(r'DpHostCall\s+(\w+),[^\s\n]+',dp,text)
    local=set(re.findall(r'\.proc\s+(\w+)|^(\w+):|^(\w+)\s*=',text,re.M));local={v for row in local for v in row if v}
    tokens=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',text))
    constants={name:address(b,name)for name in tokens&b['syms'].keys()-local}
    # These two build switches select the exact current expanded source path.
    constants.update(ENABLE_MMC5_EXPANDED=1,ENABLE_CROSSOVER=1)
    return '.setcpu "6502x"\n.macpack longbranch\n'+''.join(f'{n}=${v:04x}\n'for n,v in sorted(constants.items()))+text

def assemble(name,text,b):
    path=O/'source.s';cfg=O/'source.cfg';obj=O/'source.o';blob=O/(name+'.bin');lbl=O/(name+'.lbl')
    exports=set();depth=0
    for line in text.splitlines():
        proc=re.match(r'\s*\.proc\s+(\w+)',line)
        if proc:exports.add(proc.group(1));depth+=1
        elif re.match(r'\s*\.endproc',line):depth-=1
        elif depth==0:
            label=re.match(r'^(\w+):',line)
            if label:exports.add(label.group(1))
    exports=sorted(exports)
    text='.segment "CROSSOVER_HELPERS"\nHpSpanBegin:\n'+qualify(text,b)+'\n.segment "CROSSOVER_HELPERS"\n'+''.join('.export '+n+'\n'for n in exports)
    path.write_text(text);cfg.write_text('MEMORY{M:start=$a800,size=$b2a,file=%O;}SEGMENTS{CROSSOVER_HELPERS:load=M,type=ro;}')
    for command in[[str(R/'tools/Windows/cc65/bin/ca65.exe'),str(path),'-o',str(obj)],
        [str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(cfg),str(obj),'-o',str(blob),'-Ln',str(lbl)]]:
        p=subprocess.run(command,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
    obj.unlink()
    labels={m.group(2):int(m.group(1),16)for m in re.finditer(r'al ([0-9A-Fa-f]+) \.(\w+)',lbl.read_text())}
    return blob.read_bytes(),labels

def successor(text):
    assert text.count('HELPER_RECORDS = 34')==1
    text=text.replace('HELPER_RECORDS = 34','HELPER_RECORDS = 35')
    clause='  .byte 1,3,0,0,0,0,0,0 ; explicit new-profile H/V accommodations'
    assert text.count(clause)==1
    text=text.replace(clause,'  .byte 1,3,0,0,0,0,0,0,0,8 ; raw28 none, raw29 isolated WWF gate8')
    for name,value in dict(Key=0,Area=37,XLo=120,XHi=5,Y=208,Width=6,Axis=0,EasyGate=8,HardGate=8).items():
        text,n=re.subn(r'(^HpData'+name+r':\n\s*\.byte [^\n]+)',lambda m:m.group(1)+','+str(value),text,flags=re.M)
        assert n==1,name
    clause='  cpx #28\n.else\n  cpx #20\n.endif\n  bcs Next'
    assert text.count(clause)==1 and text.count('  cpy #28')==1
    text=text.replace(clause,'''  cpx #28
  bcc MaskOwner
  cpx #29
  bne Next
MaskOwner:
.else
  cpx #20
  bcs Next
.endif''').replace('  cpy #28','  cpy #30')
    save='''  .repeat 8,I
    lda R0+I
    pha
  .endrepeat'''
    restore='''  .repeat 8,I
    pla
    sta R0+7-I
  .endrepeat'''
    assert text.count(save)==1 and text.count(restore)==1
    text=text.replace(save,'''  ldx #0
SaveScratch:
  lda R0,x
  pha
  inx
  cpx #8
  bcc SaveScratch''')
    text=text.replace(restore,'''  ldx #7
RestoreScratch:
  pla
  sta R0,x
  dex
  bpl RestoreScratch''')
    # All foreign owners still iterate exactly the original34 records and
    # return their original final A/X/Y/P/scratch. WWF alone starts at34.
    entry='  ldy #0\nRecord:';assert text.count(entry)==1
    text=text.replace(entry,'''  ldy #0
  lda SelectedCharacter
  cmp #29
  bne Record
  ldy #34
Record:''')
    end='  cpy #HELPER_RECORDS\n  jne Record\n  rts';assert text.count(end)==1
    text=text.replace(end,'''  cpy #34
  beq RecordDone
  cpy #HELPER_RECORDS
  jne Record
RecordDone:
  rts''')
    return text+'\n.segment "CROSSOVER_HELPERS"\n.res $b2a-(*-HpSpanBegin),$ea\n'

def cpu_checks(b,new,newlabels):
    import check_hogan_current_bounded_v1 as M
    z=copy.deepcopy(b);raw=bytearray(z['raw']);at=16+26*8192+0x800;raw[at:at+len(new)]=new;z['raw']=bytes(raw)
    for name,pc in newlabels.items():
        if name in z['syms']:z['syms'][name]['val']=hex(pc)
    seed=M.fresh(b)
    def fork(bundle,**kw):
        m=M.fork(seed);m.bundle=bundle;M.put(m,**kw);return m
    def state(m,result):
        return tuple(result[k]for k in['A','X','Y','P']),bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x6000:0x8000]),tuple(m.rawtags)
    admissions=0;own=[];maskcases=0
    for owner in range(256):
        for mode in[0,1]:
            pair=[]
            for bundle in[b,z]:
                m=fork(bundle,SelectedCharacter=owner,Cv3Variant=0,CrossoverBehaviorVersion=mode,WorldNumber=0,LevelNumber=0,AreaType=1,AreaAddrsLOffset=5,AreaPointer=37,TimerControl=1)
                result=M.invoke(m,'HpConfigure',a=85,x=177,y=66,p=0x71);pair.append((m,result))
            if owner!=29:assert state(*pair[0])==state(*pair[1]),('Foreign exact admission ABI',owner,mode)
            else:
                m=pair[1][0];assert M.get(m,'HpCount')==1 and M.get(m,'HpRecord')==34
                assert [M.get(m,n)for n in['HpXLo','HpXHi','HpY','HpWidth','HpKind']]==[120,5,208,6,0]
                own.append(dict(raw=29,mode=mode,records=[34],center_x=1400,left_x=1376,initial_y=208,width=48))
            admissions+=1
        for cv in[0,1,2,3]:
            pair=[]
            for bundle in[b,z]:
                m=fork(bundle,SelectedCharacter=owner,Cv3Variant=cv);result=M.invoke(m,'HpGetCharacterMask',a=91,x=177,y=owner,p=0x71);pair.append((m,result))
            if owner!=29:assert state(*pair[0])==state(*pair[1]),('Foreign exact mask ABI',owner,cv)
            else:assert pair[1][1]['A']==8
            maskcases+=1
    # Every oldrecord's exact key/area and all owner/mask classes are tested;
    # all-byte foreign owners also have the complete1-1 ABI check above.
    scene_cases=0
    for record in range(34):
        key=b['raw'][location(b,'HpDataKey')+record];area=b['raw'][location(b,'HpDataArea')+record]
        for owner,cv in[(0,0),(1,0),(5,0),(5,1),(11,0),(24,0),(28,0),(29,0),(30,0),(34,0),(255,0)]:
            for mode in[0,1]:
                pair=[]
                for bundle in[b,z]:
                    m=fork(bundle,SelectedCharacter=owner,Cv3Variant=cv,CrossoverBehaviorVersion=mode,WorldNumber=key//4,LevelNumber=key%4,AreaType=area>>5,AreaAddrsLOffset=area&31,TimerControl=1)
                    result=M.invoke(m,'HpConfigure',a=85,x=177,y=66,p=0x71);pair.append((m,result))
                if owner!=29:assert state(*pair[0])==state(*pair[1]),('Foreign original34records',record,owner,cv,mode)
                else:assert M.get(pair[1][0],'HpCount')==int(key==0 and area==37)
                scene_cases+=1
    return dict(all_byte_owners_both_modes_exact_admission_cases=admissions,
        all_byte_masks_CV3_foreign_AXYP_RAM_maps_cases=maskcases,
        original34records_scene_mask_class_full_ABI_cases=scene_cases,WWF_new_record_cases=own,
        source_only_in_memory_overlay=True,ROM_written=False),z

def main():
    assert sha(BASE)==PIN;O.mkdir(exist_ok=True);b=scoped_load(BASE)
    text=expanded_source();old,oldlabels=assemble('original',text,b)
    start=16+26*8192+0x800;actual=b['raw'][start:start+0xb2a]
    assert old==actual,('Exact source/current helper mismatch',next((i for i,(a,z)in enumerate(zip(old,actual))if a!=z),None),len(old),len(actual))
    print(json.dumps(dict(source_reproduction=True,bytes=len(old),labels=len(oldlabels))))
    revised=successor(text);new,newlabels=assemble('proposed',revised,b)
    assert len(new)==len(old)
    checks,newbundle=cpu_checks(b,new,newlabels)
    q=dict(passed=True,source_reproduced=True,source_bytes=len(old),ROM_written=False,native=False,granted=False,
        physical_PRG=26,source_half_open=[0xa800,0xb32a],original_SHA256=hashlib.sha256(old).hexdigest(),
        labels=oldlabels,new_labels=newlabels,checks=checks,
        proposed_SHA256=hashlib.sha256(new).hexdigest(),
        relocations={n:dict(old=pc,new=newlabels[n])for n,pc in oldlabels.items()if n in newlabels and pc!=newlabels[n]},
        funding=dict(scratch_push_saved_bytes=14,scratch_restore_saved_bytes=16,new_record_and_masks_bytes=11,
            foreign_34_record_iteration_preservation_bytes=13,foreign_raw28_scratch_preservation_bytes=4,new_source_declared_padding_bytes=2),
        requested=dict(raw=29,all_six_WWF=True,isolated_gate_bit=8,new_record=34,
        center_x=1400,native_left_x=1376,initial_y=208,width_pixels=48,axis='horizontal',native_actor=40),
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),BASE,R/'src/crossover_helpers.s',R/'src/crossover_helper_data.inc',R/'src/native_platform16.s',R/'src/native_platform16_v2.s',R/'src/native_helper_pause.s',R/'tools/prepare_dragon_power_platform_v1.py',R/'tools/prepare_dragon_power_two_platforms_v1.py',R/'build/karnov-native-platform-1101-v1/shared-tick.s']})
    (O/'source-reproduction.json').write_text(json.dumps(q,indent=2)+'\n')
    own=[p for p in O.parent.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128

if __name__=='__main__':main()
