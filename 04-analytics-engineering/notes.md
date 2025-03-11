rank() vs dense_rank()

For cases where more than one row has the same rank, say there are 2 rows rank 1 and 3 rows rank 2. If you use rank, the next rank will start with 6.
If you use dense rank, it will just start with rank 3.


percentile_con()