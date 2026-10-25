from pathlib import Path
D=Path(__file__).resolve().parent;f=D/'build_pz_mmc3_private_v12.py';t=f.read_text();a="R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent";b="D=Path(__file__).resolve().parent;R=D/'native-probes-qa-v2/packet-v1/source'";assert t.count(a)==1;t=t.replace(a,b).replace("O=D/'ryu-head-oversized-mmc3-v12'","O=D/'native-probes-qa-mmc3-compat-v13'")
a="str(R/'tools/Windows/cc65/bin/cl65.exe')";assert t.count(a)==1;t=t.replace(a,"'C:/Users/kando/Documents/ChatGPT/SMB Crossover/tools/Windows/cc65/bin/cl65.exe'")
t += "\nassert report['ROM_sha256']=='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867','MMC3 bytes changed unexpectedly'\n"
# The original exits before appended code; make the same final assertion run
# before that existing exit, so neither a host exception nor mismatch is hidden.
t=t.replace("raise SystemExit(p.returncode)","assert p.returncode==0 and report['ROM_sha256']=='43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867'\nraise SystemExit(p.returncode)")
(D/'build_native_probes_qa_mmc3_compat_v13.py').write_text(t)
