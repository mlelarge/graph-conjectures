import os
import sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k4_ground
t0 = time.time()
checked, mism, details = k4_ground.validate_encoding()
print(f"checked={checked} random tournaments n in 4..7, mismatches={mism} ({time.time()-t0:.1f}s)")
if mism:
    for d in details[:10]:
        print("MISMATCH", d)
