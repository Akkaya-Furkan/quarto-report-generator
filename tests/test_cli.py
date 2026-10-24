import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from quarto_report.cli import main, render
from quarto_report.analysis import InputError

DATA = Path(__file__).resolve().parents[1] / 'examples/data/measurements.csv'


@pytest.mark.parametrize('content', ['', 'group,dose,response\na,bad,1\n', 'wrong\n'])
def test_invalid_cli_leaves_no_artifacts(tmp_path, content):
    source = tmp_path / 'input.csv'
    source.write_text(content)
    output = tmp_path / 'out.html'
    proc = subprocess.run([sys.executable, '-m', 'quarto_report.cli', str(source),
                           '--output', str(output)], capture_output=True, text=True)
    assert proc.returncode == 2
    assert 'Error:' in proc.stderr
    assert not output.exists()
    assert not output.with_suffix('.json').exists()


def test_failed_renderer_leaves_no_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr('quarto_report.cli.shutil.which', lambda _: '/fake/quarto')
    monkeypatch.setattr('quarto_report.cli.subprocess.run', lambda *a, **kw:
                        SimpleNamespace(returncode=1, stderr='deliberate render failure', stdout=''))
    output = tmp_path / 'out.html'
    with pytest.raises(InputError, match='no report published'):
        render(DATA, output)
    assert list(tmp_path.iterdir()) == []


def test_existing_output_is_preserved(tmp_path):
    output = tmp_path / 'out.html'
    output.write_text('existing report')
    assert main([str(DATA), '--output', str(output)]) == 2
    assert output.read_text() == 'existing report'
    assert not output.with_suffix('.json').exists()


def test_existing_sidecar_is_preserved(tmp_path):
    output = tmp_path / 'out.html'
    output.with_suffix('.json').write_text('existing metadata')
    assert main([str(DATA), '--output', str(output)]) == 2
    assert not output.exists()
    assert output.with_suffix('.json').read_text() == 'existing metadata'


def test_no_quarto(tmp_path, monkeypatch):
    monkeypatch.setattr('quarto_report.cli.shutil.which', lambda _: None)
    assert main([str(DATA), '--output', str(tmp_path / 'out.html')]) == 2
    assert list(tmp_path.iterdir()) == []


def test_pdf_without_latex(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr('quarto_report.cli.shutil.which', lambda name: '/quarto' if name == 'quarto' else None)
    assert main([str(DATA), '--output', str(tmp_path / 'out.pdf'), '--format', 'pdf']) == 2
    assert 'PDF not done' in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('args', [ ['--group', 'missing'], ['--min-dose', '100'],
                                  ['--min-dose', 'nan'], ['--format', 'pdf'] ])
def test_invalid_parameters(tmp_path, args):
    assert main([str(DATA), '--output', str(tmp_path / 'out.html'), *args]) == 2
    assert list(tmp_path.iterdir()) == []


@pytest.mark.integration
def test_real_parameterised_render(tmp_path):
    from bs4 import BeautifulSoup
    results = []
    for group, expected in [('reference', 14), ('comparison', 18)]:
        output = tmp_path / f'{group}.html'
        proc = subprocess.run(['measurement-report', str(DATA), '--output', str(output),
                               '--group', group, '--min-dose', '2', '--title', f'{group} profile'],
                              capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        metadata = json.loads(output.with_suffix('.json').read_text())
        soup = BeautifulSoup(output.read_text(), 'html.parser')
        assert soup.find('main').find('h2').get_text().strip() == f'{group} profile'
        assert soup.find('table').find_all('tr')[1].find_all('td')[3].text == f'{expected:.6f}'
        assert soup.find('img')['src'].startswith('data:image/png;base64,')
        assert not any(link.get('href', '').endswith('.pdf') for link in soup.find_all('a'))
        assert metadata['selected_rows'] == 9
        assert metadata['summary'][0]['mean'] == expected
        assert metadata['input_sha256'] in soup.get_text()
        results.append(metadata)
    assert results[0]['summary'] != results[1]['summary']


def test_sidecar_write_failure_rolls_back_report(tmp_path, monkeypatch):
    monkeypatch.setattr('quarto_report.cli.shutil.which', lambda _: '/fake/quarto')

    def successful_renderer(*args, **kwargs):
        (Path(kwargs['cwd']) / 'report.html').write_text('<html>complete</html>')
        return SimpleNamespace(returncode=0, stdout='', stderr='')

    monkeypatch.setattr('quarto_report.cli.subprocess.run', successful_renderer)
    output = tmp_path / 'out.html'
    sidecar = output.with_suffix('.json')
    original_open = Path.open

    def deny_sidecar(path, *args, **kwargs):
        if path == sidecar:
            raise PermissionError('deliberate sidecar failure')
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', deny_sidecar)
    with pytest.raises(PermissionError):
        render(DATA, output)
    assert list(tmp_path.iterdir()) == []
