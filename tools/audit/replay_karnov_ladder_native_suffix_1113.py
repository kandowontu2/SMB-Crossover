"""Separate controller-only native wall assist; frozen Karnov7d1 remains intact."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import replay_karnov_ladder_early_1113 as Frozen

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
BASE='7d1ea719a760ac0dedb17fedde3705d5ccfdc67d1af34018efc017f859c79091'
SOURCE=Frozen.SOURCE.with_name('karnov_ladder_native_suffix_1113.lua')


def controller(raw,*,force_settle=False):
    assert sha256(raw).hexdigest()==PIN
    text=Frozen.current_controller(raw);assert sha256(text.encode()).hexdigest()==BASE
    before='local function control()';assert text.count(before)==1
    text=text.replace(before,'local FORCE_SETTLE='+str(force_settle).lower()+'\n'+SOURCE.read_text()+'\n'+before)
    before=' if #pickups>=4 then return fifthControl(x,y,ground,item)end'
    assert text.count(before)==1
    text=text.replace(before,''' if #pickups>=4 then
  local navOK,navHandled,navPad=pcall(nativeSuffixControl,x,y,ground,item)
  if not navOK then finish(false,'native suffix: '..tostring(navHandled));return 0 end
  if navHandled then return navPad end
  return fifthControl(x,y,ground,item)
 end''')
    Frozen.Late.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def cpu(raw,*,force_settle=False,limit=12000):
    with patch.object(Frozen.Late,'controller',lambda image:controller(image,force_settle=force_settle)):
        report=Frozen.Late.run(raw,limit=limit)
    report['ROM_SHA256']=PIN
    result={key:report[key]for key in('passed','controller_error','seconds','actual_Main_NMI_updates','opening','pickups','terminal','source','manual_helpers','boots_activation','controller_SHA256','ROM_or_runtime_fixture_edits','new_helper_allocations','output_files','Mesen_run')}
    result.update(ROM_SHA256=PIN,force_settle_development_inputs=force_settle,
        native_suffix=report['fifth'].get('native_suffix'),
        ladder={key:report['fifth'].get(key)for key in('stage','site','art','grown','climbed','complete','restored_cells','restored_attributes')})
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',action='store_true')
    p.add_argument('--force-settle',action='store_true');p.add_argument('--limit',type=int,default=12000)
    args=p.parse_args();raw=Frozen.Late.Feature.Owner.NIGHTLY.read_bytes()
    if args.cpu:
        q=cpu(raw,force_settle=args.force_settle,limit=args.limit);print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Separate native suffix controller must pass its declared source route'
    else:
        text=controller(raw,force_settle=args.force_settle)
        print(json.dumps(dict(ROM_SHA256=PIN,base_controller_SHA256=BASE,controller_SHA256=sha256(text.encode()).hexdigest(),
            bytes=len(text),Lua_compile=True,force_settle=args.force_settle,native_run=False,outputs=0),separators=(',',':')),flush=True)
