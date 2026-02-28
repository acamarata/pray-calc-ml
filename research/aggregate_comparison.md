# Aggregate D0 Values: Comparison Across Published Research

This file compiles all known aggregate solar depression angles (D0) for Fajr and Isha from published academic research. These are NOT per-night observation records. They represent mean angles reported across multi-night observation campaigns.

The structured data is in `aggregate_d0_values.csv` (same directory).

## Key Findings

### Fajr Depression Angle by Sky Quality

| Sky Quality | D0 Range | Mean D0 | Method | Notes |
| --- | --- | --- | --- | --- |
| Pristine/dark | 15.5-19.9 | 17.5 | SQM, naked-eye | Banyuwangi 19.9, Labuan Bajo 19.3, Jordan 19.5, Karimunjawa 15.5, Agam 16.7 |
| Rural/somewhat dark | 13.4-17.6 | 15.0 | SQM, DSLR, photometer | LAPAN stations, Tilong 14.4, Malaysian coast, Egyptian desert, Biak 13.4 |
| Suburban/somewhat bright | 12.3-17.0 | 13.8 | SQM | Bosscha 13.7, Pasuruan 13.9, Pontianak 12.3, Subang 12.7 |
| Urban/bright | 9.1-14.0 | 12.6 | SQM | Mangkangkulon 12.8, Medan 11.9, Depok 13.6, 15th of May City 12.7 |

### Isha Depression Angle by Sky Quality

| Sky Quality | D0 Range | Mean D0 | Method | Notes |
| --- | --- | --- | --- | --- |
| Pristine | 17.5-18.9 | 17.7 | SQM, naked-eye | Coonabarabran, Sabah, Kelantan coast |
| Rural | 14.0-16.5 | 15.4 | SQM | Malaysia east coast, Egypt |
| Urban (LP) | 11.5-12.9 | 12.2 | SQM | Putrajaya, Kuala Lumpur |

### Regional Summary

#### Southeast Asia (Indonesia + Malaysia)

- 58 Fajr entries, 16 Isha entries (including 15 Basthoni 2022 per-site means)
- Latitude range: 10.1S to 7.2N (equatorial)
- Fajr D0: 11.9-19.9 (wide range driven by light pollution gradient)
- Dark Indonesian sites (Banyuwangi, Labuan Bajo, Mombhul Beach): 19.1-19.9
- Basthoni 2022 dark-sky mean across 594 nights: 16.3
- Basthoni 2022 somewhat dark mean across 380 nights: 14.1
- Basthoni 2022 somewhat bright mean across 418 nights: 13.4
- Basthoni 2022 bright/urban mean across 229 nights: 12.8
- LAPAN 8-station mean: 16.51 (moderate sky quality)
- Urban LP sites (Medan 11.9, Mangkangkulon 12.8, Depok 13.6): 11.9-13.6
- Isha data mostly from Malaysian SQM campaigns: 11.5-18.0

#### Middle East / North Africa (Egypt, Saudi, Libya, Mauritania, Jordan)
- 19 Fajr entries, 4 Isha entries
- Latitude range: 18N to 32N
- Fajr D0: 12.7-19.5 (Egypt urban vs Jordan pristine)
- Egypt NRIAG multi-site mean: 14.56 (consistent across 6 sites)
- Saudi Hail desert: 14.0 (SQM+photoelectric, 32 nights)
- Libya Tubruq: 13.48 (1053 naked-eye observations)
- Jordan pristine: 19.5 (naked-eye, very dark sites)

#### Europe / UK
- 4 Fajr entries, 2 Isha entries
- Latitude: 51.2N to 53.7N
- Fajr D0: 15.0-18.0 (Blackburn to Ankara)
- Isha D0: 15.0 (Exmoor, Blackburn)

### Interpretation Notes

1. Sky quality is the dominant factor in D0 variation. Pristine sites consistently produce 17-19 degree angles, while urban sites produce 12-14 degrees. This is not measurement error but reflects when the twilight signal becomes distinguishable from artificial sky glow.

2. The Egypt NRIAG studies show remarkable consistency (14.5-14.7) across desert and Mediterranean sites, suggesting this is a robust estimate for low-LP Middle Eastern sites.

3. The LAPAN 16.51 degree mean across 8 Indonesian stations is a good representative value for the region's typical sky quality.

4. The 100k-row target in the PRI is aspirational. Published per-night observation data worldwide totals approximately 4,500-5,000 records (dominated by OpenFajr Birmingham). Reaching 10,000+ requires institutional data sharing.

## Sources

See `aggregate_d0_values.csv` for the full structured dataset with coordinates, methods, and citations.
