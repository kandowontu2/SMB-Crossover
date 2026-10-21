"""Bind unchanged native fixtures and the corrected frozen Arm successor to K."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=R/'tools/audit/check_roster49_water_enemy_filter_hd.py';code=source.read_text(encoding='utf-8')
def change(old,new,count=1):
 global code
 assert code.count(old)==count,(old[:80],code.count(old),count)
 code=code.replace(old,new)
change('root49-water-filter-native-hd','root49-combined-k-native-hk')
change('root49-water-enemy-filter-gy/build-review-ha.json','root49-components-combined-k/build-review-hj.json',2)
change('6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6','8178d16675961c3d801ef19f0cff208482a0273333748ecd6d61e951212fb7ea')
change('root49-water-enemy-filter-gy/source/build','root49-components-combined-k/source/build')
change("R/'tests/water-shield-performance.lua'","R/'build/verification/agent49-super-arm-h-a/fixture-r/bass-special-weapons.lua',R/'tests/water-shield-performance.lua'")
change("args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/'tests'/f'{name}.lua'),str(rom),'--timeout','180']", "fixture=R/'build/verification/agent49-super-arm-h-a/fixture-r/bass-special-weapons.lua'if name=='bass-special-weapons'else R/'tests'/f'{name}.lua'\n   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(fixture),str(rom),'--timeout','180']")
change("scope='PrivateJ: I plus exact50B batch offscreen reject; unchanged authored mechanics/geometry/OAM/native performance and foreign weapons fixtures. Setup/grants mean no ordinary acquisition. Original Bass Arm cost oracle remains wrong and is not promoted to source accuracy; no new Arm implementation is present here.'", "scope='PrivateK: reviewed audio/cache+J batch reject+Arm+Rush mechanics, bothmappers. Eight unchanged Water/armor fixtures plus frozen corrected Arm fixtureS: free funded lift,8-unit throw. All other original Bass assertions retained. Setup/grants mean no ordinary acquisition/fullroute/source/finalmovie claim. Land/Ryu/HUD are not yet included.'")if "no new Arm implementation is present here."in code else change("scope='PrivateJ: I plus exact50B batch offscreen reject; unchanged authored mechanics/geometry/OAM/native performance and foreign weapons fixtures. Setup/grants mean no ordinary acquisition. Original Bass Arm cost oracle remains wrong and is not promoted to source accuracy; no new Arm implementation is present.'", "scope='PrivateK: reviewed audio/cache+J batch reject+Arm+Rush mechanics, bothmappers. Eight unchanged Water/armor fixtures plus frozen corrected Arm fixtureS: free funded lift,8-unit throw. All other original Bass assertions retained. Setup/grants mean no ordinary acquisition/fullroute/source/finalmovie claim. Land/Ryu/HUD are not yet included.'")
change('PASS_PRIVATE_J_18_UNCHANGED_NATIVE_WATER_AND_FOREIGN_GROUPS','PASS_PRIVATE_K_18_NATIVE_WATER_ARM_AND_FOREIGN_GROUPS')
change('RETAINED_PRIVATE_J_NATIVE_FAILURES','RETAINED_PRIVATE_K_NATIVE_FAILURES')
out=R/'tools/audit/check_roster49_combined_k_native_hk.py';assert not out.exists();out.write_text(code,encoding='utf-8');print(json.dumps(dict(path=str(out.relative_to(R)),sha256=sha(out),parent_script_sha256=sha(source))))
