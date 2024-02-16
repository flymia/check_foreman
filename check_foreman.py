#!/usr/bin/env python3

# check_foreman by Marc Sauer
# Licensed under GPL v3

import json
import sys
import argparse
import requests

# Edit these variables accordingly
SATELLITE_SERVER_IP="satellite.example"
SATELLITE_API_ENDPOINT="https://" + SATELLITE_SERVER_IP + "/api/hosts"
SATELLITE_API_USER="changeme"
SATELLITE_API_TOKEN="changeme"

# Static variables
EXIT_CODE_GENERAL_ERROR=1
EXIT_CODE_HOST_NOT_FOUND=2
EXIT_CODE_JSON_ERROR=3
EXIT_CODE_EXAMPLE_FILE_NOT_FOUND=4
EXIT_CODE_TARGET_EMPTY=5
EXIT_CODE_REQUEST_ERROR=6

def debug_message(message, debug=False):
    if debug:
        print(f"DEBUG: {message}")

def error_message(message):
    sys.stderr.write(f"ERROR: {message}\n")

def load_example_file(filepath):
    try:
        with open(filepath, 'r') as datei:
            data = json.load(datei)
        return data
    except FileNotFoundError:
        error_message(f'The file {filepath} was not found.')
        sys.exit(EXIT_CODE_EXAMPLE_FILE_NOT_FOUND)

    except json.JSONDecodeError:
        print(f'The file {filepath} is not valid JSON.')

def get_api_data(api_url, insecure, debug=False):
    try:
        # TODO: logging.captureWarnings(True) for TLS warning stuff
        response = requests.get(api_url, auth=HTTPBasicAuth(SATELLITE_API_USER, SATELLITE_API_TOKEN), verify=insecure)
        response.raise_for_status()  # Raises an HTTPError exception if the HTTP status code is not 200.

        # Extract JSON from the response
        data = response.json()

        if not data:
            error_message("Error: Empty response from the API.")
            sys.exit(EXIT_CODE_REQUEST_ERROR)
        return data

    except requests.exceptions.RequestException as e:
        error_message(f"Error making GET request: {e}")
        sys.exit(EXIT_CODE_REQUEST_ERROR)

def output_simple_checkmk_check(service_status, service_name, output_text):
    checkmk_check = f'{service_status} "{service_name}" - {output_text}'
    print(checkmk_check)

def get_host_index(sourcedata, target_name, debug=False):
    try:
        for index, host in enumerate(sourcedata["results"]):
            if host["name"] == target_name:
                return index

        print(f"Host with name {target_name} not found.")
        sys.exit(EXIT_CODE_HOST_NOT_FOUND)

    except KeyError as e:
        print(f"Error accessing JSON key: {e}")
        sys.exit(EXIT_CODE_JSON_ERROR)

def print_execution_status(sourcedata, hostname, debug=False):
    service_name = "Execution status"
    index = get_host_index(sourcedata, hostname, debug)

    last_execution_status = sourcedata["results"][index]["execution_status"]
    last_execution_label = sourcedata["results"][index]["execution_status_label"]

    debug_message(last_execution_label, debug)
    debug_message(last_execution_status, debug)

    if last_execution_status == 0:
        output_simple_checkmk_check(0, service_name, last_execution_label)
    elif last_execution_status == 1:
        output_simple_checkmk_check(1, service_name, last_execution_label)
    else:
        build_error = f"Could not get any last execution details. Error: {last_execution_label}"
        output_simple_checkmk_check(3, service_name, build_error)

def print_global_status(sourcedata, hostname, debug=False):
    service_name = "Global status"
    index = get_host_index(sourcedata, hostname, debug)

    last_global_status = sourcedata["results"][index]["global_status"]
    last_global_label = sourcedata["results"][index]["global_status_label"]

    debug_message(last_global_label, debug)
    debug_message(last_global_status, debug)

    if last_global_status == 2:
        output_simple_checkmk_check(1, service_name, last_global_label)
    elif last_global_status == 0:
        output_simple_checkmk_check(0, service_name, last_global_label)
    else:
        build_error = f"Could not get any last execution details. Error: {last_global_label}"
        output_simple_checkmk_check(3, service_name, build_error)

def print_errata_status(sourcedata, hostname, debug=False):
    service_name = "Errata status"
    index = get_host_index(sourcedata, hostname, debug)

    last_errata_status = sourcedata["results"][index]["errata_status"]
    last_errata_label = sourcedata["results"][index]["errata_status_label"]

    debug_message(last_errata_status, debug)
    debug_message(last_errata_label, debug)

    if last_errata_status == 0:
        output_simple_checkmk_check(0, service_name, last_errata_label)
    elif last_errata_status == 1:
        output_simple_checkmk_check(1, service_name, last_errata_label)
    elif last_errata_status == 3:
        output_simple_checkmk_check(1, service_name, last_errata_label)
    else:
        build_error = f"Could not get any last execution details. Error: {last_errata_label}"
        output_simple_checkmk_check(3, service_name, build_error)

def parse_arguments():
    parser = argparse.ArgumentParser(prog='check_foreman', description='CheckMK check_foreman Script')

    parser.add_argument('-t', '--target', help='Specify the target hostname', required=True)
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-s', '--simulate', action='store_true', help='Do not make any real API calls. Just use the example-data/example-api-response.json file')
    parser.add_argument('--insecure', action='store_true', help='Ignore TLS certificate warnings')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    if args.target:
        target_host = args.target
    else:
        error_message("Target shall not be empty!")
        sys.exit(EXIT_CODE_TARGET_EMPTY)

    if args.simulate:
        debug_message("Simulation mode enabled", args.debug)
        data = load_example_file("example-data/example-api-response.json")
    elif args.insecure:
        debug_message("Insecure detected, setting TLS Check", args.debug)
        verify_tls = False
        data = get_api_data(SATELLITE_API_ENDPOINT, verify_tls, args.debug)
    else:
        debug_message("No other modifier detected. Secure Mode enabled", args.debug)
        verify_tls = True
        data = get_api_data(SATELLITE_API_ENDPOINT, verify_tls, args.debug)

    debug_message(f'Got target hostname {target_host}', args.debug)

    print_execution_status(data, target_host, args.debug)
    print_global_status(data, target_host, args.debug)
    print_errata_status(data, target_host, args.debug)
