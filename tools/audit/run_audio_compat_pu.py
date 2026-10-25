"""Retain every OC compatibility case, adding exact owned UI/weapon ranges."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--inlined-special-leaf',action='store_true');p.add_argument('--native-mix-shortcut',action='store_true');p.add_argument('--tmnt-middle-probe',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    original=ROOT/'tools/audit/check_tmnt_audio_fallback_oc.py';data=original.read_bytes()
    assert hashlib.sha256(data).hexdigest()=='ea61148dbd4c4804b89e7fd02388558bb1bce573ae451fc6eb89d82ccccc5232'
    code=original.read_text()
    if a.inlined_special_leaf:
        # One of the five generated resident farcalls is now the exact7-byte
        # native leaf plus11bytes padding. Keep an explicit count assertion.
        assert code.count("qb[('_FARCALL_COUNT',)]+3")==1
        code=code.replace("qb[('_FARCALL_COUNT',)]+3","qb[('_FARCALL_COUNT',)]+2")
        code=code.replace('build_only_farcall_counter_delta=3','build_only_farcall_counter_delta=2')
    changes={
      'foreground={1:set(),4:set()}':'foreground={0:set(),1:set(),4:set()}',
      "('TnFastDrawSpan',3,'TnFastDrawGate')]":"('TnFastDrawSpan',3,'TnFastDrawGate'),('TnFastWeaponsSpan',18,'TnFastWeaponsGate')]",
      'if bank not in [1,4,38,123,124,125,127]:':'if bank not in [0,1,4,38,86,123,124,125,127]:',
    }
    for old,new in changes.items():assert code.count(old)==1,old;code=code.replace(old,new)
    if a.native_mix_shortcut:
        assert code.count('if bank not in [0,1,4,38,86,123,124,125,127]:')==1
        code=code.replace('if bank not in [0,1,4,38,86,123,124,125,127]:','if bank not in [0,1,4,29,38,86,123,124,125,127]:')
    marker="    hold=address(new,'TnAudioDacHold');dmc_cases=dispatch_cases=native_cases=0"
    assert code.count(marker)==1
    extra='''    # The native-UI shortcut changes only its old18-byte tail and an
    # appended leaf in bank86. Every original other bank86byte remains fixed.
    origin=qa[('X5OwnInventoryUi','Legacy')]-18
    pos=16+86*8192+origin-0xa000
    target=address(new,'X5NativeInventoryUiLeaf')
    assert after[pos:pos+18]==bytes([0x4c,target&255,target>>8])+bytes([0xea])*15
    bg=next(g for g in old['segs'].values()if g['name']=='"X5_BOUNCE"')
    ng=next(g for g in new['segs'].values()if g['name']=='"X5_BOUNCE"')
    start=int(bg['ooffs'],0);prior_size=int(bg['size'],0);new_size=int(ng['size'],0)
    assert start==int(ng['ooffs'],0)and int(bg['start'],0)+prior_size==target
    assert before[start+prior_size:start+new_size]==bytes([255])*(new_size-prior_size)
    allowed=set(range(pos,pos+18))|set(range(start+prior_size,start+new_size))
    actual={i for i in range(16+86*8192,16+87*8192)if before[i]!=after[i]}
    assert actual<=allowed,actual-allowed
    assert before[:16]==after[:16]and before[16+128*8192:]==after[16+128*8192:],'Header and every CHR byte preserved'
'''
    code=code.replace(marker,extra+marker)
    if a.native_mix_shortcut:
        extra_mix='''    pos=location(new,'X5NativeNoiseSpan');assert (pos-16)//8192==29
    changed={i for i in range(16+29*8192,16+30*8192)if before[i]!=after[i]}
    assert changed<=set(range(pos,pos+3))
    old_operand=address(old,'GuestMixChanged');target=address(new,'X5NativeNoiseMask')
    assert before[pos:pos+3]==bytes([0x0d,old_operand&255,old_operand>>8])
    assert after[pos:pos+3]==bytes([0x20,target&255,target>>8])
'''
        code=code.replace(marker,extra_mix+marker)
    if a.tmnt_middle_probe:
        old_list='if bank not in [0,1,4,29,38,86,123,124,125,127]:'
        assert code.count(old_list)==1
        code=code.replace(old_list,'if bank not in [0,1,4,29,38,86,89,123,124,125,127]:')
        extra_probe='''    pos=location(new,'TnMiddleProbeSpan');assert (pos-16)//8192==89
    prior_target=address(old,'BlockBufferColli_Side');target=address(new,'TnSideMiddleProbe')
    assert before[pos:pos+3]==bytes([0x20,prior_target&255,prior_target>>8])
    assert after[pos:pos+3]==bytes([0x20,target&255,target>>8])
    bg=next(g for g in old['segs'].values()if g['name']=='"TMNT_COMBAT"')
    ng=next(g for g in new['segs'].values()if g['name']=='"TMNT_COMBAT"')
    start=int(bg['ooffs'],0);prior=int(bg['size'],0);size=int(ng['size'],0)
    assert start==int(ng['ooffs'],0)and int(bg['start'],0)+prior==target
    assert before[start+prior:start+size]==bytes([255])*(size-prior)
    changed={i for i in range(16+89*8192,16+90*8192)if before[i]!=after[i]}
    assert changed<=set(range(pos,pos+3))|set(range(start+prior,start+size))
'''
        code=code.replace(marker,extra_probe+marker)
    fixture=a.output/'checker.py';fixture.write_text('import sys\nsys.path.insert(0,'+json.dumps(str(ROOT/'tools/audit'))+')\n'+code)
    args=[sys.executable,str(fixture),'--rom',str(a.rom.resolve()),'--baseline',str(a.baseline.resolve()),'--output',str(a.output/'checks')]
    r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(a.output/'host.log').write_text(r.stdout+r.stderr)
    print((r.stdout+r.stderr)[-2500:],flush=True);return r.returncode
if __name__=='__main__':raise SystemExit(main())
