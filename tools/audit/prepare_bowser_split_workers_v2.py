"""Real, source-linked split loader/router preparation; no playable ingress."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load

P = R/'build/coherent62-lives-fixes-v1'
O = R/'build/bowser-split-workers-v2'
J = O/'joint'
D = J/'bowser'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, s):
    if p.suffix == '.s' and p.parent == D:
        for name in ['Rejected','Warm','ColdReturn','Failed','Restore','Page','No','Set','Byte','Reject','Publish','Done']:
            s=re.sub(r'\b'+name+r'\b','Bw'+p.stem.title()+name,s)
    p.write_text(s, encoding='utf-8', newline='\n')


COMMON = r'''
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,OperMode,DisableScreenFlag,NmiDisable,FamilyMainCommit
.import Mirror_PPUMASK,Mirror_PPUCTRL,HorizontalScroll,VerticalScroll
.import CurrentBank,CurrentBankC,ReloadCHRBank,X5PublishChr
.import FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.importzp R0,R1
.macro BwFar Target,Mode
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
'''

LOAD = r'''
.include "common.inc"
.import BwPrepare,BwCopyVerify,BwRestorePPU
.export BwLoad
.segment "BW_ROM_LOAD"
; Outer frame owns the original eight saved bytes. Inner bank calls return
; before this frame is inspected. Result changes only original carry.
BwLoad:
 php
 pha
 txa
 pha
 tya
 pha
 lda R0
 pha
 lda R1
 pha
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 BwFar BwPrepare,jsr
 bcc Rejected
 bne Warm
 sei
 lda #0
 sta ReloadCHRBank
 BwFar X5PublishChr,jsr
 BwFar BwCopyVerify,jsr
 bcc Failed
 tsx
 lda $0108,x
 ora #1
 sta $0108,x
 jmp ColdReturn
Failed:
 lda #0
 sta $dfe0
 tsx
 lda $0108,x
 and #$fe
 sta $0108,x
ColdReturn:
 BwFar BwRestorePPU,jsr
 jmp Restore
Warm:
 tsx
 lda $0108,x
 ora #1
 sta $0108,x
 jmp Restore
Rejected:
 tsx
 lda $0108,x
 and #$fe
 sta $0108,x
Restore:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta R1
 pla
 sta R0
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.assert *<=$c000,lderror,"Bowser A68 exact224B lease"
'''

COPY = r'''
.include "common.inc"
.import BwPublishCookie
.export BwCopyVerify,BwCopy256,BwVerify256,BwMapPage,BwRestorePPU
.segment "BW_ROM_COPY"
; Called only by the gated outer loader; raw C3 remains selected throughout
; nested A-view farcalls. Source cookie bytes are zero until valid-last.
BwCopyVerify:
 lda #3
 sta CurrentBankC
 sta $5116
 lda #0
 sta $dfe0
 lda Mirror_PPUCTRL
 and #$fb
 ora #$20
 sta $2000
 lda #0
 sta R0
 lda #$c0
 sta R1
Page:
 jsr BwMapPage
 ldx #4
BwCopy256:
 lda $2007
 sta (R0),y
 iny
 bne BwCopy256
 inc R1
 dex
 bne BwCopy256
 lda R1
 sec
 sbc #4
 sta R1
 jsr BwMapPage
 ldx #4
BwVerify256:
 lda $2007
 cmp (R0),y
 bne Failed
 iny
 bne BwVerify256
 inc R1
 dex
 bne BwVerify256
 lda R1
 cmp #$e0
 bne Page
 BwFar BwPublishCookie,jmp
Failed:
 clc
 rts
BwMapPage:
 lda #3
 sta $5130
 lda R1
 sec
 sbc #$c0
 lsr
 lsr
 clc
 adc #$9f                    ; physical927 + destination1KB index
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                    ; genuine buffered-read discard
 ldy #0
 rts
BwRestorePPU:
 BwFar X5PublishChr,jsr
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005
 rts
.assert *<=$b600,lderror,"Bowser A36 exact221B lease"
'''

CHECK = r'''
.include "common.inc"
.export BwCheck,BwPrepare,BwCookie,BwPublishCookie
.segment "BW_ROM_CHECK"
BwCheck:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 lda SelectedCharacter
 cmp #27
 bne No
 lda #3
 sta CurrentBankC
 sta $5116
 ldx #15
Byte:
 lda $dfe0,x
 cmp BwCookie,x
 bne No
 dex
 bpl Byte
 tsx
 lda $0104,x
 ora #1
 bne Set
No:
 tsx
 lda $0104,x
 and #$fe
Set:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts
; C=eligible, A=warm0/1. This is an internal volatile-A predicate, not the
; public loader ABI. It cannot authorize an active, non-busy or foreign load.
BwPrepare:
 lda SelectedCharacter
 cmp #27
 bne Reject
 lda OperMode
 beq Reject
 lda FamilyMainCommit
 and #1
 beq Reject
 lda Mirror_PPUMASK
 and #$18
 bne Reject
 lda DisableScreenFlag
 beq Reject
 lda NmiDisable
 bpl Reject
 jsr BwCheck
 lda #0
 adc #0
 sec
 rts
Reject:
 lda #0
 clc
 rts
BwPublishCookie:
 php
 pha
 txa
 pha
 ldx #15
Publish:
 lda BwCookie,x
 sta $dfe0,x
 dex
 bne Publish
 lda #$a7
 sta $dfe0                    ; valid LAST after every copied byte verified
 pla
 tax
 pla
 plp
 sec
 rts
BwCookie:.incbin "cookie.bin"
.assert *<=$b600,lderror,"Bowser A84 exact215B lease"
'''

RETIRE = r'''
.include "common.inc"
.export BwRetire
.segment "BW_ROM_AUX"
; Resolver must call before publishing the next selected owner. No wrong
; family is invalidated, and no bank0/global/cache-state byte is borrowed.
BwRetire:
 php
 pha
 lda CurrentBankC
 pha
 lda #3
 sta CurrentBankC
 sta $5116
 lda $dfe0
 cmp #$a7
 bne Done
 lda $dfe1
 cmp #27
 bne Done
 lda #0
 sta $dfe0
Done:
 pla
 sta CurrentBankC
 sta $5116
 pla
 plp
 rts
.assert *<=$b400,lderror,"Bowser A88 exact204B lease"
'''


def main():
    assert not O.exists()
    proof = json.loads((R/'build/bowser-resource-closure-v1/proposal.json').read_text())
    assert sha(R/'build/bowser-resource-closure-v1/proposal.json') == '99dda7b3296c1fc2d44f662e328d46ad8ecec7a31d4541a60d5286bf560a1b7e'
    for p, h in proof['bindings'].items():
        assert sha(p) == h, p
    shutil.copytree(P/'joint', J)
    D.mkdir()
    grant = dict(status='ROOT_GRANTED_PRIVATE_BOWSER_SOURCE_PARTITION',
        authority='Root message grants these exact six A-view-only islands, body824..<827, carrier927..<935, temporalRAM3 family27. No widening/C-view/globalRAM/ZP/common growth/native/admission.',
        parent=proof['parent'], closure=sha(R/'build/bowser-resource-closure-v1/proposal.json'),
        ROM=proof['ROM'], CHR=proof['CHR'], temporal_RAM_bank=3, family=27,
        cookie='A3 BFE0..<BFF0, C3 DFE0..<DFF0; full16bytes, invalid-first/valid-last',
        interface_state='Only inside owned8KB image; no new global state',
        bindings={str(R/'build/bowser-resource-closure-v1/proposal.json'):sha(R/'build/bowser-resource-closure-v1/proposal.json')})
    write(O/'root-grant-and-partition.json', json.dumps(grant, indent=2)+'\n')
    # Current config is copied, then every explicit side-output is redirected
    # deliberately. Old object/source paths remain read-only dependencies.
    cfg=(J/'private.cfg').read_text()
    cfg=re.sub(r'file="([^"]+)"',lambda m:'file="'+str(J/Path(m[1]).name).replace('\\','/')+'"' if m[1] else m[0],cfg)
    source=load(P/'joint/candidate.nes')
    islands=[('LOAD',68,0x1f20,0x2000),('COPY',36,0x1523,0x1600),
             ('CHECK',84,0x1529,0x1600),('ROUTER',67,0x122b,0x1300),
             ('PREVIEW',83,0x1534,0x1600),('AUX',88,0x1334,0x1400)]
    segments_text=cfg.split('SEGMENTS {',1)[1]
    for name,bank,start,end in islands:
        # Locate the containing actual MEMORY record, not a guessed old name.
        pattern=re.compile(r'(?m)^\s*(\w+)\s*:\s*start\s*=\s*\$([0-9a-f]+)\s*,\s*size\s*=\s*\$([0-9a-f]+)[^;]*bank\s*=\s*\$'+f'{bank:02x}'+r'\s*;',re.I)
        matches=[m for m in pattern.finditer(cfg.split('SEGMENTS {',1)[0])
                 if (int(m[2],16)&0x1fff)<=start and end<=(int(m[2],16)&0x1fff)+int(m[3],16)]
        assert len(matches)==1,(name,[m[0] for m in matches])
        m=matches[0];old,base,size=m[1],int(m[2],16),int(m[3],16);first=base&0x1fff
        row=lambda n,a,z:f'{n}:start=${a:x},size=${z:x},type=ro,file=%O,fill=yes,fillval=$ff,bank=${bank:x};'
        replacement=row(old,base,start-first)+'\n'+row('BW_'+name+'_MEM',0xa000+start,end-start)
        post=first+size-end
        if post:
            replacement+='\n'+row(old+'_BW_POST',base+end-first,post)
        cfg=cfg[:m.start()]+replacement+cfg[m.end():]
        if post:
            for g in source['segs'].values():
                if 'ooffs' not in g:continue
                pos=int(g['ooffs'],0)-16
                if pos//8192!=bank or pos%8192<end:continue
                n=g['name'].strip('"')
                rg=re.compile(r'(?m)^(\s*'+re.escape(n)+r'\s*:[^;]*?load\s*=\s*)'+re.escape(old)+r'\b')
                cfg,count=rg.subn(lambda z:z[1]+old+'_BW_POST',cfg)
                assert count==1,(n,old)
    # These CHR owner budgets are split only at verified unemitted holes.
    old='TMNT_CHR_AFTER_GM:start=$cd000,size=$3000,type=ro,fill=yes,file=%O,fillval=$00;'
    normalized=re.sub(r'\s+','',cfg)
    # Match spacing in the real current source rather than replace an old CFG.
    pat=r'TMNT_CHR_AFTER_GM\s*:\s*start=\$cd000,\s*size=\$3000,[^;]*;'
    repl='TMNT_CHR_AFTER_GM:start=$cd000,size=$1000,type=ro,fill=yes,file=%O,fillval=$00;\nBW_BODY_MEM:start=$ce000,size=$c00,type=ro,fill=yes,file=%O,fillval=$00;\nBW_BODY_POST:start=$cec00,size=$1400,type=ro,fill=yes,file=%O,fillval=$00;'
    cfg,n=re.subn(pat,repl,cfg,flags=re.I);assert n==1
    pat=r'UNALLOCATED_CHR_MEM\s*:\s*start=\$e1400,\s*size=\$1ec00,[^;]*;'
    repl='UNALLOCATED_CHR_MEM:start=$e1400,size=$6800,type=ro,fill=yes,file=%O,fillval=$00;\nBW_STREAM_MEM:start=$e7c00,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;\nBW_STREAM_POST:start=$e9c00,size=$16400,type=ro,fill=yes,file=%O,fillval=$00;'
    cfg,n=re.subn(pat,repl,cfg,flags=re.I);assert n==1
    at=cfg.index('SEGMENTS {')
    cfg=cfg[:at].rstrip().removesuffix('}')+'\nBW_IMAGE_MEM:start=$a000,size=$2000,type=ro,bank=3,file="'+str(J/'bowser.bin').replace('\\','/')+'",fill=yes,fillval=$ff;\n}\n'+cfg[at:]
    cfg+='\n' if not cfg.endswith('\n') else ''
    insert='\n'.join('BW_ROM_'+n+':load=BW_'+n+'_MEM,type=ro;' for n,_,_,_ in islands)
    insert+='\nBW_BODY:load=BW_BODY_MEM,type=ro;\nBW_STREAM:load=BW_STREAM_MEM,type=ro;\nBW_IMAGE:load=BW_IMAGE_MEM,type=ro;\n'
    # Append inside the actual SEGMENTS block, before its matching close.
    at=cfg.index('SEGMENTS {');close=cfg.index('}',at)
    cfg=cfg[:close]+insert+cfg[close:]
    write(J/'private.cfg',cfg)
    write(D/'common.inc',COMMON)
    for name,text in [('load',LOAD),('copy',COPY),('check',CHECK),('retire',RETIRE)]:write(D/(name+'.s'),text)
    # This is the actual qualified BT-shaped typed frame transport, copied as
    # source and rebound, never its ROM bytes or physical addresses.
    router=(R/'build/battletoads-current-host-v4/joint/bt/router.s').read_text().replace('Bt','Bw').replace('BT_ROM_ROUTER','BW_ROM_ROUTER')
    router=router.replace('*<=$b100','*<=$b300').replace('Exact BT224B Quick partition','Bowser exact213B A67 lease')
    write(D/'router.s',router)
    # Source-authenticated cold standing data only, four complete records.
    v=R/'build/bowser-source-core-v5';bundle=load(v/'arena.bin')
    def record(n):
        pos=int(bundle['syms'][n]['val'],0)-0x8000;raw=bundle['raw'];return list(raw[pos:pos+1+raw[pos]])
    rr=record('Bw3Pose0');flip=rr[:]
    for i in range(1,len(flip),4):flip[i+1]^=64;flip[i+3]=(16-flip[i+3])&255
    records=[('BwPortrait1Right',record('Bw1OPEN1RIGHT')),('BwPortrait1Left',record('Bw1OPEN1LEFT')),('BwPortrait3Right',flip),('BwPortrait3Left',rr)]
    preview='.segment "BW_ROM_PREVIEW"\n.export '+','.join(n for n,_ in records)+'\n'
    preview+='\n'.join(n+':.byte '+','.join(str(x)for x in r)for n,r in records)+'\n.assert *<=$b600,lderror,"Bowser A83 exact204B lease"\n'
    write(D/'preview.s',preview)
    (D/'body.chr').write_bytes((v/'bowser1.chr').read_bytes()+(v/'bowser3.chr').read_bytes())
    # Transport-only image: every public service explicitly declines. This
    # prevents accidental readiness before real native world/combat joins.
    # The separate frozen688B source kernel is intentionally not substituted
    # with a fake floor/contact callback here.
    image='.segment "BW_IMAGE"\n.export BwCacheServices,BwCacheDecline\nBwCacheServices:\n.repeat 36\n jmp BwCacheDecline\n.endrepeat\nBwCacheDecline:clc\n rts\n'
    image+='\n'+(v/'art.s').read_text().replace('.segment "BW_ART"','.segment "BW_IMAGE"')
    image+='\n.res $1fe0-(*-BwCacheServices),$ff\n.res 16,0\n.res $10,$ff\n.assert *-BwCacheServices=$2000,lderror,"Exact8KB isolated image"\n'
    write(D/'image.s',image)
    write(D/'image.cfg','MEMORY { M:start=$a000,size=$2000,type=ro,bank=3,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { BW_IMAGE:load=M,type=ro; }\n')
    recipes=[]
    ca=str(R/'tools/Windows/cc65/bin/ca65.exe');ld=str(R/'tools/Windows/cc65/bin/ld65.exe')
    def run(name,c):
        pre=validate(c,J,cwd=R)
        z=subprocess.run(c,cwd=R,text=True,capture_output=True)
        write(O/(name+'.json'),json.dumps(dict(command=c,validation=pre,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
        assert z.returncode==0,(name,z.stderr)
        recipes.append(name)
    def assemble(name):
        run(name+'-build',[ca,'-g','-I',str(D),'--create-full-dep',str(D/(name+'.dep')),'-o',str(D/(name+'.o')),str(D/(name+'.s'))])
    assemble('image')
    run('image-link',[ld,'-C',str(D/'image.cfg'),'-o',str(J/'bowser.bin'),'-Ln',str(D/'image.lbl'),'--dbgfile',str(D/'image.dbg'),str(D/'image.o')])
    imagebytes=(J/'bowser.bin').read_bytes();assert len(imagebytes)==8192
    (D/'cookie.bin').write_bytes(bytes([0xa7,27,0,1])+hashlib.sha256(imagebytes).digest()[:12])
    write(D/'stream.s','.segment "BW_BODY"\n.incbin "body.chr"\n.segment "BW_STREAM"\n.incbin "'+str(J/'bowser.bin').replace('\\','/')+'"\n')
    for n in ['load','copy','check','retire','router','preview','stream']:assemble(n)
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
        if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
    for i,x in enumerate(link):
        if x=='--ld-args':
            a=link[i+1].split(',')
            for k in range(1,len(a),2):a[k]=str(J/Path(a[k]).name)
            link[i+1]=','.join(a)
    link += [str(D/(n+'.o'))for n in ['load','copy','check','retire','router','preview','stream','image']]
    run('actual-host-link',link)
    # This leaf has no fixed-entry source edits; the actual mirror producer
    # must still reproduce unchanged fixed125 from exact current127.
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes')
    out=load(J/'candidate.nes')
    for n,z in source['syms'].items():
        assert n in out['syms'] and z['val']==out['syms'][n]['val'],('Moved old symbol',n)
    permitted=set()
    for _,b,s,e in islands:permitted.update(range(16+b*8192+s,16+b*8192+e))
    for s,e in [(824,827),(927,935)]:permitted.update(range(16+128*8192+s*1024,16+128*8192+e*1024))
    changed=[i for i,(a,b)in enumerate(zip(source['raw'],out['raw']))if a!=b]
    assert set(changed)<=permitted
    for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n),n
    occupied=[]
    for g in out['segs'].values():
        if not g['name'].startswith('"BW_ROM_'):continue
        occupied.append(dict(segment=g['name'].strip('"'),CPU_start=int(g['start'],0),bytes=int(g['size'],0),file_offset=int(g['ooffs'],0)))
    report=dict(status='REAL_SOURCE_SPLIT_TRANSPORT_COMPONENT_NO_INGRESS',source=True,candidate=sha(J/'candidate.nes'),
        parent=proof['parent'],ready=62,menu_common_native_entrypoints_unchanged=True,
        occupied=occupied,resident_used=sum(q['bytes']for q in occupied),resident_granted=1281,
        carrier_bytes=8192,body_CHR_bytes=3072,cookie=list((D/'cookie.bin').read_bytes()),
        changed_bytes=len(changed),all_old_symbols_exact=True,FF_Quick_Arthur_payloads_exact=True,
        cache_services='All36 explicitly C-clear decline; no fake host callbacks or native movement/admission claim. Frozen source core remains separate until authentic native contacts join.',
        root_grant=sha(O/'root-grant-and-partition.json'),recipes=recipes,
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),P/'handoff.json',R/'build/bowser-source-core-v5/handoff.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'bowser.bin',D/'cookie.bin',J/'private.cfg',O/'root-grant-and-partition.json']})
    write(O/'source-stage.json',json.dumps(report,indent=2)+'\n');write(J/'source-stage.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='bindings'}))


if __name__=='__main__':main()
