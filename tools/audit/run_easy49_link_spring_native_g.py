"""Actual spring contact/compression/controller boost checks for Link modes."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, shutil, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-link-spring-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--control', action='store_true')
    a = p.parse_args()
    sys.dont_write_bytecode = True
    review = json.loads((H / 'report.json').read_text())
    assert review['status'] == 'PASS_PRIVATE_LINK_SPRING_BUILD_ONLY'
    spec = importlib.util.spec_from_file_location('spring_native_g', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    directory = V / 'root49-easy-union-c' if a.control else H
    im = mod.Image(directory / ('source/build/smb-crossover-' + a.mapper + '.nes'))
    out = H / 'native' / a.tag
    out.mkdir(parents=True, exist_ok=False)
    hooks = {'NonMaskableInterrupt': im.hook('NonMaskableInterrupt'),
             'NonMaskableInterrupt_RTI': im.hook('NonMaskableInterrupt', None, 'last'),
             'IrqScrollSplit': im.hook('IrqScrollSplit'),
             'IrqScrollSplit_RTI': im.hook('IrqScrollSplit', None, 'last'),
             'MegaManSpringVelocity': im.hook('MegaManSpringVelocity'),
             'DrawJumpSpring': im.hook('DrawJumpSpring')}
    text = (R / 'tests/world-springs.lua').read_text()
    old = "local function character()local c=math.floor(phase/4);return c==12 and 3 or c==13 and 12 or c end"
    assert text.count(old) == 1
    text = text.replace(old, 'local function character()return 4 end')
    text = text.replace("w('SelectedCharacter',character());w('BillVariant'", "w('CrossoverBehaviorVersion',math.floor(phase/4));w('SelectedCharacter',character());w('BillVariant'")
    text = text.replace('expected[character()+1][boosted()and 2 or 1]', '((phase<4 and (boosted() and 800 or 400) or (boosted() and 950 or 450))/120)')
    text = text.replace('start=frame==200,', 'start=frame==60 or frame==200,')
    text = text.replace('if phase==56 then', 'if phase==8 then')
    old = "   print('PASS 56 native spring contacts: all thirteen characters plus Lance, slots 0/5, ordinary/boosted launches, source forces, preserved X and live airborne rebound')"
    new = "   local f=assert(io.open(SPRING_CASE.out..'result.json','w'));f:write('{\"status\":\"PASS_NATIVE_LINK_MODE_SPRINGS\",\"cases\":8,\"route_proof\":false}');f:close();print('PASS 8 native Link springs: both modes, slots0/5, controller boost, source forces and live rebound')"
    assert text.count(old) == 1
    text = text.replace(old, new)
    guard = '''local C=assert(SPRING_CASE)
local rawAdd=emu.addMemoryCallback
emu.addMemoryCallback=function(fn,kind,first,last,...)
 if kind==emu.callbackType.exec then
  local h;for _,v in pairs(C.hooks)do if v.address==first then h=v end end
  assert(h,'Bound spring hook');local original=fn
  fn=function(...)
   local actual=emu.convertAddress(first)
   if not actual or actual.memType~=emu.memType.nesPrgRom or actual.address//8192~=h.physical_bank then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(first+i-1,emu.memType.nesDebug)==v,'Actual eightbyte spring hook')end
   return original(...)
  end
 end
 return rawAdd(fn,kind,first,last,...)
end
'''
    core = out / 'native-core.lua'
    core.write_text(guard + text)
    cfg = dict(hooks=hooks, out=out.as_posix() + '/', ROM=im.metadata(), kind='control' if a.control else 'candidate')
    wrapper = out / ('link-spring-' + a.tag + '.lua')
    wrapper.write_text('SPRING_CASE=' + mod.lua(cfg) + '\n' + ''.join('L[' + mod.lua(n) + ']=' + str(h['address']) + '\n' for n, h in hooks.items()) + 'dofile(' + mod.lua(core.as_posix()) + ')\n')
    (out / 'binding.json').write_text(json.dumps(cfg, indent=2) + '\n')
    sys.path.insert(0, str(R / 'tools'))
    import run_mesen
    rc = run_mesen.run(wrapper, im.path, timeout=90,
                       emulator_options=['--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false', '--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(V / f'{im.path.stem}-{wrapper.stem}.log', out / 'native.log')
    result_path = out / 'result.json'
    admitted = rc == 0 and result_path.exists() if not a.control else rc != 0 and 'Character spring force: -3.75' in (out / 'native.log').read_text()
    (out / 'host-report.json').write_text(json.dumps(dict(exit=rc, admitted=admitted,
        result=json.loads(result_path.read_text()) if result_path.exists() else None,
        binding_sha256=sha(out / 'binding.json'), core_sha256=sha(core), launcher_sha256=sha(__file__),
        parent_fixture_sha256=sha(R / 'tests/world-springs.lua'), route_proof=False), indent=2) + '\n')
    print(a.mapper, cfg['kind'], 'ADMITTED' if admitted else 'UNADMITTED', flush=True)
    return 0 if admitted else 1


if __name__ == '__main__':
    raise SystemExit(main())
