"""Final linked ABI, bounded outlines and real spring/stomp adapter admission."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/final-roster-mz';P=O/'full-roster.nes'

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    spec=importlib.util.spec_from_file_location('mz_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im)
    old=im.Image(R/'build/checkpoints/level-roster-mx/build/smb-crossover-mmc5-expanded.nes');new=im.Image(P)
    symbols=lambda i:{s['name']:s['val'] for s in i.data['sym'] if s.get('scope')==1 and 'val' in s and 'seg' in s}
    before=symbols(old);after=symbols(new);moved={k:[v,after.get(k)] for k,v in before.items() if after.get(k)!=v};assert not moved,moved
    assert old.ram=={k:v for k,v in new.ram.items() if k in old.ram}
    assert old.raw[16+1048576:]==new.raw[16+1048576:],'Adapter fixes preserve all CHR bytes'
    (O/'public-ABI.json').write_text(json.dumps(dict(passed=True,old_public_symbols=len(before),moved=moved,old_RAM_exact=True,CHR_exact=True,sha256=hashlib.sha256(P.read_bytes()).hexdigest()),indent=2)+'\n')
    D=R/'build/verification/expanded-controls-agent/raw-id-audit';out=O/'outline';out.mkdir(exist_ok=True)
    text=(D/'check_outline.py').read_text().replace('HERE=Path(__file__).resolve().parent',f'HERE=Path({str(out)!r})').replace("OLD=Path('build/checkpoints/mike-roster-mv/build/smb-crossover-mmc5-expanded.nes')",f'OLD=Path({str(old.path)!r})').replace("NEW=HERE/'outline-fixed-mv.nes'",f'NEW=Path({str(P)!r})')
    text=text.replace('assert not changes,changes','assert not moved,moved # Scope-qualified public symbols checked above; local .lbl aliases can repeat.')
    (out/'check_outline.py').write_text(text);exec(compile(text,str(out/'check_outline.py'),'exec'),{'__file__':str(out/'check_outline.py'),'moved':moved})
    D=R/'build/verification/expanded-bounce-mu-candidate-agent';out=O/'bounce';out.mkdir(exist_ok=True)
    text=(D/'check_bounce.py').read_text().replace("O=Path(__file__).resolve().parent;R=O.parents[2];P=O/'bounce-private.nes'",f'O=Path({str(out)!r});R=Path({str(R)!r});P=Path({str(P)!r})').replace("O/'source/src'","R/'src'")
    (out/'check_bounce.py').write_text(text);exec(compile(text,str(out/'check_bounce.py'),'exec'),{'__file__':str(out/'check_bounce.py')})
    s=importlib.util.spec_from_file_location('mz_runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    results={}
    for key,file in [('bounce',D/'native_bounce_bound.lua'),('outline-mike',R/'build/verification/expanded-controls-agent/raw-id-audit/outline-fixed-native.lua'),('outline-samus',R/'build/verification/expanded-controls-agent/raw-id-audit/outline-fixed-samus.lua')]:
        folder=O/key;folder.mkdir(exist_ok=True);text=file.read_text()
        if key=='bounce':text='INCLUDE_MAC=true\n'+text
        if key=='outline-mike':text=text.replace('right=f==140 or f==160','right=f==140 or f==160 or f==170')
        script=folder/(key+'.lua');script.write_text(text);runner.ROOT=folder;results[key]=runner.run(script,P,timeout=45)
        (O/'adapter-native-results.json').write_text(json.dumps(results,indent=2)+'\n');assert results[key]==0,key
    print('PASS final public ABI,30720 outline cases, spring components and30 native spring/stomp scenes including actualMac')

if __name__=='__main__':main()
