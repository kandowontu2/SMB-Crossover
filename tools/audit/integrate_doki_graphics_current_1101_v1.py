"""Link original Doki rendering, palettes and eight-choice SMB2 selector."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/doki-current-component-1101-v1';S=O/'src';A=R/'build/doki-original-art-1101-v1';P=R/'build/wwf-roster-native-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


def main():
    assert not(O/'source-stage.json').exists()
    names=['component.s','smb2_roster.s','smb2_roster_render.s','smb2_roster_host_v5.s','smb2_roster_objects.s','smb2_roster_objects_native.inc','smb2_roster_core.s','smb2_roster_main_v2.s','smb2_roster_art.inc']
    snap=O/'before-graphics-sources.json'
    if not snap.exists():
        q=json.loads((O/'physics-controls.json').read_text());assert q['passed']
        for p,h in q['bindings'].items():assert sha(p)==h,p
        save(snap,{n:(S/n).read_text()for n in names})
    original=json.loads(snap.read_text())
    if 'smb2_roster_art.inc' not in original:
        original['smb2_roster_art.inc']=(S/'smb2_roster_art.inc').read_text();save(snap,original)
    text=original.copy()
    q=json.loads((A/'asset-controls.json').read_text());assert q['passed']
    for p,h in q['bindings'].items():assert sha(p)==h,p
    for src,dest in [('frames.bin','doki-frames.bin'),('palettes.bin','doki-palettes.bin')]: (S/dest).write_bytes((A/src).read_bytes())
    helper=R/'tools/reference/doki_current_draw_v1.s';write(S/'doki_current_draw.s',helper.read_text())
    text['component.s']+='\n.include "doki_current_draw.s"\n'
    render=text['smb2_roster_render.s']
    render=once(render,'Pose:jsr S2GraphicsBank\n','''Pose:jsr S2GraphicsBank
 lda S2Variant
 and #4
 beq DokiUSAGraphics
 lda S2Animation
 cmp #11
 bcs No
 jsr DdqBuildPose
 jmp DokiMeta
DokiUSAGraphics:
''')
    render=once(render,' sta SmChrBank\n lda #METASPRITE_SAMUS_BODY',' sta SmChrBank\nDokiMeta:\n lda #METASPRITE_SAMUS_BODY')
    # Native class3 has exactly the same64 record indices as class0.
    art=text['smb2_roster_art.inc'];m=re.search(r'^S2BodyRecord: \.byte ([^\n]+)',art,re.M)
    indices=list(map(int,m[1].split(',')));assert len(indices)==256 and indices[:64]==indices[192:]
    text['smb2_roster_art.inc']=art[:m.start()]+'S2BodyRecord: .byte '+','.join(map(str,indices[:192]))+art[m.end():]
    art=text['smb2_roster_art.inc'];records=re.findall(r'^S2Art(\d+): \.byte ([^\n]+)',art,re.M)
    assert [len(v.split(','))for _,v in records]==[21]*70+[9]*3
    art=re.sub(r'^S2Art(?:Lo|Hi):[^\n]+\n','',art,flags=re.M)
    art=art.replace('S2ArtEnd:','S2ObjectArtLo:.byte <S2Art70,<S2Art71,<S2Art72\nS2ObjectArtHi:.byte >S2Art70,>S2Art71,>S2Art72\nS2ArtEnd:')
    text['smb2_roster_art.inc']=art
    render=render.replace(' lda S2NativeCharacter\n asl\n ora S2Size',' lda S2NativeCharacter\n cmp #3\n bne :+\n lda #0\n:\n asl\n ora S2Size',1)
    start=render.index('.proc S2SetRecord\n');end=render.index('.endproc',start)+len('.endproc')
    render=render[:start]+'''.proc S2SetRecord
 tax
 cmp #70
 bcs Object
 ; All70 body records are exactly21B. Derive their16-bit address instead
 ; of storing146 pointer bytes. Keep X=record and preserve Y and R0..R7.
 sta SmPosePtr
 lda #0
 sta SmPosePtr+1
 .repeat 2
 asl SmPosePtr
 rol SmPosePtr+1
 .endrepeat
 txa
 clc
 adc SmPosePtr
 sta SmPosePtr
 bcc :+
 inc SmPosePtr+1
:
 .repeat 2
 asl SmPosePtr
 rol SmPosePtr+1
 .endrepeat
 txa
 clc
 adc SmPosePtr
 sta SmPosePtr
 lda SmPosePtr+1
 adc #0
 sta SmPosePtr+1
 lda SmPosePtr
 clc
 adc #<S2Art0
 sta SmPosePtr
 lda SmPosePtr+1
 adc #>S2Art0
 sta SmPosePtr+1
 rts
Object:
 lda S2ObjectArtLo-70,x
 sta SmPosePtr
 lda S2ObjectArtHi-70,x
 sta SmPosePtr+1
 rts
.endproc'''+render[end:]
    render=once(render,' lda #<Palettes\n clc\n adc NativePaletteOffset,x    ; table-index is native character*4.',' clc\n adc #<Palettes')
    render=once(render,'NativePaletteOffset:.byte 0,0,0,0,4,0,0,0,8,0,0,0,12,0,0,0\n','')
    render=once(render,' lda S2NativeCharacter\n asl\n asl\n tax\n clc\n adc #<Palettes',''' lda S2Variant
 and #4
 beq USAPalette
 lda S2Variant
 and #3
 asl
 asl
 tax
 clc
 adc #<DdqPalettes
 sta R0
 lda #>DdqPalettes
 adc #0
 jmp PaletteHigh
USAPalette:
 lda S2NativeCharacter
 asl
 asl
 tax
 clc
 adc #<Palettes''')
    render=once(render,' lda #>Palettes\n adc #0\n sta R1',' lda #>Palettes\n adc #0\nPaletteHigh:\n sta R1')
    text['smb2_roster_render.s']=render
    host=text['smb2_roster_host_v5.s']
    host=once(host,' farcall FmQueueName,jmp\n .res 3,$ea',' farcall DdqMenuName,jmp\n .res 3,$ea')
    host=once(host,' inc S2Variant\n lda S2Variant\n and #3',' inc S2Variant\n lda S2Variant\n and #7')
    start=host.index(' lda S2NativeCharacter\n',host.index('.proc S2MenuPortrait'))
    end=host.index(' farcall S2PublishBody',start)
    # Its source block has a fixed byte footprint in the foreign menu bank.
    host=host[:start]+' farcall DdqS2Standing\n .res 18,$ea\n'+host[end:]
    start=host.index('.proc S2MenuCopyC\n');end=host.index('.endproc',start)+len('.endproc')
    strings=['MARIO','LUIGI','TOAD','PEACH','IMAJIN','LINA','PAPA','MAMA'];offsets=[];n=0
    for item in strings:offsets.append(n);n+=len(item)+1
    data='S2MenuCopyC:=S2TextStatusC::CopyName\nS2NameOffsets:.byte '+','.join(map(str,offsets))+'\nS2DenseNames:\n'+''.join('.byte "'+v+'",0\n'for v in strings)
    host=host[:start]+data+host[end:];text['smb2_roster_host_v5.s']=host
    base=text['smb2_roster.s'];anchor=' .assert *-S2LivesOwnStart<=219,error,"Existing C80 source padding only"'
    base=once(base,anchor,'''CopyName:
 lda S2Variant
 and #7
 tay
 lda S2NameOffsets,y
 tay
NameLoop:
 lda S2DenseNames,y
 bne NameChar
 lda #$24
NameChar:
 sta VRAM_Buffer1,x
 inx
 cmp #$24
 beq NameSpace
 iny
NameSpace:
 dec R0
 bne NameLoop
 rts
'''+anchor);text['smb2_roster.s']=base
    # Compact the three genuinely class-dependent carry fields; validate
    # every original stored byte before replacing its four duplicate tables.
    objnative=text['smb2_roster_objects_native.inc']
    match=re.search(r'^S2CarryOffsets: \.byte ([^\n]+)',objnative,re.M);values=list(map(int,match[1].split(',')));assert len(values)==116
    groups=[values[i:i+29]for i in range(0,116,29)]
    assert all(all(g[i]==groups[0][i]for i in range(29)if i not in [1,8,22])for g in groups)
    tables='S2CarryOffsets: .byte '+','.join(map(str,groups[0]))+'\nS2CarryBigLo:.byte '+','.join(str(g[1])for g in groups)+'\nS2CarrySmallLo:.byte '+','.join(str(g[8])for g in groups)+'\nS2CarrySmallHi:.byte '+','.join(str(g[22])for g in groups)
    objnative=objnative[:match.start()]+tables+objnative[match.end():];text['smb2_roster_objects_native.inc']=objnative
    obj=text['smb2_roster_objects.s'];start=obj.index('.proc S2CarrySelect\n');end=obj.index('.proc S2FreeObject\n',start)
    obj=obj[:start]+'''.proc S2CarryAddHi
 php
 pha
 tya
 clc
 adc #14
 tay
 jmp S2CarryValue
.endproc
.proc S2CarryAddLo
 php
 pha
 sty R2
.endproc
S2CarryValue:
 cpy #1
 beq CarryBig
 cpy #8
 beq CarrySmall
 cpy #22
 beq CarrySmallHi
 lda S2CarryOffsets,y
 jmp CarryAdd
CarryBig:
 ldy S2NativeCharacter
 lda S2CarryBigLo,y
 jmp CarryAdd
CarrySmall:
 ldy S2NativeCharacter
 lda S2CarrySmallLo,y
 jmp CarryAdd
CarrySmallHi:
 ldy S2NativeCharacter
 lda S2CarrySmallHi,y
CarryAdd:
 sta R3
 pla
 plp
 adc R3
 php
 ldy R2
 plp
 rts
'''+obj[end:];text['smb2_roster_objects.s']=obj
    for n,t in text.items():write(S/n,t)
    # Existing S2 allocation is12KB. Preserve its first eight body pages and
    # all three vegetable pairs before filling only804..807.
    parent=(P/'candidate.nes').read_bytes();chrbytes=bytearray(parent[1048592+796*1024:1048592+808*1024]);chrbytes[8192:]=(A/'doki-shared-pages.chr').read_bytes();assert chrbytes[:8192]==parent[1048592+796*1024:1048592+804*1024]
    (O/'doki12k.chr').write_bytes(chrbytes);write(O/'asset.s','.segment "SMB2_ROSTER_CHR"\n.incbin "doki12k.chr"\n')
    build=json.loads((O/'doki-component-build.json').read_text())['command'];link=json.loads((O/'doki-link.json').read_text())['command'][:]
    asset=str(R/'build/arthur-goku-smb2-palette-v1/joint/asset.o');assert link.count(asset)==1;link[link.index(asset)]=str(O/'asset.o')
    def run(tag,cmd,check=True):
        guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(tag+'.json'),dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr))
        if check:assert q.returncode==0,q.stderr
        return q
    menu=O/'menu';menu.mkdir(exist_ok=True)
    t=(P/'full_roster_menu.s').read_text()
    t=once(t,' inc $5fe3\n lda $5fe3\n and #3',' inc $5fe3\n lda $5fe3\n and #7')
    write(menu/'full_roster_menu.s',t);write(menu/'entrypoint.s',(P/'entrypoint.s').read_text())
    cmd=json.loads((P/'main-build.json').read_text())['command'][:]
    for option,target in [('--create-full-dep',O/'main.dep'),('-o',O/'main.o')]:cmd[cmd.index(option)+1]=str(target)
    cmd[-1]=str(menu/'entrypoint.s');cmd[1:1]=['-I',str(menu)]
    run('graphics-main-build',cmd)
    oldmain=str(P/'main.o');assert link.count(oldmain)==1;link[link.index(oldmain)]=str(O/'main.o')
    run('graphics-asset-build',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','-I',str(O),str(O/'asset.s'),'-o',str(O/'asset.o')])
    def assemble():
        for attempt in range(16):
            z=run('graphics-build',build,check=False)
            if z.returncode==0:return
            repairs=re.findall(r'([^\r\n]+):(\d+): Error: Range error',z.stderr);assert repairs,z.stderr
            by={}
            for file,line in repairs:by.setdefault(Path(file),[]).append(int(line)-1)
            for path,indices in by.items():
                assert path.parent==S;lines=path.read_text().splitlines()
                for i in indices:
                    m=re.search(r'\bb(cc|cs|eq|ne|pl|mi|vc|vs)\b',lines[i]);assert m,lines[i];lines[i]=lines[i][:m.start()]+'j'+m[1]+lines[i][m.end():]
                write(path,'\n'.join(lines)+'\n')
        raise AssertionError('Graphics branch repair bound')
    def linked():
        run('graphics-link',link);p=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
        p.write_bytes(b''.join(l for l in p.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes');return scoped_load(O/'candidate.nes')
    # First shorten original object branches using already-linked source PCs.
    b=scoped_load(O/'candidate.nes')
    native=S/'smb2_roster_objects_native.inc';t=native.read_text()
    def short(m):
        lab,cond,target=m.groups()
        if lab in b['syms']and target in b['syms']and -128<=address(b,target)-address(b,lab)-2<=127:return lab+': b'+cond+' '+target
        return m[0]
    write(native,re.sub(r'^(S2O[0-9A-F]+): j(cc|cs|eq|ne|pl|mi|vc|vs) (\w+)',short,t,flags=re.M))
    assemble();b=linked()
    # The normal core linker limit catches overcommit. Exact source/helper
    # drawing and all old/new motion checks follow before native admission.
    assert address(b,'DdqPalettes')+16<=0xd600
    assert all(x==y or 1048592+804*1024<=i<1048592+808*1024 for i,(x,y)in enumerate(zip(parent,b['raw']))if i>=1048592)
    refs=[Path(__file__),helper,snap,A/'asset-controls.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.cfg',O/'asset.s',O/'doki12k.chr',O/'graphics-main-build.json',menu/'entrypoint.s',menu/'full_roster_menu.s',*[p for p in S.iterdir()if p.is_file()]]
    save(O/'graphics-assembly.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),private_playable=85,total_identities=90,conditional_active_guest_draw_bytes=17,draw_buffer=[0x5c90,0x5ca1],new_host_global_or_ZP_bytes=0,original_vegetable_prefix_unchanged=True,
        scope='Source-linked original Doki drawing/palettes/names/eight-choice selector. Motion,128 actual drawing packets, full menu/cold controller checks and native verification still required before any nightly replacement.',bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(source_assembled=True,candidate=sha(O/'candidate.nes'),private_playable=85,total=90,native=False,installed=False)))


if __name__=='__main__':main()
