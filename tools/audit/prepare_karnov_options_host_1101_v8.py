"""Source-only graft for original Karnov options in a separate C2 carrier.

CHR1021/1022 and C2D600..DDFF require the integrator's independent ownership
grant. The returned source does not allocate or mutate the current ROM.
"""
from pathlib import Path
from prepare_karnov_options_1101_v7 import transform_terrain

R=Path(__file__).resolve().parents[2]
HOST=R/'tools/reference/karnov_options_1101_v7.inc'
PORTABLE=R/'build/karnov-options-component-1101-v7/karnov-options-portable-v7.inc'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform_sources(*,kernel,resident,terrain,config,output,carrier_helper):
    assert 'kr-options-host-v8.inc'not in kernel
    fragments={}
    # Original full controller/stock/timer bodies; bind only the already
    # authenticated actor dispatcher, private source RAM and source callbacks.
    constants='''KrOptionSound=KrSoundCallback
KrOptionUnsupportedScene=KrSceneCallback
KrExternal_C6FC=KrOptionUnsupportedScene
KrExternal_C28C=Kr_C28C
KrExternal_C534=Kr_C534
KrExternal_C5A0=Kr_C5A0
KrExternal_CF9A=Kr_CF9A
'''
    fragments['karnov-options-portable-v7.inc']=PORTABLE.read_text()
    fragments['kr-options-host-v8.inc']=('''; Original options execute in the authenticated selected C2 bank.
.pushseg
.segment "KR_OPTIONS_ROM"
'''+constants+HOST.read_text()+'''
.assert KrOptionsEnd <= $de00,lderror,"Karnov options exceed the explicit2KB lease"
.popseg
''')
    kernel=once(kernel,'KrKernelEnd:', '.include "kr-options-host-v8.inc"\nKrKernelEnd:')
    terrain=transform_terrain(terrain)
    # Original EAA7 publishes NONE on a new life with no earned equipment.
    # Do it at the actual reset owner; same-life scene transfer bypasses it.
    terrain=once(terrain,' jsr KrPickupReset         ; new life only; same-life seam bypasses',
                 ' jsr KrPickupReset         ; new life only; same-life seam bypasses\n lda #$ff\n sta KrState+$8e')
    resident=once(resident,' cmp #10\n bne KrCopyRow',' cmp #12\n bne KrCopyRow')
    helper=once(carrier_helper,'KrCarrierDestHi:.byte $c0,$c4,$c8,$cc,$d0,$d4,$d8,$dc,$c9,$cd',
                'KrCarrierDestHi:.byte $c0,$c4,$c8,$cc,$d0,$d4,$d8,$dc,$c9,$cd,$d6,$da')
    helper=once(helper,'KrCarrierChrLo:.byte <399,<400,<401,<402,<403,<404,<405,<406,<1019,<1020',
                'KrCarrierChrLo:.byte <399,<400,<401,<402,<403,<404,<405,<406,<1019,<1020,<1021,<1022')
    # Fund the table growth in the existing3-byte pre-water fill: one byte
    # saved in cold mapper setup, four table bytes added. No hot code change.
    helper=once(helper,'''KrCarrierMap:
 lda #1
 ldx R2
 cpx #8
 bcc :+
 lda #3
:sta $5130''','''KrCarrierMap:
 ldx R2
 lda #3
 cpx #8
 bcs :+
 lsr                         ; first8 rows use upper1, the four C2 rows upper3
:sta $5130''')
    fragments['kr-loader-carrier-v6.inc']=helper
    memory=f'KR_OPTIONS_RAM_MEM:start=$d600,size=$800,type=ro,bank=2,fill=yes,fillval=$ff,file="{(Path(output)/"kr-options.bin").as_posix()}";\n'
    assert 'KR_OPTIONS_RAM_MEM'not in config
    config=once(config,'MEMORY {\n','MEMORY {\n'+memory)
    config+='\nSEGMENTS { KR_OPTIONS_ROM:load=KR_OPTIONS_RAM_MEM,type=ro; KR_OPTIONS_IMAGE:load=CF_CHR_POST,type=ro,start=$ff400; }\n'
    return dict(kernel=kernel,resident=resident,terrain=terrain,config=config,fragments=fragments,
                additional_CHR_carrier=[1021,1022],C2_code_interval=[0xd600,0xde00],
                additional_context=[0xc865],ownership_granted=False)
