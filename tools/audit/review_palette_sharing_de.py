"""Bind the reported brown underground brick to current code and Bass art."""
from pathlib import Path
import collections,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'palette-sharing-de'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def at(ad):return ad if ad<2048 else ad-0x6000+2048
def main():
    assert not O.exists();O.mkdir()
    m=load('palette_de_model',V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py')
    tags=load('palette_de_tags',R/'tools/reference/tag_player_outlines.py')
    maptext=(R/'src/chr_map_mmc3.inc').read_text().split('ChrPhysicalMap:\n')[1].split('.popseg')[0]
    mapping=[tags.number(n.strip())for line in maptext.splitlines()if'.byte 'in line for n in line.split('.byte ')[1].split(',')]
    chrdata=(R/'chr/characters/packed-mmc3.chr').read_bytes();art=[]
    for filename,prefix in(('bass_metasprites.inc','XgBASS'),('bass_special_poses.inc','SsBass')):
        text=(R/'src'/filename).read_text();banks=[tags.number(v)for v in tags.table(text,prefix+'Banks')]
        aliases=dict(re.findall(r'^(\w+)\s*=\s*(\w+)\s*$',text,re.M));contexts={}
        for side in('Left','Right'):
            refs=[v.lstrip('<>')for v in tags.table(text,prefix+side+'Lo')]
            assert len(refs)==len(banks)
            for name,bank in zip(refs,banks):
                seen=set()
                while name in aliases:assert name not in seen;seen.add(name);name=aliases[name]
                contexts.setdefault(name,set()).add(bank)
        counts=collections.Counter();examples={};current=None
        for line in text.splitlines():
            label=re.fullmatch(r'(\w+):',line)
            if label:current=label[1]
            match=tags.PART.fullmatch(line)
            if not match or current not in contexts or int(match[3],16)&3!=3:continue
            tile=int(match[2],16);colors=set()
            for bank in contexts[current]:
                start=mapping[bank]*1024+tile*16;data=chrdata[start:start+32];assert len(data)==32
                for half in(0,16):
                    for y in range(8):
                        for x in range(8):
                            color=((data[half+y]>>(7-x))&1)+2*((data[half+y+8]>>(7-x))&1)
                            if color:colors.add(color)
            key=','.join(map(str,sorted(colors)));counts[key]+=1
            examples.setdefault(key,[])
            if len(examples[key])<8:examples[key].append(current)
        art.append(dict(source=filename,source_sha256=sha(R/'src'/filename),palette3_parts_by_used_pixel_indices=dict(counts),examples=examples))
    groups=[]
    for mapper in('mmc3','mmc5'):
        im=m.q.Image(R/'build'/f'smb-crossover-{mapper}.nes');L=im.ram
        def run(name,character,metatile=0x52):
            raw=bytearray(10240)
            for seg in im.segs.values():
                if seg['name']=='SMCCODE':raw[seg['start']:seg['start']+seg['size']]=im.raw[seg['ooffs']:seg['ooffs']+seg['size']]
            hook=im.hook(name);bank=hook['physical_bank']
            for n,value in dict(SelectedCharacter=character,AreaType=2,ObjectOffset=0,Block_Metatile=metatile,CurrentBank=bank|(128 if im.mapper==5 else 0)).items():raw[at(L[n])]=value
            raw[0x1ef]=255;raw[0x1f0]=92
            return m.execute(im,raw,[0,0,0,1,238],{0x8000:62,0xa000:bank,0xc000:12,0xe000:63},hook['address'],0x5d00,240)
        palette=run('QueueMegaManFacePalette',9);block=run('DrawBlock',9)
        packet=list(palette['ram'][at(L['VRAM_Buffer1']):at(L['VRAM_Buffer1'])+7])
        control=run('QueueMegaManFacePalette',0);native=list(control['ram'][at(L['VRAM_Buffer1'])+3:at(L['VRAM_Buffer1'])+6])
        assert packet==[63,29,3,15,55,23,0]and native==[12,60,28]
        assert block['ram'][at(L['Block_SprAttrib'])]==3
        groups.append(dict(mapper=mapper,ROM_sha256=sha(im.path),Bass_underground_palette3_packet=packet,native_underground_palette3_colors=native,
            ordinary_bouncing_brick_palette=3,GetFacePalette_hook=im.hook('QueueMegaManFacePalette'),DrawBlock_hook=im.hook('DrawBlock')))
    report=dict(status='CONFIRMED_CURRENT_SHARED_PALETTE_CONFLICT_NOT_REPAIRED',groups=groups,Bass_art=art,
        conclusion='Bouncing bricks and debris use sprite palette3, but the guest face setup replaces native underground cyan colors with black/skin/brown. Bass has28 base pose parts containing actual color2 skin pixels, so turning off pure-black outline layers does not free that palette. Restoring native palette3 globally would visibly recolor his face and special poses.',
        scope='Current compiled code and actual mapped CHR records; binds the mechanism seen in the retained1:38 footage. Not a fresh ordinary-controller reproduction or a completed palette allocator.',goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['status'],flush=True)
if __name__=='__main__':main()
