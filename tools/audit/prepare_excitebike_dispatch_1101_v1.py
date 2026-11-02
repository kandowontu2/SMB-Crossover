"""Lease source-declared Proto padding and add a fail-closed raw37 transport.

The 37 private services reject until owning host adapters exist. This is neither
native gameplay nor menu admission. Does not launch Mesen or install the ROM.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_hogan_current_bounded_v1 as M
import compose_excitebike_owner_1101_v1 as C
O=R/'build/excitebike-pose-1101-v3'
BASE=R/'build/shinobi-camera-1101-v20/candidate.nes'
PIN='fe4e9a6d5aef0c2e3848a501f487e7791cd75b9db5cf5297ebad395162560ad9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def labels(p):return {n:int(a,16)for a,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',p.read_text(),re.M)}
def save(name,q):(O/name).write_text(json.dumps(q,indent=2)+'\n')

def lease():
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    metal=R/'build/metal-storm-idle-shots-1101-v41/candidate.nes'
    current=R/'build/shinobi-bbox-candidate-1101-v30/candidate.nes'
    assert installed.read_bytes()==current.read_bytes(),'Installed nightly changed; review lease against its current candidate'
    assert sha(current)=='6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428'
    assert sha(BASE)==PIN
    source=(R/'src/protoman.s').read_text()
    assert '.res $1108-(*-ProtoArtBegin), $ff' in source
    art=(R/'src/protoman_art.inc').read_text()
    allrows=[];bindings={}
    for rom in [BASE,metal,current]:
        b=scoped_load(rom);raw=b['raw'];origin=location(b,'ProtoArtBegin')
        assert origin==16+65*8192 and address(b,'ProtoArtBegin')==0xc000
        assert address(b,'ProtoArtEnd')==0xc738
        tail=raw[origin+0x740:origin+0x800]
        assert tail==bytes([255])*192
        named=[]
        for name,sym in b['syms'].items():
            if sym.get('seg')!=b['syms']['ProtoArtBegin'].get('seg'):continue
            try:at=location(b,name)
            except (KeyError,AssertionError,ValueError,TypeError):continue
            if origin+0x740<=at<origin+0x800:named.append(name)
        assert not named,named
        rows=[]
        for facing in ['Left','Right']:
            lo=location(b,'ProtoPose'+facing+'Lo');hi=location(b,'ProtoPose'+facing+'Hi')
            names=re.search(r'ProtoPose'+facing+r'Lo:\s*\.byte ([^\n]+)',art)[1].split(',')
            assert len(names)==27
            for i,name in enumerate(names):
                name=name.strip().lstrip('<');pc=raw[lo+i]+256*raw[hi+i]
                assert pc==address(b,name) and 0xc000<=pc<0xc696
                at=origin+pc-0xc000;length=1+raw[at]
                assert raw[at]%4==0 and pc+length<=0xc696
                rows.append(dict(facing=facing,index=i,target=pc,bytes=length))
        allrows.append(dict(ROM=rom.relative_to(R).as_posix(),ROM_SHA256=sha(rom),
                            descriptor_rows=len(rows),last_descriptor_end=max(z['target']+z['bytes']for z in rows),
                            art_end=0xc738,lease_symbols=named,lease_all_FF=True))
        bindings[rom.relative_to(R).as_posix()]=sha(rom)
    # All declared immutable table readers are in these two source components.
    # The selector clamps its initial render index to 0..15 and uses enumerated
    # constants/carry walk indices ending at26 before ProtoSetPose reads tables.
    readers=[]
    for p in (R/'src').rglob('*'):
        if p.suffix not in ['.s','.inc']:continue
        text=p.read_text(errors='replace')
        if re.search(r'\blda ProtoPose(?:Left|Right|Chr)(?:Lo|Hi),x',text,re.I):readers.append(p.relative_to(R).as_posix())
    assert readers==['src/protoman_cold.s'],readers
    ids=(R/'src/protoman_pose_ids.inc').read_text()
    assert 'PROTO_POSE_CARRY_JUMP = 26' in ids or re.search(r'PROTO_POSE_CARRY_JUMP\s*=\s*26',ids)
    for p in [R/'src/protoman.s',R/'src/protoman_art.inc',R/'src/protoman_cold.s',R/'src/protoman_pose_ids.inc']:
        bindings[p.relative_to(R).as_posix()]=sha(p)
    q=dict(passed=True,bank=65,A_CPU_half_open=[0xa740,0xa800],C_CPU_half_open=[0xc740,0xc800],
           physical_half_open=[0x740,0x800],bytes=192,rows=allrows,
           typed_descriptor_rows=162,table_reader_sources=readers,source_declared_padding=True,
           scope='All54 immutable Proto pose descriptors in each linked image, complete table end and symbol exclusion; current installed6f319 equals its candidate. Source-valid pose selector indices only.',
           bindings=bindings)
    save('dispatch-lease.json',q)
    return q

def main():
    l=lease();C.main()
    assert sha(O/'candidate.nes')==json.loads((O/'composition.json').read_text())['ROM_SHA256']
    base_loader=(O/'owner-loader.bin').read_bytes();assert len(base_loader)<=652
    source=(O/'owner-loader.s').read_text()
    b=scoped_load(BASE)
    for alias,n in [('ExOriginalColors','NrColors'),('ExOriginalStatus','RlNameDispatch')]:
        source+=f'\n{alias}=${address(b,n):04x}\n{alias}Bank=${((location(b,n)-16)//8192)|128:02x}\n'
    source+='\nExCacheServices=$a500\n.include "excitebike_resident_dispatch_1101_v1.inc"\n'
    (O/'dispatch.s').write_text(source)
    cfg='MEMORY{L:start=$ae00,size=$233,file="'+(O/'dispatch-loader.bin').as_posix()+'";D:start=$a740,size=$a9,file="'+(O/'dispatch-body.bin').as_posix()+'";V:start=$b08c,size=$6f,file="'+(O/'dispatch-veneers.bin').as_posix()+'";F:start=$b031,size=49,file="'+(O/'dispatch-foreign.bin').as_posix()+'";FB:start=$b105,size=2,file="'+(O/'dispatch-foreign-bank.bin').as_posix()+'";}\nSEGMENTS{EXCITEBIKE_RESIDENT:load=L,type=ro;EX_DISPATCH:load=D,type=ro;EX_VENEERS:load=V,type=ro;EX_FOREIGN_UI:load=F,type=ro;EX_FOREIGN_BANK:load=FB,type=ro;}'
    (O/'dispatch.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe','-I',R/'tools/reference','-I',O,'--bin-include-dir',O,O/'dispatch.s','-o',O/'dispatch.o'],
                [cc/'ld65.exe','-C',O/'dispatch.cfg',O/'dispatch.o','-o',O/'dispatch-unused.bin','-Ln',O/'dispatch.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    assert (O/'dispatch-loader.bin').read_bytes()==base_loader
    body=(O/'dispatch-body.bin').read_bytes();veneers=(O/'dispatch-veneers.bin').read_bytes()
    assert len(body)<=192 and len(veneers)==111
    raw=bytearray((O/'candidate.nes').read_bytes())
    for off,data in [(0x740,body),(0x108c,veneers),(0x1031,(O/'dispatch-foreign.bin').read_bytes()),(0x1105,(O/'dispatch-foreign-bank.bin').read_bytes())]:
        at=16+65*8192+off;assert raw[at:at+len(data)]==bytes([255])*len(data)
        raw[at:at+len(data)]=data
    # A complete private vector explicitly rejects every service. No source
    # routine is callable under a host ABI before its adapter has been built.
    kernel=bytearray((O/'owner-actor.bin').read_bytes())
    assert not any(kernel[0x500:0x571])
    kernel[0x500:0x56f]=bytes([0x4c,0x6f,0xa5])*37
    kernel[0x56f:0x571]=bytes([0x18,0x60])
    (O/'dispatch-kernel.bin').write_bytes(kernel)
    for i,page in enumerate(range(728,734)):
        at=1048592+page*1024;raw[at:at+1024]=kernel[i*1024:i*1024+1024]
    metadata=(O/'owner-metadata.bin').read_bytes();art=(O/'body-native.chr').read_bytes()
    oldcookie=(O/'excitebike-cookie.bin').read_bytes();cookie=bytes([167,37,1])+hashlib.sha256(kernel+metadata+art).digest()[:13]
    lab=labels(O/'dispatch.lbl');at=16+65*8192+lab['ExCookie']-0xa000
    assert raw[at:at+16]==oldcookie;raw[at:at+16]=cookie
    (O/'dispatch-cookie.bin').write_bytes(cookie);(O/'candidate.nes').write_bytes(raw)
    q=dict(passed=True,ROM_SHA256=sha(O/'candidate.nes'),baseline_ROM_SHA256=PIN,
           resident_loader_bytes=len(base_loader),dispatch_body_bytes=len(body),veneer_bytes=len(veneers),
           dispatch_body_remaining=192-len(body),resident_tail_remaining=124-len(veneers),
           code_vector=0xa500,service_rows=37,implemented_gameplay_rows=[],all_rows_explicitly_reject=True,
           pending_menu_locked=True,native=False,installed=False,
           scope='Complete exact-cookie authenticated37-row ROM transport. No shared gameplay routing or native owning adapters yet.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc',O/'dispatch-lease.json',O/'dispatch-body.bin',O/'dispatch-veneers.bin',O/'dispatch-kernel.bin',O/'dispatch-cookie.bin']})
    save('dispatch-assembly.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))

if __name__=='__main__':main()

