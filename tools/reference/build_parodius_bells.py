"""Retarget the Famicom Bell/pickup state machines with explicit SMB callbacks.

Palette transfer and enemy/terrain damage are integration interfaces. Timing,
roulette, pickup acceptance, Bell flags, Red firing/retraction and White1UP
state follow the authenticated cartridge instructions.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pn_native',ROOT/'tools/reference/build_parodius_native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
from py65.disassembler import Disassembler

RANGES=[(0x80b5,0x8136),(0x97fc,0x98a8),(0x98f5,0x991e),
        (0x9a6b,0x9bba),(0x9bd5,0x9beb),(0x9bf7,0x9c42)]
EXTERNALS={0x98a8:'PnBombPalettePrime',0x991e:'PnBombPaletteAdjust',
           0xfb1d:'PnBombWorldDamage',0xfd4e:'PnBellGainLife',
           0x9756:'PnBellBonusContact',0xfe20:'PnSoundEvent',
           0xc905:'PnTerrainQuery',0x90e6:'PnTerrainImpact',
           0xc977:'PnNativeSetAnimation',0xc98a:'PnNativeAnimate',
           0x9bba:'PnNativeKill'}
EXTRA={0x26:('PnNativeVramBusy',0x5da7),0x56:('PnNativePaletteStyle',0x5da6),
       0x1f:('PnNativePaletteMode',0x5d77),0x2c:('PnNativePaletteRestore',0x5d78),
       0x9e:('PnBombTerrainCursor',0x5d79),0x80:('PnNativeLives',0x5da5),
       0x6a:('PnNativeScrollXHi',0x5de1),0x6b:('PnNativeScrollXLo',0x5de0),
       0x66:('PnNativeScrollFlags',0x5de2),0x65ab:('PnRedRemaining',0x5dd7)}
ENTRIES={0x80b5:'PnNativePickup',0x97fc:'PnNativeBellUpdate',0x9c1e:'PnNativeRoulette'}


def generate(output):
    raw,cpu=native.source_cpu();dis=Disassembler(cpu);output.mkdir(parents=True,exist_ok=True)
    _,ram=native.mappings();ram.update({address:name for address,(name,_)in EXTRA.items()})
    starts=set()
    for lo,hi in RANGES:
        pc=lo
        while pc<hi:
            starts.add(pc);size,_=dis.instruction_at(pc);pc+=size
        assert pc==hi
    lines=['; Original Famicom Parodius Bell state; generated, not hand tuned.']
    for _,(name,address)in EXTRA.items():lines += [f'{name}=${address:04x}',f'.export {name}']
    lines+=['.pushseg','.segment "PARODIUS_BELLS"']
    instructions=[]
    for lo,hi in RANGES:
        pc=lo
        while pc<hi:
            size,text=dis.instruction_at(pc);mnemonic,_,operand=text.partition(' ')
            if mnemonic in native.BRANCH or mnemonic in ('JSR','JMP'):
                target=int(operand[1:],16)
                if pc<0x8136 and target in (0x8136,0x813a,0x814d):symbol='PbPickupDone'
                elif target==0x9bd4:symbol='PbReturn'
                elif target in EXTERNALS:symbol='PbCallback'+format(target,'04x')
                else:
                    assert target in starts,(hex(pc),text)
                    symbol='Pb'+format(target,'04x')
                assembly=native.BRANCH.get(mnemonic,mnemonic.lower())+' '+symbol
            elif operand and not operand.startswith('#')and'$'in operand:
                match=re.search(r'\$([a-fA-F0-9]+)',operand);address=int(match[1],16)
                if address==0x6590 and operand.endswith(',X'):
                    # Every indexed access in these ranges owns Bell actor27.
                    # Its remaining Red charges are not the player's Big phase.
                    assert pc in (0x9a77,0x9a7e,0x9a8b,0x9baf)
                    assembly=mnemonic.lower()+' PnRedRemaining'
                else:
                    if address>=0x8000:
                        if 0x9a57<=address<0x9a6b or 0x9beb<=address<0x9bf7:symbol='Pb'+format(address,'04x')
                        else:
                            assert 0x9153<=address<0x9371,(hex(pc),text)
                            symbol='Pn'+format(address,'04x')
                    else:
                        assert address in ram,(hex(pc),text)
                        symbol=ram[address]
                    assembly=mnemonic.lower()+' '+operand[:match.start()]+symbol+operand[match.end():]
            else:assembly=text.lower()
            lines.append(f'Pb{pc:04x}: {assembly} ; original ${pc:04x}')
            instructions.append(dict(address=pc,source_assembly=text,assembly=assembly))
            pc+=size
        if hi==0x8136:lines.append('PbPickupDone:rts')
        elif hi==0x98a8:lines.append('jmp PbCallback98a8 ; native fallthrough into palette publication')
        elif hi==0x9bba:lines.append('jmp PbCallback9bba ; native final Red cleanup')
    lines.append('PbReturn:rts')
    for address,target in EXTERNALS.items():
        lines += [f'PbCallback{address:04x}:']
        if target in ('PnBombPalettePrime','PnBombPaletteAdjust','PnBombWorldDamage','PnBellGainLife','PnBellBonusContact'):
            lines.append(f' jmp {target}')
        else:
            lines += ['.ifdef PARODIUS_CPU_FIXTURE',f' jmp {target}',
                      '.else',f' farcall {target},jmp','.endif']
    for address,name in ENTRIES.items():lines += [f'{name}=Pb{address:04x}',f'.export {name}']
    lines += ['.popseg','.pushseg','.segment "VIC_GFX"']
    for address in [*range(0x9a57,0x9a6b),*range(0x9beb,0x9bf7)]:
        lines.append(f'Pb{address:04x}:.byte {cpu.memory[address]}')
    lines.append('.popseg')
    actors=raw[16+6*8192:16+7*8192]
    lines += ['.ifndef PARODIUS_CPU_FIXTURE','.pushseg','.segment "VIC_WORLD"',
              'PnBellColorSteps:.byte '+','.join(map(str,actors[0x1527:0x1538])),
              'PnBellContactTypes:.byte '+','.join(map(str,actors[0x153d:0x1542])),'.popseg','.endif']
    (output/'parodius_bell_native.s').write_text('\n'.join(lines)+'\n')
    report=dict(source_sha256=native.SHA,ranges=RANGES,entries=ENTRIES,callbacks=EXTERNALS,
                extra_aliases={hex(a):dict(name=n,address=v)for a,(n,v)in EXTRA.items()},
                instructions=instructions,adaptations=['Pickup hazard exits return to the SMB caller.',
                'Actor27 Red charge counter has a dedicated exclusive byte.',
                'Palette transfers and damage/1UP delivery use explicit host callbacks.'],
                output_sha256=hashlib.sha256((output/'parodius_bell_native.s').read_bytes()).hexdigest())
    (output/'bell-native-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/generated/parodius-bells')
    a=p.parse_args();r=generate(a.output);print(json.dumps(dict(instructions=len(r['instructions']),output=str(a.output))))
