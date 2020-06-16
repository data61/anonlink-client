import os
import unittest
import mock
import requests
from requests.models import Response
import pytest
from click.testing import CliRunner

from .test_cli import CLITestHelper
from anonlinkclient.rest_client import ServiceError, RestClient, ServiceError
import anonlinkclient.cli as cli
from tests import *


def create_rest_client_response(server, retry_multiplier, retry_max_exp, retry_stop, verbose):
    response = Response()
    response.code = 'error'
    response.status_code = 400

    raise ServiceError('Create rest client failed', response)


def get_temporary_objectstore_credentials_response(project, apikey):
    response = Response()
    response.code = 'error'
    response.status_code = 400

    raise ServiceError('Create rest client failed', response)


def test_create_project():
    """Test service error with mocked server."""
    command = ['create-project', '--server', 'https://test', '--schema', SIMPLE_SCHEMA_PATH]

    runner = CliRunner()
    with mock.patch('anonlinkclient.cli.create_rest_client', side_effect=create_rest_client_response):
        response = runner.invoke(cli.cli, command)
        assert response.exit_code == -1


def test_create():
    """Test command create with mocked response."""
    command = [
        'create',
        '--server', 'https://test',
        '--threshold', '0.8',
        '--project', '1',
        '--apikey', 'secretAPI',
    ]

    runner = CliRunner()
    with mock.patch('anonlinkclient.cli.create_rest_client', side_effect=create_rest_client_response):
        response = runner.invoke(cli.cli, command)
        assert response.output == 'Unexpected response with status 400\n\n'

    command = [
        'create',
        '--server', 'https://test',
        '--threshold', None,
        '--project', '1',
        '--apikey', 'secretAPI',
    ]

    with mock.patch('anonlinkclient.cli.create_rest_client', side_effect=create_rest_client_response):
        response = runner.invoke(cli.cli, command)
        assert response.exit_code == 1
        assert response.exception.args[0] == 'Please provide a threshold'


def test_upload():
    """Test command upload with mocked response."""
    clk_file = create_temp_file()
    command = [
        'upload',
        '--server', 'https://test',
        '--project', '1',
        '--apikey', 'secretAPI',
        '--retry-multiplier', 50,
        '--retry-exponential-max', 1000,
        '--retry-max-time', 30000,
        '--verbose',
        clk_file.name
    ]

    runner = CliRunner()
    with mock.patch('anonlinkclient.rest_client.RestClient.get_temporary_objectstore_credentials', side_effect=get_temporary_objectstore_credentials_response):
        response = runner.invoke(cli.cli, command)
        assert response.exit_code == 1


def test_delete():
    """Test command delete with mocked response."""
    command = [
        'delete',
        '--project', '1',
        '--run', 'r1',
        '--apikey', 'secretAPI',
    ]
    runner = CliRunner()
    with mock.patch('anonlinkclient.cli.create_rest_client', side_effect=create_rest_client_response):
        response = runner.invoke(cli.cli, command)
        assert response.output == 'Unexpected response with status 400\n\n'


def test_delete_project():
    """Test command delete project with mocked response."""
    command = [
        'delete-project',
        '--project', '1',
        '--apikey', 'secretAPI',
    ]
    runner = CliRunner()
    with mock.patch('anonlinkclient.cli.create_rest_client', side_effect=create_rest_client_response):
        response = runner.invoke(cli.cli, command)
        assert response.output == 'Unexpected response with status 400\n\n'
