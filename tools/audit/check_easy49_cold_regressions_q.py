"""Real coin-brick and native music regressions after cold-bank relocation."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-cold-bank-n'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    out = H / 'native/cold-regressions-q'
    out.mkdir(parents=True, exist_ok=False)
    review = json.loads((H / 'report.json').read_text())
    assert review['status'] == 'PASS_PRIVATE_COLD_BANK_RELOCATION_BUILD_ONLY'
    spec = importlib.util.spec_from_file_location('cold_p_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    report = dict(status='RUNNING_COLD_RELOCATION_REGRESSIONS', script_sha256=sha(__file__),
                  build_review_sha256=sha(H / 'report.json'), retained_bootstrap_negative_sha256=sha(H / 'native/cold-regressions-p/report.json'), explicit_original_fixture_bootstrap_sha256=sha(R / 'tests/menu-bootstrap.lua'), rows=[], route_proof=False, accepted_release=False, goal_complete=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        im = mod.Image(H / ('source/build/smb-crossover-' + mapper + '.nes'))
        old = mod.Image(V / ('root49-easy-samus-bomb-m/source/build/smb-crossover-' + mapper + '.nes'))
        symbol, before = im.sym('MegaManCoinBrick'), old.sym('MegaManCoinBrick')
        hook, old_hook = im.hook('MegaManCoinBrick'), old.hook('MegaManCoinBrick')
        assert symbol['size'] == before['size'] == 199
        assert im.raw[hook['rom_offset']:hook['rom_offset'] + 199] == old.raw[old_hook['rom_offset']:old_hook['rom_offset'] + 199]
        assert hook['physical_bank'] == 11 and old_hook['physical_bank'] == 8
        for name in ['megaman-buster', 'megaman-music', 'megaman-audio-effects']:
            script = R / ('tests/' + name + '.lua')
            wrapper = out / ('cold-n-' + mapper + '-' + name + '.lua')
            guard = '''local h=COLD_COIN;local receipts=0
emu.addMemoryCallback(function()
 local actual=emu.convertAddress(h.address)
 if not actual or actual.memType~=emu.memType.nesPrgRom or actual.address//8192~=h.physical_bank then return end
 for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual relocated coin closure')end
 receipts=receipts+1
end,emu.callbackType.exec,h.address)
local originalStop=emu.stop
emu.stop=function(code)
 if code==0 then assert(receipts>=16,'Actual relocated fourteen-coin/window native contacts');print('PASS guarded cold coin entries '..receipts)end
 return originalStop(code)
end
'''
            wrapper.write_text('dofile(' + mod.lua((R / 'tests/menu-bootstrap.lua').as_posix()) + ')\n' + ('COLD_COIN=' + mod.lua(hook) + '\n' + guard if name == 'megaman-buster' else '') + 'dofile(' + mod.lua(script.as_posix()) + ')\n')
            rc = run_mesen.run(wrapper, im.path, timeout=90,
                               emulator_options=['--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
            log = out / (mapper + '-' + name + '.log')
            shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', log)
            report['rows'].append(dict(mapper=mapper, test=name, exit=rc, test_sha256=sha(script),
                                       wrapper_sha256=sha(wrapper), log_sha256=sha(log), ROM_sha256=sha(im.path),
                                       coin_closure_byte_exact=True, coin_hook=hook))
            save()
    passed = all(row['exit'] == 0 for row in report['rows'])
    report['status'] = 'PASS_SIX_COIN_MUSIC_REGRESSION_GROUPS' if passed else 'FAILED_COLD_RELOCATION_REGRESSIONS'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
