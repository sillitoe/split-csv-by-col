#!/usr/bin/env python3
"""
Script that splits a CSV file into multiple files based on the contents of a specified column.

For large files, it is recommended to sort the input file by the column you want to split on.

Input CSV file:

test.csv
```
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED01	3.40.50.300	94.83	5o8wA01
AF-A0A0A7M1B3-F1-model_v4_TED02	2.40.30.10	92.63	5o8wA02
```

Usage:

```
$ python split_csv_by_col.py -i test.csv -n 2 --stub test- --suffix .csv
```

Output:

test-3.40.50.300.csv
```
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED01	3.40.50.300	94.83	5o8wA01
```

test-2.40.30.10.csv
``` 
ted_domain_id	foldseek_cath_code	overlap_percentage	hmm_id
AF-A0A0A7M1B3-F1-model_v4_TED02	2.40.30.10	92.63	5o8wA02
```

"""


import csv
import logging
import re
import click

logging.basicConfig(level="INFO")
LOG = logging.getLogger(__name__)


@click.command()
@click.option("-i", "input", required=True, help="input file")
@click.option(
    "-n",
    "column",
    required=True,
    type=int,
    help="column to split into output files (1-n)",
)
@click.option(
    "--stub", "output_stub", required=True, help="stub to use when writing output files"
)
@click.option(
    "--suffix",
    "output_suffix",
    default=".tsv",
    help="suffix to use when writing output files",
)
@click.option(
    "--use_headers", is_flag=True, default=True, help="use headers in input file"
)
@click.option("--delimiter", default="\t", help="CSV delimiter")
@click.option("--force", is_flag=True, default=False, help="callously ignore warnings")
def run(input, column, output_stub, output_suffix, delimiter, use_headers, force):

    seen_unique_fields = dict()

    with open(input, "r") as in_fh:
        in_reader = get_csv_reader(in_fh, delimiter=delimiter)
        if use_headers:
            headers = next(in_reader)
        last_unique_field = None
        current_unique_field = None
        out_fh = None
        out_writer = None
        for line_count, cols in enumerate(in_reader, 1):
            current_unique_field = cols[column - 1]

            # swap output file handles
            if current_unique_field != last_unique_field:
                if current_unique_field in seen_unique_fields:
                    msg = f"Already seen field '{current_unique_field}', you probably want to sort the input file before running this script (line: {line_count})"
                    if force:
                        LOG.warning(msg)
                    else:
                        raise KeyError(msg)

                if last_unique_field:
                    LOG.info(
                        f" ... wrote {seen_unique_fields[last_unique_field]} records (field: {last_unique_field})"
                    )

                out_file = get_output_filename(
                    output_stub, protect_filename(current_unique_field), output_suffix
                )
                LOG.info(f"Writing to {out_file} (field: {current_unique_field})")
                if out_fh:
                    out_fh.close()
                out_fh = open(out_file, "w")
                out_writer = get_csv_writer(out_fh, delimiter=delimiter)

                if current_unique_field not in seen_unique_fields:
                    seen_unique_fields[current_unique_field] = 0
                    if use_headers:
                        out_writer.writerow(headers)

            seen_unique_fields[current_unique_field] += 1

            out_writer.writerow(cols)

            last_unique_field = current_unique_field

        if out_fh:
            out_fh.close()

        total_records = sum(seen_unique_fields.values())
        total_files = len(seen_unique_fields.keys())
        LOG.info(f"Wrote {total_records} records to {total_files} files")
        LOG.info("Done")


def get_csv_reader(filehandle, delimiter):
    reader = csv.reader(filehandle, delimiter=delimiter)
    return reader


def get_csv_writer(filehandle, delimiter):
    writer = csv.writer(filehandle, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    return writer


def protect_filename(column_text):
    filename = re.sub(r"[^0-9a-zA-Z_.\-]", "", column_text)
    return filename


def get_output_filename(output_stub, unique_field, suffix):
    return f"{output_stub}{unique_field}{suffix}"


if __name__ == "__main__":
    run()
