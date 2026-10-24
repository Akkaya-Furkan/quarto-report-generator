from pathlib import Path

import pytest

from quarto_report.analysis import InputError, analyse

DATA = Path(__file__).resolve().parents[1] / 'examples/data/measurements.csv'


def test_known_statistics_and_selection():
    result = analyse(DATA, 'reference', 2)
    assert result['input_rows'] == 30
    assert result['selected_rows'] == 9
    assert [r['mean'] for r in result['summary']] == [14, 18, 26]
    assert all(r['sd'] == 1 and r['count'] == 3 for r in result['summary'])
    assert len(result['input_sha256']) == 64


def test_groups_are_not_pooled():
    assert len(analyse(DATA)['summary']) == 10


@pytest.mark.parametrize(('content', 'message'), [
    ('', 'empty'),
    ('group,dose,response\n', 'no data rows'),
    ('dose,response\n0,1\n', 'header'),
    ('group,dose,response\na,0\n', 'three fields'),
    ('group,dose,response\na,0,1,2\n', 'three fields'),
    ('group,dose,response\na,oops,1\n', 'numeric'),
    ('group,dose,response\na,0,nan\n', 'finite'),
    ('group,dose,response\na,inf,1\n', 'finite'),
    ('group,dose,response\na,-1,1\n', 'nonnegative'),
    ('group,dose,response\n ,0,1\n', 'nonempty'),
    ('group,dose,response\n"a,0,1\n', 'Malformed'),
])
def test_invalid_csv(tmp_path, content, message):
    path = tmp_path / 'input.csv'
    path.write_text(content)
    with pytest.raises(InputError, match=message):
        analyse(path)


@pytest.mark.parametrize('minimum', [-1, float('nan'), float('inf')])
def test_invalid_cutoff(minimum):
    with pytest.raises(InputError, match='Minimum dose'):
        analyse(DATA, min_dose=minimum)


def test_empty_selection():
    with pytest.raises(InputError, match='No observations'):
        analyse(DATA, group='missing')


def test_singleton(tmp_path):
    path = tmp_path / 'single.csv'
    path.write_text('group,dose,response\na,0,1\n')
    assert analyse(path)['summary'][0]['sd'] is None


def test_missing_and_non_utf8(tmp_path):
    with pytest.raises(InputError, match='Cannot read'):
        analyse(tmp_path / 'missing.csv')
    path = tmp_path / 'bad.csv'
    path.write_bytes(b'\xff')
    with pytest.raises(InputError, match='UTF-8'):
        analyse(path)


def test_example_is_reproducible(tmp_path):
    from scripts.generate_example import generate
    path = tmp_path / 'measurements.csv'
    generate(path)
    assert path.read_bytes() == DATA.read_bytes()
