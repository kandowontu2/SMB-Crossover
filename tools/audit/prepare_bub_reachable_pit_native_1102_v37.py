"""Use the source-proven reachable X2443 takeoff; all jump guards stay exact."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-current-landing-'+args.identity+'-full11-final-pit/controller.lua');text=source.read_text()
    proof=O/'reachable-pit-takeoff-v36-CPU.json';p=json.loads(proof.read_text());assert p['passed']and p['ROM_sha256']==PIN
    assert {c['identity']for c in p['cases']}=={0,1}
    for c in p['cases']:
        assert c['final_x']==2501 and c['final_y']==128 and c['final_native_state']==0 and c['lives']==2
        assert [(v['x'],v['native_state'],v['left'],v['right'])for v in c['actual_original_jumps']]==[(2443,0,True,False),(2472,0,False,True)]
    # Exactly these three positions: edge-decision instrumentation, approach
    # request, and supported final-pit continuation. No other policy changes.
    assert text.count('full_solid(x+4,y+32)')==3;text=text.replace('full_solid(x+4,y+32)','full_solid(x+5,y+32)')
    assert text.count('edge_missing=not forward,edge_tile=edge_tile,')==1
    text=text.replace('edge_missing=not forward,edge_tile=edge_tile,','edge_missing=not forward,edge_tile=edge_tile,edge_probe_dx=5,')
    for guard in["q.native_state==0 and(q.foot[2].solid or q.foot[4].solid)",
                  "full_state(actor+9)==0 and full_state(actor+1)&128~=0",
                  "r('Player_State')~=0 or ram(142)~=0",'if#full_clears~=7',
                  'if full_stationary>500',"full_stair_target=x-6"]:assert guard in text
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-current-landing-'+args.identity+'-full11-reachable-pit');assert not target.exists()
    prepare(target,O/'combined-current-landing.nes',text,
        [Path(__file__),source,proof,O/'landing-current-supplement-v35.zip',O/'combined-current-landing.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Actualv34 missing final-pit ingress resolved only by controller lookahead4to5. ReachableX2443 remains native0/DY0/leftfoot; actualnextX2445 is native2 and remainsrejected. BothIDs actualGameCore source fixture at actualcamera2364/clock21 qualifies D36B2443(leftfoot)then2472(rightfoot), supportedfarlanding2501/Y128/native0. Every physicalnative0/realfoot/A/nobubblemarker/max2 guard unchanged; same6pxstairretreat/6earnedbubblecrossings/naturalcombat/noinjury/lives/all7crossings/actual1-2/sourcehardware assertions. Current9cf keepsSunny5patches; no gameplaybyte, sourcephysics, resources orhelperschanged. Boundedge decisions include actual5pxprobe.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(k))==v for k,v in ready['bindings'].items())
    print(json.dumps(dict(READY=True,immutable=True,identity=args.identity,ROM_sha256=PIN,path=str(target),all_bindings_verified=True,Lua54_syntax=True)))


if __name__=='__main__':main()
