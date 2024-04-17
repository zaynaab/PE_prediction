Raw data to final modeling

Pre-processing:

samenvatting_notwinsProcess.py
weightProcess.py
heartrateProcess.py

Removes duplicates, and matches diastolic/systolic values.
bloodPressureProcess.py

Interpolates values, and finishes processing BP data by user.
bloodPressureModelBuildUsers.py

Generates additional values (no necessary operations, but further modeling performed on files generated with this script).
modelBP_ModParameters.py


Modeling
bpHMM.py

Supplementary scripts
Returns user if it passes criteria
appendEntry.py
Generate summary values from model results
summarizeGest.py

