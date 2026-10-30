"""Private source scheduler successor. Requires an explicit alias receipt.

Never run using an unrelated reservation: source receipt must approve exact
Turn/Last/Packet/Pending reuse before this script can install those references.
All output-producing commands are inspected by the shared private-output guard.
"""
from pathlib import Path
import argparse,difflib,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/ff-fx-world-marker-proposal-v2'
S=R/'build/ff-fx-epoch-workers-sizing-v3'
O=R/'build/ff-fx-epoch-cart-v1'
RETIRED=['FwActionTick','FwWeapons','FwEnemyContact','FwForgetEnemy']

def run(d,cmd,phase):
    B.save(d/(phase+'-validated-outputs.json'),validate(cmd,O,cwd=R))
    B.run(d,cmd,phase)

def assemble(d,name,phase=None):
    cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','-I',str(d),'-I',str(R/'src'),
        '--bin-include-dir',str(d),'--bin-include-dir',str(R),'--create-full-dep',str(d/(name+'.dep')),
        '-o',str(d/(name+'.o')),str(d/(name+'.s'))]
    run(d,cmd,phase or name+'-build')

def replace_once(source,a,z):
    assert source.count(a)==1,a
    return source.replace(a,z)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--alias-receipt',type=Path,required=True)
    parser.add_argument('--alias-receipt-sha256',required=True);args=parser.parse_args()
    assert not O.exists()
    receipt=args.alias_receipt.resolve();assert B.sha(receipt)==args.alias_receipt_sha256
    approval=json.loads(receipt.read_text())
    assert approval.get('exact_FF_epoch_aliases_approved')is True,'Explicit exact alias approval required'
    assert approval.get('alias_proposal_sha256')=='28df95b2c1d1328ef3bce86532f348cc01c67a84e8a4edb19caed64ba445a0e6'
    files=B.validate(P/'handoff.json','ea94867c9b3c808ea6124560be6330970dad9ac79d000d5b7f826856fffa83e3')
    sizes=json.loads((S/'sizing.json').read_text())
    for f,h in sizes['bindings'].items():assert B.sha(f)==h,f
    files|={receipt,S/'sizing.json',Path(__file__),R/'tools/audit/private_build_outputs_v1.py'}
    O.mkdir();d=O/'joint';d.mkdir();patch=[]
    for f in(P/'joint').rglob('*'):
        if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
    p=d/'loader.s';old=p.read_text()
    gates='\n'.join('FW_GATE '+n+','+t for n,t in zip(RETIRED,['FfActionTick','FfWeapons','FfEnemyContact','FfForgetEnemy']))
    rom=(S/'rom.s').read_text().replace('.segment "FF_MUX_ROM_PROPOSAL"','.segment "FF_ROM_HOST"')
    rom+='\n .res 104-(*-FfMuxNativeROM),$ea\n .assert *-FfMuxNativeROM=104,error,"Explicit retired104B owner span"\n'
    B.write(d/'ff-epoch-rom.inc',rom)
    new=replace_once(old,gates,'.include "ff-epoch-rom.inc"')
    B.write(p,new);patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/loader.s',tofile='new/loader.s'))
    p=d/'ff-palette.s';old=p.read_text()
    a='''Native:
 sta SafecallA_SMC+1
 lda #<DrawAllMetasprites
 sta FarcallJmpTarget_SMC+1
 lda #>DrawAllMetasprites
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawAllMetasprites)|$80)
 jmp FarCallCommon'''
    new='.import FfMuxNativeROM\n'+replace_once(old,a,'Native:\n jmp FfMuxNativeROM\n .res 15,$ea')
    B.write(p,new);patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/ff-palette.s',tofile='new/ff-palette.s'))
    p=d/'veneers.s';old=p.read_text()
    new='.import FfMuxTickROM\n'+replace_once(old,'; 29 UI cached_body_palette_tick\n jmp FwPaletteTick','; 29 UI original_body_tick_then_verified_FX_heartbeat\n jmp FfMuxTickROM')
    B.write(p,new);patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/veneers.s',tofile='new/veneers.s'))
    (d/'ff-epoch-workers.s').write_bytes((S/'workers.s').read_bytes())
    p=d/'entrypoint.s';B.write(p,p.read_text()+'\n.export RgOamPlayerStart,RgOamUsed,Sprite_Tilenumber\n')
    p=d/'private.cfg';cfg=p.read_text().replace((P/'joint').as_posix(),d.as_posix())
    # Every original owner of FF_RAM3_MEM has an explicit fixed start. Insert
    # only between those fixed FF owners in ascending address order. Appending
    # an A289 start after the existing BECF tail would make ld65 backtrack.
    # No automatic native/other-family segment or MEMORY order changes.
    additions={
        'FF_RAM_PUBLISHER:load=FF_RAM3_MEM,type=ro,start=$a275;':'FF_EPOCH_CLASSIFY:load=FF_RAM3_MEM,type=ro,start=$a289;',
        'FF_HOST_RENDER:load=FF_RAM3_MEM,type=ro,start=$a300;':'FF_EPOCH_COLORS:load=FF_RAM3_MEM,type=ro,start=$a6e5;',
        'FINAL_FANTASY_CORE:load=FF_RAM3_MEM,type=ro,start=$aa00;':'FF_EPOCH_PACKET:load=FF_RAM3_MEM,type=ro,start=$b68b;',
        'FF_FX_DATA3:load=FF_RAM3_MEM,type=ro,start=$bcef;':
            'FF_EPOCH_MAIN:load=FF_RAM3_MEM,type=ro,start=$becf;\nFF_EPOCH_HEARTBEAT:load=FF_RAM3_MEM,type=ro,start=$bf9f;\nFF_EPOCH_TABLES:load=FF_RAM3_MEM,type=ro,start=$bff0;',
    }
    for anchor,addition in additions.items():cfg=replace_once(cfg,anchor,anchor+'\n'+addition)
    B.write(p,cfg)
    cmd=json.loads((P/'joint/main-build.json').read_text())['command']
    run(d,[v.replace(str(P/'joint'),str(d))for v in cmd],'main-build')
    for name in ['loader','veneers','ff-palette','ff-epoch-workers']:assemble(d,name)
    cmd=json.loads((P/'joint/final-link.json').read_text())['command']
    original_objects={}
    for v in cmd:
        if v.endswith('.o')and Path(v).name in['main.o','loader.o','veneers.o','ff-palette.o','stream.o']:
            name=Path(v).stem;assert name not in original_objects;original_objects[name]=v
    assert len(original_objects)==5
    cmd=[v.replace(str(P/'joint/candidate'),str(d/'candidate')).replace(str(P/'joint/private.cfg'),str(d/'private.cfg'))for v in cmd]
    cmd=[str(d/(name+'.o'))if (name:=next((n for n,p in original_objects.items()if p==v),None))else v for v in cmd]
    cmd.append(str(d/'ff-epoch-workers.o'))
    # Original stream is copied source, not an executable binary overlay.
    assemble(d,'stream');run(d,cmd,'layout-link')
    image=(d/'ram3.bin').read_bytes();prior=(P/'joint/ram3.bin').read_bytes();assert len(image)==8192
    spans=[(0xa289,0xa289+74),(0xa6e5,0xa700),(0xb68b,0xb68b+107),(0xbecf,0xbecf+208),
        (0xbf9f,0xbf9f+49),(0xbff0,0xbfff)]
    changes=[i+0xa000 for i,(a,z)in enumerate(zip(prior,image))if a!=z]
    assert all(any(a<=i<z for a,z in spans)for i in changes)
    assert all(set(prior[a-0xa000:z-0xa000])=={255}for a,z in spans)
    (d/'ff-stream.bin').write_bytes(image)
    cookie=bytes([167,22,0,7])+hashlib.sha256(image).digest()[:12]
    (d/'ff-cookie.bin').write_bytes(cookie)
    assemble(d,'loader','loader-authenticated-build');assemble(d,'stream','stream-authenticated-build')
    run(d,cmd,'final-link');prepare(R,d/'candidate.nes');assert(d/'ram3.bin').read_bytes()==image
    old=qualified(P/'joint/candidate.nes');new=qualified(d/'candidate.nes')
    for n in RETIRED:assert n not in new['syms']
    moved={n:[address(old,n),address(new,n)]for n,v in old['syms'].items()if 'seg'in v and n not in RETIRED and address(old,n)!=address(new,n)}
    assert not moved,moved
    assert address(new,'FfMuxNativeROM')==0xadde and address(new,'FwProjectileEntry')==0xae46
    for n,a in [('FfMuxClassify',0xa289),('FfMuxColors',0xa6e5),('FfMuxPacket',0xb68b),
                ('FfMuxNativeLate',0xbecf),('FfMuxHeartbeat',0xbf9f)]:assert address(new,n)==a
    cs=1048592
    ranges=[(location(old,'FwActionTick'),location(old,'FwProjectileEntry'),'explicit_retired_unused104B'),
        (location(old,'FwNativeDrawAll::Native'),location(old,'FwNativeDrawAllEnd'),'existing18Bnative_tail'),
        (location(old,'FwServiceVeneers')+29*3,location(old,'FwServiceVeneers')+30*3,'own_row29_only'),
        (location(old,'FwCookie'),location(old,'FwCookie')+16,'own_fullcookie_v7'),
        (cs+893*1024,cs+901*1024,'own_existing8KBcarrier')]
    diff=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    assert all(any(a<=i<z for a,z,n in ranges)for i in diff)
    B.write(O/'source.patch',''.join(patch))
    files|={Path(v)for v in cmd if v.endswith('.o')}|{f for f in O.rglob('*')if f.is_file()}
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,actual_source_cart=True,
        candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),
        RAM3_sha256=B.sha(d/'ram3.bin'),cookie=list(cookie),alias_receipt=str(receipt),explicit_own_ABI_retired=RETIRED,
        all_other_public_and_source_PCs_exact=True,source_occupied_CORE_ART_code_CHR_bytes_exact=True,
        RAM3_new_spans=spans,ROM_allowed_ranges=ranges,changed_ROM_bytes=len(diff),changed_RAM3_bytes=len(changes),
        ROM_new_bytes=98,RAM3_new_bytes=480,C93_lifecycle_marker_exact_8B_remaining=True,
        limits=['Source build only: actual OAM/pixel/heartbeat/queue/fullMain/foreign/ISR/loader controls not run.',
            'Source iterator timing/OAM and hardware8sprite/performance/campaign/admission remain separate.'],
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)}))
    print(json.dumps(dict(passed=True,ROM=B.sha(d/'candidate.nes'),RAM3=B.sha(d/'ram3.bin'),cookie=list(cookie))),flush=True)

if __name__=='__main__':main()
