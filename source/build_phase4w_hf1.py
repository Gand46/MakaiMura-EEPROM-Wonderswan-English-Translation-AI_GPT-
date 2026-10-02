#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys,json
from verify_bps import apply as bps_apply

def sha(b): return hashlib.sha256(b).hexdigest()
EXPECTED_JP='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
EXPECTED_S='b9e1d32b90b7820114cc1106e4cd481f304f9233072024ca65c7ce8c41d0f1c9'
EXPECTED_W='f9ad88e458fd603081bde91cf3f49399307f96e65016b3123410095e7a1d11dd'
D=0x1D0000
RESTORE=((0x32D0,0x366F),(0xFF77,0x10000))

def main():
 if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf1.py original_jp.ws [out.ws]')
 base=Path(sys.argv[1]).read_bytes(); outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF1_PRIVATE.ws')
 if sha(base)!=EXPECTED_JP: raise SystemExit('wrong original JP SHA-256: '+sha(base))
 root=Path(__file__).resolve().parent.parent
 s=bps_apply(base,(root/'reference/Makaimura_EN_US_Phase4S_CUMULATIVE_FROM_JP.bps').read_bytes())
 w=bps_apply(base,(root/'reference/Makaimura_EN_US_Phase4W_CUMULATIVE_FROM_JP.bps').read_bytes())
 if sha(s)!=EXPECTED_S: raise SystemExit('Phase4S reconstruction mismatch')
 if sha(w)!=EXPECTED_W: raise SystemExit('Phase4W reconstruction mismatch')
 out=bytearray(w)
 for a,b in RESTORE: out[D+a:D+b]=s[D+a:D+b]
 out[-2:]=(sum(out[:-2])&0xffff).to_bytes(2,'little'); out=bytes(out)
 outp.write_bytes(out)
 print(json.dumps({'sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','restored_ranges_D000':[[hex(a),hex(b)] for a,b in RESTORE]},indent=2))
if __name__=='__main__': main()
