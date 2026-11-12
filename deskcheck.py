"""DeskCheck Lab: offline Windows snapshot triage. Python 3.10+, stdlib only."""
import argparse
import html
import json
import math
from pathlib import Path


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('Unexpected or missing fields; use schema version 1')


def percent(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError('Percent must be a finite number between 0 and 100')


def validate(data):
    exact_keys(data, ['schema_version', 'memory_free_percent', 'disks', 'interfaces'])
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported schema')
    percent(data['memory_free_percent'])
    for key in ('disks', 'interfaces'):
        if not isinstance(data[key], list) or len(data[key]) > 128:
            raise ValueError('Expected a list with at most 128 items')
    for disk in data['disks']:
        exact_keys(disk, ['free_percent'])
        percent(disk['free_percent'])
    for interface in data['interfaces']:
        exact_keys(interface, ['has_ipv4', 'has_apipa', 'has_gateway', 'has_dns'])
        if any(type(value) is not bool for value in interface.values()):
            raise ValueError('Interface flags must be booleans')
    return data


def analyze(data):
    validate(data)
    findings = []
    def add(code, evidence, action):
        findings.append(dict(code=code, evidence=evidence, next_step=action))
    if data['memory_free_percent'] < 10:
        add('LOW_MEMORY', f"Free memory: {data['memory_free_percent']}%", 'Review Task Manager memory usage; do not end unfamiliar processes.')
    if not data['disks']:
        add('NO_DISK_DATA', 'No fixed-disk readings', 'Verify collection permissions and disk availability.')
    for i, disk in enumerate(data['disks'], 1):
        if disk['free_percent'] < 15:
            add('LOW_DISK', f"Disk {i}: {disk['free_percent']}% free", 'Review Storage settings and approved cleanup; do not delete user files.')
    if not data['interfaces']:
        add('NO_ACTIVE_INTERFACE', 'No active interfaces collected', 'Check cable, Wi-Fi connection and adapter state.')
    for i, interface in enumerate(data['interfaces'], 1):
        label = f'Interface {i}'
        if not interface['has_ipv4']:
            add('NO_IPV4', label, 'Check whether IPv4 is expected; an IPv6-only network may be intentional.')
        if interface['has_apipa']:
            add('APIPA', label, 'If DHCP is expected, inspect cable/VLAN and DHCP availability; APIPA alone does not prove a DHCP outage.')
        if not interface['has_gateway']:
            add('NO_GATEWAY', label, 'Confirm whether this interface needs routed IPv4 access; local-only links may not.')
        if not interface['has_dns']:
            add('NO_DNS', label, 'Review approved DNS configuration; this flag does not test name resolution.')
    return findings


def render(findings):
    rows = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(f[k]))}</td>' for k in ('code', 'evidence', 'next_step')) + '</tr>' for f in findings)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>DeskCheck Lab</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px;background:#f4f7fb;color:#17304b}td,th{padding:14px;border:1px solid #ccd6e0;text-align:left}table{border-collapse:collapse;background:white}h1{color:#126b78}</style><h1>DeskCheck Lab</h1><p>Offline triage • Review by a technician required</p><p>Findings: ' + str(len(findings)) + '</p><table><tr><th>Check</th><th>Evidence</th><th>Next step</th></tr>' + rows + '</table><p>Zero findings means only that these limited snapshot rules did not flag a condition. No connectivity or security test was performed.</p></html>'


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--out', type=Path, default=Path('reports'))
    args = parser.parse_args(argv)
    try:
        with args.snapshot.open('rb') as source:
            raw = source.read(1_048_577)
        if len(raw) > 1_048_576:
            raise ValueError('Input exceeds 1 MiB')
        data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=no_duplicates)
        findings = analyze(data)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'report.html').write_text(render(findings), encoding='utf-8')
        (args.out / 'report.json').write_text(json.dumps({'findings': findings}, indent=2), encoding='utf-8')
        print(f'{len(findings)} findings; reports written')
        return 1 if findings else 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'Unable to complete: {exc}')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
