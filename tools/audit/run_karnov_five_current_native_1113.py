"""Root's natural five-pickup Karnov qualification on actual Downloads."""
import argparse
from hashlib import sha256
import json

import replay_karnov_ladder_early_1113 as E
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
BASE='7d1ea719a760ac0dedb17fedde3705d5ccfdc67d1af34018efc017f859c79091'
LEDGE='d6d0f47e1d7cf1d6544073c0937835d7b520a80bb6b2aa56614e406b9cf09a44'
DIAGNOSTIC='1b998db9a3758e697e1ccc6eecffcc85097370767aaa1cad5f3d575666a41937'
OUT=E.Late.Feature.Owner.R/'build/metal-flower-native-1112'


def controller(raw, *, images=False, ledge=False, diagnostic=False):
    assert sha256(raw).hexdigest()==PIN
    if diagnostic:
        import replay_karnov_ladder_suffix_diagnostic_1113 as D
        text=D.controller(raw)
    elif ledge:
        import replay_karnov_ladder_native_suffix_1113 as Suffix
        text=Suffix.controller(raw)
    else:
        text=E.current_controller(raw)
    assert sha256(text.encode()).hexdigest()==(DIAGNOSTIC if diagnostic else LEDGE if ledge else BASE)
    if images:
        # Reuse the qualified two-PNG encoder, in memory. No controller
        # decisions or original assertions are changed by these observers.
        source=(E.Late.Feature.Owner.R/'tools/reference/karnov_ladder_native_1113.lua').read_text()
        start=source.index('local alphabet=')
        end=source.index('\nemu.addEventCallback',start)
        encoder=source[start:end].replace('base64(bytes)','karnovImage64(bytes)',1).replace('alphabet','karnovImageAlphabet')
        binary_check=E.Late.LuaRuntime().eval('function()\n'+encoder+
            '\nreturn karnovImage64(string.char(137,80,78,71,13,10,26,10))end')
        assert binary_check()=='iVBORw0KGgo=','PNG binary transport encoder'
        text+='\n'+encoder+r'''
local karnovImages={}
emu.addEventCallback(function()
 if done or not stockFifth then return end
 local stage=stockFifth.stage
 if (stage=='climb'or stage=='down')and not karnovImages[stage]then
  local count=0;for _ in pairs(karnovImages)do count=count+1 end
  assert(count<2,'At most two passive natural-scene PNGs')
  local png=emu.takeScreenshot()
  assert(type(png)=='string'and png:sub(1,8)=='\137PNG\r\n\26\n','Actual in-memory natural-scene PNG')
  assert(#png<=4*1024*1024,'Single PNG bound4MB')
  karnovImages[stage]=true;print('SMB_NATIVE_IMAGE '..karnovImage64(png))
 end
end,emu.eventType.endFrame)
'''
    E.Late.LuaRuntime().compile(text)
    return text


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images',action='store_true')
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--ledge',action='store_true')
    modes.add_argument('--diagnose-ledge',action='store_true')
    args=p.parse_args()
    rom=E.Late.Feature.Owner.NIGHTLY
    assert check(rom)['ROM_sha256']==PIN
    text=controller(rom.read_bytes(),images=args.images,ledge=args.ledge,diagnostic=args.diagnose_ledge)
    script=OUT/'controller.lua';script.write_text(text,encoding='utf-8',newline='\n')
    result=run(script,rom,OUT/'capture',PIN,240)
    receipt=result['receipt']
    compact={key:value for key,value in receipt.items()
        if not isinstance(value,(dict,list)) or key in('terminal','manual_helpers','boots_activation',
            'native_suffix','native_suffix_diagnostic')}
    compact['pickups']=[]
    for q in receipt.get('pickups',[]):
        row={key:value for key,value in q.items() if key in('frame','epoch','item','native','erased')}
        for when in ('before','after'):
            row[when]={key:value for key,value in q.get(when,{}).items()
                if key in('frame','epoch','world','level','x','y','health','lives',
                    'shot','cycle','option','owned','stock','boots_stock')}
        compact['pickups'].append(row)
    fifth=receipt.get('fifth',{})
    compact['fifth']={key:value for key,value in fifth.items()
        if key in('stage','main','movement_updates','GameLoop_entries','GameLoop_returns','native_suffix',
            'site','art','grown','climbed','complete','restored_cells','restored_attributes')}
    compact['fifth']['last_progress']=fifth.get('progress',[])[-6:]
    print(json.dumps(dict(passed=result['passed'],ROM_SHA256=PIN,
        script_SHA256=result['script_SHA256'],base_controller_SHA256=BASE,
        decision_controller_SHA256=DIAGNOSTIC if args.diagnose_ledge else LEDGE if args.ledge else BASE,
        receipt_SHA256=result['receipt_SHA256'],receipt=compact,
        images=result['images'],outputs_written=result['outputs_written']),
        separators=(',',':')),flush=True)
    assert check(rom)['ROM_sha256']==PIN


if __name__=='__main__':
    main()
