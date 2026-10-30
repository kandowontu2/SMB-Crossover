"""Real enemy identity/flash hooks in existing FF and native source spans."""
from pathlib import Path
import difflib,hashlib,json,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare

P=R/'build/ff-joint-terrain-hooks-1030-v3'
O=R/'build/ff-joint-combat-hooks-1030-v2'
H=R/'build/ff-joint-terrain-hooks-qualified-1030-v1/handoff.json'


def rep(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)


def main():
    assert not O.exists()
    files=B.validate(H,'083d29e895c386bdf172274d35c25cc419c852ccdffcd4c4e626e36d6642ef65')
    O.mkdir();d=O/'joint';d.mkdir();changed=[]
    for p in(P/'joint').rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg','.bin','.chr']:
            q=d/p.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def edit(rel,fn):
        p=d/rel;old=p.read_text();new=fn(old);assert old!=new;B.write(p,new);changed.append(rel)
    old=(d/'src/object.s').read_text()
    prefix=old.split('CheckpointEnemyID:\n.if ::ENABLE_CROSSOVER\n',1)[1].split('.endif',1)[0]
    assert prefix.startswith('  lda #0\n')and prefix.endswith('  sta GuestBodyNow\n')
    # Native41B clear prefix is retained verbatim in an actual typed ROM62
    # worker. Every native spawn still executes it before the identity hook.
    edit('src/object.s',lambda s:rep(s,prefix,'''  farcall FwNativeEnemyInit
  jmp :+
  .res 20,$ea
:
'''))
    worker=prefix.replace('GuestContactClearBits','FwEnemyClearBits')
    worker='''
.export FwNativeEnemyInit
.import FwHostNewEnemy
.import MmEnemyHealthLo,MmEnemyHealthHi,MmEnemyFlash,RgEnemyStun,LsrFrozenPose
.import AvFrozen,AvFrozenHi,GuestBodyPrev,GuestBodyNow
FwNativeEnemyInit:
'''+worker+''' php
 jsr FwCheck
 bcc NoFF
 plp
 jmp FwHostNewEnemy
NoFF:plp
 rts
FwEnemyClearBits:.byte $fe,$fd,$fb,$f7,$ef,$df
'''
    edit('typed-services.s',lambda s:rep(s,'FwSvcEnd:',worker+'FwSvcEnd:'))
    edit('entrypoint.s',lambda s:'.import FwNativeEnemyInit\n.export RgEnemyStun,LsrFrozenPose,AvFrozen,AvFrozenHi,GuestBodyPrev,GuestBodyNow\n'+s)
    edit('combat.s',lambda s:rep(s,' jsr FfWeapons\n ldx #5\nFfHostActorLoop:', ''' ; Existing native flash counter ages once per accepted logical weapon tick.
 ldx #5
FfHostFlashTick:
 lda MmEnemyFlash,x
 beq :+
 dec MmEnemyFlash,x
:dex
 bpl FfHostFlashTick
 jsr FfWeapons
 ldx #5
FfHostActorLoop:'''))
    edit('private.cfg',lambda s:rep(s,(P/'joint/ram3.bin').as_posix(),(d/'ram3.bin').as_posix()))
    before,after=str(P/'joint'),str(d)
    for phase in sorted((P/'joint').glob('*-build.json')):
        B.run(d,[v.replace(before,after)for v in json.loads(phase.read_text())['command']],phase.stem)
    cmd=[v.replace(before,after)for v in json.loads((P/'joint/final-link.json').read_text())['command']]
    B.run(d,cmd,'payload-link')
    image=(d/'ram3.bin').read_bytes();cookie=bytes([167,22,0,5])+hashlib.sha256(image).digest()[:12]
    (d/'ff-stream.bin').write_bytes(image);(d/'ff-cookie.bin').write_bytes(cookie)
    for n in['stream','loader']:
        B.run(d,[v.replace(before,after)for v in json.loads((P/'joint'/(n+'-build.json')).read_text())['command']],n+'-build')
    B.run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    new=qualified(d/'candidate.nes');old=qualified(P/'joint/candidate.nes')
    assert(d/'ram3.bin').read_bytes()==image
    assert new['raw'][1048592+893*1024:1048592+901*1024]==image
    assert address(new,'FwSvcEnd')<=0xb690
    assert address(new,'FfHostCombatEnd')<=0xb900
    allowed=[]
    p=location(old,'CheckpointEnemyID');allowed.append((p,p+41,'original41B_clear_prefix'))
    p=location(old,'DrawBrickDebris::Part');allowed.append((p,p+90,'original90B_debris_helpers'))
    p=location(old,'FwSvcEnd');allowed.append((p,16+62*8192+0x1690,'own_FF_typed_tail'))
    allowed.append((16+62*8192+0xa00,16+62*8192+0x131c,'own_FF_ROM_gate_operands_cookie'))
    allowed.append((1048592+893*1024,1048592+901*1024,'existing_FF_RAM3_carrier'))
    # This genuine shared near JMP is the sole caller of the moved private
    # debris-helper tail; other bodies/positions keep their original PCs.
    p=location(old,'RlNativeRenderDispatch')
    # No unconditional exemption: find actual native JMP operands to the old
    # HuMaaRenderLegacy, require new target and unchanged adjacent opcode.
    oldpc=address(old,'HuMaaRenderLegacy');newpc=address(new,'HuMaaRenderLegacy')
    instruction=bytes([0x4c,oldpc&255,oldpc>>8])
    found=[]
    for i in range(16,1048592-2):
        if old['raw'][i:i+3]==instruction and new['raw'][i:i+3]==bytes([0x4c,newpc&255,newpc>>8]):
            found.append(i);allowed.append((i+1,i+3,'actual_JMP_rebound_own_helper'))
    moved={n:[address(old,n),address(new,n)]for n,s in old['syms'].items()
       if 'seg'in s and '::'not in n and address(new,n)!=address(old,n)}
    assert set(moved)<={'FwSvcEnd','FfHostNewEnemy','FfHostFresh','FfHostCombatEnd','HuMaaRenderLegacy'},moved
    diffs=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    outside=[i for i in diffs if not any(a<=i<z for a,z,_ in allowed)]
    assert not outside,outside[:32]
    # All non-combat cache bytes are pinned, including code and predecoded FX.
    oldimage=(P/'joint/ram3.bin').read_bytes()
    assert image[:0x1700]==oldimage[:0x1700]and image[0x1900:]==oldimage[0x1900:]
    patch=''.join(''.join(difflib.unified_diff((P/'joint'/rel).read_text().splitlines(True),
          (d/rel).read_text().splitlines(True),fromfile=rel,tofile=rel))for rel in changed)
    B.write(O/'source-hooks.patch',patch)
    for dep in d.rglob('*.dep'):files.update(dependencies(dep))
    files.update(p for p in O.rglob('*')if p.is_file());files.add(Path(__file__))
    files.update(Path(v)for v in cmd if v.endswith('.o'))
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,
      candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),
      changed_bytes=len(diffs),allowed_ranges=allowed,old_public_entries_moved=moved,
      original_native_enemy_clear_before_source_forget=True,actual_FF_flash_age=True,FF_flash_renderer_installed=False,
      RAM3_sha256=hashlib.sha256(image).hexdigest(),cookie=list(cookie),
      limits=['CPU/current-caller/ISR controls pending; no native,playable or performance claim.',
              'FF flash renderer,postBG shared ingress,palette,audio and actual earned1-1 remain separate.'],
      bindings={str(p.resolve()):B.sha(p)for p in sorted(files)}))
    print('FF COMBAT SOURCE',B.sha(d/'candidate.nes'),flush=True)


if __name__=='__main__':main()
