"""Use source-explicit relocated-water padding for Metal menu lifecycle."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_menu_pending_1101_v14 as V
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
P=V.O;O=R/'build/metal-storm-menu-1101-v15';sha=V.sha
REF=R/'tools/reference/metal_storm_menu_1101_v15.inc'
SOURCE=R/'build/karnov-host-resource-base-1101-v1/megaman_physics.s'
def main():
    prior=json.loads((P/'menu-assembly.json').read_text());assert sha(P/'candidate.nes')==prior['ROM_sha256']
    b=qualified(P/'candidate.nes');raw=bytearray(b['raw']);O.mkdir(exist_ok=True)
    source=SOURCE.read_text();assert '.res $72,$ff' in source and '.res $1f,$ff' in source
    assert address(b,'KrServiceVeneers')==0xb400 and address(b,'KrMarioWaterProductHi')==0xbb8e
    table=location(b,'KrMarioWaterProductHi');assert raw[table:table+256]==bytes((i*62344)>>16 for i in range(256))
    for off,size in [(0x138e,114),(0x146f,31)]:assert raw[16+29*8192+off:16+29*8192+off+size]==b'\xff'*size
    labelpath=R/'build/metal-storm-native-integration-1101-v12/native-component.lbl'
    labels={m[2]:int(m[1],16) for line in labelpath.read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    names=['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','KrMenuResolve','CrossoverMenuIndex','FmAlts','SelectedCharacter','FmStartRetireFlags']
    text=''.join(f'{n}=${address(b,n):04x}\n' for n in names)
    text+=''.join(f'{n}=${labels[n]:04x}\n' for n in ['Ms8Auth','Ms12RetireHeaders'])+REF.read_text()
    (O/'menu.s').write_text(text)
    cfg='MEMORY { A:start=$b38e,size=114,file="'+(O/'resolve.bin').as_posix()+'"; B:start=$b46f,size=31,file="'+(O/'start.bin').as_posix()+'"; } SEGMENTS { RESOLVE:load=A,type=ro; START:load=B,type=ro; }'
    (O/'menu.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'menu.s','-o',O/'menu.o'],[cc/'ld65.exe','-C',O/'menu.cfg',O/'menu.o','-o',O/'unused.bin','-Ln',O/'menu.lbl']]:
        cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
    patches=[]
    def patch(at,old,new,role):
        assert len(old)==len(new) and raw[at:at+len(old)]==old,role
        patches.append(dict(role=role,offset=at,old=old.hex(),new=new.hex()));raw[at:at+len(old)]=new
    for name,off,cap in [('resolve',0x138e,114),('start',0x146f,31)]:
        data=(O/(name+'.bin')).read_bytes();assert len(data)<=cap
        patch(16+29*8192+off,b'\xff'*len(data),data,name)
    # The public bank29 Start entry remains at its established address.
    at=location(b,'KrStartFlags');patch(at,bytes(raw[at:at+23]),bytes([0x4c,0x6f,0xb4])+bytes([0xea])*20,'KrStartFlags trampoline')
    # Existing Tank retirement still runs first; replace only its tail target.
    at=16+66*8192+(0xb957-0xa000)+18
    target=address(b,'KrMenuResolve');old=bytes(raw[at:at+18])
    assert old[4]==target&255 and old[9]==target>>8 and old[14]==157 and old[15]==0x4c
    new=bytearray(old);new[4]=0x8e;new[9]=0xb3
    patch(at,old,new,'Tank-retire then Metal/Karnov resolve chain')
    at=location(b,'FmResolve');old=bytes([0x20,address(b,'FmPending')&255,address(b,'FmPending')>>8])
    hp=prior['helper_PC'];patch(at,old,bytes([0x20,hp&255,hp>>8]),'Playable resolver predicate')
    at=location(b,'CrossoverMenuInput::CheckConfirm');pattern=bytes([0xa9,address(b,'FmPending')&255,0x8d,0x6c,1,0xa9,address(b,'FmPending')>>8])
    i=bytes(raw).find(pattern,at,at+40);assert i>=at
    new=bytearray(pattern);new[1]=hp&255;new[6]=hp>>8;patch(i,pattern,new,'Start predicate only; cold portrait check unchanged')
    # Name-marker removal is deferred until the native menu image is inspected.
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P/('candidate'+suffix)).read_bytes())
    q=dict(passed=True,installed=False,menu_admitted=True,native_tested=False,ROM_sha256=sha(O/'candidate.nes'),base_ROM_sha256=sha(P/'candidate.nes'),
           labels=dict(Ms15Resolve=0xb38e,Ms15StartFlags=0xb46f),patches=patches,
           allocation=dict(bank=29,source=str(SOURCE),source_sha256=sha(SOURCE),ranges=[[0x138e,0x1400],[0x146f,0x148e]],relocated_water_table_verified=True),
           limitations='Private menu admission only. Native gameplay, health/combat/audio and complete main interrupt paths unverified.',
           bindings={str(p):sha(p) for p in [Path(__file__),REF,SOURCE,P/'candidate.nes',O/'menu.s',O/'candidate.nes']})
    (O/'menu-assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k not in ['patches','bindings']}))
if __name__=='__main__':main()
