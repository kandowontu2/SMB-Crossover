"""Deduplicate logical CHR banks without changing sprite/area bank IDs.

MMC3's background windows retain aligned, contiguous 2 KiB pairs. Sprite
windows may share any identical 1 KiB bank. Both mappers use the resulting
logical-to-physical table, with independent physical banks for special art.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]


def main():
    from build_ordinary_body_layout import main as build_ordinary_layout
    build_ordinary_layout()
    from build_megaman_injury_art import main as build_injury_art
    build_injury_art()
    folder=ROOT/'chr/characters'
    report={}
    for mapper in ('mmc3','mmc5'):
        base=ROOT/'chr'
        data=b''.join((base/f'mmc5/bg_{a}.chr').read_bytes()
                      for a in ('water','ground','underground','castle'))
        data+=(base/f'{mapper}/sprites_mario.chr').read_bytes()
        data+=(base/f'{mapper}/sprites_misc.chr').read_bytes()
        if mapper=='mmc5':data+=(base/'mmc5/sprites_enemies.chr').read_bytes()
        else:data+=b''.join((base/f'mmc3/sprites_{a}.chr').read_bytes()
                           for a in ('water','overworld','underground','castle'))
        assert len(data)<=0x7400
        data+=bytes(0x7400-len(data))
        data+=(folder/'crossover-roster-low.chr').read_bytes()[:0x7c00]
        data+=(folder/'crossover-menu.chr').read_bytes()
        assert len(data)<=0x10000
        data+=bytes(0x10000-len(data))
        for name in (f'crossover-megaman-{mapper}.chr','crossover-samus.chr',
                     'crossover-roster-high.chr','crossover-expanded.chr'):
            data+=(folder/name).read_bytes()
        logical=[data[i:i+1024] for i in range(0,len(data),1024)]
        overflow=folder/'crossover-roster-overflow.chr'
        if overflow.exists():
            extra=overflow.read_bytes();assert len(extra)%1024==0 and len(extra)<=3072
            for i in range(len(extra)//1024):
                assert logical[0x84+i]==bytes(1024),'Bill growth logical$84..$86 must be unallocated'
                logical[0x84+i]=extra[i*1024:(i+1)*1024]
        samus_extra=folder/'samus-extra-body.chr' 
        if samus_extra.exists():
            extra=samus_extra.read_bytes()
            assert len(extra)<=1024, 'Samus auxiliary body reserves only logical $80'
            assert logical[0x80]==bytes(1024), 'Logical $80 must remain free for Samus auxiliary artwork'
            if extra:logical[0x80]=extra
        # Firebars cannot borrow the active player's CHR. These two unused
        # pairs in the stable misc bank retain Mario's native fireball art.
        misc=bytearray(logical[0x14])
        misc[:64]=logical[0x12][0x3c*16:0x40*16]
        logical[0x14]=bytes(misc)
        specialbody=folder/'special-bass-body.chr'
        if specialbody.exists():
            body=specialbody.read_bytes()
            ids=list(range(244,256))+list(range(0x72,0x78))+list(range(0x7a,0x80))
            logical += [bytes(1024)]*(256-len(logical))
            for i in range(len(body)//1024):logical[ids[i]]=body[i*1024:(i+1)*1024]
        lance=folder/'crossover-lance.chr'
        if lance.exists():
            body=lance.read_bytes();ids=list(range(0x74,0x78))+list(range(0x7a,0x80))
            for i in range(len(body)//1024):logical[ids[i]]=body[i*1024:(i+1)*1024]
        megaspecial=folder/'special-megaman-body.chr'
        if megaspecial.exists():
            body=megaspecial.read_bytes()
            for i in range(len(body)//1024):logical[0xaa+i]=body[i*1024:(i+1)*1024]
        scrooge=folder/'crossover-scrooge.chr'
        if scrooge.exists():
            body=scrooge.read_bytes()
            for i in range(len(body)//1024):logical[0xa7+i]=body[i*1024:(i+1)*1024]
        sophia=folder/'crossover-sophia-extra.chr'
        if sophia.exists():
            body=sophia.read_bytes()
            assert len(body)<=4096, 'Sophia auxiliary banks must stay in $ad..$b0'
            for i in range(len(body)//1024):logical[0xad+i]=body[i*1024:(i+1)*1024]
        physical=[];mapping=[0]*256
        paired=list(range(0,16,2))+[0x3c,0x3e,0x70,0x78]
        for index in paired:
            pair=logical[index:index+2]
            found=next((i for i in range(0,len(physical),2)
                        if physical[i:i+2]==pair),None)
            if found is None:found=len(physical);physical+=pair
            mapping[index:index+2]=[found,found+1]
        for index,bank in enumerate(logical):
            if index in paired or index-1 in paired:continue
            if bank not in physical:physical.append(bank)
            mapping[index]=physical.index(bank)
        original=len(physical)
        artpath=folder/f'special-weapons-{mapper}.chr'
        special=[]
        if artpath.exists():
            art=artpath.read_bytes()
            shared=folder/f'special-remaining-shared-{mapper}.chr'
            if shared.exists():art=art[:-2048]+shared.read_bytes()
            assert len(art)%2048==0
            if len(physical)%2:physical.append(bytes(1024))
            for i in range(0,len(art),2048):
                special.append(len(physical))
                physical += [art[i:i+1024],art[i+1024:i+2048]]
        samus=[]
        artpath=folder/f'samus-weapons-{mapper}.chr'
        if artpath.exists():
            art=artpath.read_bytes()
            shared=folder/f'samus-remaining-shared-{mapper}.chr'
            if shared.exists():art=art[:-2048]+shared.read_bytes()
            if len(physical)%2:physical.append(bytes(1024))
            for i in range(0,len(art),2048):
                samus.append(len(physical))
                physical += [art[i:i+1024],art[i+1024:i+2048]]
        remaining=[samus[-1],special[-1]] if samus and special else []
        artpath=folder/f'remaining-weapons-{mapper}.chr'
        if artpath.exists():
            art=artpath.read_bytes()
            if len(physical)%2:physical.append(bytes(1024))
            for i in range(0,len(art),2048):
                remaining.append(len(physical));physical += [art[i:i+1024],art[i+1024:i+2048]]
        hud=[]
        hudpath=folder/'inventory-hud.chr'
        if hudpath.exists():
            data=hudpath.read_bytes()
            if mapper=='mmc3' and len(physical)%2:physical.append(bytes(1024))
            for i in range(0,len(data),2048):
                hud.append(len(physical))
                physical.append(data[i:i+1024])
                if mapper=='mmc3':physical.append(data[i+1024:i+2048])
        hurtpath=folder/'crossover-hurt-body.chr'
        if hurtpath.exists():
            hurt=hurtpath.read_bytes()
            assert len(hurt)==2048
            for slot in (0x81,0x82):
                assert logical[slot]==bytes(1024),'Private injury logical banks must be unused before overlay'
                mapping[slot]=len(physical)
                physical.append(hurt[(slot-0x81)*1024:(slot-0x81+1)*1024])
        ordinarypath=folder/'ordinary-bass-walk.chr'
        if ordinarypath.exists():
            ordinary=ordinarypath.read_bytes()
            assert len(ordinary)==1024
            assert logical[0x83]==bytes(1024),'Ordinary Bass viewport bank must not replace existing logical CHR'
            mapping[0x83]=len(physical)
            physical.append(ordinary)
        assert len(physical)<=256,(mapper,len(physical),'CHR capacity exceeded')
        (folder/f'packed-{mapper}.chr').write_bytes(b''.join(physical))
        lines=['; Generated logical-to-physical CHR map.','.pushseg','.segment "FIXED"','ChrPhysicalMap:']
        for off in range(0,256,16):lines.append(' .byte '+','.join(map(str,mapping[off:off+16])))
        lines+=['.popseg','.pushseg','.segment "SPECIAL_MM"','SsPhysicalBanks:',
                ' .byte '+','.join(map(str,special or [0])),'.popseg',
                '.pushseg','.segment "SAMUS"','SmWeaponPhysicalBanks:',
                ' .byte '+','.join(map(str,samus or [0])),'.popseg',
                '.pushseg','.segment "SPECIAL_ROSTER"','AvPhysicalBanks:',
                ' .byte '+','.join(map(str,remaining or [0])),'.popseg',
                '.pushseg','.segment "INVENTORY"','InvHudPhysicalBanks:',
                ' .byte '+','.join(map(str,hud or [0])),'.popseg']
        (ROOT/f'src/chr_map_{mapper}.inc').write_text('\n'.join(lines)+'\n')
        report[mapper]=dict(original_banks=len(logical),deduplicated_banks=original,
                            special_families=len(special),used_banks=len(physical),capacity=256)
    (ROOT/'build/chr-packing.json').write_text(json.dumps(report,indent=2)+'\n')
    # Optional expanded-only overlay; both ordinary outputs/assets stay exact.
    from patch_samus_fixed_hud_v2 import apply_expanded_assets
    apply_expanded_assets(folder)


if __name__=='__main__':main()
