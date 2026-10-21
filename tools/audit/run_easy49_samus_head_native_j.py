"""Exercise actual upright Samus head contacts across source power/mode rules."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, shutil, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-h'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    p.add_argument('--tag', required=True)
    a = p.parse_args()
    sys.dont_write_bytecode = True
    review = json.loads((H / 'report.json').read_text())
    assert review['status'] == 'PASS_PRIVATE_SHARED_MARIO_UNION_H_BUILD_ONLY'
    assert all(sha(H / 'source' / n) == h for n, h in review['source_hashes'].items())
    spec = importlib.util.spec_from_file_location('head_j_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    im = mod.Image(H / ('source/build/smb-crossover-' + a.mapper + '.nes'))
    out = H / 'native' / a.tag
    out.mkdir(parents=True, exist_ok=False)
    text = (R / 'tests/samus-head-bricks.lua').read_text()
    text = text.replace('local checked=0', 'local checked=0\nlocal headReceipts=0')
    text = text.replace('start=frame==200,', 'start=frame==60 or frame==200,')
    text = text.replace('frame<950', 'frame<1350').replace('frame<=810', 'frame<=1200').replace('frame<=885', 'frame<=1275').replace('if frame==900 then', 'if frame==1290 then')
    text = text.replace('local status=math.floor((frame-550)/130)', 'local case=math.floor((frame-550)/130);local status=case%3;local mode=math.floor(case/3)')
    text = text.replace('local status=math.floor((frame-625)/130)', 'local case=math.floor((frame-625)/130);local status=case%3;local mode=math.floor(case/3)')
    text = text.replace("w('BlockBounceTimer',0);w('PlayerStatus',status);w('SmBall',0)", "headReceipts=0;w('SelectedCharacter',2);w('CrossoverBehaviorVersion',mode);w('BlockBounceTimer',0);w('PlayerStatus',status);w('SmBall',0);w('SmCrouch',0);w('GuestPowerupActive',0);w('GuestLegacyHurt',0);w('GuestHurtTicks',0);w('TimerControl',0)")
    old = "  assert(r('Block_Buffer_1',118)==(status==2 and 0x51 or 0),'Samus head behavior matches the hosted suit rule: '..status..' / '..r('Block_Buffer_1',118))"
    new = "  assert(headReceipts>0,'Actual controller jump reaches the native head rule');assert(r('Block_Buffer_1',118)==((mode==0 and status<2)and 0 or 0x51),'Samus source head rule mode'..mode..' tier'..status..' cell'..r('Block_Buffer_1',118));assert(r('Player_X_Position')==88 and r('Player_PageLoc')==0,'Head bump keeps horizontal position')"
    assert text.count(old) == 1
    text = text.replace(old, new).replace("assert(checked==3,'All Samus suits tested')", "assert(checked==6,'Both modes and all three upright Samus suits tested')")
    old = "  print('PASS Samus head breaks bricks in her first two suits; wave suit bumps as in the hosted game');emu.stop(0)"
    new = "  local f=assert(io.open(HEAD_RULE.out..'result.json','w'));f:write('{\"status\":\"PASS_NATIVE_SAMUS_UPRIGHT_HEAD_MODES\",\"cases\":6,\"route_proof\":false}');f:close();print('PASS six upright Samus head contacts: Easy suits0/1 break, Easy2 and all Hard suits bump');emu.stop(0)"
    assert text.count(old) == 1
    text = text.replace(old, new)
    h = im.hook('CrossoverBlockSize')
    guard = '''local h=HEAD_RULE.hook
emu.addMemoryCallback(function()
 local actual=emu.convertAddress(h.address)
 if not actual or actual.memType~=emu.memType.nesPrgRom or actual.address//8192~=h.physical_bank then return end
 for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact compiled head hook')end
 if frame>=550 then headReceipts=headReceipts+1 end
end,emu.callbackType.exec,h.address)
'''
    marker = 'local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end\n'
    assert text.count(marker) == 1
    text = text.replace(marker, marker + guard)
    core = out / 'native-core.lua'
    core.write_text(text)
    cfg = dict(hook=h, out=out.as_posix() + '/', ROM=im.metadata())
    wrapper = out / ('samus-head-' + a.tag + '.lua')
    wrapper.write_text('HEAD_RULE=' + mod.lua(cfg) + '\ndofile(' + mod.lua(core.as_posix()) + ')\n')
    (out / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    rc = run_mesen.run(wrapper, im.path, timeout=90, emulator_options=['--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', out / 'native.log')
    result_path = out / 'result.json'
    (out / 'host-report.json').write_text(json.dumps(dict(exit=rc, result=json.loads(result_path.read_text()) if result_path.exists() else None,
        binding_sha256=sha(out / 'binding.json'), core_sha256=sha(core), launcher_sha256=sha(__file__),
        parent_fixture_sha256=sha(R / 'tests/samus-head-bricks.lua'),
        scope='Actual upright brick head contacts only; no Morph Ball NONE/item-emergence or full-stage claim.', route_proof=False), indent=2) + '\n')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
