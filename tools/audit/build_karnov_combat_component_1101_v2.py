"""Assemble only Karnov contacts in existing authenticated-owner padding."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
P=R/'build/karnov-host-resource-base-1101-v1';O=R/'build/karnov-combat-component-1101-v2'
SRC=R/'tools/reference/karnov_combat_1101_v2.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    stage=json.loads((P/'terrain-assembly.json').read_text());assert stage['passed']and stage['menu']
    assert sha(P/'candidate.nes')==stage['ROM_sha256']
    b=scoped_load(P/'candidate.nes');text=SRC.read_text();banks={}
    for n in re.findall(r'\.import ([^\n]+)',text):
        for name in n.split(','):
            name=name.strip()
            if name.startswith('KC_')and name.endswith('_BANK'):
                target=name[3:-5];banks[name]=((location(b,target)-16)//8192)|128
    assert address(b,'MTILE_SOLID')==1 and address(b,'Sfx_Bump')==2 and address(b,'Goomba')==6 and address(b,'Bowser')==45
    symbols={};types={}
    for kind,groups in re.findall(r'\.(importzp|import) ([^\n]+)',text):
        for name in groups.split(','):
            name=name.strip();symbols[name]=banks[name]if name in banks else address(b,name);types[name]=kind
    binding=['.setcpu "6502"\n']
    for n,v in symbols.items():binding.append(('.exportzp 'if types[n]=='importzp'else'.export ')+n+f'\n{n}=${v:04x}\n')
    (O/'bindings.s').write_text(''.join(binding));(O/'component.s').write_text('.setcpu "6502"\n.macpack longbranch\n.include "karnov_combat_1101_v2.inc"\n')
    kernel=address(b,'KrKernelEnd');resident=0xc900;klimit=0xbfe0;rlimit=0xd000
    assert kernel<klimit
    # Proposed private selected-C2 code lease. This output supplies assembly
    # and CPU proof only. There is deliberately no ROM patch, loader or claim
    # that a carrier exists. Root must fund/copy/verify this before publishing
    # the selected C2 cookie; C900 is beyond original2KB source state and
    # contexts, below copied D000 metasprites and DFE0 cookie.
    image=(P/'kr-kernel.bin').read_bytes();assert image[kernel-0xa000:klimit-0xa000]==bytes([255])*(klimit-kernel)
    cfg=f'''MEMORY {{
 CORE:start=${kernel:04x},size=${klimit-kernel:04x},bank=3,file="{(O/'kernel.bin').as_posix()}";
 ROM:start=${resident:04x},size=${rlimit-resident:04x},bank=2,file="{(O/'resident.bin').as_posix()}";
}}
SEGMENTS {{KR_COMBAT_KERNEL:load=CORE,type=ro;KR_COMBAT_ROM:load=ROM,type=ro;}}
'''
    (O/'component.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin';logs=[]
    commands=[[cc/'ca65.exe','-g','-I',SRC.parent,O/'component.s','-o',O/'component.o'],[cc/'ca65.exe','-g',O/'bindings.s','-o',O/'bindings.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o',O/'bindings.o','-o',O/'unused.bin','-Ln',O/'component.lbl','--dbgfile',O/'component.dbg']]
    for cmd in commands:
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);logs.append(dict(command=cmd,guard=guard,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));save(O/'build-commands.json',logs);assert q.returncode==0,q.stderr
    kr=(O/'kernel.bin').read_bytes();rr=(O/'resident.bin').read_bytes()
    raw=ROM.read_bytes();assert sha(ROM)==EXPECTED
    # Authenticated original status transition: normal hits use C0|18;
    # the immediately preceding CMP08/BEQ bypass keeps boomerang motion live.
    original_impact=bytes.fromhex('c908f008b56e29c00918956e')
    assert raw[16+11*8192+0xfc4:16+11*8192+0xfd1].find(original_impact)>=0 or original_impact in raw[16:16+131072]
    paths=[Path(__file__).resolve(),SRC,P/'candidate.nes',P/'candidate.dbg',P/'candidate.cfg',P/'terrain-assembly.json',P/'kr-kernel.bin',ROM,O/'component.s',O/'bindings.s',O/'component.cfg',O/'kernel.bin',O/'resident.bin',O/'component.lbl',O/'component.dbg',O/'build-commands.json']
    save(O/'assembly-stage.json',dict(passed=True,parent_ROM_sha256=sha(P/'candidate.nes'),source_CPU_only=True,native=False,installed=False,root_build_modified=False,kernel_lease=[kernel,klimit],kernel_bytes=len(kr),proposed_C2_code_lease=[resident,rlimit],resident_bytes=len(rr),context_C2=[0xc840,0xc860],carrier_funded=False,loader_implemented=False,original_impact_encoding=original_impact.hex(),native_imports=symbols,limits=['Independent component only; root must fund a carrier, copy/verify before publishing C2 cookie and alias genuine services4/34. CPU fixtures explicitly inject the proposed C2 code.','Contact pass follows original actor/weapons once per accepted epoch. It never changes source projectile velocities or advances the source clock.','Center-point cell query and8x8 native enemy box are explicit SMB host collision adaptations.','Boomerang damages each canonical native enemy slot once per throw; a reused enemy slot during the same throw remains masked.','No native controller, raster/audio playback, full level, health or item progression qualification.'],bindings={str(p.resolve()):sha(p)for p in paths}))
    print(json.dumps(dict(passed=True,kernel_bytes=len(kr),kernel_available=klimit-kernel,resident_bytes=len(rr),resident_available=rlimit-resident,parent=sha(P/'candidate.nes'))))

if __name__=='__main__':main()
