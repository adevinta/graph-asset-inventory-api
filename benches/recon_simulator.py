#!/usr/bin/python3

"""This script simulates a RECON service that finds AWS assets on different
points in time."""

import sys
import logging
import csv
import argparse
import random
import string
import itertools
import math
import time


AWS_REGIONS = [
    'us-east-2',
    'us-east-1',
    'us-west-1',
    'us-west-2',
    'eu-central-1',
    'eu-west-1',
    'eu-west-2',
    'eu-south-1',
    'eu-west-3',
    'eu-north-1',
]

DOMAINS = ['adevinta.com', 'cloudfront.net'] + [
    region + '.compute.amazonaws.com' for region in AWS_REGIONS
]

ALPHA_NUM = string.ascii_lowercase + string.digits


def aws_account_generator(num):
    """Generates random AWS account numbers."""
    for _ in range(num):
        acc_id = random.randint(100000000000, 9999999999999)
        yield acc_id


def hostname_generator(num):
    """Generates random hostnames."""
    for _ in range(num):
        rnd_str = ''
        for _ in range(random.randint(1, 20)):
            rnd_str += random.choice(ALPHA_NUM + '.-')

        host = random.choice(ALPHA_NUM) + rnd_str + random.choice(ALPHA_NUM)
        domain = random.choice(DOMAINS)
        hostname = host + '.' + domain
        yield hostname


class Inventory:
    """Represents an asset inventory of AWS accounts and hostnames."""

    def __init__(self, num_accounts, num_hosts):
        self.accounts = {}
        self.hosts = {}
        self.accounts_missing = float(num_accounts)
        self.accounts_leftover = 0
        self.hosts_missing = float(num_hosts)
        self.hosts_leftover = 0
        self._update()

    def get_aws_accounts(self):
        """Returns the current AWS accounts in the inventory."""
        return self.accounts

    def get_hostnames(self):
        """Returns the current hostnames in the inventory."""
        return self.hosts

    def grow_and_decline(self, grow_factor, decline_factor):
        """Add and remove assets based on the grow and decline factors."""
        self.accounts_missing += len(self.accounts) * grow_factor
        self.accounts_leftover += len(self.accounts) * decline_factor
        self.hosts_missing += len(self.hosts) * grow_factor
        self.hosts_leftover += len(self.hosts) * decline_factor

        logging.debug(
            'updating inventory aws-accounts(cur=%d miss=%.02f '
            'leftover=%.02f) hostnames(cur=%d miss=%.02f leftover=%.02f)',
            len(self.accounts),
            self.accounts_missing,
            self.accounts_leftover,
            len(self.hosts),
            self.hosts_missing,
            self.hosts_leftover,
        )

        self._update()

    def _update(self):
        """Updates the state of the inventory."""

        # Add more accounts
        num = math.floor(self.accounts_missing)
        self.accounts_missing -= num
        for acc_id in aws_account_generator(num):
            self.accounts[acc_id] = {
                'weight': random.betavariate(6, 6),
                'host_count': 0,
            }

        # Get list of accounts and their weights for parent selection
        accounts_keys_list = list(self.accounts.keys())
        cum_weights = list(
            itertools.accumulate(v['weight'] for v in self.accounts.values())
        )

        # Add more hostnames
        num = math.floor(self.hosts_missing)
        self.hosts_missing -= num
        for hostname in hostname_generator(num):
            parent = random.choices(
                accounts_keys_list,
                cum_weights=cum_weights,
                k=1,
            )[0]
            self.hosts[hostname] = {'parent': parent}
            self.accounts[parent]['host_count'] += 1

        # Delete accounts randomly
        random.shuffle(accounts_keys_list)
        deleted_accounts = []
        while self.accounts_leftover >= 1.0:
            selected = None
            extra_hostnames = 0
            for acc_id in accounts_keys_list:
                # Choose accounts with no more hostnames than we want to delete
                host_count = self.accounts[acc_id]['host_count']
                if self.hosts_leftover >= host_count:
                    selected = acc_id
                    extra_hostnames = host_count
                    break
            if selected:
                self.accounts_leftover -= 1
                self.hosts_leftover -= extra_hostnames
                accounts_keys_list.remove(selected)
                deleted_accounts.append(selected)
                del self.accounts[selected]
            else:
                break

        # Delete orphans hostnames
        if deleted_accounts:
            for k, v in list(self.hosts.items()):
                if v['parent'] in deleted_accounts:
                    del self.hosts[k]

        # Delete hostnames randomly
        if self.hosts_leftover >= 1.0:
            num = math.floor(self.hosts_leftover)
            self.hosts_leftover -= num

            host_key_list = list(self.hosts.keys())
            random.shuffle(host_key_list)

            for k in host_key_list[:num]:
                host = self.hosts.pop(k)
                self.accounts[host['parent']]['host_count'] -= 1


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-r',
        dest='rounds',
        type=int,
        help='redcon simulations to run',
        default=10,
    )
    parser.add_argument(
        '-a',
        dest='assets',
        help='initial number of assets <aws-accounts>,<hostnames>',
        default='150,1000',
        type=lambda arg: [int(i) for i in arg.split(',')],
    )
    parser.add_argument(
        '-gr',
        type=float,
        help='inventory growth ratio per round',
        default=0.03,
    )
    parser.add_argument(
        '-dr',
        type=float,
        help='inventory decline ratio per round',
        default=0.01,
    )
    args = parser.parse_args()

    if args.rounds < 1:
        parser.error('Miminun rounds is 1')
    if len(args.assets) != 2:
        parser.error('-a format is <aws-accounts>,<hostnames>')
    if args.assets[0] < 1:
        parser.error('Miminun number of aws-accounts is 1')

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    fields = [
        'seq',
        'type',
        'identifier',
        'timestamp',
        'expiration',
        'parent_type',
        'parent_identifier',
        'parent_of_timestamp',
        'parent_of_expiration',
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=fields)
    rows = 0

    ts_interval = 24 * 3600
    ts_end = int(time.time())
    ts_start = ts_end - (ts_interval * args.rounds)

    inventory = Inventory(args.assets[0], args.assets[1])

    for timestamp in range(ts_start, ts_end, ts_interval):
        if timestamp != ts_start:
            inventory.grow_and_decline(args.gr, args.dr)

        expiration = timestamp + ts_interval

        for k, v in inventory.get_aws_accounts().items():
            writer.writerow(
                {
                    'seq': rows,
                    'type': 'AwsAccount',
                    'identifier': k,
                    'timestamp': timestamp,
                    'expiration': expiration,
                    'parent_type': '',
                    'parent_identifier': '',
                    'parent_of_timestamp': timestamp,
                    'parent_of_expiration': expiration,
                }
            )
            rows += 1

        for k, v in inventory.get_hostnames().items():
            writer.writerow(
                {
                    'seq': rows,
                    'type': 'Hostname',
                    'identifier': k,
                    'timestamp': timestamp,
                    'expiration': timestamp + ts_interval,
                    'parent_type': 'AwsAccount',
                    'parent_identifier': v['parent'],
                    'parent_of_timestamp': timestamp,
                    'parent_of_expiration': expiration,
                }
            )
            rows += 1


if __name__ == '__main__':
    main()
