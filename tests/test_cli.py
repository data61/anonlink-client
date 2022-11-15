"""
http://click.pocoo.org/5/testing/
"""

import json
import logging
import os
import random
import unittest

from click.testing import CliRunner
from clkhash import randomnames, schema

import anonlinkclient
import anonlinkclient.cli as cli
from tests import *

ES_TIMEOUT = os.environ.get("ES_TIMEOUT", 60)


class CLITestHelper(unittest.TestCase):
    SAMPLES = 100

    @classmethod
    def setUpClass(cls) -> None:
        CLITestHelper.pii_file = create_temp_file()
        CLITestHelper.pii_file_2 = create_temp_file()

        # Get random PII
        pii_data = randomnames.NameList(CLITestHelper.SAMPLES)
        data = [(name, dob) for _, name, dob, _ in pii_data.names]

        headers = ["NAME freetext", "DOB YYYY/MM/DD"]
        randomnames.save_csv(data, headers, CLITestHelper.pii_file)

        random.shuffle(data)
        randomnames.save_csv(data[::2], headers, CLITestHelper.pii_file_2)

        CLITestHelper.default_schema = [
            {"identifier": "INDEX"},
            {"identifier": "NAME freetext"},
            {"identifier": "DOB YYYY/MM/DD"},
            {"identifier": "GENDER M or F"},
        ]

        CLITestHelper.pii_file.close()
        CLITestHelper.pii_file_2.close()

    def setUp(self):
        super(CLITestHelper, self).setUp()

    @classmethod
    def tearDownClass(cls) -> None:
        # Delete temporary files if they exist.
        for f in CLITestHelper.pii_file, CLITestHelper.pii_file_2:
            try:
                os.remove(f.name)
            except:
                pass

    def tearDown(self):
        super(CLITestHelper, self).tearDown()

    def run_command_capture_output(self, command):
        """
        Creates a NamedTempFile and saves the output of running a
        cli command to that file by adding `-o output.name` to the
        command before running it.

        :param command: e.g ["status"]
        :returns: The output as a string.
        :raises: AssertionError if the command's exit code isn't 0
        """

        runner = CliRunner()

        with temporary_file() as output_filename:
            command.extend(["-o", output_filename])
            cli_result = runner.invoke(cli.cli, command)
            assert cli_result.exit_code == 0, "Output:\n{}\nException:\n{}".format(
                cli_result.output, cli_result.exception
            )
            with open(output_filename, "rt") as output:
                return output.read()

    def run_command_load_json_output(self, command):
        """
         Parses the file as JSON.

        :param command: e.g ["status"]
        :return: The parsed JSON in the created output file.
        :raises: AssertionError if the command's exit code isn't 0
        :raises: json.decoder.JSONDecodeError if the output isn't json
        """
        logging.info(command)
        output_str = self.run_command_capture_output(command)
        return json.loads(output_str)


class BasicCLITests(unittest.TestCase):
    def test_list_commands(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, [])
        expected_options = ["--version", "--verbose", "--help"]
        expected_commands = [
            "benchmark",
            "describe",
            "generate",
            "generate-default-schema",
            "hash",
            "validate-schema",
        ]
        for expected_option in expected_options:
            assert expected_option in result.output

        for expected_command in expected_commands:
            assert expected_command in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["--version"])
        assert result.exit_code == 0
        assert anonlinkclient.__version__ in result.output

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, "--help")
        result_without_command = runner.invoke(cli.cli, [])
        assert result.output == result_without_command.output

    def test_bench(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["benchmark"])
        assert "hashes in" in result.output

    def test_describe(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            with open("in.csv", "w") as f:
                f.write("Alice,1967/09/27")

            runner.invoke(
                cli.cli,
                ["hash", "in.csv", "a", SIMPLE_SCHEMA_PATH, "out.json", "--no-header"],
            )

            result = runner.invoke(cli.cli, ["describe", "out.json"])
            assert result.exit_code == 0


class TestSchemaValidationCommand(unittest.TestCase):
    @staticmethod
    def validate_schema(schema_path):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["validate-schema", schema_path])
        return result

    def test_good_v1_schema(self):
        for schema_path in GOOD_SCHEMA_V1_PATH, SIMPLE_SCHEMA_PATH:
            result = self.validate_schema(schema_path)
            assert result.exit_code == 0
            assert "schema is valid" in result.output

    def test_bad_v1_schema(self):
        result = self.validate_schema(BAD_SCHEMA_V1_PATH)
        assert result.exit_code == -1
        assert "schema is not valid." in result.output
        assert "'l' is a required property" in result.output

    def test_good_v2_schema(self):
        for schema_path in GOOD_SCHEMA_V2_PATH, RANDOMNAMES_SCHEMA_PATH:
            result = self.validate_schema(schema_path)
            assert result.exit_code == 0
            assert "schema is valid" in result.output

    def test_bad_v2_schema(self):
        result = self.validate_schema(BAD_SCHEMA_V2_PATH)
        assert result.exit_code == -1
        assert "schema is not valid." in result.output

    def test_good_v3_schema(self):
        result = self.validate_schema(GOOD_SCHEMA_V3_PATH)
        assert result.exit_code == 0
        assert "schema is valid" in result.output

    def test_bad_v3_schema(self):
        result = self.validate_schema(BAD_SCHEMA_V3_PATH)
        assert result.exit_code == -1
        assert "schema is not valid." in result.output


class TestSchemaConversionCommand(unittest.TestCase):

    LATEST_VERSION = max(schema.MASTER_SCHEMA_FILE_NAMES.keys())

    @staticmethod
    def convert_schema(schema_path):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["convert-schema", schema_path, "out.json"])
        return result

    def test_good_v1_schema(self):
        for schema_path in GOOD_SCHEMA_V1_PATH, SIMPLE_SCHEMA_PATH:
            result = self.convert_schema(schema_path)
            assert result.exit_code == 0
            with open("out.json") as f:
                json_dict = json.load(f)
                self.assertEqual(json_dict["version"], self.LATEST_VERSION)

    def test_bad_v1_schema(self):
        result = self.convert_schema(BAD_SCHEMA_V1_PATH)
        assert result.exit_code == 1
        self.assertIsInstance(result.exception, schema.SchemaError)
        assert "schema is not valid." in result.exception.msg
        assert "'l' is a required property" in result.exception.msg

    def test_good_v2_schema(self):
        for schema_path in GOOD_SCHEMA_V2_PATH, RANDOMNAMES_SCHEMA_PATH:
            result = self.convert_schema(schema_path)
            assert result.exit_code == 0
            with open("out.json") as f:
                json_dict = json.load(f)
                self.assertEqual(json_dict["version"], self.LATEST_VERSION)

    def test_bad_v2_schema(self):
        result = self.convert_schema(BAD_SCHEMA_V2_PATH)
        assert result.exit_code == 1
        self.assertIsInstance(result.exception, schema.SchemaError)
        assert "schema is not valid." in result.exception.msg

    def test_good_v3_schema(self):
        result = self.convert_schema(GOOD_SCHEMA_V3_PATH)
        assert result.exit_code == 0
        with open("out.json") as f:
            json_dict = json.load(f)
            self.assertEqual(json_dict["version"], self.LATEST_VERSION)

    def test_bad_v3_schema(self):
        result = self.convert_schema(BAD_SCHEMA_V3_PATH)
        assert result.exit_code == 1
        self.assertIsInstance(result.exception, schema.SchemaError)
        assert "schema is not valid." in result.exception.msg


class TestHashCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_hash_auto_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["hash"])
        assert "Missing argument" in result.output

    def test_hash_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["hash", "--help"])
        assert "secret" in result.output.lower()
        assert "schema" in result.output

    def test_hash_requires_secret(self):
        runner = self.runner

        with runner.isolated_filesystem():
            with open("in.csv", "w") as f:
                f.write("Alice, 1967")

            result = runner.invoke(cli.cli, ["hash", "in.csv"])
            assert result.exit_code != 0
            self.assertIn("Usage: anonlink hash", result.output)
            self.assertIn("Missing argument", result.output)

    def test_hash_with_provided_schema(self):
        runner = self.runner

        with runner.isolated_filesystem():
            with open("in.csv", "w") as f:
                f.write("Alice,1967/09/27")

            result = runner.invoke(
                cli.cli,
                ["hash", "in.csv", "a", SIMPLE_SCHEMA_PATH, "out.json", "--no-header"],
            )

            with open("out.json") as f:
                self.assertIn("clks", json.load(f))

    def test_hash_febrl_data(self):
        runner = self.runner
        schema_file = os.path.join(
            os.path.dirname(__file__), "testdata/dirty-data-schema.json"
        )
        a_pii = os.path.join(os.path.dirname(__file__), "testdata/dirty_1000_50_1.csv")

        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.cli, ["hash", a_pii, "a", schema_file, "out.json"]
            )

            result_2 = runner.invoke(
                cli.cli, ["hash", a_pii, "a", schema_file, "out-2.json"]
            )

            with open("out.json") as f:
                hasha = json.load(f)["clks"]

            with open("out-2.json") as f:
                hashb = json.load(f)["clks"]

        for i in range(1000):
            self.assertEqual(hasha[i], hashb[i])

    def test_hash_wrong_schema(self):
        runner = self.runner

        # This schema only has 4 features
        schema_file = os.path.join(
            os.path.dirname(__file__), "testdata/randomnames-schema.json"
        )

        # This CSV has 14 features
        a_pii = os.path.join(os.path.dirname(__file__), "testdata/dirty_1000_50_1.csv")

        with runner.isolated_filesystem():

            result = runner.invoke(
                cli.cli,
                ["hash", "--quiet", "--schema", schema_file, a_pii, "a", "b", "-"],
            )

        assert result.exit_code != 0

    def test_hash_schemaerror(self):
        runner = self.runner

        schema_file = os.path.join(TESTDATA, "bad-schema-v1.json")
        a_pii = os.path.join(TESTDATA, "dirty_1000_50_1.csv")

        # with self.assertRaises(SchemaError):
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.cli, ["hash", a_pii, "horse", schema_file, "out.json"]
            )
        assert result.exit_code != 0
        assert "schema is not valid" in result.output

    def test_hash_invalid_data(self):
        runner = self.runner
        with runner.isolated_filesystem():
            with open("in.csv", "w") as f:
                f.write("Alice,")

            result = runner.invoke(
                cli.cli,
                ["hash", "in.csv", "a", SIMPLE_SCHEMA_PATH, "out.json", "--no-header"],
            )

            assert "Invalid entry" in result.output


class TestBlockCommand(unittest.TestCase):
    def test_cli_includes_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)

        assert "block" in result.output.lower()

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["--version"])
        assert result.exit_code == 0
        self.assertIn(anonlinkclient.__version__, result.output)

    def test_lambda_fold(self):
        runner = CliRunner()
        with temporary_file() as output_filename:
            with open(output_filename, "wt") as output:
                schema_path = os.path.join(TESTDATA, "lambda_fold_schema.json")
                data_path = os.path.join(TESTDATA, "small.csv")
                cli_result = runner.invoke(
                    cli.cli, ["block", data_path, schema_path, output.name]
                )
            self.assertEqual(
                cli_result.exit_code,
                0,
                msg="result={}; exception={}".format(cli_result, cli_result.exception),
            )

            with open(output_filename, "rt") as output:
                outjson = json.load(output)
                self.assertIn("blocks", outjson)
                self.assertIn("state", outjson["meta"])
                self.assertIn("config", outjson["meta"])


class TestCompareSchemaCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_includes_help(self):
        result = self.runner.invoke(cli.cli, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)

        assert "compare-schema" in result.output.lower()

    def test_compare_ndiff(self):
        cli_result = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-n",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result.exit_code,
            0,
            msg="result={}; exception={}".format(cli_result, cli_result.exception),
        )
        default_result = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            default_result.exit_code,
            0,
            msg="result={}; exception={}".format(
                default_result, default_result.exception
            ),
        )
        self.assertEqual(
            cli_result.output,
            default_result.output,
            msg="ndiff format is not the default, but should",
        )
        self.assertIn("?", cli_result.output)

    def test_compare_schema_context_diff(self):
        cli_result = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-c",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result.exit_code,
            0,
            msg="result={}; exception={}".format(cli_result, cli_result.exception),
        )
        cli_result_larger_l = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-c",
                "-l 5",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result_larger_l.exit_code,
            0,
            msg="result={}; exception={}".format(
                cli_result_larger_l, cli_result_larger_l.exception
            ),
        )
        self.assertGreater(cli_result_larger_l.output, cli_result.output)
        self.assertIn("!", cli_result.output)

    def test_compare_schema_unified_diff(self):
        cli_result = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-u",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result.exit_code,
            0,
            msg="result={}; exception={}".format(cli_result, cli_result.exception),
        )
        cli_result_larger_l = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-u",
                "-l 5",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result_larger_l.exit_code,
            0,
            msg="result={}; exception={}".format(
                cli_result_larger_l, cli_result_larger_l.exception
            ),
        )
        self.assertGreater(cli_result_larger_l.output, cli_result.output)
        self.assertIn("@@", cli_result.output)

    def test_compare_schema_html_diff(self):
        cli_result = self.runner.invoke(
            cli.cli,
            [
                "compare-schema",
                "-m",
                os.path.join(TESTDATA, "bad-schema-v2.json"),
                os.path.join(TESTDATA, "bad-schema-v3.json"),
            ],
        )
        self.assertEqual(
            cli_result.exit_code,
            0,
            msg="result={}; exception={}".format(cli_result, cli_result.exception),
        )
        self.assertIn("<html>", cli_result.output)
        self.assertIn("</table>", cli_result.output)


class TestHasherDefaultSchema(unittest.TestCase):

    samples = 100

    def setUp(self):
        self.pii_file = create_temp_file()

        pii_data = randomnames.NameList(TestHasherDefaultSchema.samples)
        randomnames.save_csv(
            pii_data.names,
            [f.identifier for f in pii_data.SCHEMA.fields],
            self.pii_file,
        )
        self.pii_file.flush()

    def test_cli_includes_help(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)

        assert "Usage" in result.output
        assert "Options" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli, ["--version"])
        assert result.exit_code == 0
        self.assertIn(anonlinkclient.__version__, result.output)

    def test_generate_command(self):
        runner = CliRunner()
        with temporary_file() as output_filename:
            with open(output_filename) as output:
                cli_result = runner.invoke(cli.cli, ["generate", "50", output.name])
            self.assertEqual(cli_result.exit_code, 0, msg=cli_result.output)
            with open(output_filename, "rt") as output:
                out = output.read()
        assert len(out) > 50

    def test_generate_default_schema_command(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            generate_schema_result = runner.invoke(
                cli.cli, ["generate-default-schema", "pii-schema.json"]
            )
            self.assertEqual(
                generate_schema_result.exit_code, 0, msg=generate_schema_result.output
            )

            hash_result = runner.invoke(
                cli.cli,
                [
                    "hash",
                    self.pii_file.name,
                    "secret",
                    "pii-schema.json",
                    "pii-hashes.json",
                ],
            )
            self.assertEqual(hash_result.exit_code, 0, msg=hash_result.output)

    def test_basic_hashing(self):
        runner = CliRunner()
        with temporary_file() as output_filename:
            with open(output_filename, "wt") as output:
                cli_result = runner.invoke(
                    cli.cli,
                    [
                        "hash",
                        self.pii_file.name,
                        "secret",
                        RANDOMNAMES_SCHEMA_PATH,
                        output.name,
                    ],
                )
            self.assertEqual(cli_result.exit_code, 0, msg=cli_result.output)

            with open(output_filename, "rt") as output:
                self.assertIn("clks", json.load(output))


class TestHasherSchema(CLITestHelper):
    def test_hashing_json_schema(self):
        runner = CliRunner()

        pii_data = randomnames.NameList(self.SAMPLES)
        pii_file = create_temp_file()
        randomnames.save_csv(
            pii_data.names, [f.identifier for f in pii_data.SCHEMA.fields], pii_file
        )
        pii_file.close()

        with temporary_file() as output_filename:
            with open(output_filename) as output:
                cli_result = runner.invoke(
                    cli.cli,
                    [
                        "hash",
                        pii_file.name,
                        "secret",
                        RANDOMNAMES_SCHEMA_PATH,
                        output.name,
                    ],
                )

            self.assertEqual(cli_result.exit_code, 0, msg=cli_result.output)

            with open(output_filename) as output:
                self.assertIn("clks", json.load(output))


class TestFindSimilarityCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_includes_help(self):
        runner = self.runner
        result = runner.invoke(cli.cli, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)

        assert "find-similarity" in result.output.lower()

    def test_version(self):
        runner = self.runner
        result = runner.invoke(cli.cli, ["--version"])
        assert result.exit_code == 0
        self.assertIn(anonlinkclient.__version__, result.output)

    def test_find_similarities(self):
        runner = self.runner
        clks_a = os.path.join(TESTDATA, "novt_clk_0.json")
        blocks_a = os.path.join(TESTDATA, "novt_blocks_0.json")
        clks_b = os.path.join(TESTDATA, "novt_clk_1.json")
        blocks_b = os.path.join(TESTDATA, "novt_blocks_1.json")

        with temporary_file() as output_filename:
            with open(output_filename) as output:
                result = runner.invoke(
                    cli.cli,
                    [
                        "find-similarity",
                        "0.8",
                        output.name,
                        "--files",
                        clks_a,
                        blocks_a,
                        "--files",
                        clks_b,
                        blocks_b,
                        "--blocking",
                        "True",
                    ],
                )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(result.output.rstrip(), "Found 1309 matches")
