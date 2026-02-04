from pybaseball import batting_stats, cache
from nameparser import HumanName
cache.enable()
fangraphs_2025 = batting_stats(2025, 2025)
fangraphs_2025['Name'] = fangraphs_2025['Name'].apply(
    lambda x: f"{HumanName(x).last}{(' ' + HumanName(x).suffix) if HumanName(x).suffix else ""}, {HumanName(x).first}"
)
fangraphs_2025.replace('- - -', '2TM', inplace=True)
fangraphs_2025.to_csv('data/team_data.csv', index=False)