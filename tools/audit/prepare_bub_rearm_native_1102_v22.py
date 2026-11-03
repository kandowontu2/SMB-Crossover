"""Respect actual source leftwall phase and original first facing-ready epoch."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2';PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11/controller.lua');text=source.read_text()
    proof=O/'rearm-phase-v22-CPU.json';q=json.loads(proof.read_text());assert q['passed']and q['ROM_sha256']==PIN and len(q['cases'])==4
    assert all(c['launch']['x']==646 and c['final_x']==776 and c['final_y']==176 and c['lives']==2 for c in q['cases'])
    changes={
      "if full_rearm_mode=='rewind'and x>full_rearm_target then":"if full_rearm_mode=='rewind'and x>full_rearm_target+1 then",
      "if full_rearm_age<2 or full_state(0x102+oy)&64==0 then":"if full_rearm_age<1 or full_state(0x102+oy)&64==0 then",
    }
    for a,b in changes.items():assert text.count(a)==1,a;text=text.replace(a,b)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-landing-'+args.identity+'-full11-rearm2');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,O/'combined-landing.json',O/'landing-v21-proposal.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Unchanged private landing ROM/strictfullstageassertions. Controller-only two measured phase corrections: accept sourceleftwall at nominaltarget+1, and freshB after firstactualRight-facing sourceupdate plus existingattr40/cooldown0/Breleased. FourcurrentMain sourceproofcases bothidentities/parities earn launch646 and actualthird64pipefar776/Y176/lives2. Old1066Mainrearmnegative preserved. All7crossings/naturaldefeats/stairs/active1-2/lives/source/hardwareguards remain.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))

if __name__=='__main__':main()
