# Naked Eye Determination of the Dawn at Tubruq of Libya Through Four Years Observations

**Authors:** A.H. Hassan and Yasser A. Abdel-Hadi
**Year:** 2015
**Journal:** Middle-East Journal of Scientific Research, 23(11): 2627-2632
**DOI:** 10.5829/idosi.mejsr.2015.23.11.22607
**URL:** https://www.idosi.org/mejsr/mejsr23(11)15/3.pdf
**Sites studied:** Tubruq, Libya (S2 site: desert background, 7km inland from coast)
**Observation method:** Naked eye
**Date range:** January 2010 to July 2013 (S2); December 2007 to December 2009 (S1)
**Records:** 623 twilight observations (S2), 429 (S1), total 1052
**Mean angle (Fajr):** S2: 13.144 +/- 0.757 (high confidence D0 = 14.7 using mean+2sigma)

## Location Details

- S1: 32 05'N, 23 59'E, 10m elevation, Mediterranean coast, water vapor background
- S2: 32 05'N, 23 59'E, 40m elevation, desert background, 7km south of S1

## Summary

The largest single-site naked-eye Fajr observation campaign in the published literature. 623 observations at site S2 (desert background, 40m elevation) from 2010-2013 produced a mean depression angle of 13.144 degrees with standard deviation 0.757 degrees. The distribution ranges from 11.13 to 14.7 degrees.

The paper uses the "high confidence" convention of D0 = mean + 2 sigma = 14.7 degrees, which represents the 99.77th percentile. The mode is 13.372 degrees (in the 13.14-13.39 range, 14.6% of observations).

S1 (coastal, water vapor background) gave a lower mean of 12.351 degrees with high confidence of 13.43 degrees, attributed to reduced visibility from water vapor.

Key Table 4 gives frequency distribution across 14 bins of width 0.255 degrees. Table 5 gives finer 0.1 degree bins in the 14.0-14.7 range (91 observations total, 14.4% of S2 data).

The paper compares the 14.7 result with the official Libyan value of 18.25, finding a difference of 3.55 degrees (18-23 minutes).

## Data Availability

**AGGREGATE ONLY.** The paper reports statistical distributions (Tables 1-5) and histograms, but does NOT publish per-night dates, times, or individual D0 values. Only bin counts are available.

The 14-bin frequency distribution (Table 4) and 7-bin fine distribution (Table 5) provide histogram data that could be used for distribution modeling, but not per-night angle extraction.

## For ML Training

This paper cannot provide per-night training rows. However, the aggregate statistics are valuable:
- n=623, mean=13.144, sigma=0.757, min=11.13, max=14.7 at lat 32.08, lng 23.98, elev 40m
- Can generate representative seasonal samples using the distribution parameters
- Already referenced in research/aggregate_d0_database.csv
