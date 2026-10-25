from pathlib import Path
import importlib.util
base=Path(__file__).with_name('extend_pz_mmc3_v7.py')
spec=importlib.util.spec_from_file_location('v7',base);v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)
def apply(source):
 v7.apply(source)
 p=source/'src/megaman_weapons.s';t=p.read_text()
 a='  .res 37,$ea\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"'
 b='  .assert *-MegaManFullShotBank=18,error,"MMC3 full-shot jump wrapper has no dead preservation padding"'
 assert t.count(a)==1;t=t.replace(a,b);p.write_text(t)
 p=source/'smb1base-mmc3-oversized.cfg';t=p.read_text()
 a='    SAMUS_CROUCH_WATER: load = PRGLow, type = ro, optional=yes;\n'
 assert t.count(a)==1;t=t.replace(a,'')
 a='    SAMUS_CROUCH_BODY: load = PRGFix, type = ro, optional=yes;'
 assert t.count(a)==1;t=t.replace(a,a+'\n    SAMUS_CROUCH_WATER: load = PRGFix, type = ro, optional=yes;');p.write_text(t)
