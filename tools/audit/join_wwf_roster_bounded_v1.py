"""Source-link all six original wrestlers onto the verified76-character ROM."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
from prepare_cv3_dmc_mirror import prepare
from prepare_wwf_roster_package_bounded_v1 import decode
P=R/'build/ready76-menu-fixed-v5';O=R/'build/wwf-roster-native-1101-v1'
H=R/'build/hogan-adapter';M=R/'build/wwf-hogan-natural-source-v15/joint'
PK=R/'build/wwf-roster-package-1101-v1';AU=R/'build/wwf-audio-private-1101-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')


def once(s,a,z):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='28693c0bf61926f5bef62511b5da0b71f97543170d27d0e03e59bb5e70edf0ca'
    refs={Path(__file__)}
    for p in[P/'source-stage.json',PK/'source-package.json',AU/'source-controls.json']:
        q=json.loads(p.read_text());assert q['passed']
        for f,h in q['bindings'].items():assert sha(f)==h,f
        refs.add(p)
    parent=scoped_load(P/'candidate.nes');raw=parent['raw']
    # These are actual un-emitted FF tails, not padding inside a live segment.
    gaps=[(65,0x1b46,0x1c00),(71,0xeae,0xf00),(71,0xf53,0x1000),(121,0x1f5f,0x2000)]
    for bank,a,z in gaps:
        assert raw[16+bank*8192+a:16+bank*8192+z]==bytes([255])*(z-a)
        assert not any('ooffs'in s and 'candidate.nes'in s.get('oname','')and int(s['ooffs'],0)<16+bank*8192+z and int(s['ooffs'],0)+int(s['size'],0)>16+bank*8192+a for s in parent['segs'].values())
    save(O/'resident-data-leases.json',dict(parent=sha(P/'candidate.nes'),leases=[dict(bank=b,A_view=[a+0xa000,z+0xa000],bytes=z-a,preimage='allFF/no emitted segment')for b,a,z in gaps],owners=['PROTO_GFX endDB46 preserves full original payload','BASS_POST endAF53 preserves all code','ROGUE_DAWN_HOST_AUX endBF5F preserves full original payload'],new_global_or_ZP_bytes=0))
    meta=json.loads((PK/'roster.json').read_text());blob=(PK/'metadata-and-cookie-slots.bin').read_bytes();rows={c['id']:c for c in meta['variants']}
    menu=[5,0,1,2,3,4];order=[5,0,2,3,4,1];packed=bytearray();offsets={}
    for actor in order:
        c=rows[actor];offsets[actor]=len(packed);packed.extend(blob[c['package_offset']:c['cookie_offset']]);packed.extend(bytes(16))
    assert len(packed)==8182
    windows=[bytes(packed[offsets[i]:offsets[i]+1687])for i in menu];assert all(len(w)==1687 for w in windows)
    (O/'metadata.chr').write_bytes(bytes(packed)+bytes(8192-len(packed)))
    (O/'wf-meta-offsets.bin').write_bytes(b''.join(offsets[i].to_bytes(2,'little')for i in menu))
    sources=[*range(637,645),667,667,645,667,646,647,648,649,*range(650,658)]
    assert len(sources)==24
    (O/'wf-page-sources.bin').write_bytes(bytes(p&255 for p in sources))
    (O/'wf-cookies.bin').write_bytes(bytes(96))
    def physical(page):return 546+page if page<58 else 442+page-58 if page<76 else 629+page-76
    idles={}
    for i in menu:
        c=rows[i];b=blob[c['package_offset']:c['cookie_offset']];_,cells=decode(b,0,0)
        idles[i]=bytes([len(cells)*4]+[v for t,role,x,y,p in cells for v in[t,role,y&255,x&255]])
    data0=['.setcpu "6502"','.segment "WF_ROSTER_DATA0"','.export WfIdleLow,WfIdleHigh,WfIdleBanks,WfIdlePages,WfRolePackets,WfIdleRecord,WfIdlePage']
    for i in[5,4]:data0+=['WfIdle%d:'%i,' .byte '+','.join(str(v)for v in idles[i])]
    data0+=['WfIdleRecord:=WfIdle5','WfIdlePage:=%d'%physical(decode(blob[rows[5]['package_offset']:rows[5]['cookie_offset']],0,0)[1][0][4]),
            'WfIdleLow: .byte '+','.join('<(WfIdle%d+$2000)'%i for i in menu),
            'WfIdleHigh: .byte '+','.join('>(WfIdle%d+$2000)'%i for i in menu),
            'WfIdleBanks: .byte '+','.join('$%02x'%(193 if i in[5,4] else 199)for i in menu),
            'WfIdlePages: .byte '+','.join(str(decode(blob[rows[i]['package_offset']:rows[i]['cookie_offset']],0,0)[1][0][4])for i in menu),
            'WfRolePackets:']
    for i in menu:data0+=[' .byte '+','.join(str(v)for v in[63,17,3,*rows[i]['palette'],63,21,3,*rows[i]['alternate_palette'],0])]
    data0+=['.assert *<=$bc00,lderror,"Native65 data tail only"']
    # Cross-bank idle pointers are ordinary source symbols, never guessed PCs.
    data0.insert(1,'.import WfIdle0,WfIdle1,WfIdle2,WfIdle3\n.export WfIdle4')
    write(O/'data0.s','\n'.join(data0)+'\n')
    data1=['.setcpu "6502"','.segment "WF_ROSTER_DATA2"','.export WfIdle0,WfIdle1,WfIdle2,WfIdle3',
           'WfIdle1:',' .byte '+','.join(str(v)for v in idles[1]),'.assert *<=$af00,lderror,"Native71 pre-Bass data tail only"',
           '.segment "WF_ROSTER_DATA1"']
    for i in[0,2,3]:data1+=['WfIdle%d:'%i,' .byte '+','.join(str(v)for v in idles[i])]
    data1+=['.assert *<=$b000,lderror,"Native71 data tail only"'];write(O/'data1.s','\n'.join(data1)+'\n')
    for leaf in['wwf_roster_native_support_v1.s','wwf_roster_cold_v1.s','wwf_roster_workers_v1.s']:
        path=R/'tools/reference'/leaf;refs.add(path);write(O/(leaf.replace('wwf_roster_','').replace('_v1','')),path.read_text())
    # Restore only this exact current91-byte common-gate source, not its tree.
    with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')as z:
        idx={q['path']:q for q in json.loads(z.read('index.json'))};q=idx['functional-roster-smb2-v1/joint/gm-nmi.s'];s=z.read('objects/'+q['sha256']).decode()
    s=once(s,'.include "gimmick_state.inc"','.import GmReady,GmPrevious,GmFresh,GmClock\nCHARACTER_GIMMICK=%d'%address(parent,'CHARACTER_GIMMICK'))
    write(O/'gm-nmi.s',s+'\n.assert *=$b65b,lderror,"Keep genuine common clock PCs"\n')
    # Native music is emitted into the existing acquired mixer image. Mark only
    # source length-counter writes dirty; preserve the original flags exactly.
    audio=(AU/'audio.s').read_text();audio=once(audio,'.segment "WF_AUDIO"','.segment "WF_A1_INACTIVE"')
    audio='.import GuestNativeApu,GuestNativeDirty,GuestNativeEnable\n'+audio
    def apu(m):
        op,hexaddr,suffix,pc=m.groups();a=int(hexaddr,16)
        if a==0x4017:return m[0]
        if a==0x4015:return f' {op} GuestNativeEnable ; original{pc}'
        if 0x4000<=a<=0x400f or 0x3ff0<=a<=0x3fff:
            d=a-0x4000;operand='GuestNativeApu'+('%+d'%d if d else'')+(suffix or'')
            out=f' {op} {operand} ; original{pc}'
            if d&3==3:out+='\n php\n inc GuestNativeDirty%+d%s\n plp'%(d,suffix or'')
            return out
        return m[0]
    audio=re.sub(r' (sta|stx|sty) \$([0-9a-f]{4})(,x|,y)? ; original([0-9A-F]{4})',apu,audio)
    write(O/'audio.s',audio)
    # C2's public boundaries remain fixed before runtime state. Source original
    # sound callbacks now enqueue their own distinct original channels in A3.
    world=(M/'world.s').read_text();world=once(world,'WfRenderBuffer:.res 64','WfRenderBuffer:.res 69')
    world='.import WfQueueAudioCue\n'+once(world,' inc WfCuePending\n rts',' jmp WfQueueAudioCue')
    write(O/'world.s',world)
    selected='''.setcpu "6502"
.segment "WF_HOGAN_METADATA"
.export WfHoganMetadata,WfHoganMetadataEnd
WfHoganMetadata:.res 1687,0
WfHoganMetadataEnd:
.segment "WF_OWNER_STATE"
.export WfHostReady
WfHostReady:.res 1
.segment "WF_OWNER_COOKIE"
.export WfOwnerCookie
WfOwnerCookie:.res 16,0
.segment "WF_RAM3_COOKIE"
.res 16,0
''';write(O/'selected-extra.s',selected)
    owner=(R/'build/hogan-thomas-current/wf-owner.s').read_text()
    owner=re.sub(r' lda FmGroups\n and #7\n bne (\w+)',r' lda FmGroups\n and #7\n cmp #6\n bcs \1',owner)
    owner=once(owner,' ldx #15\nWfAuthByte:\n lda WfOwnerCookie,x\n cmp WfExpectedCookie,x\n bne WfAuthNo\n dex\n bpl WfAuthByte',
        ' lda FmGroups\n and #7\n asl\n asl\n asl\n asl\n clc\n adc #15\n tay\n ldx #15\nWfAuthByte:\n lda WfOwnerCookie,x\n cmp WfExpectedCookie,y\n bne WfAuthNo\n dey\n dex\n bpl WfAuthByte')
    owner=once(owner,'WfConstructNew:\n lda #5','WfConstructNew:\n lda FmGroups\n and #7\n bne :+\n lda #6\n:\n sec\n sbc #1')
    owner=once(owner,'WfCopyVerified:\n','WfCopyVerified:\n jsr WfLoadRosterMeta\n jcc WfCopyFailed\n lda FmGroups\n and #7\n asl\n asl\n asl\n asl\n clc\n adc #<WfCookieC\n sta R0\n lda #>WfCookieC\n adc #0\n sta R1\n')
    owner=once(owner,' lda WfCookieC,y',' lda (R0),y')
    owner=once(owner,' lda R2\n clc\n adc #<629',' ldx R2\n lda WfPageSourceTable,x')
    owner=re.sub(r'\.incbin "[^"\n]+wf-cookie\.bin"','.incbin "wf-cookies.bin"',owner)
    owner='.import WfLoadRosterMeta,WfPageSourceTable\n'+owner
    owner=once(owner,' lda #2\n sta CurrentBankC\n sta $5116\n lda FmGroups',
               'WfAuthCookie:\n lda #2\n sta CurrentBankC\n sta $5116\n lda FmGroups')
    owner='.export WfAuthCookie,WfCookieC\n'+owner
    write(O/'owner.s',owner)
    write(O/'expected.s','.import WfCookieC\n.export WfExpectedCookie:=WfCookieC-$2000\n')
    runtime=(H/'runtime.s').read_text()
    runtime='.export WfColdIdentity\n.import WfColdBody,WfQueueRolesWorker,WfStatusHeaderWorker\n'+runtime
    runtime=re.sub(r' lda FmGroups\n and #7\n bne (\w+)',r' lda FmGroups\n and #7\n cmp #6\n bcs \1',runtime)
    start=runtime.index('WfBuildPose:\n');end=runtime.index('WfDrawBody:\n',start)
    decoder=(R/'tools/reference/wwf_roster_pose_decoder_v1.s').read_text().split('WfDecodeRosterPose:\n',1)[1].split('WfDecodeRosterPoseEnd:',1)[0]
    assert decoder.endswith(' rts\n');decoder=decoder[:-5]+''' lda WfPosePage
WfMapBodyPage:
 cmp #58
 bcc BodyFirst
 sbc #58
 cmp #18
 bcc BodySecond
 sbc #18
 clc
 adc #<629
 ldx #>629
 bne BodyPublish
BodySecond:
 clc
 adc #<442
 ldx #>442
 bne BodyPublish
BodyFirst:
 clc
 adc #<546
 ldx #>546
BodyPublish:
 ldy #0
 WfFar X5SetPhysicalChr
 rts
'''
    runtime=runtime[:start]+'WfBuildPose:\n'+decoder+'\n'+runtime[end:]
    runtime='.export WfMapBodyPage\n'+runtime
    start=runtime.index('WfColdPortrait:\n');end=runtime.index('WfColors:\n',start)
    runtime=runtime[:start]+'''WfColdPortrait:
 SaveRuntime
 jsr WfColdIdentity
 jcc WfRuntimeReturnC
 jsr WfColdBody
 sec
 jmp WfReturnPending

'''+runtime[end:]
    start=runtime.index('WfQueueRoles:\n');end=runtime.index('WfFresh:\n',start)
    runtime=runtime[:start]+'WfQueueRoles:\n WfFar WfQueueRolesWorker\n rts\n\n'+runtime[end:]
    start=runtime.index('StatusHeader:\n');end=runtime.index('StatusDone:rts',start)
    runtime=runtime[:start]+'''StatusHeader:
 WfFar WfStatusHeaderWorker
 jmp WfRuntimeReturnOriginal
'''+runtime[end:]
    runtime=once(runtime,' beq StatusHeader\n cmp #1',' beq StatusSave\n cmp #1')
    runtime=once(runtime,' SaveRuntime\n sty VRAM_Buffer1_Offset','StatusSave:\n SaveRuntime\n tsx\n lda $0112,x\n beq StatusHeader\n sty VRAM_Buffer1_Offset')
    runtime=once(runtime,'WfHudName:.byte " HOGAN "','')
    runtime=runtime.replace(' bne StatusDone',' jne StatusDone')
    write(O/'runtime.s',runtime)
    # Menu and fixed audio changes retain every following original public PC.
    parent_cmd=json.loads((P/'main-build.json').read_text())['command'][:]
    entry=next(Path(p)for p in parent_cmd if p.endswith('.s'))
    write(O/'entrypoint.s',entry.read_text()+'\n.import WfAudioProbe\n.export WfAtomicRti:=IrqScrollSplit+67\n.export GuestAudioBegin,GuestAudioFinish,GuestNativeApu,GuestNativeDirty,GuestNativeEnable\n')
    full=R/'build/hogan-thomas-current/src/full_roster_menu.s'
    write(O/'full_roster_menu.s',once(full.read_text(),' adc #18\n cmp #19',' adc #18\n cmp #24'))
    aud=R/'build/bt-ready-menu-1031-v2/joint/src/music_drivers/audio.s'
    audio_main=once(aud.read_text(),'  jmp GmFamilyNmiGate','  jmp WfAudioProbe')
    audio_main=once(audio_main,'  lda #$bf\n  sta $5115','  lda #$e0\n  sta $5115')
    write(O/'audio-main.s',audio_main)
    # The include uses music_drivers/audio.s, so install only this one graft.
    (O/'music_drivers').mkdir(exist_ok=True);write(O/'music_drivers/audio.s',(O/'audio-main.s').read_text())
    cfg=(P/'candidate.cfg').read_text()
    cfg=once(cfg,'X5_NEW_41: start=$c000, size=$1c00,','X5_NEW_41: start=$c000, size=$1b46,')
    anchor=re.search(r'X5_NEW_41:[^;]+;',cfg)[0];cfg=once(cfg,anchor,anchor+'\nWF_DATA0_MEM:start=$bb46,size=$ba,type=ro,file=%O,fill=yes,fillval=$ff,bank=$41;')
    cfg=once(cfg,'RD_WX_AUX_MEM: start=$ad60, size=$12a0,','RD_WX_AUX_MEM: start=$ad60, size=$11ff,')
    anchor=re.search(r'RD_WX_AUX_MEM:[^;]+;',cfg)[0];cfg=once(cfg,anchor,anchor+'\nWF_WORKER_MEM:start=$bf5f,size=$a1,type=ro,file=%O,fill=yes,fillval=$ff,bank=$79;')
    cfg=once(cfg,'WF_RESIDENT_C:start=$dd00,size=$300,','WF_RESIDENT_C:start=$dd00,size=$2a6,')
    anchor=re.search(r'WF_RESIDENT_C:[^;]+;',cfg)[0];cfg=once(cfg,anchor,anchor+'\nWF_ALIAS_MEM:start=$bfa6,size=$5a,type=ro,file=%O,fill=yes,fillval=$ff,bank=$60;\nWF_AUDIO_C3_RUN:start=$de2e,size=$1b2,type=ro,file="",bank=3;')
    cfg=re.sub(r'CD_CHR_POST\s*:[^;]+;', 'WF_BODY_B_MEM:start=$6e800,size=$4800,type=ro,file=%O,fill=yes,fillval=0;',cfg,count=1)
    cfg=re.sub(r'WF_BODY_MEM\s*:[^;]+;\s*M3_WWF_UNALLOCATED\s*:[^;]+;', 'WF_BODY_MEM:start=$88800,size=$e800,type=ro,file=%O,fill=yes,fillval=0;',cfg,count=1)
    cfg=re.sub(r'WF_TEMPLATE_MEM\s*:[^;]+;\s*WF_METADATA_MEM\s*:[^;]+;\s*TMNT_WWF_UNALLOCATED\s*:[^;]+;', 'WF_WIDE_MEM:start=$9d400,size=$9c00,type=ro,file=%O,fill=yes,fillval=0;',cfg,count=1)
    cfg=once(cfg,'WF_TEMPLATE_CHR:load=WF_TEMPLATE_MEM,','WF_TEMPLATE_CHR:load=WF_WIDE_MEM,')
    cfg=re.sub(r'\s*WF_METADATA_CHR:[^;]+;','',cfg,count=1)
    cfg=once(cfg,'SEGMENTS {','SEGMENTS {\nWF_ROSTER_DATA0:load=WF_DATA0_MEM,type=ro;\nWF_ROSTER_WORKERS:load=WF_WORKER_MEM,type=ro;\nWF_ALIAS_A:load=WF_ALIAS_MEM,type=ro;\nWF_BODY_B_CHR:load=WF_BODY_B_MEM,type=ro;')
    cfg=once(cfg,'WF_RAM3_COOKIE:','WF_AUDIO_C3:load=WF_A3_MEM,run=WF_AUDIO_C3_RUN,type=ro;\nWF_ROSTER_CUES:load=WF_A3_MEM,type=ro;\nWF_RAM3_COOKIE:')
    # Data1 must follow BASS_POST and precede the original fixed B000 pages.
    line='WF_ROSTER_DATA1:load=X5_NEW_47,type=ro,start=$af53;'
    anchor=re.search(r'BASS_POST:[^;]+;',cfg)[0];cfg=once(cfg,anchor,'WF_ROSTER_DATA2:load=X5_NEW_47,type=ro,start=$aeae;\n'+anchor+'\n'+line)
    outputs={};counter=0
    def redirect(m):
        nonlocal counter
        if m[1]in['','%O']:return m[0]
        counter+=1;p=O/'sideoutputs'/(f'{counter:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    write(O/'candidate.cfg',re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,cfg))
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    def asm(stem):
        run(stem+'-build',[R/'tools/Windows/cc65/bin/ca65.exe','-g','-I',O,'-I',R,'-I',M,'-I',H,O/(stem+'.s'),'-o',O/(stem+'.o'),'-l',O/(stem+'.lst')])
    # Include priority changes only these reviewed source grafts.
    cmd=parent_cmd[:];cmd[1:1]=['-I',str(O)]
    cmd[cmd.index(str(entry))]=str(O/'entrypoint.s')
    for flag,name in[('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/name)
    run('main-build',cmd)
    stems=['owner','expected','runtime','world','selected-extra','audio','native_support','cold','workers','data0','data1','gm-nmi']
    for stem in stems:asm(stem)
    bodies=(PK/'body-pages.chr').read_bytes();(O/'body0.chr').write_bytes(bodies[:58*1024]);(O/'body1.chr').write_bytes(bodies[58*1024:76*1024])
    (O/'stream.chr').write_bytes(bytes(39*1024))
    write(O/'stream.s','\n'.join(f'.segment "{seg}"\n.incbin "{(O/name).as_posix()}"'for seg,name in[('WF_BODY_CHR','body0.chr'),('WF_BODY_B_CHR','body1.chr'),('WF_TEMPLATE_CHR','stream.chr')])+'\n');asm('stream')
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    replacements={str(P/'main.o'):O/'main.o',str(R/'build/hogan-thomas-current/wf-owner.o'):O/'owner.o',str(R/'build/hogan-thomas-current/wf-expected.o'):O/'expected.o',str(H/'runtime.o'):O/'runtime.o',str(M/'world.o'):O/'world.o',str(M/'selected-extra.o'):O/'selected-extra.o',str(R/'build/hogan-thomas-current/wf-stream.o'):O/'stream.o',str(R/'build/functional-roster-smb2-v1/joint/gm-nmi.o'):O/'gm-nmi.o'}
    del replacements[str(R/'build/functional-roster-smb2-v1/joint/gm-nmi.o')]
    for old,new in replacements.items():assert link.count(old)==1,old;link[link.index(old)]=str(new)
    link.remove(str(M/'idle.o'))
    link += [str(O/(s+'.o'))for s in['audio','native_support','cold','workers','data0','data1']]
    for flag,name in[('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def linked(tag):
        run(tag+'-link',link);p=O/'candidate.dbg';data=p.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
        p.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
    linked('provisional')
    def image(suffix):return next(p for n,p in outputs.items()if n.endswith(suffix)).read_bytes()
    images=[image(n)for n in['final-a1.bin','final-c2.bin','final-a3.bin']]
    c2=images[1];assert not any(c2[address(parent,'WfHoganMetadata')-0xc000:address(parent,'WfHoganMetadata')-0xc000+1687])
    assert [i for i in range(8)if not any(c2[1024*i:1024*i+1024])]==[0,1,3]
    cookies=[]
    for variant,window in enumerate(windows):
        selected=bytearray(c2);selected[0xa42:0xa42+1687]=window
        cookies.append(bytes([167,29,variant,2])+hashlib.sha256(images[0]+selected+images[2]+bodies).digest()[:12])
    (O/'wf-cookies.bin').write_bytes(b''.join(cookies));asm('owner')
    cache=bodies[76*1024:]+images[0]+b''.join(c2[i*1024:(i+1)*1024]for i in[2,4,5,6,7])+images[2]+(O/'metadata.chr').read_bytes()+bytes(2048)
    assert len(cache)==39*1024;(O/'stream.chr').write_bytes(cache);asm('stream')
    linked('final');prepare(R,O/'candidate.nes')
    assert images==[image(n)for n in['final-a1.bin','final-c2.bin','final-a3.bin']]
    actual=scoped_load(O/'candidate.nes');assert native_abi(actual)==native_abi(parent)
    assert address(actual,'WfHoganMetadata')==0xca42 and address(actual,'WfHoganMetadataEnd')==0xd0d9
    assert address(actual,'WfPosePage')==address(parent,'WfPosePage')+5
    allowed=[(442,460),(546,604),(629,668)]
    assert all(a==z or any(1048592+lo*1024<=i<1048592+hi*1024 for lo,hi in allowed)for i,(a,z)in enumerate(zip(raw,actual['raw']))if i>=1048592)
    # Thomas source imports are unchanged, so its exact selected image is retained.
    assert image('kernel.bin')==next(p for p in(P/'sideoutputs').iterdir()if p.name.endswith('kernel.bin')).read_bytes()
    refs|={Path(p)for p in link if p.endswith('.o')}
    dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs|={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
    refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'assembly-stage.json',dict(passed=True,source=True,native=False,installed=False,parent=sha(P/'candidate.nes'),candidate=sha(O/'candidate.nes'),private_playable=81,CHR_owner_pages=115,all_six_original_metadata_windows=True,
                                  limits=['Native/controller/IRQ/SMC/graphics/audio and full-roster transition checks remain required','Source-only until exact candidate passes; installed76 ROM unchanged'],bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),private_playable=81,native=False,installed=False)))


if __name__=='__main__':main()
