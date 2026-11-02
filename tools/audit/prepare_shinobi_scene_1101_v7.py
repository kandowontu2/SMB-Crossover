"""Compose scene ingress on the verified Shinobi CHR successor."""
import prepare_shinobi_chr_1101_v6 as B
B.BASE=B.O
B.O=B.R/'build/shinobi-scene-1101-v7'
B.PIN='e3bec84b8721984bebd84dfd1121080b21d95e4662a829611987ed0addd3657b'
B.SCENE=True
if __name__=='__main__':B.main()
