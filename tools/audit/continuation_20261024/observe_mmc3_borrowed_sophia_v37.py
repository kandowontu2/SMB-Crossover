from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'observe_mmc3_borrowed_motion_v25_v2.py').read_text(encoding='utf-8')
s=s.replace("V=D/'mmc3-ship-lives-v25';O=V/'borrowed-motion-v2'","V=D/'mmc3-static-call-v37';O=V/'borrowed-sophia-v1'")
s=s.replace("for name in ['proto','bill','lance']:","for name in ['sophia']:")
s=s.replace("route=V/'remaining-routes-v1'/(name+'-easy')","route=V/'native-sophia-v2/fresh'")
s=s.replace('three previously rejected raw endFrame motion traces','the five Sophia physical-frame query origins from the independently captured current-hash route')
exec(compile(s,str(D/'observe_mmc3_borrowed_motion_v25_v2.py'),'exec'),globals())
