"""Buffer guest APU output without changing native instruction widths.

Documented stores and two MMC5-only Metroid scanner regions are transformed.
Offsets come from the pinned disassembly, never raw opcode-pattern searches.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/generated/guest-audio'
helpers={}

def metroid_provenance():
    path=ROOT/'docs/reference/metroid-apu-stores.json'
    if path.exists():return json.loads(path.read_text())['banks']
    source=ROOT/'.upstream/metroid/Source_Files'
    aliases={k:int(v,16) for k,v in re.findall(r'^\.alias\s+(\w+)\s+\$([0-9a-f]+)',(source/'Metroid_Defines.asm').read_text(),re.I|re.M)}
    banks={}
    for bank in (0,1,2,4,5):
        stores=[]
        for m in re.finditer(r'^L([A-F0-9]{4}):\s*\*?\s*(STA|STX|STY)\s+([^;\n]+)',(source/f'Bank{bank:02d}.asm').read_text(),re.M):
            pc=int(m[1],16);parts=m[3].strip().split(',');base=parts[0].strip();address=aliases.get(base)
            if address is None and re.fullmatch(r'\$[a-fA-F0-9]{4}',base):address=int(base[1:],16)
            if 0xb200<=pc<0xc000 and address is not None and 0x4000<=address<=0x400f:
                stores.append([pc,m[2],address,parts[1].strip().lower() if len(parts)>1 else ''])
        banks[str(bank)]=stores
    path.write_text(json.dumps({'source':'https://github.com/nmikstas/metroid-disassembly','description':'Documented APU store instruction locations; no ROM data.','banks':banks},indent=2)+'\n')
    return banks

def write(op,address,index='',stream='Native'):
    reg=address-0x4000
    # Indexed writers can reach a timer-high register even when their base
    # is $4000. Track those writes so note retriggers survive buffering.
    if index or reg%4==3 or reg in (1,5):
        name=f'Guest{stream}Store{op}{reg:02x}{index.upper()}'
        helpers[name]=(op,reg,index,stream)
        return 'JSR ::'+name
    return op+f' ::Guest{stream}Apu+${reg:02x}'

def transform(source,stream='Native'):
    aliases={k:int(v,16) for k,v in re.findall(r'^\s*(\w+)\s*=\s*\$([0-9a-f]+)\b',source,re.I|re.M)}
    aliases.update({'SND_SQUARE1_REG':0x4000,'SND_SQUARE2_REG':0x4004,'SND_NOISE_REG':0x400c,'SND_REGISTER':0x4000,'SND_MASTERCTRL_REG':0x4015})
    pattern=re.compile(r'(?i)\b(STA|STX|STY)\s+(\$[0-9a-f]{4}|[a-z_]\w*)(\s*\+\s*[0-9]+)?(?:\s*,\s*([xy]))?(?=\s*(?:;|$))')
    def replace(m):
        name=m[2];address=int(name[1:],16) if name.startswith('$') else aliases.get(name)
        if address is None:return m[0]
        address+=int(m[3].split('+')[1]) if m[3] else 0
        if address==0x4015:
            if stream=='Fx':return m[1]+' ::GuestFxApu+$15'
            assert not m[4],m[0]
            return 'JSR ::GuestNativeStatus'+m[1].upper()
        if not 0x4000<=address<=0x400f:return m[0]
        return write(m[1].upper(),address,(m[4] or '').lower(),stream)
    return '\n'.join(pattern.sub(replace,line) if not line.lstrip().startswith(';') else line for line in source.splitlines())+'\n'

def megaman3():
    source=transform((ROOT/'audio/megaman3/imported.s').read_text())
    # These two documented routine tails have balanced stacks and no work
    # after the flag-preserving APU writer. Keep the four-byte span so later
    # code/song addresses and MMC3's original bytes remain unchanged.
    for start,end in (('_init_channel:','_handle_channel:'),
                      ('_handle_channel:','_audio_track_queue:')):
        start_anchor='\n'+start+'\n';end_anchor='\n'+end+'\n'
        assert source.count(start_anchor)==source.count(end_anchor)==1,(start,end)
        lo=source.index(start_anchor)+1;hi=source.index(end_anchor,lo+len(start))
        block=source[lo:hi]
        tail='\tJSR ::GuestNativeStoreSTA00Y\n\tRTS'
        assert block.count(tail)==1,(start,'Documented four-byte writer tail')
        replacement=('.if ::MAPPER_MMC5\n\tJMP ::GuestNativeStoreSTA00Y\n\tNOP\n'
                     '.else\n'+tail+'\n.endif')
        source=source[:lo]+block.replace(tail,replacement)+source[hi:]
    return source

def metroid(bank):
    original=(ROOT/f'src/audio/metroid/bank{bank}.inc').read_text()
    cells=[]
    for line in original.splitlines()[2:]:
        line=line.strip()
        if line.startswith('.byte '): cells += [int(v.strip()[1:],16) for v in line[6:].split(',')]
        elif line.startswith('.word '): cells += [line[6:],None]
        else:assert not line,line
    assert len(cells)==8192
    patches={}
    for pc,op,address,index in metroid_provenance()[str(bank)]:
        pos=pc-0xa000
        assert cells[pos+1:pos+3]==[address%256,address//256],(bank,hex(pc),cells[pos:pos+3])
        patches[pos]=write(op,address,index)
    # LoadSFXRegisters writes through ($e0),Y, then INY. Unlike the direct
    # stores above this otherwise bypasses the shadow image entirely: the
    # mixer would immediately restore old music sweep/timer registers over
    # the beam's envelope. Replace the documented three-byte pair together.
    assert cells[0x1386:0x1389]==[0x91,0xe0,0xc8],(bank,cells[0x1386:0x1389])
    patches[0x1386]='JSR ::GuestMetroidStoreIndirectY'
    # Exact, same-size performance replacements in the pinned SoundEngine and
    # CheckSFXFlag code. Keep all song data, routine addresses and default RTS
    # B4EE intact. The source input remains the original relocated native code.
    # Both mappers use the same flag-scan replacement. Tests compare routines,
    # all flags/registers/private RAM and ordered APU writes, including empty
    # scans whose Multi Add8 still clears overflow even without any effect.
    def span(start,end):
        out=[];at=start
        while at<end:
            if isinstance(cells[at],str):
                assert at+1<end and cells[at+1] is None
                out.append('  .word '+cells[at]);at+=2
            else:
                values=[]
                while at<end and len(values)<16 and isinstance(cells[at],int):values.append(cells[at]);at+=1
                assert values,at
                out.append('  .byte '+','.join(f'${v:02x}' for v in values))
        return out
    assert cells[0x13ca:0x13d3]==[0x20,0x1b,0xb3,0x20,0x4b,0xb3,0x20,0x3d,0xb3]
    flags_word='SmAudioRam+$4d'
    assert cells[0x14dd:0x14ef]==[0x48,0x0e,flags_word,None,0xb0,0x0c,0xc8,0xc8,0x98,0xc9,0x10,0xd0,0xf4,0x68,0x8d,flags_word,None,0x60]
    special={
        0x13ca:(['.if ::MAPPER_MMC5','  jsr ::SamusAudioSfxScans','  .byte $ea,$ea,$ea,$ea,$ea,$ea','.else']+
                span(0x13ca,0x13d3)+['.endif'],9),
        0x14dd:([
                 '  .byte $f0,$07,$0a,$b0,$0d,$c8,$c8,$d0,$f9,$a0,$10,$38,$ea,$ad',
                 '  .word '+flags_word,'  .byte $ea,$60'],18),
    }
    lines=[f'.segment "METROID_AUDIO_{bank}"',f'MetroidAudio{bank}:']
    pos=0
    while pos<len(cells):
        if pos in special:
            block,width=special[pos];lines+=block;pos+=width
        elif pos in patches:lines.append('  '+patches[pos]);pos+=3
        elif isinstance(cells[pos],str):lines.append('  .word '+cells[pos]);pos+=2
        else:
            values=[]
            while pos<len(cells) and len(values)<16 and pos not in patches and pos not in special and isinstance(cells[pos],int):values.append(cells[pos]);pos+=1
            assert values,pos
            lines.append('  .byte '+','.join(f'${v:02x}' for v in values))
    return '\n'.join(lines)+'\n',len(patches)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ('contra','zelda','castlevania'):
        (OUT/f'{name}.inc').write_text(transform((ROOT/f'src/audio/roster/{name}.inc').read_text()))
    (OUT/'megaman3.inc').write_text(megaman3())
    counts={}
    for bank in (0,1,2,4,5):
        content,counts[bank]=metroid(bank);(OUT/f'metroid{bank}.inc').write_text(content)
    fx=(ROOT/'src/music_drivers/vanilla_sfx.s').read_text().split('.proc SFXSoundEngine',1)[1]
    # The imported music owns the NES frame sequencer. Resetting it every
    # world-effect update would change that music's envelopes and sweeps.
    fx=fx.replace('sta APU_FRAMECOUNTER','; guest music owns APU_FRAMECOUNTER')
    (OUT/'shared-sfx.inc').write_text('.scope GuestSharedSfx\n.proc SFXSoundEngine'+transform(fx,'Fx')+'\n.endscope\n')
    # MM2 already routes its dynamic stores through fixed-bank helpers.
    helpers['GuestNativeStoreSTA00X']=('STA',0,'x','Native')
    helpers['GuestNativeStoreSTA01X']=('STA',1,'x','Native')
    lines=['; Generated flag/register-preserving APU dirty writers.','.pushseg','.segment "FIXED"']
    for name,(op,reg,index,stream) in sorted(helpers.items()):
        suffix=','+index if index else ''
        lines += [name+':',f'  {op} Guest{stream}Apu+${reg:02x}{suffix}','  php']
        if index!='y':
            # A dirty counter is consumed every update; an audio driver cannot
            # issue 256 writes to one register in that time. INC preserves A.
            lines += [f'  inc Guest{stream}Dirty+${reg:02x}{suffix}']
        else:
            lines += ['  pha','  lda #1',f'  sta Guest{stream}Dirty+${reg:02x}{suffix}','  pla']
        lines += ['  plp','  rts']
    lines += ['.popseg']
    (OUT/'writers.inc').write_text('\n'.join(lines)+'\n')
    print('Guest APU buffering:',len(helpers),'writers; Metroid provenance patches',counts)

if __name__=='__main__':main()
