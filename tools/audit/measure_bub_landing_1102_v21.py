"""Measure a private source-funded original landing adapter; no ROM output."""
import json,re,subprocess
from pathlib import Path
import check_bubble_native_event_1102_v9 as E

N,Q,P,R,address=E.N,E.Q,E.P,E.R,E.address
O=R/'build/bub-menu-candidate-1102-v2';B=E.O
CURRENT=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'

def assemble(stem,source,cfg):
    path=O/stem;path.with_suffix('.s').write_text(source);path.with_suffix('.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for command in[[cc/'ca65.exe',path.with_suffix('.s'),'-o',path.with_suffix('.o')],
                   [cc/'ld65.exe','-C',path.with_suffix('.cfg'),path.with_suffix('.o'),'-o',path.with_suffix('.bin'),'-Ln',path.with_suffix('.lbl')]]:
        z=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    return P.P.labels(path.with_suffix('.lbl'))

def bundle():
    _,b,q,route=E.bundle();b['raw']=CURRENT.read_bytes();assert P.sha(b['raw'])==PIN
    layout=json.loads((O/'landing-v21-layout.json').read_text());image=(O/'landing-v21-image.bin').read_bytes();art=(O/'landing-v21-helper.chr').read_bytes()
    raw=bytearray(b['raw'])
    for i,page in enumerate([301,305,337,362,363,440,819,666]):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[1048592+441*1024:1048592+442*1024]=art
    at=layout['cookie_offset'];assert raw[at:at+16].hex()==q['BB_cookie'];raw[at:at+16]=bytes.fromhex(layout['cookie'])
    new=dict(b);new['raw']=bytes(raw);return b,new,layout,route

def main():
    _,b,q,route=E.bundle();b['raw']=CURRENT.read_bytes();assert P.sha(b['raw'])==PIN
    old=(B/'native-event-v9-image.bin').read_bytes();helper=(B/'native-cold-fix-helper.chr').read_bytes();core=P.P.labels(B/'component.lbl')
    source=(B/'native-stomp-leaves.s').read_text();cfg=(B/'native-stomp-leaves.cfg').read_text()
    cfg=cfg.replace(B.as_posix()+'/native-stomp-',O.as_posix()+'/landing-v21-')
    assert str(B).replace('\\','/')not in cfg
    def once(oldtext,newtext):
        nonlocal source
        assert source.count(oldtext)==1,(oldtext,source.count(oldtext));source=source.replace(oldtext,newtext)
    # Reproduce the current v9 event and removed inferred-bounce ingress as
    # source, rather than carrying a stale v7 linked output into the successor.
    once('BbNativeIn:\n jsr BbNativeActor\n jsr BbNativeStomp\n','BbNativeIn:\n jsr BbNativeActor\n .byte $ea,$ea,$ea\n')
    oldevent='''BbNativeStomp:
 lda Player_Y_Speed
 bpl :+
 lda $c003,x
 cmp #2
 bne :+
 lda #0
 sta $c003,x
 jmp $a4cc
:
 rts
'''
    event=f'''BbNativeStomp:
 php
 pha
 txa
 pha
 tya
 pha
 jsr BbNativeActor
 lda #0
 sta $c003,x
 jsr ${core['BbOriginal_D36B']:04x}
 jmp $d3b2
'''
    once(oldevent,event)
    labels=assemble('landing-v21-leaves',source,cfg)
    placements=[('leaves',0xb540),('box-hole',0xa0b0),('sound-hole',0xb53a),('admission',0xa074)]
    for name,pc in placements:
        part=(O/('landing-v21-'+name+'.bin')).read_bytes();assert old[pc-0xa000:pc-0xa000+len(part)]==part,('current source reproduction',name)
    before_source=source
    prefix=' jsr BbNativeProxiesIn\n jsr BbNativeActor\n jsr BbPlayerStep\n'
    landing=f''' jsr BbNativeProxiesIn
 jsr BbNativeActor
BbNativeLanding:
 ; State0 is the prior actual native foot/platform landing result. Source
 ; NativeOut otherwise publishes falling1 while selector2/3 is active.
 lda Player_State
 ora Player_Y_Speed
 bne BbNativeLandingDone
 lda $c003,x
 and #$fe
 cmp #2
 bne BbNativeLandingDone
 jsr ${core['BbOriginal_D41C']:04x}
BbNativeLandingDone:
 jsr BbPlayerStep
'''
    once(prefix,landing)
    once(' lda #0\n sta $c3ef\n','')
    once(' jsr BbNativeCeiling\n bcc :+\n inc $c3ef\n:\n',' jsr BbNativeCeiling\n')
    source+='\n.export BbNativeLanding,BbNativeLandingDone\n'
    labels=assemble('landing-v21-leaves',source,cfg)
    assert labels['BbNativePaletteEnd']==0xbfe0,(hex(labels['BbNativePaletteEnd']))
    assert labels['BbNativeUpdate']==q['labels']['BbNativeUpdate']
    image=bytearray(old)
    for name,pc in placements:
        part=(O/('landing-v21-'+name+'.bin')).read_bytes();image[pc-0xa000:pc-0xa000+len(part)]=part
    hs=(B/'native-stomp-helpers.s').read_text()
    for name in['BbNativeFresh','BbNativeDraw','BbNativeActor','BbNativeHurtChoose','BbNativeAreaBackdrop','BbNativeStatusBob']:
        hs,n=re.subn(name+r'=\$[0-9a-f]+',f'{name}=${labels[name]:04x}',hs);assert n==1,name
    hl=assemble('landing-v21-helpers',hs,'MEMORY{H:start=$d320,size=$e0,file=%O;}SEGMENTS{BB_HELPERS:load=H,type=ro;}')
    art=helper[:800]+(O/'landing-v21-helpers.bin').read_bytes();assert len(art)==1024
    assert hl['BbHelperRegsRestore']==0xd3b2
    assert image[0x100:0x153a]==old[0x100:0x153a]
    # No admitted vector or copied-source import may retain a moved target.
    vectors=q['vectors']
    for row,item in vectors.items():
        target=labels.get(item['name'],q['labels'][item['name']]);at=int(row)*3
        assert old[at:at+3]==bytes([76,item['target']&255,item['target']>>8]),('actual service vector preimage',row,item)
        image[at:at+3]=bytes([76,target&255,target>>8])
    cookie=bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13]
    offset=q['common_cookie_ROM_file_offset'];assert b['raw'][offset:offset+16].hex()==q['BB_cookie']
    out=dict(passed=True,proposal_only=True,ROM_written=False,native=False,base_ROM_SHA256=PIN,labels={**q['labels'],**labels,**hl},
        code_end=labels['BbNativePaletteEnd'],code_spare=0,cookie=cookie.hex(),cookie_offset=offset,
        exact_current_native_source_reproduced_before_change=True,original_A100_B53A_exact=True,source_added_bytes=18,source_reclaimed_bytes=10,net_bytes=8,
        reclaim='C3EF ceiling telemetry only: its2writes have no reader in current native source, original5434B or observers; no original state/coordinate/timer is removed.',
        guard='NativeInput already authenticates actor/activeEngine8/normalnewsourceepoch/unpaused; immediately before original PlayerStep, prior actual nativePlayerState0 plus DY0 and healthy source selector2or3 calls exact originalD41C landing reset. No impulse/height/clock change.',
        moved_aliases={n:[q['labels'][n],v]for n,v in labels.items()if n in q['labels']and v!=q['labels'][n]and not n.startswith(('BbProxyRelax','BbStompRelax'))},
        inputs={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),CURRENT,B/'native-stomp-leaves.s',B/'native-stomp-leaves.cfg',B/'native-stomp-helpers.s',B/'native-event-v9-image.bin',B/'native-cold-fix-helper.chr',O/'stair-route-v20-CPU.json']})
    (O/'landing-v21-image.bin').write_bytes(image);(O/'landing-v21-helper.chr').write_bytes(art)
    (O/'landing-v21-layout.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k not in['labels','inputs']}))

if __name__=='__main__':main()
