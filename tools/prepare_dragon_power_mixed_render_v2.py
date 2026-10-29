"""Private lossless body+wave packing; frozen Goku inputs are read-only.

Produces a separately linked component and a sparse, NOT PLAYABLE d52 overlay.
No shared source, native emulator, allocations, or installed files are changed.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import dragon_power_art_v1 as A
import dragon_power_component_v1 as B

R=Path(__file__).resolve().parents[1]
OUT=R/'build/dragon-power-mixed-render-v2'
PARENT=R/'build/celeste-small-v1'
OLD=R/'build/dragon-power-component-v1'
PARENT_SHA='d52eeefe78c5f050d276a833c651456b717157856d1783b98c131f9da29f8a60'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def binding(p):p=Path(p);return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def absolute(p):return str(Path(p).resolve()).replace('\\','/')
def include_path(p):return Path(p).resolve().relative_to(R).as_posix()

def parts(pose,face,wave=False):
    px,oam,cycles=A.pixels(pose,face,wave);out=[]
    for y in range(min(k[1]for k in px)//16*16,max(k[1]for k in px)+1,16):
        for x in range(min(k[0]for k in px)//8*8,max(k[0]for k in px)+1,8):
            for pal in [0,1]:
                pattern=A.pair(px,x,y,pal)
                if any(pattern):out.append((pattern,pal,y,x))
    return out,dict(pose=pose,face=face,wave=wave,source_OAM=oam.hex(),source_cycles=cycles,
                    pixel_classes_sha256=hashlib.sha256(repr(sorted(px.items())).encode()).hexdigest())

def generate():
    resume='--resume-preserved-include-negative' in sys.argv
    assert not OUT.exists() or (resume and (OUT/'build-failure.txt').exists() and not (OUT/'build-proof.json').exists()),'Preserve this version; use a new version for any successor'
    assert sha(PARENT.with_suffix('.nes'))==PARENT_SHA
    frozen=[R/'src/dragon_power_render.s',R/'src/dragon_power_art.inc',R/'chr/characters/dragon-power.chr',OLD/'handoff.json']
    before={str(p):sha(p)for p in frozen}
    OUT.mkdir(exist_ok=resume)
    inputs=[parts(p,f)for p in range(32)for f in [0,64]]+[parts(0,f,True)for f in[0,64]]
    common=sorted(set(p[0]for row,_ in inputs[64:]for p in row));assert len(common)==4
    pages=[];records=[];indices=[];keys={};facts=[]
    for i,(row,fact)in enumerate(inputs):
        key=tuple(row)
        if key not in keys:
            need=set(p[0]for p in row)|set(common)
            options=[(len(need-set(page)),j)for j,page in enumerate(pages)if len(need|set(page))<=32]
            if not options:pages.append(list(common));page=len(pages)-1
            else:page=min(options)[1]
            for pat in sorted(need):
                if pat not in pages[page]:pages[page].append(pat)
            data=[]
            for pat,pal,y,x in row:data.extend([pages[page].index(pat)*2,pal,(y+15)&255,x&255])
            keys[key]=len(records);records.append((page,[len(data)]+data))
        n=keys[key];indices.append(n);facts.append(dict(**fact,record=n,page=records[n][0],parts=len(row)))
    assert len(pages)==7 and all(p[:4]==common for p in pages)
    assert all(all(v in [0,2,4,6]for v in records[indices[i]][1][1::4])for i in[64,65])
    chrdata=b''.join(b''.join(p)+bytes(1024-len(p)*32)for p in pages)
    chrdata+=bytes(8192-len(chrdata));(OUT/'mixed.chr').write_bytes(chrdata)
    lines=['; Private lossless source patterns. Four common wave pairs at indices0..3 on EVERY body page.',
           '.pushseg','.segment "DRAGON_POWER_ART"','DpArtStart:']
    for name,seq in [('DpPoseLo',[f'<DpArt{n}'for n in indices]),('DpPoseHi',[f'>DpArt{n}'for n in indices]),
                     ('DpPosePage',[str(records[n][0])for n in indices])]:lines.extend([name+':',' .byte '+','.join(seq)])
    lines+=['DpPaletteRoles:',' .byte $36,$26,$04,$30,$36,$0f']
    for i,(_,data)in enumerate(records):lines.extend([f'DpArt{i}:',' .byte '+','.join(f'${v:02x}'for v in data)])
    lines+=['DpArtEnd:','.assert DpArtEnd-DpArtStart<=$1000,error,"Goku ART budget"',
            '.export DpArtStart,DpPoseLo,DpPoseHi,DpPosePage,DpPaletteRoles','.popseg',
            '.pushseg','.segment "DRAGON_POWER_CHR"',f'.incbin "{include_path(OUT/"mixed.chr")}"','.popseg']
    (OUT/'dragon_power_art_mixed.inc').write_text('\n'.join(lines)+'\n')
    render=(R/'src/dragon_power_render.s').read_text()
    old=' lda DpPosePage,x\n clc\n adc #<DP_FIRST_CHR\n sta SmChrBank\n'
    new=''' ; Every body page contains the same wave patterns at the same indices.
 ; A wave record uses the CURRENT body page, even when shots draw first.
 ; Invalid/hidden body pose selects page0; neither an absent body nor a
 ; direction change can strand the live wave on an unrelated CHR page.
 cpx #64
 bcc BodyPage
 txa
 pha
 lda DpPose
 cmp #32
 bcc WavePose
 lda #0
WavePose:asl
 tax
 lda DpAttribute
 and #$40
 beq WavePage
 inx
WavePage:lda DpPosePage,x
 clc
 adc #<DP_FIRST_CHR
 sta SmChrBank
 pla
 tax
 lda SmChrBank
 rts
BodyPage:
 lda DpPosePage,x
 clc
 adc #<DP_FIRST_CHR
 sta SmChrBank
'''
    assert render.count(old)==1;render=render.replace(old,new)
    (OUT/'dragon_power_render_mixed.s').write_text(render)
    s=B.labels(PARENT.with_suffix('.lbl'));dbg=PARENT.with_suffix('.dbg').read_text()
    for n in ['MTILE_SOLID','METASPRITE_SAMUS_BODY']:
        m=re.search(r'^sym[^\n]*name="'+n+r'"[^\n]*val=0x([0-9A-Fa-f]+)',dbg,re.M);assert m,n;s[n]=int(m[1],16)
    pre='\n'.join(f'{n}=${s[n]:04x}'for n in B.NAMES+['MTILE_SOLID','METASPRITE_SAMUS_BODY'])
    pre+='\n.macpack longbranch\nDP_CHR_PUBLISH_BANK=62\nDP_RENDER_BANK=4\n'
    incs=[R/'src/dragon_power_state.inc',R/'src/dragon_power_native.inc',R/'src/dragon_power_host.s',
          OUT/'dragon_power_render_mixed.s',R/'src/dragon_power_contact.s',OUT/'dragon_power_art_mixed.inc']
    (OUT/'component.s').write_text(pre+''.join(f'.include "{include_path(p)}"\n'for p in incs))
    (OUT/'component.cfg').write_text('MEMORY { K:start=$A800,size=$1800,bank=86,file=%O; A:start=$C900,size=$1000,bank=85,file="'+absolute(OUT/'art.bin')+'"; C:start=$C5000,size=$2000,file="'+absolute(OUT/'chr.bin')+'"; }\nSEGMENTS { DRAGON_POWER_CORE:load=K,type=ro; DRAGON_POWER_ART:load=A,type=ro; DRAGON_POWER_CHR:load=C,type=ro; }\n')
    cc=R/'tools/Windows/cc65/bin'
    commands=[[str(cc/'ca65.exe'),'-g','-I',str(R),'--create-full-dep',str(OUT/'component.d'),str(OUT/'component.s'),'-o',str(OUT/'component.o')],
              [str(cc/'ld65.exe'),'-C',str(OUT/'component.cfg'),'-o',str(OUT/'component.bin'),'-Ln',str(OUT/'component.lbl'),'--dbgfile',str(OUT/'component.dbg'),str(OUT/'component.o')]]
    for command in commands:
        q=subprocess.run(command,capture_output=True,text=True)
        if q.returncode:
            failure=OUT/'build-failure.txt'
            if failure.exists():failure=OUT/'build-followup-failure.txt'
            assert not failure.exists()
            failure.write_text(q.stdout+q.stderr);raise AssertionError(q.stderr)
    code=(OUT/'component.bin').read_bytes();assert len(code)<=6144 and len((OUT/'art.bin').read_bytes())<=4096
    raw=PARENT.with_suffix('.nes').read_bytes();candidate=bytearray(raw);spans=[];allowed=set()
    for name,at,p,fill in [('core',16+86*8192+0x800,OUT/'component.bin',255),('art',16+85*8192+0x900,OUT/'art.bin',255),
                          ('CHR',1048592+788*1024,OUT/'chr.bin',0)]:
        data=p.read_bytes();assert raw[at:at+len(data)]==bytes([fill])*len(data),(name,'not free')
        candidate[at:at+len(data)]=data;allowed.update(range(at,at+len(data)));spans.append(dict(name=name,offset=at,bytes=len(data),sha256=sha(p)))
    assert {i for i,(a,b)in enumerate(zip(raw,candidate))if a!=b}<=allowed
    (OUT/'candidate.nes').write_bytes(candidate)
    assert before=={str(p):sha(p)for p in frozen}
    inputs_bound=frozen+incs+[PARENT.with_suffix(e)for e in['.nes','.dbg','.lbl']]+[Path(__file__),R/'tools/dragon_power_art_v1.py',R/'tools/dragon_power_reference_v1.py',R/'tools/dragon_power_map_v1.py',R/'tools/dragon_power_component_v1.py',A.O.D.ROM,cc/'ca65.exe',cc/'ld65.exe']
    proof=dict(passed=True,source_only=True,native_run=False,NOT_PLAYABLE=True,
               bindings={str(p.resolve()):sha(p)for p in inputs_bound},commands=commands,core_bytes=len(code),core_end_exclusive=0xa800+len(code),
               art_bytes=(OUT/'art.bin').stat().st_size,pages=len(pages),page_pair_counts=[len(p)for p in pages],
               common_wave_pairs=4,records=facts,source_palette_roles=[54,38,4,48,54,15],spans=spans,
               candidate=binding(OUT/'candidate.nes'),separate_genuine_component_DBG_and_parent_DBG=True,
               all_outside_allocated_component_spans_exact=True,frozen_inputs_unchanged=True,
               limits='Source pattern packing and assembled component only; no shared hook/menu/audio/enemy/block integration or native qualification.')
    (OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in['core_bytes','art_bytes','pages','page_pair_counts','candidate']},indent=2))

if __name__=='__main__':generate()
