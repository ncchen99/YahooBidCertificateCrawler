import re
pattern = r"[\s\S]*CCA[A-Z]{1}[A-Z0-9]{9,10}[\s\S]*"
if re.fullmatch(pattern, "CCA219LP1090T2"):
    print("match")
else:
    print("not match")
