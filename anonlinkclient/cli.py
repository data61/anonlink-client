import difflib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from multiprocessing import freeze_support
from typing import Callable, List
import click
import clkhash
from bashplotlib.histogram import plot_hist
from clkhash import benchmark as bench
from clkhash import randomnames, validate_data
from clkhash.describe import get_encoding_popcounts
from clkhash.schema import SchemaError, convert_to_latest_version, validate_schema_dict
from clkhash.serialization import deserialize_bitarray, serialize_bitarray
import anonlinkclient
from clkhash.clk import generate_clk_from_csv
from .utils import (
    deserialize_bitarray,
    generate_candidate_blocks_from_csv,
    combine_clks_blocks,
    deserialize_filters,
    solve,
)

# Labels for some options. If changed here, the name of the corresponding attributes MUST be changed in the methods
# using them.
VERBOSE_LABEL = "verbose"
REST_CLIENT_LABEL = "rest_client"
SERVER_LABEL = "server"
RETRY_MULTIPLIER_LABEL = "retry_multiplier"
RETRY_MAX_EXP_LABEL = "retry_max_exp"
RETRY_STOP_LABEL = "retry_stop"


def log(m, color="red"):
    click.echo(click.style(m, fg=color), err=True)


def set_verbosity(ctx, param, value):
    """
    verbose_option callback

    Set the script verbosity in the click context object which is assumed to be a dictionary.
    Note that if the verbosity is set to true, it cannot be brought back to false in the current context.
    """
    if ctx.obj is None or not ctx.obj.get(VERBOSE_LABEL):
        ctx.obj = {VERBOSE_LABEL: value}
    verbosity = ctx.obj.get(VERBOSE_LABEL)
    return verbosity


# This option will be used as an annotation of a command. If used, the command will have this option, which will
# automatically set the verbosity of the script. Note that the verbosity is global (set in the context), so the commands
#     anonlink -v status [...]
# is equivalent to
#     anonlink status -v [...]
verbose_option = click.option(
    "-v",
    "--verbose",
    VERBOSE_LABEL,
    default=False,
    is_flag=True,
    help="Script is more talkative",
    callback=set_verbosity,
)


def add_options(options):
    # type: (List[Callable]) -> Callable
    """
    Used as an annotation for click commands.
    Allow to add a list of options to the command
    From https://stackoverflow.com/questions/40182157/python-click-shared-options-and-flags-between-commands

    :param options: List of options to add to the command
    """

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def is_verbose(ctx):
    """
    Use the click context to get the verbosity of the script.
    Should have been set by the method set_verbosity.
    :param ctx:
    :return: None if not set, otherwise a boolean.
    """
    return ctx.obj.get(VERBOSE_LABEL)


@click.group("anonlink")
@click.version_option(anonlinkclient.__version__)
@verbose_option
def cli(verbose):
    """
    This command line application allows a user to hash their
    data into cryptographic longterm keys for use in
    private comparison.

    This tool can also interact with a entity matching service;
    creating new mappings, uploading locally hashed data,
    watching progress, and retrieving results.

    Example:

        anonlink hash private_data.csv secret schema.json output-clks.json


    All rights reserved Confidential Computing 2016.
    """


@cli.command("hash", short_help="generate hashes from local PII data")
@click.argument("pii_csv", type=click.File("r"))
@click.argument("secret", type=str)
@click.argument("schema", type=click.File("r", lazy=True))
@click.argument("clk_json", type=click.File("w"))
@click.option(
    "--no-header", default=False, is_flag=True, help="Don't skip the first row"
)
@click.option(
    "--check-header",
    default=True,
    type=bool,
    help="If true, check the header against the schema",
)
@click.option(
    "--validate",
    default=True,
    type=bool,
    help="If true, validate the entries against the schema",
)
@verbose_option
def hash(pii_csv, secret, schema, clk_json, no_header, check_header, validate, verbose):
    """Process data to create CLKs

    Given a file containing CSV data as PII_CSV, and a JSON
    document defining the expected schema, verify the schema, then
    hash the data to create CLKs writing them as JSON to CLK_JSON.

    It is important that the secret is only known by the two data providers. One word must be provided. For example:

    $anonlink hash pii.csv horse_stable pii-schema.json clks.json

    Use "-" for CLK_JSON to write JSON to stdout.
    """
    try:
        schema_object = clkhash.schema.from_json_file(schema_file=schema)
    except SchemaError as e:
        log(str(e))
        raise SystemExit(-1)
    header = True
    if not check_header:
        header = "ignore"
    if no_header:
        header = False

    try:
        clk_data = [
            serialize_bitarray(bf)
            for bf in generate_clk_from_csv(
                pii_csv,
                secret,
                schema_object,
                validate=validate,
                header=header,
                progress_bar=verbose,
            )
        ]
    except (validate_data.EntryError, validate_data.FormatError) as e:
        (msg,) = e.args
        log(msg)
        log("Hashing failed.")
    else:
        json.dump({"clks": clk_data}, clk_json)
        if hasattr(clk_json, "name"):
            log("CLK data written to {}".format(clk_json.name))


@cli.command("block", short_help="generate candidate blocks from local PII data")
@click.argument("pii_csv", type=click.File("r"))
@click.argument("schema", type=click.File("r", lazy=True))
@click.argument("block_json", type=click.File("w"))
@click.option(
    "--no-header", default=False, is_flag=True, help="Don't skip the first row"
)
@verbose_option
def block(pii_csv, schema, block_json, no_header, verbose):
    """Process data to create blocking information

    Given a file containing CSV data as PII_CSV, and a JSON
    document defining the blocking configuration, then generate
    candidate blocks writing to JSON output. Note the CSV
    file should contain a header row - however this row is not used
    by this tool.
    Setting the verbose flag outputs more detailed blocking statistics.

    For example:

    $anonlink block pii.csv blocking-schema.json blocks.json

    Use "-" for BLOCKS_JSON to write JSON to stdout.
    """
    header = True
    if no_header:
        header = False
    log("before generate_candidate_blocks_from_csv")
    # generate candidate blocks and save to json file
    result = generate_candidate_blocks_from_csv(
        pii_csv, schema, header, verbose=verbose
    )
    log("after generate_candidate_blocks_from_csv")
    json.dump(result, block_json, indent=4)
    log("after block_json "+os.path.realpath(block_json.name))


@cli.command("benchmark", short_help="carry out a local benchmark")
def benchmark():
    bench.compute_hash_speed(10000)


@cli.command("describe", short_help="show distribution of clk popcounts")
@click.argument("clk_json", type=click.File("r"))
def describe(clk_json):
    """show distribution of clk's popcounts using a ascii plot."""
    clks = json.load(clk_json)["clks"]
    counts = get_encoding_popcounts([deserialize_bitarray(clk) for clk in clks])
    plot_hist(counts, bincount=60, title="popcounts", xlab=True, showSummary=True)


@cli.command("convert-schema", short_help="converts schema file to latest version")
@click.argument("schema_json", type=click.File("r"))
@click.argument("output", type=click.File("w"))
def convert_schema(schema_json, output):
    """convert the given schema file to the latest version."""
    schema_dict = json.load(schema_json)
    validate_schema_dict(schema_dict)
    new_schema_dict = convert_to_latest_version(schema_dict, validate_result=True)
    json.dump(new_schema_dict, output)


@cli.command("generate", short_help="generate random pii data for testing")
@click.argument("size", type=int, default=100)
@click.argument("output", type=click.File("w"))
@click.option("--schema", "-s", type=click.File("r"), default=None)
def generate(size, output, schema):
    """Generate fake PII data for testing"""
    pii_data = randomnames.NameList(size)

    if schema is not None:
        raise NotImplementedError

    randomnames.save_csv(
        pii_data.names, [f.identifier for f in pii_data.SCHEMA.fields], output
    )


@cli.command(
    "generate-default-schema",
    short_help="get the default schema used in generated random PII",
)
@click.argument(
    "output", type=click.Path(writable=True, readable=False, resolve_path=True)
)
def generate_default_schema(output):
    """Get default schema for fake PII"""
    original_path = os.path.join(
        os.path.dirname(__file__), "data", "randomnames-schema.json"
    )
    shutil.copyfile(original_path, output)


@cli.command("validate-schema", short_help="validate linkage schema")
@click.argument("schema", type=click.File("r", lazy=True))
def validate_schema(schema):
    """Validate a linkage schema

    Given a file containing a linkage schema, verify the schema is valid otherwise
    print detailed errors.
    """

    try:
        clkhash.schema.from_json_file(schema_file=schema, validate=True)

        log("schema is valid", color="green")

    except SchemaError as e:
        log(str(e))
        raise SystemExit(-1)


@cli.command("compare-schema", short_help="compare two schemas")
@click.argument("schema1", type=click.File("r", lazy=True))
@click.argument("schema2", type=click.File("r", lazy=True))
@click.option(
    "-n",
    "output_format",
    flag_value="n",
    default=True,
    help="Produce a ndiff format diff (default)",
)
@click.option(
    "-u", "output_format", flag_value="u", help="Produce a unified format diff"
)
@click.option(
    "-m", "output_format", flag_value="m", help="Produce HTML side by side diff"
)
@click.option(
    "-c", "output_format", flag_value="c", help="Produce a context format diff"
)
@click.option(
    "-l",
    "num_context_lines",
    type=int,
    default=3,
    help="The number of context lines for context and unified format",
)
def compare_schema(schema1, schema2, output_format, num_context_lines):
    """Compare two schemas

    and output the differences. The output can be formatted in the following ways:

    \b
    - Context format:
      Context diffs are a compact way of showing just the lines that have
      changed plus a few lines of context. The changes are shown in a
      before/after style. The number of context lines is set by 'l' which
      defaults to three.
    - Unified format:
      Unified diffs are a compact way of showing just the lines that have
      changed plus a few lines of context. The changes are shown in an inline
      style (instead of separate before/after blocks). The number of context
      lines is set by 'l' which defaults to three.
    - HTML side by side:
      creates a complete HTML file containing a table showing a side by side,
      line by line comparison of text with inter-line and intra-line change
      highlights. It is advisable to pipe this output into a file and open it
      in your favorite browser.

      >>> anonlink compare-schema -m schema1.json schema2.json > diff.html

      \b
    - ndiff format (default):
      Produces human-readable differences. Each line begins with a two-letter
      code:

      \b
      ====== =========================================
      Code   Meaning
      ====== =========================================
      '- '   line unique to file 1
      '+ '   line unique to file 2
      '  '   line common to both sequences
      '? '   line not present in either input sequence
      ====== =========================================

      Lines beginning with ‘?’ attempt to guide the eye to intraline differences, and were not present in either
      input sequence. These lines can be confusing if the sequences contain tab characters.


    Example:

      \b
      schema A:                 schema B:
      {                         {
        "version": 3,             "version": 2,
        "clkConfig": {            "clkConfig": {
          "l": 1024                 "l": 1024,
        }                           "m": 33
      }                           }
                                }

    Output in ndiff format:

    \b
    {
    -   "version": 3,
    ?              ^
    +   "version": 2,
    ?              ^
        "clkConfig": {
    -     "l": 1024
    +      "l": 1024,
    ? +             +
    +      "m": 33
        }
    - }
    + }

    Output in unified format:

    \b
    --- schema_A.json       2020-06-24T10:58:23.005298+10:00
    +++ schema_B.json       2020-06-24T10:59:06.648638+10:00
    @@ -1,6 +1,7 @@
    {
    -  "version": 3,
    +  "version": 2,
       "clkConfig": {
    -    "l": 1024
    +     "l": 1024,
    +     "m": 33
       }
    -}

    Output in context format:

    \b
    *** schema_A.json       2020-06-24T10:58:23.005298+10:00
    --- schema_B.json       2020-06-24T10:59:06.648638+10:00
    ***************
    *** 1,6 ****
      {
    !   "version": 3,
        "clkConfig": {
    !     "l": 1024
        }
    ! }
    --- 1,7 ----
      {
    !   "version": 2,
        "clkConfig": {
    !      "l": 1024,
    !      "m": 33
        }
    ! }

    """

    def file_mtime(lazy_file):
        t = datetime.fromtimestamp(os.stat(lazy_file.name).st_mtime, timezone.utc)
        return t.astimezone().isoformat()

    fromdate = file_mtime(schema1)
    todate = file_mtime(schema2)

    if output_format == "m":
        # we encode the json into a readable format. No one wants a one-liner
        enc = json.JSONEncoder(sort_keys=True, indent=0)
        fromlines = [line for line in enc.iterencode(json.load(schema1))]
        tolines = [line for line in enc.iterencode(json.load(schema2))]
        diff = difflib.HtmlDiff().make_file(
            fromlines, tolines, schema1.name, schema2.name
        )
    else:
        fromlines = schema1.readlines()
        tolines = schema2.readlines()
        if output_format == "u":
            diff = difflib.unified_diff(
                fromlines,
                tolines,
                schema1.name,
                schema2.name,
                fromdate,
                todate,
                n=num_context_lines,
            )
        elif output_format == "n":
            diff = difflib.ndiff(fromlines, tolines)
        else:
            diff = difflib.context_diff(
                fromlines,
                tolines,
                schema1.name,
                schema2.name,
                fromdate,
                todate,
                n=num_context_lines,
            )
    sys.stdout.writelines(diff)


@cli.command(
    "find-similarity", short_help="find similarities between the two sets of CLKs"
)
@click.argument("threshold", type=float)
@click.argument("similarity_matches", type=click.File("w"))
@click.option(
    "--files",
    type=click.Tuple([click.File("r"), click.File("r")]),
    multiple=True,
    required=False,
)
@click.option("--clk", type=click.File("r"), multiple=True, required=False)
@click.option(
    "--blocking",
    type=bool,
    required=True,
    default=False,
)
def find_similarity(threshold, similarity_matches, files, clk, blocking):
    """
    Find similarities between multi party dataset with blocking and non-blocking methods

    Given a set of files containing CLKs and blocks data,
    generate similarty matches for multi party dataset
    The format of the ouput file is [[dataset_id, row_id], [dataset_id, row_id]]

    Example of similarity matching with blocks:
    $anonlink find-similarity 0.8 result.txt --files clk_a.json  blocks_a.json  --files clk_b.json  blocks_b.json --blocking True

    Example of similarity matching without blocks:
    $anonlink find-similarity 0.8 result.txt --clk clk_a.json  --clk  clk_b.json --blocking False
    """
    clk_groups = []
    rec_to_blocks = {}
    if blocking:
        clk_blocks = []
        for i, (clk_f, block_f) in enumerate(files):
            clk_blocks.append(
                json.load(combine_clks_blocks(clk_f, block_f))["clknblocks"]
            )

        for i, clk_blk in enumerate(clk_blocks):
            clk_groups.append(deserialize_filters([r[0] for r in clk_blk]))
            rec_to_blocks[i] = {rind: clk_blk[rind][1:] for rind in range(len(clk_blk))}
    else:
        for i, clk_blk in enumerate(clk):
            clk_groups.append(deserialize_filters([r for r in clk_blk]))

    found_groups = solve(clk_groups, rec_to_blocks, threshold, blocking)
    print("Found {} matches".format(len(found_groups)))
    json.dump(found_groups, similarity_matches, indent=4)


if __name__ == "__main__":
    freeze_support()
    cli()
