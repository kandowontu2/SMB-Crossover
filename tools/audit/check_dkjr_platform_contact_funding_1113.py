"""Zero-output source/preimage/fitting audit; does not grant or patch a ROM."""
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H

R=P.B.R
SOURCE=R/'tools/reference/dkjr_platform_contact_1113.s'
LAYOUT=dict(NATIVE=(0xb98e,44),RESTORE=(0xb707,11),
    GENERIC_A=(0xbd5b,26),GENERIC_B=(0xbdd5,26))


def at(bank,pc):return 16+bank*8192+(pc&8191)


def sources(raw):
    b=H.W.Symbols.bundle();b['raw']=raw
    names=('R0','R7','RgTempX','RgTempPage','RgTempY','RgTemp2','RgTemp3',
        'Player_X_Position','ScreenLeft_X_Pos','BoundingBox_UL_Corner',
        'BoundingBox_LR_Corner','RyuSourceBodyProfile','RelativePlayerPosition',
        'BoundingBoxCore','SelectedCharacter','CHARACTER_RYU')
    values={n:H.W.address(b,n)for n in names}
    values.update(RyuSourceBodyPlatformOverlap=0xbc2f,RyuSourceBodyPlatformBasic=0xbbf7,
        RyuSourceBodyBox=0xbaa3)
    assert values['SelectedCharacter']==0x6002 and values['CHARACTER_RYU']==10
    definitions=''.join(f'{n}=${value:x}\n'for n,value in values.items())
    save='php\npha\ntxa\npha\ntya\npha\n'
    save+=''.join(f'lda R0+{i}\npha\n'for i in range(8))
    restore=''.join(f'pla\nsta R7-{i}\n'for i in range(8))
    restore+='pla\ntay\npla\ntax\npla\nplp\n'
    temps=('RgTempX','RgTempPage','RgTempY','RgTemp2','RgTemp3')
    full_save=save+''.join(f'lda {n}\npha\n'for n in temps)
    full_restore=''.join(f'pla\nsta {n}\n'for n in reversed(temps))+restore
    text=(R/'src/ryu_source_body.s').read_text();rows=[]
    for name,pc,expected in(('Z2LegacyPlatformPrepare',0xbcf8,(125,99)),
                            ('Z2LegacyPlatformFinish',0xbd75,(122,96))):
        body=text.split('.proc '+name+'\n',1)[1].split('.endproc',1)[0].split('.endif\n',1)[1]
        assert body.count('  RP_Save\n')==body.count('  RP_Restore\n')==1
        old=body.replace('  RP_Save\n',full_save).replace('  RP_Restore\n',full_restore)
        guard='php\npha\nlda SelectedCharacter\ncmp #CHARACTER_RYU\nbne NotRyu\npla\nplp\n'
        current=body.replace('  RP_Save\n',guard+save).replace('  RP_Restore\n',restore)
        current+='NotRyu:\npla\nplp\nrts\n'
        images=[H.T.assemble(definitions+'.segment "LEAF"\n'+s,dict(LEAF=(pc,256)))
            for s in(old,current)]
        sizes=tuple(image['used']['LEAF']for image in images)
        assert sizes==expected,(name,sizes)
        full,current=[image['images']['LEAF']for image in images]
        preimage=raw[at(58,pc):at(58,pc)+len(full)]
        assert preimage==current.ljust(len(full),b'\xea'),name
        tail=pc+len(current);end=pc+len(full)
        bank=raw[16+58*8192:16+59*8192]
        calls=[]
        for target in range(tail,end):
            for op in(0x20,0x4c):
                needle=bytes((op,target&255,target>>8))
                calls += [(0xa000+i,target,op)for i in range(len(bank)-2)if bank[i:i+3]==needle]
        assert not calls,(name,calls)
        prg=raw[16:16+1048576]
        for target in range(tail,end):
            assert bytes((target&255,target>>8,0xba))not in prg,(name,'native flagged target tuple',target)
            far=(bytes((0xa9,target&255))+bytes.fromhex('8d6c01')+
                 bytes((0xa9,target>>8))+bytes.fromhex('8d6d01a9ba'))
            assert far not in prg,(name,'standard native farcall',target)
        rows.append(dict(name=name,physical_PRG=58,CPU_half_open=[pc,end],
            exact_source_original_bytes=len(full),exact_current_live_bytes=len(current),
            available_tail_half_open=[tail,end],available_tail_bytes=end-tail,
            tail_file_offset=at(58,tail),tail_preimage_hex=preimage[len(current):].hex(),
            current_full_extent_SHA256=sha256(preimage).hexdigest(),
            all_same_bank_direct_JSR_JMP_targets_exclude_tail=True,
            all_PRG_standard_native_farcall_and_flagged_tuple_targets_exclude_tail=True))
    # Assemble both segments after removing only their explicit fill directives.
    source=(R/'tools/reference/native_platform_collision_dispatch_1110_v1.s').read_text()
    source='\n'.join(line for line in source.splitlines()if not line.strip().startswith('.res'))
    original=H.T.assemble(source,dict(POLICY=(0xb707,11),DISPATCH=(0xb98e,44)))
    for segment,(pc,size)in dict(POLICY=(0xb707,11),DISPATCH=(0xb98e,44)).items():
        assert raw[at(0,pc):at(0,pc)+size]==original['images'][segment].ljust(size,b'\xea')
    return rows


def audit(raw):
    assert sha256(raw).hexdigest()==P.PRINCE_CURRENT
    leaves=sources(raw)
    linked=H.T.assemble(SOURCE.read_text(),LAYOUT)
    assert linked['used']==dict(NATIVE=42,RESTORE=8,GENERIC_A=21,GENERIC_B=24)
    assert linked['symbols']['DkPlatformDispatch']==0xb98e
    assert linked['symbols']['PlatformGeneric']==0xbd5b
    bank=raw[16:16+8192]
    assert bank[0x143f:0x144a]==bytes.fromhex('208eb9ad4a07d0032089b4')
    assert bank.count(bytes.fromhex('208eb9'))==1
    return dict(passed=True,parent_ROM_SHA256=sha256(raw).hexdigest(),
        qualified_old_source_extents=leaves,proposed_used=linked['used'],
        request_resources=[dict(name=n,physical_PRG=0 if n in('NATIVE','RESTORE')else 58,
            CPU_half_open=[pc,pc+size],file_offset=at(0 if n in('NATIVE','RESTORE')else 58,pc),
            preimage_hex=raw[at(0 if n in('NATIVE','RESTORE')else 58,pc):at(0 if n in('NATIVE','RESTORE')else 58,pc)+size].hex())
            for n,(pc,size)in LAYOUT.items()],
        sole_native_ingress=[0,0xb43f],new_RAM_bytes=0,new_CHR_bytes=0,
        ROM_written=False,outputs_written=0,formal_grant=False,
        source_SHA256={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest()for p in
            (Path(__file__),SOURCE,R/'src/ryu_source_body.s',R/'src/ryu_platform.s',
             R/'tools/audit/measure_mini_lift_actor_bridge_1108_v4.py',
             R/'tools/reference/native_platform_collision_dispatch_1110_v1.s')},
        remaining='Root lease review; actual transport/foreign/Main/IRQ/lag and current natural first/full native remain pending.')


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print('DKJR_PLATFORM_CONTACT_FUNDING '+json.dumps(audit(raw),sort_keys=True,separators=(',',':')),flush=True)
