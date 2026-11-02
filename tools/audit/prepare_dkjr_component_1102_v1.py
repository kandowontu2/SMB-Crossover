"""Recover a relocatable original DK Jr actor; no host image or allocation.

Every donor instruction is emitted with its original PC. RAM is private;
indirect operands use local writable instruction operands while preserving
AXYP. Stage probes/bonus/score/background are explicit rejecting imports.
"""
from pathlib import Path
import sys,re,json,subprocess,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import dkjr_original_cpu_1102_v1 as D
from py65.disassembler import Disassembler
O=R/'build/dkjr-source-1102-v1'
RANGES=[(0xca82,0xcabf),(0xce6c,0xcec9),(0xcf37,0xcf62),(0xd1ae,0xd2fc),(0xd405,0xd55b),
        (0xd56e,0xdb5a),(0xdbb3,0xdbe9),(0xe98b,0xec17),(0xf1af,0xf1c5)]
DATA_LO,DATA_HI=0xc2cd,0xc3cd
EXPORTS={'Initialize':0xca82,'Input':0xce6c,'LandPose':0xcea2,'DefeatTick':0xcf37,'Clock':0xf1af,
         'FruitHit':0xd1ae,'Transition':0xd251,'Bounds':0xd2bd,'Damage':0xd405,
         'Move':0xd412,'FruitCollision':0xd43a,'Jump':0xd913,'FruitTouch':0xd955,
         'FallDistance':0xda34,'Land':0xdaa5,'DetachVine':0xdad7,
         'DefeatDrop':0xdaf7,'DefeatPose':0xdb20,'FruitAdvance':0xdbb3,
         'Repeat':0xe98b,'Gravity':0xe9ae,'Pose':0xe9ee,'Rect':0xeb69}

def main():
    O.mkdir(exist_ok=True)
    c=D.boot();m=c.memory;dis=Disassembler(c);ins={}
    for lo,hi in RANGES:
        a=lo
        while a<hi:
            n,s=dis.instruction_at(a);assert a+n<=hi,(hex(a),s)
            ins[a]=(n,s.lower());a+=n
    targets=set();imports=set();pairs={}
    for a,(n,s) in ins.items():
        if s.startswith(('jsr ','jmp ')) and '$'in s:
            target=int(s.split('$')[1],16)
            (targets if target in ins else imports).add(target)
        if s.startswith(('bcc ','bcs ','beq ','bne ','bmi ','bpl ','bvc ','bvs ')):
            targets.add(int(s.split('$')[1],16))
        # The original descriptor-address construction is part of source.
        if s.startswith('lda #$') and a+2 in ins and ins[a+2][1]=='sta $02':
            b=a+4
            if b in ins and ins[b][1].startswith('lda #$') and b+2 in ins and ins[b+2][1]=='sta $03':
                p=m[a+1]+256*m[b+1]
                if DATA_LO<=p<DATA_HI:
                    pairs[a]=f'lda #<DData_{p:04x}';pairs[b]=f'lda #>DData_{p:04x}'
    assert all(t in ins for t in targets),[hex(t)for t in targets if t not in ins]
    out=['; Generated solely from authenticated DK Jr original instructions.',
         '; Code origin A000 and private RAM C000 are MEASUREMENT addresses, not host grants.',
         '.setcpu "6502"','.macpack longbranch','.segment "DKJR"']
    for name,a in EXPORTS.items():out.append(f'.export Dkjr{name}\nDkjr{name}=D_{a:04x}')
    for a in sorted(ins):
        n,s=ins[a];out.append(f'D_{a:04x}: ; original ${a:04X}: {s}')
        if a in pairs:out.append(' '+pairs[a]);continue
        op=s.split()[0]
        if op in ['bcc','bcs','beq','bne','bmi','bpl','bvc','bvs']:
            out.append(' j'+op[1:]+f' D_{int(s.split("$")[1],16):04x}');continue
        if op in ['jsr','jmp']:
            target=int(s.split('$')[1],16)
            out.append(f' {op} '+('D_'if target in ins else'DImport_')+f'{target:04x}');continue
        indirect=re.fullmatch(r'(lda|sta) \(\$([0-9a-f]{2})\),y',s)
        if indirect:
            ptr=int(indirect[2],16);tag=f'DIndirect_{a:04x}'
            # Original RAM pointer high0..7 maps to private C0..C7; code/data
            # pointer highs remain literal. Only declared OAM/table domains.
            out.extend([' php',' pha',f' lda ${0xc000+ptr:04x}',f' sta {tag}+1',
                        f' lda ${0xc001+ptr:04x}',' cmp #8',f' bcs {tag}_rom',
                        ' ora #$c0',f'{tag}_rom:',f' sta {tag}+2',' pla',' plp',
                        f'{tag}: {indirect[1]} $ffff,y'])
            continue
        def remap(match):
            v=int(match[1],16)
            if v<0x800:return f'${v+0xc000:04x}'
            if DATA_LO<=v<DATA_HI:return f'DData_{v:04x}'
            raise AssertionError((hex(a),s,hex(v)))
        if '#'not in s:s=re.sub(r'\$([0-9a-f]+)',remap,s)
        out.append(' '+s)
        if a+n==0xcabf:out.append(' rts ; typed return before original stage art/UI initialization')
    for a in sorted(imports):
        out.extend([f'.export DImport_{a:04x}',f'DImport_{a:04x}: jmp DImport_{a:04x} ; closed local trap until typed host binding'])
    out.append('.export DkjrSourceData')
    pointerbytes={p for a in [range(0xc309,0xc311,2),range(0xc369,0xc379,2)]for p in a}
    a=DATA_LO
    while a<DATA_HI:
        out.append(f'DData_{a:04x}:')
        if a==DATA_LO:out.append('DkjrSourceData:')
        if a in pointerbytes:
            p=m[a]+256*m[a+1];assert DATA_LO<=p<DATA_HI,hex(p)
            out.append(f' .word DData_{p:04x}');out.append(f'DData_{a+1:04x}=DData_{a:04x}+1');a+=2
        else:out.append(f' .byte ${m[a]:02x}');a+=1
    out.append('DkjrComponentEnd:\n.export DkjrComponentEnd')
    source='\n'.join(out)+'\n';(O/'component.s').write_text(source)
    (O/'component.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}\nSEGMENTS{DKJR:load=C,type=rw;}\n')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],
                [cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'component.bin','-Ln',O/'component.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert not p.returncode,p.stderr
    blob=(O/'component.bin').read_bytes()
    labels={name:int(a,16)for a,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)}
    # Internal labels are needed by the instruction differential, not exports.
    p=subprocess.run(list(map(str,[cc/'ca65.exe',O/'component.s','-g','-o',O/'component.o'])),capture_output=True,text=True);assert not p.returncode,p.stderr
    p=subprocess.run(list(map(str,[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'component.bin','-Ln',O/'component.lbl'])),capture_output=True,text=True);assert not p.returncode,p.stderr
    labels={name:int(a,16)for a,name in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)}
    q=dict(donor_sha256=D.SHA,original_ranges=RANGES,original_instruction_bytes=sum(b-a for a,b in RANGES),
           original_instructions=len(ins),component_bytes=len(blob),private_state_bytes=2048,
           measurement_code_origin=0xa000,measurement_state_origin=0xc000,
           exports={k:labels['Dkjr'+k]for k in EXPORTS},imports={f'{a:04X}':labels[f'DImport_{a:04x}']for a in sorted(imports)},
           original_data_half_open=[DATA_LO,DATA_HI],data_address=labels['DkjrSourceData'],
           code_sha256=hashlib.sha256(blob).hexdigest(),host_allocation=False,menu_admission=False,
           scope='Original actor/animation/fruit instructions with private RAM relocation and explicit stage/service imports. No host/native claim.')
    (O/'component-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
