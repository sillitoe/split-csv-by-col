# split-csv-by-col

Script that splits a CSV file into multiple files based on the contents of a specified column.

To avoid IO issues, it expects that the input file has already been sorted by the column to be split on.

## Usage

```
$ python split_csv_by_col.py -i test.csv -n 2 --stub test- --suffix .csv
```

Input CSV file:

`test.csv`

```
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED01	3.40.50.300	94.83	5o8wA01
AF-A0A0A7M1B3-F1-model_v4_TED02	2.40.30.10	92.63	5o8wA02
```

Output:

`test-3.40.50.300.csv`

```
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED01	3.40.50.300	94.83	5o8wA01
```

`test-2.40.30.10.csv`

```
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED02	2.40.30.10	92.63	5o8wA02
```
