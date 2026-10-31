"""Prepare additive exact-lives failure observer; no source edit or launch."""
from pathlib import Path
import difflib,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from current_roster_compact_11_v1 import linked,lua
P=R/'build/final62-smb2-bg-eye-native-1030-v1/class0';O=R/'build/smb2-lives-palette-diagnostic-v1/class0';J=R/'build/arthur-goku-smb2-palette-v1/joint';T=R/'tools/reference/smb2_lives_palette_diagnostic_v1.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir(parents=True);old=json.loads((P/'ready.json').read_text());assert sha(J/'candidate.nes')==old['ROM_sha256']=='37210891ffbf79373bf3390d16ead891b0e8f43408603a07273f12297a36121a'
 for p,h in old['bindings'].items():assert sha(p)==h,p
 raw,syms,address,location,hook=linked(J/'candidate.nes');diag=T.read_text(encoding='utf-8-sig');assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',diag)
 fields=set(re.findall(r"\br\('([^']+)'",diag))|{'VRAM_Buffer1'};prefix=[]
 for name in sorted(fields):
  v=address(name);assert v<32768,(name,v);prefix.append(f'assert(L[{lua(name)}]==nil or L[{lua(name)}]=={v},"Actual diagnostic alias {name}");L[{lua(name)}]={v}')
 hooks=[hook(n)for n in['S2MainPalette','S2NativePaletteHeader','GetPlayerColors','S2HostForcePalette','SamusFreezeUpdateScreen','PnHudPreUpdateScreen','UpdateScreen']]
 for name,offset in [('S2NativePaletteHeader',32),('S2MainPalette',59)]:
  h=hook(name,offset=offset);assert h['bytes'][0]==96,(name,h);h['name']+='-actual-RTS';hooks.append(h)
 prefix.append('S2_DIAGNOSTIC_HOOKS='+lua(hooks));s=(P/'controller.lua').read_text(encoding='utf-8');marker='local function uiDMA(stage,page)';assert s.count(marker)==1;s=s.replace(marker,diag+'\n'+marker)
 s='\n'.join(prefix)+'\n'+s
 # Correct only obvious Lua lexical spacing in the new additive observer.
 s=s.replace('and32 or1','and 32 or 1')
 assert s.count("'Actual original source body P0 '..stage")==1 and 'frame>=1200'in s
 (O/'controller.lua').write_text(s,encoding='utf-8',newline='\n');(O/'run.py').write_bytes((P/'run.py').read_bytes())
 (O/'observer.diff').write_text(''.join(difflib.unified_diff((P/'controller.lua').read_text().splitlines(True),s.splitlines(True),fromfile='unchanged-failed-v6',tofile='additive-diagnostic-v1')),encoding='utf-8',newline='\n')
 q=dict(old);q.update(predecessor=str(P/'ready.json'),predecessor_sha256=sha(P/'ready.json'),native_run=False,launch_authorized=False,observer='Additive actual palette tuple BEFORE original unchanged lives assert; all palette PPUDATA writes + native/source hook queue/register states; exact ROM/controller/guards/bounds unchanged.')
 files={Path(__file__).resolve(),T,O/'controller.lua',O/'run.py',O/'observer.diff',P/'ready.json',P/'controller.lua',P/'capture/candidate-controller.log',P/'capture/trace.csv',P/'capture/select-lives-OAM.csv',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl'}
 q['bindings']={**old['bindings'],**{str(p.resolve()):sha(p)for p in files}};(O/'ready.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
 for p,h in q['bindings'].items():assert sha(p)==h,p
 print(json.dumps(dict(prepared=str(O/'ready.json'),sha256=sha(O/'ready.json'),bindings=len(q['bindings']),candidate=q['ROM_sha256'],native=False)),flush=True)
if __name__=='__main__':main()
