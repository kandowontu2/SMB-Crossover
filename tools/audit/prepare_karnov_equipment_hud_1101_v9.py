"""Assemble a source-backed one-page Karnov equipment HUD proposal."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,graph,emit
from private_build_outputs_v1 import validate
O=R/'build/karnov-equipment-hud-1101-v9';HOST=R/'tools/reference/karnov_equipment_hud_1101_v9.inc'
BASE=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='0ffb1d79c4fbc52bb337a4726f8e61f984f30e4795fd2555b204322140c0a717'
FONT=R/'chr/mmc5/bg_ground.chr'
FONT_SHA='275ff7fb837629ec43321dcc4167453e0a176fb62a86ae55733b826a601e67cb'
F=R/'docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7/source.zip'
CURRENT=R/'docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/source.zip'
CURRENT_SHA='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
NATIVE=R/'build/karnov-native-reference-1101-v1/capture/reference.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SPANS=[('icons',0xc534,0xc5a0,None,()),('owner',0xc28c,0xc29d,None,(0xc8b2,)),
 ('cursor',0xa02d,0xa070,11,()),('stockBoots',0xe25e,0xe2cf,None,()),
 ('stockBoomerang',0xe2cf,0xe340,None,()),('stockWings',0xe340,0xe3a5,None,())]


def split_source(text):
    """Pure owning-source proposal. No outputs, grants or owning mutations."""
    assert text.count('KrHudDataStart:\n')==text.count('KrHudDataEnd:\n')==1
    text=text.replace('KrHudDataStart:\n','.pushseg\n.segment "KR_COMBAT_ROM"\nKrHudDataStart:\n')
    text=text.replace('KrHudDataEnd:\n','KrHudDataEnd:\n.popseg\n')
    return '.pushseg\n.segment "KR_OPTIONS_ROM"\n'+text+'.popseg\n'


def main():
    O.mkdir(exist_ok=True);raw=ROM.read_bytes();assert sha(ROM)==EXPECTED
    base=BASE.read_bytes();observed=hashlib.sha256(base).hexdigest()
    prg=(base[4]+((base[9]&15)<<8))*16384;font=FONT.read_bytes()[:1024];assert len(font)==1024
    assert hashlib.sha256(font).hexdigest()==FONT_SHA and base[16+prg:16+prg+1024]==font
    (O/'base-font.chr').write_bytes(font)
    native=json.loads(NATIVE.read_text());assert native['passed']and native['ROM_sha256']==EXPECTED
    ram=native['initial_fixture'];assert ram[9]&16==0 and ram[0x14]==38
    # Original NMI selects raw MMC3 register numbers5..0 with no CHR inversion,
    # then publishes shadow13+X. BG0000 tile82 is window0800 physical page38.
    mapper=raw[16+15*8192+0x99:16+15*8192+0xa6]
    assert mapper==bytes.fromhex('a2058e0080b5138d0180ca10f5')
    chr=raw[16+131072:];assert len(chr)==65536
    atlas=bytearray(font);patterns=[];rows=[]
    for item,tile,target in[(0,0x82,0x30),(3,0x88,0x34),(7,0x8c,0x38)]:
        original_tiles=[tile,tile+1,tile+16,tile+17]
        for source,dest in zip(original_tiles,range(target,target+4)):
            at=38*1024+(source&63)*16;p=chr[at:at+16];assert len(p)==16
            # Source icons use2(gray)/3(light) against transparent0. Existing
            # native HUD ink is1(white), so swap the planes:2->1,1->2,3->3.
            # This is an explicit palette-index adaptation, preserving every
            # pixel/alpha and color distinction without changing PPU palette.
            atlas[dest*16:dest*16+16]=p[8:]+p[:8];patterns.append(p)
        rows.append(dict(option=item,source_tiles=original_tiles,native_tiles=list(range(target,target+4))))
    # A plain '+' control glyph, not character art. Copyright2F, coin2E,
    # all letters/digits, dash/x/blank stay unchanged.
    atlas[0x3c*16:0x3d*16]=bytes([0,0x18,0x18,0x7e,0x18,0x18,0,0]+[0]*8)
    changed={i//16 for i,(a,b)in enumerate(zip(font,atlas))if a!=b};assert changed<=set(range(0x30,0x3d))
    preserved=set(range(0x24))|{0x24,0x28,0x29,0x2e}
    assert not changed&preserved
    (O/'equipment-font.chr').write_bytes(atlas);(O/'original-icon-patterns.chr').write_bytes(b''.join(patterns))
    chunks=[];defs=set();original='.setcpu "6502"\n';mem=[];seg=[];sources=[];metadata=[]
    for name,lo,hi,bank,data in SPANS:
        m,code,tables,external,ramfields,reads=graph(raw,lo,hi,{},(1,bank)if bank else None,data)
        assert not tables
        text=emit(m,code,tables,False,lo,hi);p=O/('original-'+name+'.inc');p.write_text(text);sources.append(p)
        chunks.append(bytes(m.memory[lo:hi]));defs.update(external)
        original+=f'.segment "N_{name}"\n.include "original-{name}.inc"\n'
        mem.append(f'M_{name}:start=${lo:04x},size=${hi-lo:04x},file=%O;');seg.append(f'N_{name}:load=M_{name},type=ro;')
        metadata.append(dict(name=name,start=lo,end=hi,instructions=len(code),external={hex(k):list(map(hex,v))for k,v in external.items()}))
    original=original.replace('.setcpu "6502"\n','.setcpu "6502"\n'+''.join(f'KrExternal_{a:04X}=${a:04x}\n'for a in sorted(defs)))
    (O/'original.s').write_text(original);(O/'original.cfg').write_text('MEMORY{'+''.join(mem)+'}SEGMENTS{'+''.join(seg)+'}\n')
    constants='''KrState=$c000
KrHudCache=$c87a
KrHudPhysicalLow=$ff
KrHudPhysicalHigh=3
SelectedCharacter=$6000
OperMode=$6001
OperMode_Task=$6002
GameEngineSubroutine=$6003
DisableScreenFlag=$6004
NmiDisable=$6005
VRAM_Buffer_AddrCtrl=$6006
VRAM_Buffer1_Offset=$6007
InvHudActive=$6008
InvHudPhysical=$6009
X5HudChrUpper=$600a
X5WideChrActive=$600b
ReloadCHRBank=$600c
VRAM_Buffer1=$0301
'''
    (O/'component.s').write_text('.setcpu "6502"\n.macpack longbranch\n.include "inc/charmap.inc"\n'+constants+'.segment "CODE"\n.include "karnov_equipment_hud_1101_v9.inc"\n')
    (O/'component.cfg').write_text('MEMORY{P:start=$9000,size=$1000,file=%O;}SEGMENTS{CODE:load=P,type=ro;}\n')
    (O/'split-hud-proposal.inc').write_text(split_source(HOST.read_text()))
    (O/'split.s').write_text('.setcpu "6502"\n.macpack longbranch\n.include "inc/charmap.inc"\n'+constants+'.include "split-hud-proposal.inc"\n')
    (O/'split.cfg').write_text('MEMORY{P:start=$9000,size=$1000,file=%O;D:start=$cd40,size=$c0,file=%O;}SEGMENTS{KR_OPTIONS_ROM:load=P,type=ro;KR_COMBAT_ROM:load=D,type=ro;}\n')
    commands=[];cc=R/'tools/Windows/cc65/bin'
    for name in['original','component','split']:
        for cmd in[[cc/'ca65.exe','-g','-I',R,'-I',O,'-I',HOST.parent,O/(name+'.s'),'-o',O/(name+'.o')],
                   [cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin'),'--dbgfile',O/(name+'.dbg'),'-Ln',O/(name+'.lbl')]]:
            cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True)
            commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    assert(O/'original.bin').read_bytes()==b''.join(chunks)
    all_labels={}
    for mode in['component','split']:
        labels={}
        for line in(O/(mode+'.dbg')).read_text().splitlines():
            if line.startswith('sym\t'):
                z=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
                if 'val'in z:labels[z['name'].strip('"')]=int(z['val'],0)
        all_labels[mode]=labels
    labels=all_labels['component'];sl=all_labels['split']
    assert labels['KrHudEnd']-0x9000==440 and sl['KrHudEnd']-0x9000==361 and sl['KrHudDataEnd']-sl['KrHudDataStart']==79
    assert sl['KrHudDataStart']==0xcd40
    assert (O/'component.bin').read_bytes()[-79:]==(O/'split.bin').read_bytes()[-79:]
    # Capture only the two exact immutable consumer leaves, not a ROM/DBG copy.
    assert observed==CURRENT_SHA
    irq=base[16+126*8192:16+126*8192+68]
    assert irq.startswith(bytes.fromhex('488a482c0452ad380129010a0a8d0620a9008d2851'))and irq.endswith(bytes.fromhex('68aa6840'))
    tail=bytes.fromhex('8d2b5148a9008d30516860');at=base.find(tail)
    assert at>=16 and base.find(tail,at+1)==-1
    assert(at-16)//8192==62
    (O/'native-IRQ31.bin').write_bytes(irq);(O/'native-publisher-tail.bin').write_bytes(tail)
    with zipfile.ZipFile(F)as z:
        screen=z.read('host/screen_render.s').decode();kernel=z.read('host/kr-kernel.s').decode()
        assert re.search(r'KrCacheServices:\s*'+r'\s*jmp \w+'*29+r'\s*jmp KrReject',kernel)
        lo=screen.index('TopStatusBarLine:');hi=screen.index('WorldLivesDisplay:',lo)
        top=screen[lo:hi];assert '.byte $20, $52, $0b, "WORLD  TIME"'in top
    (O/'native-top-status-input.txt').write_text(top)
    q=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False,
        base_ROM_sha256=PIN,observed_latest_ROM_sha256=observed,base_font_sha256=FONT_SHA,donor_sha256=EXPECTED,source_component_bytes=labels['KrHudEnd']-0x9000,
        original_island_bytes=sum(map(len,chunks)),original_islands_reproduced=True,spans=metadata,labels=labels,split_labels=sl,commands=commands,
        split=dict(options_bytes=361,combat_data_bytes=79,fixture_data_address=0xcd40,code_lease_granted=False),
        exact_native_consumers=dict(ROM_sha256=observed,IRQ=dict(physical_PRG=126,CPU=0x8000,bytes=len(irq)),publisher_tail=dict(physical_PRG=62,CPU=0xa000+(at-16)%8192,bytes=len(tail))),
        source_icon_mapping=dict(MMC3_mode=0,BG_pattern_base=0,physical_CHR_page=38,mapper_publisher=mapper.hex(),options=rows),
        font_bytes=1024,font_changed_cells=sorted(changed),font_preserved_native_HUD_cells=sorted(preserved),
        proposed_CHR_page=1023,CHR_lease_granted=False,proposed_cache=[0xc87a,0xc880],cache_lease_granted=False,
        queue_command_bytes=35,queue_total_bytes_with_terminator=36,existing_inventory_queue_command_bytes=34,
        source_palette_adaptation='Original icon pixels/alpha retained under bijective1<->2 plane swap for native white HUD ink; existing native HUD palette2 stays owner. No palette or attribute writes.',
        imports=['KrState','KrHudCache','KrHudPhysicalLow','KrHudPhysicalHigh','SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','DisableScreenFlag','NmiDisable','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer1','InvHudActive','InvHudPhysical','X5HudChrUpper','X5WideChrActive','ReloadCHRBank'],
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),HOST,ROM,F,CURRENT,NATIVE,FONT,R/'inc/charmap.inc',R/'src/reset.s',R/'src/mmc5_expanded.s',R/'src/inventory.s',R/'src/nmi_vram_fast.s',
            *sources,O/'original.s',O/'original.cfg',O/'original.bin',O/'component.s',O/'component.cfg',O/'component.bin',O/'component.dbg',O/'base-font.chr',O/'equipment-font.chr',O/'original-icon-patterns.chr',O/'native-top-status-input.txt',
            O/'split-hud-proposal.inc',O/'split.s',O/'split.cfg',O/'split.bin',O/'split.dbg',O/'native-IRQ31.bin',O/'native-publisher-tail.bin']})
    # The source font is extracted once from the exact0ff ROM; mutable Downloads
    # is deliberately not a future binding. The1024B font + recorded source hash
    # remain reviewable even after root publishes the next nightly.
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in['passed','source_component_bytes','original_island_bytes','queue_command_bytes','font_changed_cells','CHR_lease_granted','cache_lease_granted']}))
if __name__=='__main__':main()
