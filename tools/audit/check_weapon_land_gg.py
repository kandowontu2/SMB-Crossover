"""Rebind the frozen Land lifecycle/source checks to the current GF composition."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=R/'tools/audit/check_roster49_land_l_native_id.py'
code=original.read_text()
code=code.replace("S=V/'root49-components-land-l-ia/source';O=V/'root49-land-l-native-ie'", "S=V/'weapons-current-gf/source';O=V/'weapons-land-gg'")
old="build=V/'root49-components-land-l-ia/build-review-ic.json';assert sha(build)=='2e9afeb6045b6f557881a4fc7b2040e4e0feea3ddf6229e99aa8741d40d67ffc'"
assert code.count(old)==1
code=code.replace(old,"build=V/'weapons-current-gf/build.json';assert sha(build)=="+repr(sha(R/'build/verification/weapons-current-gf/build.json')))
code=code.replace("sha(V/'root49-components-land-l-ia/preparation.json')", "sha(V/'weapons-current-gf/preparation.json')")
code=code.replace('PASS_PRIVATE_L_12_FRESH_NATIVE_LAND_SOURCE_LIFECYCLE_GROUPS_AND_EXACT_516_CALLERS','PASS_CURRENT_GF_12_FRESH_NATIVE_LAND_SOURCE_LIFECYCLE_GROUPS_AND_EXACT_516_CALLERS')
code=code.replace('Land is combined with I/J/Arm/Rush/HU, but Ryu/HUD/visibleWater are not inL. MainHU remains installed.','GF is current GA with Arm/Rush/Land and the native audio optimization. All GA terrain/HUD/Water/menu/firebar fixes are retained. Main GA is unchanged.')
path=R/'build/verification/weapons-land-gg-runner.py.txt';assert not path.exists();path.write_text(code)
exec(compile(code,str(original),'exec'),{'__name__':'__main__','__file__':str(original)})
out=R/'build/verification/weapons-land-gg/rebinding.json'
out.write_text(json.dumps(dict(original_driver_sha256=sha(original),adapter_sha256=sha(__file__),bound_driver_sha256=sha(path),candidate_build_sha256=sha(R/'build/verification/weapons-current-gf/build.json'),scope='Only actual ROM/Image and fresh output bindings changed; frozen fixture/oracle cores unchanged.'),indent=2)+'\n')
