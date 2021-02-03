# Benchmark Results

## Beasley and Christofides (1989)

CPU time (ms)


| Instance | forward (elementary) | forward (non-elementary) | bidirectional (elementary) | bidirectional (non-elementary) |
|----------|------------|----------------|------------|----------------|
| 1        | 5          | 3              | 7          | 6              |
| 2        | 5          | 5              | 9          | 7              |
| 3        | 9          | 6              | 20         | 12             |
| 4        | 10         | 6              | 18         | 12             |
| 5        | 5          | 5              | 8          | 7              |
| 6        | 5          | 5              | 7          | 5              |
| 7        | 92         | 58             | 372        | 272            |
| 8        | 35         | 21             | 228        | 146            |
| 9        | 4          | 4              | 7          | 5              |
| 10       | 4          | 4              | 7          | 5              |
| 11       | 23         | 15             | 43         | 30             |
| 12       | 23         | 15             | 44         | 29             |
| 13       | 14         | 10             | 23         | 14             |
| 14       | 9          | 7              | 17         | 14             |
| 15       | 85         | 50             | 357        | 244            |
| 16       | 30         | 17             | 148        | 93             |
| 17       | 41         | 31             | 61         | 47             |
| 18       | 38         | 30             | 61         | 45             |
| 19       | 51         | 39             | 103        | 72             |
| 20       | 53         | 40             | 100        | 70             |
| 21       | 32         | 28             | 48         | 36             |
| 22       | 32         | 28             | 44         | 33             |
| 23       | 1102       | 836            | 3137       | 2536           |
| 24       | 366        | 233            | 1551       | 1171           |


### Comparison against `r_c_shortest_paths`

Some instances fail with bounds_pruning=true (only in the forward direction interestingly).
Unfair comparison as I ran the r_c_shortest_paths in docker and the others on my machine.

Both on docker see a lot worse results, but clear winner on hard instances (e.g. 5, 23 and 24).

Will be interesting to fix direction="both" to perform as it should (faster than just forward) and see

| Instance | r_c_shortest_paths (docker) | fwd_bounds_pruning (local) | Speed up (%) | fwd_bounds_pruning (docker) | Speed up (%) |
|----------|-----------------------------|----------------------------|--------------|-----------------------------|--------------|
| 1        | 4                           | 3                          | 25.00        | 5                           | -25.00       |
| 2        | 4                           | 3                          | 25.00        | 5                           | -25.00       |
| 3        | 3                           | 5                          | -66.67       | 8                           | -166.67      |
| 4        | 3                           | 5                          | -66.67       | 8                           | -166.67      |
| 5        | 125                         | 3                          | 97.60        | 5                           | 96.00        |
| 6        | 81                          | 3                          | 96.30        | 5                           | 93.83        |
| 7        | 53                          | 16                         | 69.81        | 31                          | 41.51        |
| 8        | 16                          | 19                         | -18.75       | 45                          | -181.25      |
| 9        | 2                           | 2                          | 0.00         | 3                           | -50.00       |
| 10       | 2                           | 2                          | 0.00         | 3                           | -50.00       |
| 11       | 7                           | 8                          | -14.29       | 18                          | -157.14      |
| 12       | 7                           | 8                          | -14.29       | 18                          | -157.14      |
| 13       | 7                           | 5                          | 28.57        | 10                          | -42.86       |
| 14       | 6                           | 3                          | 50.00        | 7                           | -16.67       |
| 15       | 38                          | 28                         | 26.32        | 49                          | -28.95       |
| 16       | 13                          | 14                         | -7.69        | 21                          | -61.54       |
| 17       | 39                          | -                          | -            | -                           | -            |
| 18       | 37                          | -                          | -            | -                           | -            |
| 19       | 18                          | -                          | -            | -                           | -            |
| 20       | 18                          | -                          | -            | -                           | -            |
| 21       | 71                          | 17                         | 76.06        | 24                          | 66.20        |
| 22       | 32                          | 16                         | 50.00        | 22                          | 31.25        |
| 23       | 4566                        | 28                         | 99.39        | 42                          | 99.08        |
| 24       | 274                         | 84                         | 69.34        | 131                         | 52.19        |
|          |                             | Average Speed up           | 26.25        |                             | -32.44       |

