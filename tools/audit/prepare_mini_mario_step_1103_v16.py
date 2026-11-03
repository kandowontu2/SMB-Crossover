"""Compile first source-state slice with proven motion and root native sampler.

No ROM or shared/native allocation. Successor tests must qualify the complete
Step before native admission. Original extended states reject explicitly.
"""
from pathlib import Path
import hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
R,O=W.R,W.O
sha=W.sha
INC=R/'tools/reference/mini_mario_world_1103_v16.inc'

def build():
    source=(O/'motion-proposed-v11.s').read_text()
    body=INC.read_text()
    body='.macpack longbranch\n'+re.sub(r'(?m)^(\s*)b(cc|cs|eq|ne|mi|pl|vc|vs)\b',r'\1j\2',body,flags=re.I)
    tile=(R/'build/mini-mario-native-tile-1103-v13/native-tile.s').read_text().replace('.segment "MINI_NATIVE"','.segment "CODE"')
    return W.assemble('world-step-v16',source+'\n'+body+'\n'+tile)

def main():
    data,L=build()
    fields={name:int(value,16)for name,value in re.findall(r'^(Mini\w+)\s*=\s*\$([0-9A-Fa-f]+)',INC.read_text(),re.M)}
    out=dict(passed=True,compiled_only=True,CPU_qualified=False,native_admitted=False,bytes=len(data),code_range=[0xa000,0xa000+len(data)],SHA256=sha(data),exports=L,fields=fields,source_motion_prefix_842_exact=data[:842]==(O/'motion-proposed-v11.bin').read_bytes(),ABI='MiniInit clearsC200..C280; caller then sets sourceX/Y16.4,boundsL/R/T/B signedintegerpixels,viewportEdgeLeft/Right16.4; heldNES C248. MiniStep maintains edges and originalqueuedstate C228. NativeTile usesC2E0..E9 and exactimmutable D000..D100 table. Climb/swim/blank rejectfault1; attachedplatform rejects2. Rootmustimplement nativehead/power/death/platform imports; no host writes.',scope='Ground/fall/crouch/skid/jump dispatcher and source8px collision kernel; extended source tileX16-bit for SMB. This first receipt is compilation only, not originalC differential or native qualification.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),INC,O/'world-inputs-v11.json',R/'build/mini-mario-native-tile-1103-v13/native-tile.s',R/'build/mini-mario-native-tile-1103-v13/receipt.json']})
    assert out['source_motion_prefix_842_exact']
    (O/'world-step-v16.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','compiled_only','CPU_qualified','bytes','code_range','SHA256','exports']}))
if __name__=='__main__':main()
