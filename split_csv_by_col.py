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
import re
import click


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

    app = CsvSplitter(
        input_file=input,
        column=column,
        output_stub=output_stub,
        output_suffix=output_suffix,
        delimiter=delimiter,
        use_headers=use_headers,
        force=force,
    )
    app.run()


class CsvSplitter:
    """
    Splits a CSV into multiple files based on the contents of a specified column.
    """

    def __init__(
        self,
        input_file,
        column,
        output_stub,
        output_suffix,
        delimiter,
        use_headers,
        force,
    ):
        self.input_file = input_file
        self.column = column
        self.output_stub = output_stub
        self.output_suffix = output_suffix
        self.delimiter = delimiter
        self.use_headers = use_headers
        self.force = force

        self._headers = None
        self._last_field = None
        self._records_by_field = dict()
        self._out_fh = None
        self._out_writer = None

    def run(self):

        with open(self.input_file, "r") as in_fh:
            in_reader = get_csv_reader(in_fh, delimiter=self.delimiter)
            if self.use_headers:
                self._headers = next(in_reader)

            current_field = None
            for line_count, cols in enumerate(in_reader, 1):
                current_field = cols[self.column - 1]

                # swap output writer when we encounter a different field
                if current_field != self._last_field:
                    if current_field in self._records_by_field:
                        msg = f"Already seen field '{current_field}', you probably want to sort the input file before running this script (line: {line_count})"
                        if self.force:
                            click.echo(msg, err=True)
                        else:
                            raise KeyError(msg)

                    self.close_output_file()

                    self.init_output_file(current_field)

                self._records_by_field[current_field] += 1

                self._out_writer.writerow(cols)

                self._last_field = current_field

            self.close_output_file()

            total_records = sum(self._records_by_field.values())
            total_files = len(self._records_by_field.keys())

            click.echo(f"Wrote {total_records} records to {total_files} files")
            click.echo("Done")

    def close_output_file(self):
        if self._last_field:
            click.echo(
                f" ... wrote {self._records_by_field[self._last_field]} records (field: {self._last_field})"
            )

        if self._out_fh:
            self._out_fh.close()

    def init_output_file(self, current_field):
        out_file = get_output_filename(
            self.output_stub,
            protect_filename(current_field),
            self.output_suffix,
        )
        click.echo(f"Writing to {out_file} (field: {current_field})")

        self._out_fh = open(out_file, "w")
        self._out_writer = get_csv_writer(self._out_fh, delimiter=self.delimiter)

        if current_field not in self._records_by_field:
            self._records_by_field[current_field] = 0
            if self.use_headers and self._headers:
                self._out_writer.writerow(self._headers)


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
