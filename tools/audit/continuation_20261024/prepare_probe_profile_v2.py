from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'profile_pz_megaman_v5.py').read_text();a="O=BASE/'profile-megaman-v5'";assert t.count(a)==1;t=t.replace(a,"O=D/'native-probes-qa-v2/profile-v1'")
a="ROM=D/'ryu-head-candidate-v5/candidate.nes';route=BASE/'finish-v2/discover-megaman-easy'";assert t.count(a)==1;t=t.replace(a,"ROM=D/'native-probes-qa-v2/candidate.nes';route=D/'native-probes-qa-v2/routes-v1/megaman-easy'")
(D/'profile_native_probes_qa_v2.py').write_text(t)
