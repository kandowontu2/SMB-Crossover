"""Prepare ONE unlaunched450 publication-priority pilot with fresh metadata."""
from pathlib import Path
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import address,location
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'mm-proto-publication-candidate-v3'
REF=D/'root-presentation450-731-v1'
EXPECTED='a801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(R)
    frozen=B/'freeze-v1/receipt.json';assert sha(frozen)=='7d8aa2433f882e65718d1dccd845c63a60ce54656eaea79189f8918bf890cab6'
    binding=json.loads((frozen.parent/'bindings.json').read_text())
    for path,z in binding.items():assert sha(path)==z['sha256'],path
    cmd=[sys.executable,'-B',str(R/'tools/audit/presentation_timing_prepare_v1.py'),'--candidate',str(B),'--expected-ROM-sha256',EXPECTED,'--output',str(a.output)]
    z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    if not a.output.exists():a.output.mkdir(parents=True)
    put(a.output/'base-preparer.json',dict(command=cmd,exit=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stdout+z.stderr
    shutil.copyfile(a.output/'readiness.json',a.output/'base-readiness.json');shutil.copyfile(a.output/'run.lua',a.output/'base-run.lua')
    base=json.loads((a.output/'readiness.json').read_text());cfg=json.loads((a.output/'config.json').read_text());old=json.loads((REF/'config.json').read_text())
    assert(a.output/'prefix.csv').read_bytes()==(REF/'prefix.csv').read_bytes()
    assert all(cfg[n]==old[n]for n in['limit','hooks','ram','smc'])
    b=scoped_load(B/'candidate.nes');q=qualified(B/'candidate.nes')
    names=['NmiDisable','NmiSkipped','ShouldSkipDrawSprites','FramesSinceLastSpriteDraw','FrameCounter','SelectedCharacter','ProtoVariant','OperMode','OperMode_Task','GameEngineSubroutine','CrossoverMenuState','DisableScreenFlag','GamePauseStatus','MmDeathFlag','MmSliding','ObjectMetasprite','SprObject_SprAttrib','ObjectVerticalFlip','MmPublicationState','Player_X_Position','Player_Y_Position','Player_PageLoc','Player_Y_HighPos','AreaPointer','WorldNumber','LevelNumber','NumberofLives','GuestOamRotationActive','RgOamFirst','RgOamRotation','RgOamUsed','RgOamPlayerStart','CurrentOAMOffset','SsDrawFirst','SpriteShuffleOffset','ReloadCHRBank','X5WideChrActive','CurrentBank','CurrentBankC']
    ordinary=['MmBulletType','MmBulletAge','MmBulletX','MmBulletPage','MmBulletY','MmBulletDir'];special=['RgShotType','RgShotAge','RgShotX','RgShotPage','RgShotY','RgShotDir']
    hooks={}
    for alias,name in [('GameLoopEntry','GameLoop'),('DrawAll','DrawAllMetasprites'),('RosterReady','RosterOamReady'),('MoveAll','MoveAllSpritesOffscreen'),('InitializeArea','InitializeArea'),('InitializeGame','InitializeGame'),('MegaClear','MegaManClearState')]:
        pc,off=address(b,name),location(b,name);hooks[alias]=dict(pc=pc,bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
    release=q[('GameLoop','PauseSkip')];off=location(b,'GameLoop')+release-address(b,'GameLoop')
    assert release==0x8350 and b['raw'][off:off+6]==bytes.fromhex('a9008d390160')
    hooks['GameLoopDone']=dict(pc=release+5,bank=126,bytes=[96]);hooks|={n:cfg['hooks'][n]for n in['NmiEntry','NmiReturn','DmaComplete']}
    assert hooks['RosterReady']['pc']==41545 and hooks['RosterReady']['bank']==4
    own=dict(out=cfg['out'],limit=450,ROM_sha256=EXPECTED,hooks=hooks,ram={n:address(b,n)for n in names+ordinary+special},state_names=names,ordinary_names=ordinary,special_names=special)
    assert own['ram']['MmPublicationState']==0x5ff8
    put(a.output/'ownership-config.json',own)
    module=R/'tools/audit/mm_proto_publication_candidate_observer_v1.lua';original=R/'tools/audit/mm_proto_publication_ownership_observer_v1.lua'
    text=module.read_text();before=original.read_text()
    # Exactly one added static RAM callback and state snapshot on the already
    # existing NMI-return hook; original physical guard module is unchanged.
    oldline="hook('NmiReturn',function(s)row({kind='NMI-return',ppu=stamp(),main=main and main.id or-1,sp=s['cpu.sp'],depth=depth});depth=depth-1 end)"
    newline=oldline.replace('depth=depth}','depth=depth,state=state()}')
    added="""emu.addMemoryCallback(function(_,v)
 local s=emu.getState()
 row({kind='publication-state-write',value=v,callback_pc=s['cpu.pc'],callback_bank=bank(s['cpu.pc']),ppu=stamp(),main=main and main.id or-1,construction=draw and draw.id or-1,nmi_depth=depth})
end,emu.callbackType.write,C.ram.MmPublicationState)
"""
    assert text.count(newline)==1 and text.count(added)==1
    assert text.replace(newline,oldline).replace(added,'')==before
    assert not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(',text)
    assert not re.search(r'\b(?:removeMemoryCallback|removeEventCallback)\b',text)
    assert set(re.findall(r"r\('([^']+)'\)",text))<=own['ram'].keys()
    sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'));from luaparser import ast
    ast.parse(text)
    script='PUBLICATION_OWNERSHIP='+lua(own)+'\ndofile('+lua(module.as_posix())+')\n'+(a.output/'base-run.lua').read_text();ast.parse(script);(a.output/'run.lua').write_text(script)
    (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),fromfile=original.name,tofile=module.name)))
    mock=a.output/'callback-mock'
    command=[sys.executable,'-B',str(R/'tools/audit/mm_proto_publication_candidate_mock_v1.py'),'--prepared',str(a.output),'--output',str(mock)]
    z=subprocess.run(command,cwd=R,capture_output=True,text=True);put(a.output/'mock-launch.json',dict(command=command,exit=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stdout+z.stderr
    assert json.loads((mock/'proof.json').read_text())['passed']
    plan='''ONE UNLAUNCHED450 candidate-only pilot, same exact controller731 reference.
All original fixed timing/input/full256 source-destination hardware/PPUMASK/
IRQ31/NMI AXY-SP/5SMC/bank guards and275raw PPU frames176..450 are unchanged.
Fresh a801 debug metadata binds genuine moved RosterReady A249 inbank4,
real source release8355 inbank126 and original fixed E008 full-DMA sensor.
Additional observer reuses the native-qualified731 ownership code with only
one static5FF8 write callback plus state on its existing NMI-return hook.
Actual ObjectVerticalFlip and publication byte are now read in snapshots.
No V-flip value, Main instruction, source write, or unlogged owner is inferred.
This observes consumed body/shot tag values, source epochs, actual live slots,
physical full pages, and paired visible pixels. It cannot guarantee universal
body/shot/world fairness or no-harm from a short route; Vine/no-draw chain,
death/later areas/Proto and denser scenes remain separately unqualified.
Owned DrawAll+189..191/NMI+17..88 and commonMoveAll+18 are material risks.
No source/default/settings changes, extra launches/retry, mask relaxations,
native grant or adoption. At mostONE worker/launch after fresh ROOT review.
'''
    (a.output/'PLAN.txt').write_text(plan)
    run=base['command'][:];run[run.index('--timeout')+1]='1200'
    deps={Path(p)for p in base['bindings']}|{Path(p)for p in binding}
    deps|={Path(__file__),module,original,R/'tools/audit/mm_proto_publication_candidate_mock_v1.py',R/'tools/audit/presentation_timing_launch_v1.py',frozen,frozen.parent/'bindings.json',frozen.parent/'catalog.json',frozen.parent/'source.zip'}
    deps|={REF/n for n in['readiness.json','native-receipt.json','prefix.csv','result.json','timing.jsonl','direct-index.csv','direct.argb']}
    deps|={p for p in a.output.rglob('*')if p.is_file()and p.name not in['readiness.json','preparation.json','catalog.json']}
    final=base|dict(command=run,native_run=False,native_grant=False,maximum_launches=1,maximum_workers=1,matched_reference_ROM_sha256=sha(Path(old['out'])/'readiness.json')if False else'731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c',fresh_candidate_hook_addresses=True,source_freeze_sha256=sha(frozen),mock_proof_sha256=sha(mock/'proof.json'),host_timeout_seconds=1200,bindings={str(p.resolve()):sha(p)for p in sorted(deps)},limits=plan)
    put(a.output/'readiness.json',final)
    catalog={p.relative_to(a.output).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(a.output.rglob('*'))if p.is_file()}
    put(a.output/'catalog.json',catalog)
    proof=dict(passed=True,prepared_only=True,native_run=False,native_grant=False,ROM_sha256=EXPECTED,maximum_launches=1,maximum_workers=1,source_packet_sha256=sha(frozen),source_costs_and_partial_writer_limits_retained=True,fresh_actual_hooks=hooks,unchanged_original_450_input_and_hardware_guards=True,observer_reverse_normalizes_exactly=True,static_callback_mock_pass=True,readiness_sha256=sha(a.output/'readiness.json'),bindings=len(deps),catalog_sha256=sha(a.output/'catalog.json'),preparer_sha256=sha(__file__))
    put(a.output/'preparation.json',proof);print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
