import pandas as pd
df = pd.read_csv('data/processed/pp_trimmed_809PM.csv')
print(f'Shape: {df.shape}')
print(f'\n=== Columbia Energy Center ===')
columbia = df[df['plant_name'].str.contains('Columbia Energy', na=False)]
print(columbia[['plant_name', 'plant_code', 'year', 'consumption_mg', 'withdrawal_mg']])
print(f'Total Columbia rows: {len(columbia)}')

print(f'\n=== Gary Works ===')
gary = df[df['plant_name'].str.contains('Gary', na=False)]
if len(gary) > 0:
    print(gary[['plant_name', 'plant_code', 'year']])
else:
    print('No Gary Works found')
print(f'Total Gary rows: {len(gary)}')

print(f'\n=== Consumption > Withdrawal check ===')
excess = (df['consumption_mg'] > df['withdrawal_mg']).sum()
print(f'Rows where consumption_mg > withdrawal_mg: {excess}')

if excess > 0:
    print(f'\nSample of problematic rows:')
    problem = df[df['consumption_mg'] > df['withdrawal_mg']][['plant_name', 'year', 'consumption_mg', 'withdrawal_mg']].head(15)
    print(problem.to_string())

print(f'\n=== Summary ===')
print(f'Total rows in pp_trimmed_809PM.csv: {len(df)}')
print(f'Rows to remove:')
rows_to_remove = 0
if len(columbia) > 0:
    rows_to_remove += len(columbia)
    print(f'  - Columbia Energy Center: {len(columbia)} rows')
if len(gary) > 0:
    rows_to_remove += len(gary)
    print(f'  - Gary Works: {len(gary)} rows')
if excess > 0:
    rows_to_remove += excess
    print(f'  - Consumption > Withdrawal: {excess} rows')
print(f'Total rows to remove: {rows_to_remove}')
print(f'Remaining rows after cleaning: {len(df) - rows_to_remove}')
