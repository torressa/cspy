# Benchmark Results

## Beasley and Christofides (1989)

### Comparison against `r_c_shortest_paths`

time in ms

instance | both | fwd | best | boost
-- | -- | -- | -- | --
1 | 6 | 5 | 5 | 5
2 | 6 | 5 | 5 | 4
3 | 6 | 5 | 5 | 2
4 | 6 | 5 | 5 | 2
5 | 119 | 79 | 79 | 120
6 | 94 | 63 | 63 | 79
7 | 57 | 68 | 57 | 50
8 | 26 | 22 | 22 | 14
9 | 1 | 1 | 1 | 1
10 | 1 | 1 | 1 | 1
11 | 14 | 12 | 12 | 6
12 | 14 | 11 | 11 | 6
13 | 6 | 6 | 6 | 3
14 | 5 | 3 | 3 | 1
15 | 35 | 52 | 35 | 36
16 | 17 | 16 | 16 | 10
17 | 52 | 45 | 45 | 39
18 | 52 | 45 | 45 | 33
19 | 32 | 28 | 28 | 15
20 | 30 | 27 | 27 | 13
21 | 6 | 77 | 6 | 60
22 | 4 | 39 | 4 | 23
23 | 1148 | 2268 | 1148 | 4629
24 | 240 | 291 | 240 | 330
average | 82.38 | 132.25 | 77.875 | 228.42

### Replicate results

```bash
cd tools/dev/
./build -s
cat ../../build_boost/results_boost.txt
cat ../../build_boost/results_both.txt
cat ../../build_boost/results_fwd.txt
```
