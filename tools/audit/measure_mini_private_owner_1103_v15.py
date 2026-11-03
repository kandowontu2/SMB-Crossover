"""Source-only fifth-owner/carrier measurement over granted shared83.

No ROM, shared source or allocation is changed. The Mini cookie is a clearly
marked fit placeholder until the complete native component is bound.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import build_storage_guard_v1 as G
O=R/'build/mini-mario-owner-1103-v15'
P=R/'build/bub-menu-candidate-1102-v2'
BASE=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
CODE=list(range(962,967));META=967;ART=968
sha=lambda v:hashlib.sha256(v).hexdigest()


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def assemble(stem,text,cfg):
    p=O/stem;p.with_suffix('.s').write_text(text);p.with_suffix('.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],
                [cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        run=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
        assert run.returncode==0,run.stderr
    p.with_suffix('.o').unlink()
    labels={name:int(value,16)for value,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return p.with_suffix('.bin').read_bytes(),labels


def main():
    G.preflight(private_root=O,reserved_bytes=200000,reserved_files=25,fresh=True);O.mkdir(exist_ok=True)
    raw=BASE.read_bytes();assert sha(raw)==PIN
    old=json.loads((P/'combined-auth-v83-measurement.json').read_text())
    # The only map-latch write removed is after the physical pair has latched.
    # Each next row writes its own upper before5123, and the resident cold
    # caller publishes the complete native CHR state before headers go live.
    worker=(R/'build/bubble-bobble-source-1101-v1/common-split.s').read_text()
    inc=(R/'tools/reference/bubble_bobble_common_cold_1102_v4.inc').read_text()
    inc=once(inc,' ldy #0\n sty $5130\n bit $2002',' ldy #0\n bit $2002')
    worker=once(worker,'.include "bubble_bobble_common_cold_1102_v4.inc"',inc)
    worker+='\n.segment "BB_COLD_MAP"\n.export MiniDescriptor,MiniDescriptorEnd\nMiniDescriptor:\n .byte 1,0,9,$d0\n .word 967\nMiniDescriptorEnd:\n'
    cfg='MEMORY{P:start=$af40,size=$c0,file=%O;M:start=$b9d6,size=$2a,file="'+(O/'common-v15-map.bin').as_posix()+'";}SEGMENTS{BB_COLD_PROPOSAL:load=P,type=ro;BB_COLD_MAP:load=M,type=ro;}'
    common,CL=assemble('common-v15',worker,cfg)
    assert common==(R/'build/bubble-bobble-source-1101-v1/common-split.bin').read_bytes()
    assert CL['MiniDescriptor']==0xb9f9 and CL['MiniDescriptorEnd']<=0xba00
    source=(P/'combined-auth-v83.s').read_text()
    source='MiniDescriptor=$%04x\n'%CL['MiniDescriptor']+source
    source=once(source,' lda #0\n pha\n beq CoSave\nCoRetire:',' lda #0\n beq CoSave\nCoRetire:')
    source=once(source,' lda #1\n pha\nCoSave:',' lda #1\nCoSave:\n pha')
    source=source.replace(' cmp #4\n bcs CoSelectNo',' cmp #5\n bcs CoSelectNo')
    assert source.count(' cmp #5\n bcs CoSelectNo')==2
    source=once(source,'CoRetireOwners:\n ldx #3','CoRetireOwners:\n ldx #4')
    source=once(source,' sta $5116\n sta SafecallA_SMC+1\n lda #3',' sta $5116\n lda #3')
    source=once(source,'CoPublishChr:\n sta SafecallA_SMC+1','CoPublishChr:')
    source=once(source,'.macro CoFar Target,Bank\n sta SafecallA_SMC+1','.macro CoFar Target,Bank')
    source=once(source,' eor #14 ;38xor40, retains successful common carry\n bne PrWorkerDone',' eor #14 ;38xor40; 37/39 produce odd13/15 and keep successfulC1 afterLSR\n lsr\n bne PrWorkerDone')
    source=once(source,' ldx #4\n jsr CoCheckIndex',' ldx #5\n jsr CoCheckIndex')
    source=once(source,' sta $2005\n rts\nCoPublishChr:',' sta $2005\nPrCopyLiveDone:\n rts\nCoPublishChr:')
    source=once(source,' lda #3\n jsr $015a\nPrCopyLiveDone:\n rts',' lda #3\n jmp $015a')
    for oldtext,newtext in [
        ('<DkCookie,<$aa78','<DkCookie,<MiniCookie,<$aa78'),
        ('>DkCookie,>$aa78','>DkCookie,>MiniCookie,>$aa78'),
        ('<CoBBDescriptor,<DkDescriptor','<CoBBDescriptor,<DkDescriptor,<MiniDescriptor'),
        ('>CoBBDescriptor,>DkDescriptor','>CoBBDescriptor,>DkDescriptor,>MiniDescriptor'),
        ('<BbNativeRetire,<$d60c','<BbNativeRetire,<$d60c,0'),
        ('>BbNativeRetire,>$d60c','>BbNativeRetire,>$d60c,0')]:source=once(source,oldtext,newtext)
    cookie=bytes([0xa7,41,1])+hashlib.sha256(b'Mini-source-fit-placeholder-not-native').digest()[:13]
    source=once(source,'CoDataEnd:\n','MiniCookie:\n .byte '+','.join('$%02x'%v for v in cookie)+'\nCoDataEnd:\n')
    source+='\n.export MiniCookie,CoSelect,CoRestorePpu\n'
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'owner-v15-extra.bin').as_posix()+'";S:start=$a800,size=$49,file="'+(O/'owner-v15-Sh.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;SH_SHARED_AUTH:load=S,type=ro;}'
    manager,L=assemble('owner-v15',source,cfg)
    assert len(manager)==531 and L['CoCold']==0xae00 and L['MiniCookie']==0xb003
    extra=(O/'owner-v15-extra.bin').read_bytes();assert len(extra)==98
    selector=(P/'combined-auth-v83-selector.s').read_text()
    selector=once(selector,'CoCheckCode=$aee3','CoCheckCode=$%04x'%L['CoCheckCode'])
    selector=once(selector,' cmp #4\n bcc PrOdd',' cmp #5\n bcc PrOdd')
    sel,SL=assemble('selector-v15',selector,'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}')
    assert len(sel)==176
    # Exact native jump operands that must follow the moved retirement entry.
    aliases=[]
    for pc in [0xb026,0xb100]:
        at=16+65*8192+pc-0xa000;before=raw[at:at+3]
        assert before[0]in[32,76]and before[1:]==bytes.fromhex('0bae')
        aliases.append(dict(physical_PRG=65,CPU=pc,file_offset=at,old_hex=before.hex(),new_hex=(before[:1]+L['CoRetire'].to_bytes(2,'little')).hex()))
    q=dict(passed=True,source_fit_only=True,CPU_qualified=False,ROM_written=False,resource_granted=False,
        parent_SHA256=PIN,manager_bytes=len(manager),extra_bytes=len(extra),selector_bytes=len(sel),Sh_bytes=(O/'owner-v15-Sh.bin').stat().st_size,
        common_main_exact=True,common_map_and_descriptor_bytes=(O/'common-v15-map.bin').stat().st_size,
        Mini_cookie_placeholder=cookie.hex(),Mini_cookie_CPU=L['MiniCookie'],labels=L,selector_labels=SL,common_labels=CL,
        retired_entry_rebind=aliases,CoRetire_entry_moved=[old['labels']['CoRetire'],L['CoRetire']],
        physical_request=dict(code=CODE,immutable=META,art=ART,pages=7,bytes=7168,
            preimages=[dict(page=p,file_offset=1048592+p*1024,SHA256=sha(raw[1048592+p*1024:1048592+(p+1)*1024]))for p in CODE+[META,ART]]),
        RAM_request=dict(code=['RAM3:A000','RAM3:B400'],state=['RAM2:C000','RAM2:C900'],immutable=['RAM2:D000','RAM2:D400'],cold_boot=['RAM2:D25E','RAM2:D2D0'],both_headers=['RAM2:DFE0..DFF0','RAM3:BFE0..BFF0']),
        Mini_descriptor=[1,0,9,208,199,3],private_cold_requirement='D25E copier5rows962..966, preservingR5/R6, C1 only after copy/readback; sourceinit deferred to first genuine native8 epoch.',
        source_funding=['SharedmodePHA1B; publicRetire movesAE0B→AE0A with two exact nativeJMP imports rebased.',
            'Dead incomingA stores: common worker beginsLDA2; private cold beginsPHP/PLA; X5publisher beginsLDAwide; retire leaves preserve incomingA only until outerpublicrestore.',
            'PrCopyLive reject reuses existing PPUrestoreRTS; successful path tails through unchangedFarCallCommon.',
            'Existing mainfooter8+7saved bytes+1RTS tailbyte give exact16B Mini cookie; extra97-6+6tablebytes+1LSR=98.',
            'Common map post-pair STY5130 removed3B; current12hardwarelatches unchanged and every nextrow setsupperfirst. Residentrestore publishesallCHR beforevalidheaders. Needs actualcold/FF proof.'],
        authentication='All13 checks remain complete two16Bheaders. Sh guarded36 nowindex5; new41index4. Retirement iterates4..0 before genuine ShRetire; Mini native associations absent, callback0 only after fullheaders.',
        scene_constraint='Current B013 gate still37..39. Root must separately source-fund exact41 scene ingress without admitting40 implicitly.',
        remaining=['Current finite carrier publication/source review and grant.','Full actual fourowner cold/retire/Fresh/foreignAXYP/SMC/IRQ/FF including changed deadA and transient5130.','Complete Mini payload/cookie and five-row copier, sourceInit/Step/native first8 readiness.','Root exact scene/frontend/private composition grant before ROM/native.'],
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),BASE,P/'combined-auth-v83.s',P/'combined-auth-v83-selector.s',P/'combined-auth-v83-measurement.json',R/'tools/reference/bubble_bobble_common_cold_1102_v4.inc',R/'src/mmc5_expanded.s']})
    (O/'owner-fit-v15.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','manager_bytes','extra_bytes','selector_bytes','common_map_and_descriptor_bytes','CoRetire_entry_moved','Mini_cookie_CPU','physical_request','remaining']}))


if __name__=='__main__':main()
