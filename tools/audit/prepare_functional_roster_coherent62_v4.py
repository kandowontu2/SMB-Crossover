"""Join the frozen genuine SMB2 cold draw/name worker into coherent62.

All four source fixes remain private. The earlier metadata/DMC/stream
preparation negatives are separate immutable packets, never replayed in place.
"""
from pathlib import Path
p=Path(__file__).with_name('prepare_functional_roster_coherent62_v3.py');ns={'__file__':str(p),'__name__':'prepare_only'}
t=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'');exec(compile(t,str(p),'exec'),ns)
s=ns['s'].replace('functional-roster-coherent62-v3','functional-roster-coherent62-v4')
s=s.replace("O=R/'build/functional-roster-coherent62-v4';", "S2=R/'build/smb2-current-cold-render-v29'\nO=R/'build/functional-roster-coherent62-v4';")
s=s.replace("inputs=[P/'handoff.json',F/'handoff-source-v1.json']","inputs=[P/'handoff.json',F/'handoff-source-v1.json',S2/'handoff.json']")
a=" def edit(p,t):"
b=""" for relative in ['component.s','smb2/smb2_roster.s','smb2/smb2_roster_host_v5.s']:
  shutil.copyfile(S2/relative,J/relative)
"""+a
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("['FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF']","['FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF','SMB2 MARIO','SMB2 LUIGI','SMB2 TOAD','SMB2 PEACH']")
s=s.replace("c[1:1]=['-I',str(J/'src'),'-I',str(J)]","c[1:1]=['-I',str(J),'-I',str(J/'src')]")
a=" link=json.loads(read(P/'final-link.json'))['command'][:]"
b=""" c=json.loads(read(S2/'component-build.json'))['command'][:]
 c[1:1]=['-I',str(J),'-I',str(J/'smb2'),'-I',str(J/'src')]
 for flag in ['-o','--create-full-dep','--create-dep']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 c[-1]=str(J/'component.s');recipes.append(('s2-component-build',c))
"""+a
assert s.count(a)==1;s=s.replace(a,b)
a=" if x==str(P/'joint/main.o')or x in [str(BASE/(n+'.o'))for n in names]:link[i]=str(J/Path(x).name)"
b=" if x in [str(P/'joint/main.o'),str(R/'build/functional-roster-smb2-v1/joint/component.o')]or x in [str(BASE/(n+'.o'))for n in names]:link[i]=str(J/Path(x).name)"
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("'SOURCE_LINKED62_TARGETED_COLD_MAIN_CONTROLS_PENDING_S2_COLD_VISIBILITY_HOLD'","'SOURCE_LINKED62_GENUINE_COLD_DRAW_JOINED_TARGETED_CONTROLS_PENDING'")
s=s.replace("S2service17metadataonly nativeemptycold preview; awaitownsourcefix; FF source334b observer pattern-view issue underrootreview.","OldS2coldnativeemptynegative retained; genuinev29sourcefix nowjoined, exact finalcart targeted/nativequalification pending. FF334bThiefnative source originalpixelpass bound separately.")
exec(compile(s,__file__,'exec'),globals())
