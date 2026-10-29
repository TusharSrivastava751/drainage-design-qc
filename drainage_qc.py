"""Screen independent circular pipe reaches; never a network design solver."""
import argparse
import csv
import math
import sys
from auditlib import read_csv, number, unique, load_config, evidence, cell, write_reports

FIELDS = ['pipe_id', 'length_m', 'diameter_mm', 'outside_diameter_mm', 'invert_up_m', 'invert_down_m',
          'ground_up_m', 'ground_down_m', 'manning_n', 'catchment_ha',
          'runoff_coefficient', 'intensity_mm_hr']
CONFIG = ['minimum_cover_m', 'full_flow_velocity_min_m_s', 'full_flow_velocity_max_m_s']


def screen(rows, config):
    unique(rows, ['pipe_id'])
    if not rows:
        raise ValueError('at least one pipe is required')
    cover_min = number(config['minimum_cover_m'], 'minimum_cover_m', minimum=0)
    vmin = number(config['full_flow_velocity_min_m_s'], 'velocity_min', minimum=0)
    vmax = number(config['full_flow_velocity_max_m_s'], 'velocity_max', positive=True)
    if vmin >= vmax:
        raise ValueError('velocity minimum must be below maximum')
    results = []
    for row in rows:
        x = {k: number(row[k], k) for k in FIELDS if k != 'pipe_id'}
        for k in ['length_m', 'diameter_mm', 'outside_diameter_mm', 'manning_n']:
            number(x[k], k, positive=True)
        for k in ['catchment_ha', 'intensity_mm_hr', 'runoff_coefficient']:
            number(x[k], k, minimum=0)
        if x['runoff_coefficient'] > 1:
            raise ValueError('runoff_coefficient must be in [0, 1]')
        diameter = x['diameter_mm'] / 1000
        outside_diameter = x['outside_diameter_mm'] / 1000
        if outside_diameter < diameter:
            raise ValueError('outside diameter cannot be less than internal diameter')
        slope = (x['invert_up_m'] - x['invert_down_m']) / x['length_m']
        cover = min(x['ground_up_m'] - x['invert_up_m'] - outside_diameter,
                    x['ground_down_m'] - x['invert_down_m'] - outside_diameter)
        demand = x['runoff_coefficient'] * x['intensity_mm_hr'] * x['catchment_ha'] / 360
        flags = []
        capacity = velocity = utilization = None
        if cover < cover_min:
            flags.append('COVER_BELOW_DEMO_LIMIT')
        if slope <= 0:
            flags.append('NON_POSITIVE_SLOPE')
        else:
            area = math.pi * diameter ** 2 / 4
            velocity = (diameter / 4) ** (2 / 3) * math.sqrt(slope) / x['manning_n']
            capacity = area * velocity
            utilization = demand / capacity
            if demand > capacity:
                flags.append('DEMAND_EXCEEDS_FULL_FLOW_REFERENCE')
            if not vmin <= velocity <= vmax:
                flags.append('FULL_FLOW_VELOCITY_OUTSIDE_DEMO_RANGE')
        for value in [slope, cover, demand, capacity, velocity, utilization]:
            if value is not None:
                number(value, 'derived result')
        results.append({'pipe_id': row['pipe_id'], 'slope_m_m': slope,
                        'minimum_endpoint_cover_m': cover, 'demand_m3_s': demand,
                        'full_flow_capacity_m3_s': capacity, 'full_flow_velocity_m_s': velocity,
                        'demand_capacity_ratio': utilization, 'findings': flags})
    return {'demo': True, 'method': 'rational-and-full-circular-manning-v1',
            'criteria': config, 'pipes_checked': len(results),
            'pipes_with_findings': sum(bool(x['findings']) for x in results), 'results': results}


def render(report):
    lines = ['# Drainage screening report', '', '**Synthetic demo — screening only.**', '',
             'Full-flow velocity is a reference, not the velocity at the estimated demand.', '',
             '| Pipe | Demand m³/s | Full-flow m³/s | Min. endpoint cover m | Findings |',
             '|---|---:|---:|---:|---|']
    for r in report['results']:
        capacity = 'not calculated' if r['full_flow_capacity_m3_s'] is None else f"{r['full_flow_capacity_m3_s']:.4f}"
        lines.append(f"| {cell(r['pipe_id'])} | {r['demand_m3_s']:.4f} | {capacity} | {r['minimum_endpoint_cover_m']:.3f} | {', '.join(r['findings']) or 'No screening findings'} |")
    lines += ['', 'No finding is not design approval. Review the criteria, rainfall basis, network and hydraulic grade line.', '']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pipes')
    p.add_argument('--config', default='examples/demo_criteria.json')
    p.add_argument('--out', default='reports')
    p.add_argument('--fail-on-findings', action='store_true')
    a = p.parse_args()
    try:
        report = screen(read_csv(a.pipes, FIELDS), load_config(a.config, CONFIG))
        report['inputs'] = evidence([a.pipes, a.config])
        write_reports(a.out, report, render(report))
    except (ValueError, OSError, csv.Error, OverflowError, ZeroDivisionError) as exc:
        print(f'Input/report error: {exc}', file=sys.stderr)
        return 2
    print(f"Checked {report['pipes_checked']} pipes; {report['pipes_with_findings']} need review. Reports: {a.out}")
    return int(a.fail_on_findings and report['pipes_with_findings'] > 0)


if __name__ == '__main__':
    sys.exit(main())
