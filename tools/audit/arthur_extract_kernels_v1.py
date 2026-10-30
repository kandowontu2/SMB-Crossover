"""Emit relocatable native Arthur kernels from the authenticated original ROM.

This is a private leaf, not a host PRG/CHR/RAM allocation. Every original
instruction has a source PC and an explicit operand relocation in the receipt.
"""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from arthur_source_map_v1 import load,machine,ROM,EXPECTED
from py65.disassembler import Disassembler
OUT=ROOT/'build/arthur-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

# [bank,start,end,kind]. Data is never sent through the instruction decoder.
RANGES=[(7,0xDC5B,0xDC6B,'code'),(7,0xDDA1,0xDDF7,'code'),(7,0xDEFD,0xDF04,'data'),(7,0xDF04,0xDF5D,'code'),
 (7,0xDF93,0xE014,'code'),(7,0xE01D,0xE171,'code'),(7,0xE1EE,0xE229,'code'),
 (7,0xE307,0xE317,'data'),(7,0xE317,0xE3DC,'code'),(7,0xE3DC,0xE3E3,'data'),
 (7,0xEB75,0xECA3,'code'),(7,0xECA3,0xECAF,'data'),(7,0xECAF,0xED07,'code'),
 (7,0xED07,0xED27,'data'),(7,0xED27,0xED51,'code'),(7,0xEFDA,0xF171,'code'),
 (7,0xF181,0xF1A3,'code'),(7,0xF2A3,0xF2E3,'data'),(7,0xF2E3,0xF34F,'code'),
 (7,0xF611,0xF6EC,'code'),(7,0xF6EC,0xF6F6,'data'),(7,0xF734,0xF73A,'code'),
 (4,0xBA63,0xBA99,'code'),(4,0xBB2D,0xBB49,'data')]
EXTERNAL={0xDB99:'ArHostCameraY',0xED51:'ArHostSfx',0xE9CA:'ArHostAheadTile',
          0xEA2F:'ArHostFloorTile',0xBB27:'ArConsumePickup'}
CUTS={0xE229:'ArInjuryReady'}
EXPORTS={0xDC5B:'ArNativeSetBodyPalette',0xDDA1:'ArNativeInputDirection',0xDDB2:'ArNativeClimbPose',0xDDCF:'ArNativeCrouchPose',
 0xDF04:'ArNativeRise',0xDF33:'ArNativeFall',0xDF3C:'ArNativeTerminalFall',0xDF93:'ArNativeAirPose',
 0xE01E:'ArNativeAttack',0xE079:'ArNativeAttackPose',0xE0BE:'ArNativeThrow',0xE166:'ArNativeAlignFloor',
 0xE1EE:'ArNativeInjuryInit',0xE35E:'ArNativeIdlePose',0xE3B9:'ArNativeHurtBlink',
 0xEB75:'ArNativeLance',0xEB84:'ArNativeDagger',0xEC10:'ArNativeTorch',0xECAF:'ArNativeAxe',0xED27:'ArNativeCross',
 0xF03E:'ArNativeMove',0xF181:'ArNativeProject',0xF611:'ArNativeShotContact',0xF68E:'ArNativePlayerContact',
 0xF305:'ArNativeMarkShotHit',0xF309:'ArNativeSetCrouch',0xF311:'ArNativeSetAir',0xF319:'ArNativeSetNaked',
 0xF31D:'ArNativeSetInvulnerable',0xF32E:'ArNativeClearCrouch',0xF332:'ArNativeClearFacing',0xF336:'ArNativeClearAir',
 0xBA63:'ArNativeCollectWeapon',0xBA77:'ArNativeRepairArmor'}

def label(addr):return f'ArO_{addr:04X}'
def ramlabel(addr):return f'ArR_{addr:04X}'
def covered(addr):return addr in CUTS or any(start<=addr<end for _,start,end,_ in RANGES)

def main():
    rom=load();OUT.mkdir(parents=True,exist_ok=True)
    asm=['; Generated from exact original ROM; see kernel-source-proof.json.',
         '; Host allocation deliberately unspecified; private leaf sections only.',
         '.export ArO_BB2D,ArO_BB3B']
    # Native launch sets this player-only drift latch at DDFF; the explicit
    # scheduler owns that launch boundary and retains the same state field.
    extern=set();ram={0x065D:1};proof=[];native_bytes=0
    body=[]
    for bank,start,end,kind in RANGES:
        m=machine(bank);d=Disassembler(m);pc=start
        while pc<end:
            if pc in EXPORTS:body.extend([f'.export {EXPORTS[pc]}',f'{EXPORTS[pc]}:'])
            body.append(label(pc)+':')
            if kind=='data':
                body.append(f' .byte ${m.memory[pc]:02x}')
                proof.append(dict(bank=bank,address=pc,kind='data',bytes=f'{m.memory[pc]:02x}'))
                pc+=1;native_bytes+=1;continue
            size,text=d.instruction_at(pc);mnemonic,mode=m.disassemble[m.memory[pc]]
            assert mnemonic!='???' and pc+size<=end,(bank,hex(pc),text)
            original=text;operand=None;relocation=None
            if mode=='rel':operand=(pc+2+((m.memory[pc+1]+128)%256-128))&65535
            elif mode in ('abs','abx','aby','ind'):operand=m.memory[pc+1]+m.memory[pc+2]*256
            elif mode in ('zpg','zpx','zpy','inx','iny'):operand=m.memory[pc+1]
            if operand is not None:
                if operand<0x800:
                    extent=20 if mode in ('abx','aby')and operand>=0x100 else(2 if operand==0xC5 else 1)
                    ram[operand]=max(ram.get(operand,1),extent)
                    if mode in ('inx','iny'):ram[operand+1]=max(ram.get(operand+1,1),1)
                    target=ramlabel(operand);relocation=dict(kind='private_native_state',original=operand,symbol=target)
                elif covered(operand):
                    target=label(operand);relocation=dict(kind='native_code_or_data',original=operand,symbol=target)
                else:
                    assert operand in EXTERNAL,(bank,hex(pc),text,hex(operand))
                    target=EXTERNAL[operand];extern.add(target)
                    relocation=dict(kind='declared_external_owner',original=operand,symbol=target)
                text=re.sub(r'\$[0-9a-fA-F]{2,4}',target,text,count=1)
            # EFDA constructs a data pointer using two immediate bytes.
            if pc in (0xEFDE,0xEFE0):
                text=('LDA #>' if pc==0xEFDE else 'LDY #<')+label(0xF2A3)
                relocation=dict(kind='native_data_pointer_immediate',original=0xF2A3,symbol=label(0xF2A3))
            body.append(' '+text)
            proof.append(dict(bank=bank,address=pc,kind='instruction',bytes=bytes(m.memory[pc:pc+size]).hex(),
                original=original,ported=text,mode=mode,relocation=relocation))
            pc+=size;native_bytes+=size
        if end in CUTS:
            body += ['; Authored leaf return boundary before original knockback loop.',label(end)+':',' jmp '+CUTS[end]]
            extern.add(CUTS[end])
    for name in sorted(extern):asm.append('.import '+name)
    zp=sorted(a for a in ram if a<256);bss=sorted(a for a in ram if a>=256)
    asm+=['.segment "ARTHUR_ZP": zeropage','.exportzp ArNativeZpStart,ArNativeZpEnd','ArNativeZpStart:']
    for a in zp:asm+=['.exportzp '+ramlabel(a),ramlabel(a)+f': .res {ram[a]}']
    asm+=['ArNativeZpEnd:','.segment "ARTHUR_STATE"','.export ArNativeStateStart,ArNativeStateEnd','ArNativeStateStart:']
    for a in bss:asm+=['.export '+ramlabel(a),ramlabel(a)+f': .res {ram[a]}']
    asm+=['ArNativeStateEnd:','.segment "ARTHUR_NATIVE"','.export ArNativeStart,ArNativeEnd','ArNativeStart:']+body+['ArNativeEnd:']
    target=OUT/'native-kernels.s';target.write_text('\n'.join(asm)+'\n')
    context=['; Generated private leaf imports; no host addresses assigned.',
       'ArNativeZpBytes='+str(sum(ram[a]for a in zp)), 'ArNativeStateBytes='+str(sum(ram[a]for a in bss)),
       '.importzp ArNativeZpStart,ArNativeZpEnd','.import ArNativeStateStart,ArNativeStateEnd']
    context += ['.importzp '+ramlabel(a)for a in zp]+['.import '+ramlabel(a)for a in bss]
    context += ['.import '+name for name in EXPORTS.values()]
    (OUT/'native-context.inc').write_text('\n'.join(context)+'\n')
    record=dict(status='SOURCE_EXTRACTED_RELOCATABLE_KERNELS_NOT_YET_CPU_VERIFIED',original_ROM=str(ROM),original_ROM_sha256=EXPECTED,
        output=str(target.resolve()),output_sha256=sha(target),native_bytes=native_bytes,
        state=dict(ZP_bytes=sum(ram[a]for a in zp),BSS_bytes=sum(ram[a]for a in bss),
                   fields={ramlabel(a):dict(original=a,bytes=n)for a,n in sorted(ram.items())}),
        exports={name:addr for addr,name in EXPORTS.items()},declared_external_owners=sorted(extern),
        source_ranges=[dict(bank=b,start=s,end=e,kind=k)for b,s,e,k in RANGES],instructions_and_data=proof,
        tool=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),
        limits='No host lease, menu admission, native gameplay or sprite budget claim. Native source kernels require explicit world/contact/camera ownership.')
    p=OUT/'kernel-source-proof.json';p.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(native_bytes=native_bytes,ZP_bytes=record['state']['ZP_bytes'],BSS_bytes=record['state']['BSS_bytes'],
        records=len(proof),source_proof_sha256=sha(p))))

if __name__=='__main__':main()
