"""Keep legacy guest clamp out of RCR's native-body terrain response."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 original=R/'build/river_city_shared_v7_build.py';proof=R/'build/river-city-shared-v7-overlay/build-proof.json';d=json.loads(proof.read_text())
 assert next(r['sha256']for r in d['bindings']if Path(r['path'])==original)==sha(original)
 src=original.read_text().replace('river-city-shared-v7','river-city-shared-v8')
 token="    output=R/'build/river-city-shared-v8.nes';assert not output.exists()";assert src.count(token)==1
 added='''    def wall_gate(s):
        start=s.index('.proc LmWallGate\\n');end=s.index('.endproc',start)
        body=once(s[start:end],' lda SelectedCharacter\\n',
             ' lda SelectedCharacter\\n cmp #CHARACTER_RIVER_CITY\\n beq RcNative\\n')
        body+='RcNative:\\n pla\\n plp\\n clc                          ; real native one-pixel residual response\\n rts\\n'
        return s[:start]+body+s[end:]
    edit('src/zelda2_link_terrain.s',wall_gate)
'''
 src=src.replace(token,added+token)
 generated=R/'build/river_city_shared_v8_build.py';assert not generated.exists();generated.write_text(src,newline='\n')
 subprocess.run([sys.executable,'-B',str(generated)],cwd=R,check=True)
 p=R/'build/river-city-shared-v8-overlay/build-proof.json';out=json.loads(p.read_text());out['bindings'].append(dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)))
 out['retained_negative']='Native Ryan a29f: X2706->2719. Typed v7 confirms pre-wall bounds alone insufficient: legacy SamusStopAtWallBanked left clamp still moves+15. Exact RCR-only cold gate returnsCLC to true native one-pixel response; all foreign cold paths require fresh fullcaller checks.'
 p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
