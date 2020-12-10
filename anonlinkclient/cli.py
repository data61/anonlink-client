import difflib
import io
import json
import ijson
import os
import sys
import shutil
from datetime import datetime, timezone
from multiprocessing import freeze_support
from typing import List, Callable

import click
from bashplotlib.histogram import plot_hist

import clkhash

from clkhash import benchmark as bench, randomnames, validate_data
from clkhash.describe import get_encoding_popcounts
from clkhash.serialization import serialize_bitarray, deserialize_bitarray
from clkhash.schema import SchemaError, validate_schema_dict, convert_to_latest_version
from minio import Minio
from .progress import Progress
from minio.credentials import ChainedProvider, StaticProvider, AWSConfigProvider

from .rest_client import ClientWaitingConfiguration, ServiceError, format_run_status, RestClient


import anonlinkclient
from .utils import generate_clk_from_csv, generate_candidate_blocks_from_csv, combine_clks_blocks, deserialize_bitarray


DEFAULT_SERVICE_URL = 'https://anonlink.easd.data61.xyz'

# Labels for some options. If changed here, the name of the corresponding attributes MUST be changed in the methods
# using them.
VERBOSE_LABEL = 'verbose'
REST_CLIENT_LABEL = 'rest_client'
SERVER_LABEL = 'server'
RETRY_MULTIPLIER_LABEL = 'retry_multiplier'
RETRY_MAX_EXP_LABEL = 'retry_max_exp'
RETRY_STOP_LABEL = 'retry_stop'


def log(m, color='red'):
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
verbose_option = click.option('-v', '--verbose', VERBOSE_LABEL, default=False, is_flag=True,
                              help="Script is more talkative", callback=set_verbosity)

# Set of options required for all the commands sending a request to the entity service server.
rest_client_option = [
    click.option('--server', SERVER_LABEL, type=str, default=DEFAULT_SERVICE_URL,
                 help="Server address including protocol. Default {}.".format(DEFAULT_SERVICE_URL)),
    click.option('--retry-multiplier', RETRY_MULTIPLIER_LABEL,
                 default=ClientWaitingConfiguration.DEFAULT_WAIT_EXPONENTIAL_MULTIPLIER_MS,
                 type=int, help="<milliseconds> If receives a 503 from server, minimum waiting time before retrying. "
                                "Default {}.".format(
            ClientWaitingConfiguration.DEFAULT_WAIT_EXPONENTIAL_MULTIPLIER_MS)),
    click.option('--retry-exponential-max', RETRY_MAX_EXP_LABEL,
                 default=ClientWaitingConfiguration.DEFAULT_WAIT_EXPONENTIAL_MAX_MS,
                 type=int, help="<milliseconds> If receives a 503 from server, maximum time interval between retries. "
                                "Default {}.".format(ClientWaitingConfiguration.DEFAULT_WAIT_EXPONENTIAL_MAX_MS)),
    click.option('--retry-max-time', RETRY_STOP_LABEL,
                 default=ClientWaitingConfiguration.DEFAULT_STOP_MAX_DELAY_MS,
                 type=int, help="<milliseconds> If receives a 503 from server, retry only within this period. "
                                "Default {}.".format(ClientWaitingConfiguration.DEFAULT_STOP_MAX_DELAY_MS))
]


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


def create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """
    Create a RestClient with retry config set from command line options.
    """
    if verbose:
        log("Connecting to Entity Matching Server: {}".format(server))
    retry_config = ClientWaitingConfiguration(retry_multiplier, retry_max_exp, retry_stop)
    return RestClient(server, retry_config)


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


@cli.command('hash', short_help="generate hashes from local PII data")
@click.argument('pii_csv', type=click.File('r'))
@click.argument('secret', type=str)
@click.argument('schema', type=click.File('r', lazy=True))
@click.argument('clk_json', type=click.File('w'))
@click.option('--no-header', default=False, is_flag=True, help="Don't skip the first row")
@click.option('--check-header', default=True, type=bool, help="If true, check the header against the schema")
@click.option('--validate', default=True, type=bool, help="If true, validate the entries against the schema")
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
        header = 'ignore'
    if no_header:
        header = False

    try:
        clk_data = [serialize_bitarray(bf) for bf in generate_clk_from_csv(
            pii_csv, secret, schema_object,
            validate=validate,
            header=header,
            progress_bar=verbose)]
    except (validate_data.EntryError, validate_data.FormatError) as e:
        msg, = e.args
        log(msg)
        log('Hashing failed.')
    else:
        json.dump({'clks': clk_data}, clk_json)
        if hasattr(clk_json, 'name'):
            log("CLK data written to {}".format(clk_json.name))


@cli.command('block', short_help="generate candidate blocks from local PII data")
@click.argument('pii_csv', type=click.File('r'))
@click.argument('schema', type=click.File('r', lazy=True))
@click.argument('block_json', type=click.File('w'))
@click.option('--no-header', default=False, is_flag=True, help="Don't skip the first row")
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

    # generate candidate blocks and save to json file
    result = generate_candidate_blocks_from_csv(pii_csv, schema, header, verbose=verbose)
    json.dump(result, block_json, indent=4)


@cli.command('status', short_help='get status of entity service')
@click.option('-o', '--output', type=click.File('w'), default='-')
@add_options(rest_client_option)
@verbose_option
def status(output, server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """Connect to an entity matching server and check the service status.

    Use "-" to output status to stdout.
    """
    rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
    service_status = rest_client.server_get_status()
    if verbose:
        log("Status: {}".format(service_status['status']))
    print(json.dumps(service_status), file=output)


MAPPING_CREATED_MSG = """
The generated tokens can be used to upload hashed data and
fetch the resulting linkage table from the service.

To upload using the cli tool for entity A:

    anonlink hash a_people.csv key1 key2 schema.json A_HASHED_FILE.json
    anonlink upload --project="{project_id}" --apikey="{update_tokens[0]}"  A_HASHED_FILE.json

To upload using the cli tool for entity B:

    anonlink hash b_people.csv key1 key2 schema.json B_HASHED_FILE.json
    anonlink upload --project="{project_id}" --apikey="{update_tokens[1]}" B_HASHED_FILE.json

After both users have uploaded their data one can watch for and retrieve the results:

    anonlink results -w --project="{project_id}" --run="{run_id}" --apikey="{result_token}" --output results.txt

"""


@cli.command('create-project', short_help="create a linkage project on the entity service")
@click.option('--type', default='permutations',
              type=click.Choice(['permutations',
                                 'similarity_scores', 'groups']),
              help='Protocol/view type for the project.')
@click.option('--schema', type=click.File('r'), help="Schema to publicly share with participating parties.")
@click.option('--name', type=str, help="Name to give this project")
@click.option('--blocked', is_flag=True, default=False, help="This project uses blocking")
@click.option('--parties', default=2, type=int,
              help="Number of parties in the project")
@click.option('-o', '--output', type=click.File('w'), default='-')
@add_options(rest_client_option)
@verbose_option
def create_project(type, schema, name, blocked, parties, output, server, retry_multiplier, retry_max_exp,
                   retry_stop, verbose):
    """Create a new project on an entity matching server.

    See entity matching service documentation for details on mapping type and schema
    Returns authentication details for the created project.
    """

    if schema is not None:
        schema_json = json.load(schema)
        # Validate the schema
        clkhash.schema.validate_schema_dict(schema_json)
    else:
        raise ValueError("Schema must be provided when creating new linkage project")

    if parties > 2 and type != 'groups':
        raise ValueError("Multi-party linkage requires result type 'groups'")

    name = name if name is not None else ''

    # Creating new project
    try:
        rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
        project_creation_reply = rest_client.project_create(
            schema_json, type, name, parties=parties, uses_blocking=blocked)
    except ServiceError as e:
        log("Unexpected response - {}".format(e.status_code))
        log(e.text)
        raise SystemExit(-1)
    else:
        log("Project created")

    json.dump(project_creation_reply, output)


@cli.command('create', short_help="create a run on the entity service")
@click.option('--name', type=str, help="Name to give this run", default='')
@click.option('--project', help='Project identifier')
@click.option('--apikey', type=str, help="Project Authorization Token")
@click.option('-o', '--output', type=click.File('w'), default='-')
@click.option('-t', '--threshold', type=float)
@add_options(rest_client_option)
@verbose_option
def create(name, project, apikey, output, threshold, server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """Create a new run on an entity matching server.

    See entity matching service documentation for details on threshold.

    Returns details for the created run.
    """
    if threshold is None:
        raise ValueError("Please provide a threshold")

    # Create a new run
    try:
        rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
        response = rest_client.run_create(project, apikey, threshold, name)
    except ServiceError as e:
        log("Unexpected response with status {}".format(e.status_code))
        log(e.text)
    else:
        json.dump(response, output)


#todo
#@click.option('--upload-to', help="User supplied object store path. e.g. 's3://bucket/path'", default=None)

@cli.command('upload', short_help='upload hashes to entity service')
@click.argument('clk_json', type=click.Path(exists=True, dir_okay=False))
@click.option('--project', help='Project identifier')
@click.option('--apikey', help='Authentication API key for the server.')
@click.option('-o', '--output', type=click.File('w'), default='-')
@click.option('--blocks', help='Generated blocks JSON file', type=click.Path(exists=True, dir_okay=False))
@add_options(rest_client_option)
@click.option('--profile', help="AWS profile to use if uploading to own S3 Bucket", default=None)
@click.option('--to_entityservice', is_flag=True, default=False, help="Upload directly to entity service server")
@verbose_option
def upload(clk_json, project, apikey, output, blocks, server, retry_multiplier, retry_max_exp, retry_stop, profile,
           to_entityservice, verbose):
    """Upload CLK data to the Anonlink Entity server.

    Given a json file containing hashed clk data as CLK_JSON, upload to
    the entity resolution service.

    The following environment variables can be used to override default behaviour:

    * UPLOAD_OBJECT_STORE_SERVER

    """
    msg = 'CLK and Blocks' if blocks else 'CLK'

    if verbose:
        log("Uploading CLK data from {}".format(clk_json))
        log("Project ID: {}".format(project))
        log("Uploading {} data to the server".format(msg))

    rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)

    if verbose:
        log("Fetching temporary credentials")
    try:
        res = rest_client.get_temporary_objectstore_credentials(project, apikey)
        credentials = res['credentials']
        upload_info = res['upload']
        upload_to_object_store = True
    except ServiceError as e:
        log("Failed to retrieve temporary credentials")
        upload_to_object_store = False

    # metadata for clks
    with open(clk_json, 'rb') as f:
        clks = json.load(f)['clks']

    hash_count = len(clks)
    hash_size = (len(deserialize_bitarray(clks[0])) + 7) // 8
    encoding_metadata = {
        'hash-count': hash_count,
        'hash-size': hash_size
    }

    if upload_to_object_store and not to_entityservice:
        object_store_credential_providers = []
        if profile is not None:
            object_store_credential_providers.append(AWSConfigProvider(profile=profile))

        endpoint = os.getenv('UPLOAD_OBJECT_STORE_SERVER', upload_info['endpoint'])

        object_store_credential_providers.append(
            StaticProvider(access_key=credentials['AccessKeyId'],
                   secret_key=credentials['SecretAccessKey'],
                   session_token=credentials['SessionToken']))


        mc = Minio(
            endpoint,
            credentials=ChainedProvider(object_store_credential_providers),
            region='us-east-1',
            secure=upload_info['secure']
        )

        if verbose:
            log('Checking we have permission to upload')

        mc.put_object(upload_info['bucket'], upload_info['path'] + "/upload-test", io.BytesIO(b"something"), length=9)
        print(upload_info['bucket'])

    if blocks:
        # check size of blocks and clks consistent
        with open(blocks, 'rb') as f:
            block_counts = next(ijson.items(f, 'meta.source.clk_count.item'))
            msg = 'Size inconsistency: there are {} CLKs but {} encoding-to-blocks maps'.format(hash_count, block_counts)
            assert block_counts == hash_count, msg

        if upload_to_object_store and not to_entityservice:
            print('Anonlink client: Uploading to the external object store - MINIO')
            # upload to Minio
            progress1 = Progress()
            progress1.display_name = f'Upload {clk_json.split("/")[-1]}'
            mc.fput_object(upload_info['bucket'], upload_info['path'] + "/encodings.json", clk_json, progress=progress1,
                           metadata=encoding_metadata)

            progress2 = Progress()
            progress2.display_name = f'Upload {blocks.split("/")[-1]}'
            mc.fput_object(upload_info['bucket'], upload_info['path'] + "/blocks.json", blocks, progress=progress2)

            clk_file = upload_info['path'] + '/encodings.json'
            block_file = upload_info['path'] + '/blocks.json'

            # upload metadata to entity service
            to_entity_service = {
                'encodings': {'file': {'path': clk_file, 'bucket': upload_info['bucket']},
                              'credentials': credentials},
                'blocks': {'file': {'path': block_file, 'bucket': upload_info['bucket']},
                           'credentials': credentials}
            }
            to_entity_service_stream = io.StringIO()
            json.dump(to_entity_service, to_entity_service_stream)
            to_entity_service_stream.seek(0)
            response = rest_client.project_upload_clks(project, apikey, to_entity_service_stream)

        else:
            print('Anonlink client: Uploading to entity service')
            with open(clk_json, 'rb') as encodings:
                with open(blocks, 'rb') as blockings:
                    out = combine_clks_blocks(encodings, blockings)
                    response = rest_client.project_upload_clks(project, apikey, out)

    else:
        if upload_to_object_store and not to_entityservice:
            print('Anonlink client: Uploading to the external object store - MINIO')
            progress = Progress()
            progress.display_name = f'Upload {clk_json.split("/")[-1]}'
            mc.fput_object(upload_info['bucket'], upload_info['path'] + "/encodings.json", clk_json, progress=progress,
                           metadata=encoding_metadata)

            # upload metadata to entity service
            clk_file = upload_info['path'] + '/encodings.json'
            to_entity_service = {
                'encodings': {'file': {'path': clk_file, 'bucket': upload_info['bucket']},
                             'credentials': credentials}
            }
            to_entity_service_stream = io.StringIO()
            json.dump(to_entity_service, to_entity_service_stream)
            to_entity_service_stream.seek(0)
            response = rest_client.project_upload_clks(project, apikey, to_entity_service_stream)
        else:
            print('Anonlink client: Uploading to entity service')
            with open(clk_json, 'rb') as encodings:
                response = rest_client.project_upload_clks(project, apikey, encodings)

    if verbose:
        msg = '\n'.join(['{}: {}'.format(key, value) for key, value in response.items()])
        log(msg)

    json.dump(response, output)


@cli.command('results', short_help="fetch results from entity service")
@click.option('--project', help='Project identifier')
@click.option('--apikey', help='Authentication API key for the server.')
@click.option('--run', help='Run ID to get results for')
@click.option('-w', '--watch', help='Follow/wait until results are available', is_flag=True)
@click.option('-o', '--output', type=click.File('w'), default='-')
@add_options(rest_client_option)
@verbose_option
def results(project, apikey, run, watch, output, server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """
    Check to see if results are available for a particular run
    and if so download.

    Authentication is carried out using the --apikey option which
    must be provided. Depending on the server operating mode this
    may return a mask, a linkage table, or a permutation. Consult
    the entity service documentation for details.
    """
    rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
    status = rest_client.run_get_status(project, run, apikey)
    log(format_run_status(status))
    if watch:
        for status in rest_client.watch_run_status(project, run, apikey, 24 * 60 * 60):
            log(format_run_status(status))

    if status['state'] == 'completed':
        log("Downloading result")
        response = rest_client.run_get_result_text(project, run, apikey)
        log("Received result")
        print(response, file=output)
    elif status['state'] == 'error':
        log("There was an error")
        error_result = rest_client.run_get_result_text(project, run, apikey)
        print(error_result, file=output)
    else:
        log("No result yet")


@cli.command('delete', short_help="delete a run on the anonlink entity service")
@click.option('--project', help='Project identifier')
@click.option('--run', help='Run ID to delete')
@click.option('--apikey', type=str, help="Project Authorization Token")
@add_options(rest_client_option)
@verbose_option
def delete(project, run, apikey, server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """Delete a run on an entity matching server.
    """
    # Delete a run
    try:
        rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
        msg = rest_client.run_delete(project, run, apikey)
        if verbose:
            log(msg)
    except ServiceError as e:
        log("Unexpected response with status {}".format(e.status_code))
        log(e.text)
    else:
        log("Run deleted")


@cli.command('delete-project', short_help="delete a project on the anonlink entity service")
@click.option('--project', help='Project identifier')
@click.option('--apikey', type=str, help="Project Authorization Token")
@add_options(rest_client_option)
@verbose_option
def delete_project(project, apikey, server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    """Delete a project on an entity matching server.
    """
    try:
        rest_client = create_rest_client(server, retry_multiplier, retry_max_exp, retry_stop, verbose)
        rest_client.project_delete(project, apikey)
    except ServiceError as e:
        log("Unexpected response with status {}".format(e.status_code))
        log(e.text)
    else:
        log("Project deleted")


@cli.command('benchmark', short_help='carry out a local benchmark')
def benchmark():
    bench.compute_hash_speed(10000)


@cli.command('describe', short_help='show distribution of clk popcounts')
@click.argument('clk_json', type=click.File('r'))
def describe(clk_json):
    """show distribution of clk's popcounts using a ascii plot.
    """
    clks = json.load(clk_json)['clks']
    counts = get_encoding_popcounts([deserialize_bitarray(clk) for clk in clks])
    plot_hist(counts, bincount=60, title='popcounts', xlab=True, showSummary=True)


@cli.command('convert-schema', short_help='converts schema file to latest version')
@click.argument('schema_json', type=click.File('r'))
@click.argument('output', type=click.File('w'))
def convert_schema(schema_json, output):
    """convert the given schema file to the latest version.
    """
    schema_dict = json.load(schema_json)
    validate_schema_dict(schema_dict)
    new_schema_dict = convert_to_latest_version(schema_dict, validate_result=True)
    json.dump(new_schema_dict, output)


@cli.command('generate', short_help='generate random pii data for testing')
@click.argument('size', type=int, default=100)
@click.argument('output', type=click.File('w'))
@click.option('--schema', '-s', type=click.File('r'), default=None)
def generate(size, output, schema):
    """Generate fake PII data for testing"""
    pii_data = randomnames.NameList(size)

    if schema is not None:
        raise NotImplementedError

    randomnames.save_csv(
        pii_data.names,
        [f.identifier for f in pii_data.SCHEMA.fields],
        output)


@cli.command('generate-default-schema',
             short_help='get the default schema used in generated random PII')
@click.argument('output', type=click.Path(writable=True,
                                          readable=False,
                                          resolve_path=True))
def generate_default_schema(output):
    """Get default schema for fake PII"""
    original_path = os.path.join(os.path.dirname(__file__),
                                 'data',
                                 'randomnames-schema.json')
    shutil.copyfile(original_path, output)


@cli.command('validate-schema', short_help="validate linkage schema")
@click.argument('schema', type=click.File('r', lazy=True))
def validate_schema(schema):
    """Validate a linkage schema

    Given a file containing a linkage schema, verify the schema is valid otherwise
    print detailed errors.
    """

    try:
        clkhash.schema.from_json_file(
            schema_file=schema,
            validate=True
        )

        log("schema is valid", color='green')

    except SchemaError as e:
        log(str(e))
        raise SystemExit(-1)


@cli.command('compare', short_help="compare two schemas")
@click.argument('schema1', type=click.File('r', lazy=True))
@click.argument('schema2', type=click.File('r', lazy=True))
@click.option('-n', 'output_format', flag_value='n', default=True, help='Produce a ndiff format diff (default)')
@click.option('-u', 'output_format', flag_value='u', help='Produce a unified format diff')
@click.option('-m', 'output_format', flag_value='m', help='Produce HTML side by side diff')
@click.option('-c', 'output_format', flag_value='c', help='Produce a context format diff')
@click.option('-l', 'num_context_lines', type=int, default=3, help='The number of context lines for context and unified format')
def compare(schema1, schema2, output_format, num_context_lines):
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

      >>> anonlink compare -m schema1.json schema2.json > diff.html

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
        t = datetime.fromtimestamp(os.stat(lazy_file.name).st_mtime,
                                   timezone.utc)
        return t.astimezone().isoformat()

    fromdate = file_mtime(schema1)
    todate = file_mtime(schema2)

    if output_format == 'm':
        # we encode the json into a readable format. No one wants a one-liner
        enc = json.JSONEncoder(sort_keys=True, indent=0)
        fromlines = [line for line in enc.iterencode(json.load(schema1))]
        tolines = [line for line in enc.iterencode(json.load(schema2))]
        diff = difflib.HtmlDiff().make_file(fromlines, tolines, schema1.name, schema2.name)
    else:
        fromlines = schema1.readlines()
        tolines = schema2.readlines()
        if output_format == 'u':
            diff = difflib.unified_diff(fromlines, tolines, schema1.name, schema2.name, fromdate, todate, n=num_context_lines)
        elif output_format == 'n':
            diff = difflib.ndiff(fromlines, tolines)
        else:
            diff = difflib.context_diff(fromlines, tolines, schema1.name, schema2.name, fromdate, todate, n=num_context_lines)
    sys.stdout.writelines(diff)


if __name__ == "__main__":
    freeze_support()
    cli()
