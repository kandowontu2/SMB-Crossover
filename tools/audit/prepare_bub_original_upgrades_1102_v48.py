"""Privately relink original branch-equivalent body and source item upgrades."""
import hashlib,json,re,subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
import check_bubble_native_event_1102_v9 as E
from check_tmnt_render_oa import address
O=R/'build/bub-upgrades-root-1102-v48'
S=R/'build/bub-upgrades-root-1102-v47'
P=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
labels=lambda p:{name:int(at,16)for at,name in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',Path(p).read_text(),re.M)}

def main():
    O.mkdir(exist_ok=True);donor=S/'receipt.json';proof=json.loads(donor.read_text());assert proof['passed']and proof['reclaimed_bytes']==729
    for name,h in proof['bindings'].items():assert sha(R/name)==h,name
    base=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=base.read_bytes();assert sha(base)==PIN
    pages=[301,305,337,362,363,440,819,666];old=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
    native=(P/'landing-v21-leaves.s').read_text();cfg=(P/'landing-v21-leaves.cfg').read_text();newlabels=labels(S/'component.lbl');oldlabels=labels(R/'build/bubble-bobble-source-1101-v1/component.lbl')
    changed=[]
    for name in['BbInput','BbOriginal_C43E','BbOriginal_DAB2','BbHurtBub','BbHurtBob','BbSourceInit','BbSourceSprites','BbPlayerStep','BbBubbleStep','BbTrappedEnemyStep','BbSourceClock']:
        pattern=name+r'=\$([0-9a-f]+)';m=re.search(pattern,native);assert m and int(m[1],16)==oldlabels[name],name
        native,n=re.subn(pattern,f'{name}=${newlabels[name]:04x}',native);assert n==1
        changed.append(dict(name=name,old=oldlabels[name],new=newlabels[name]))
    for name in['BbOriginal_D36B','BbOriginal_D41C']:
        original=f'jsr ${oldlabels[name]:04x}';assert native.count(original)==1
        native=native.replace(original,f'jsr ${newlabels[name]:04x}');changed.append(dict(name=name,old=oldlabels[name],new=newlabels[name]))
    cfg=cfg.replace(P.as_posix()+'/landing-v21-',O.as_posix()+'/native-')
    cc=R/'tools/Windows/cc65/bin'
    def assemble(stem,text,config):
        (O/(stem+'.s')).write_text(text);(O/(stem+'.cfg')).write_text(config)
        for command in[[cc/'ca65.exe',O/(stem+'.s'),'-o',O/(stem+'.o')],[cc/'ld65.exe','-C',O/(stem+'.cfg'),O/(stem+'.o'),'-o',O/(stem+'.bin'),'-Ln',O/(stem+'.lbl')]]:
            p=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert p.returncode==0,p.stderr
        return(O/(stem+'.bin')).read_bytes(),labels(O/(stem+'.lbl'))
    body,nl=assemble('native',native,cfg);prior=json.loads((P/'landing-v21-layout.json').read_text())['labels']
    assert all(prior.get(name,pc)==pc for name,pc in nl.items()),'No native adapter entry may move'
    image=bytearray(old);end=newlabels['BbCodeEnd'];code=(S/'component.bin').read_bytes()
    image[0x100:0x153a]=code[0x100:end-0xa000]+bytes([255])*(0xb53a-end)
    for stem,pc in[('native',0xb540),('native-box-hole',0xa0b0),('native-sound-hole',0xb53a),('native-admission',0xa074)]:
        part=(O/(stem+'.bin')).read_bytes();image[pc-0xa000:pc-0xa000+len(part)]=part
    _,bundle,_,_=E.bundle();bundle['raw']=raw
    power,estate=address(bundle,'PowerUpType'),address(bundle,'Enemy_State')
    pickup=f'''.setcpu "6502"
.export BbNativePickup,BbPickupEnd
PowerUpType=${power:04x}
Enemy_State=${estate:04x}
BbNativeActor=${nl['BbNativeActor']:04x}
.segment "CODE"
BbNativePickup:
 php
 pha
 txa
 pha
 tya
 pha
 lda PowerUpType,x
 cmp #2
 bcs PickupNative
 lda Enemy_State,x
 bpl PickupImmature
 lda PowerUpType,x
 pha
 jsr BbNativeActor
 pla
 tay
 lda PickupMasks,y
 ora $c002,x
 sta $c002,x
PickupNative:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
PickupImmature:
 jmp $d3b2 ; Existing exact AXYP restore then SEC: leave item untouched.
PickupMasks:
 .byte 1,6 ; Actual original item4 and item2 masks via bank6 $9C9D.
BbPickupEnd:
'''
    worker,wl=assemble('pickup',pickup,f'MEMORY{{M:start=${end:04x},size=${0xb53a-end:x},file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
    assert wl['BbPickupEnd']<=0xb53a and image[end-0xa000:end-0xa000+len(worker)]==bytes([255])*len(worker)
    image[end-0xa000:end-0xa000+len(worker)]=worker;image[14*3:14*3+3]=bytes([0x4c,end&255,end>>8])
    art=raw[1048592+441*1024:1048592+442*1024];cookie=bytes([0xa7,39,1])+hashlib.sha256(image+art).digest()[:13]
    existing=json.loads((P/'combined-current-landing.json').read_text());c=next(p for p in existing['patches']if len(bytes.fromhex(p['new']))==16)
    assert raw[c['offset']:c['offset']+16]==bytes.fromhex(c['new'])
    proposed=bytearray(raw)
    for i,page in enumerate(pages):proposed[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    proposed[c['offset']:c['offset']+16]=cookie
    (O/'private-image.bin').write_bytes(image)
    all_labels={**newlabels,**prior,**nl,**wl};all_labels.update(newlabels)
    (O/'labels.json').write_text(json.dumps(all_labels,indent=2)+'\n')
    q=dict(passed=True,proposal_only=True,ROM_written=False,installed=False,parent_ROM_SHA256=PIN,expected_memory_only_ROM_SHA256=hashlib.sha256(proposed).hexdigest(),source_reclaimed_bytes=729,pickup_bytes=len(worker),remaining_source_gap=0xb53a-wl['BbPickupEnd'],all_native_entries_exact=True,relocated_source_ingresses=changed,cookie_offset=c['offset'],old_cookie=bytes.fromhex(c['new']).hex(),new_cookie=cookie.hex(),pages=pages,helper441_exact=True,labels=all_labels,scope='Private image only: original conditional branch relaxation with all native source ingresses relinked and native entry addresses retained. Mushroom maps to original item4 bit01; flower to original item2 bits06. Mature regular pickups OR source actor flags then return C0 to genuine native bookkeeping/SFX/animation; immature regular items restore AXYP and claim without consuming; star/1up forward unchanged. This is an explicit SMB-to-original-item adaptation. Actual donor pickup comparison, full native ingress/upgrade effects/lifecycle/ISR/graphics/fullstage are NOT yet qualified.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),donor,S/'component.s',S/'component.bin',S/'component.lbl',P/'landing-v21-leaves.s',P/'landing-v21-leaves.cfg',O/'native.s',O/'native.bin',O/'pickup.s',O/'pickup.bin',O/'private-image.bin',O/'labels.json']})
    (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['labels','bindings','relocated_source_ingresses']}))

if __name__=='__main__':main()
