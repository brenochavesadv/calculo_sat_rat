let ultimaApuracao = null;

function formatarCompetencia(value) {
  const digits = value.replace(/\D/g, '').slice(0, 6);
  return digits.length > 2 ? `${digits.slice(0, 2)}-${digits.slice(2)}` : digits;
}

document.addEventListener('DOMContentLoaded', () => {
  ['comp_ini', 'comp_fim'].forEach((id) => {
    const input = document.getElementById(id);
    if (!input) return;
    input.value = formatarCompetencia(input.value);
    input.addEventListener('input', () => {
      input.value = formatarCompetencia(input.value);
    });
  });
});

async function gerarApuracao() {
  const statusEl = document.getElementById('apuracaoStatus');
  const outputEl = document.getElementById('apuracaoOutput');
  const btn = document.getElementById('btnGerarApuracao');
  let timerId = null;

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  // validate inputs before sending request
  const compIniVal = document.getElementById('comp_ini')?.value.trim() || '';
  const compFimVal = document.getElementById('comp_fim')?.value.trim() || '';
  const municipioCnpjVal = document.getElementById('municipio_cnpj')?.value.trim() || '';
  const municipioNome = document.getElementById('municipio_nome')?.value.trim() || '';

  // presence check
  if (!compIniVal || !compFimVal) {
    alert('Por favor preencha as competências inicial e final (formato MM-AAAA).');
    return;
  }

  // simple format check YYYY-MM
  const compRegex = /^\d{2}-\d{4}$/;
  if (!compRegex.test(compIniVal) || !compRegex.test(compFimVal)) {
    alert('Formato de competência inválido. Use MM-AAAA (ex: 09-2025).');
    return;
  }

  // validate CNPJ presence and basic format (14 digits)
  if (!municipioCnpjVal) {
    alert('Por favor selecione um município válido (CNPJ).');
    return;
  }
  const cnpjDigits = municipioCnpjVal.replace(/\D/g, '');
  if (cnpjDigits.length !== 14) {
    alert('CNPJ inválido. Deve conter 14 dígitos.');
    return;
  }

  const body = {
    comp_ini: compIniVal,
    comp_fim: compFimVal,
    cnpj: cnpjDigits,
    aliquota: parseFloat((document.getElementById('aliquota_gilrat')?.value || '2,00').trim().replace(',', '.')),
    municipio: municipioNome
  };

  try {
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Processando...';
    }
    if (outputEl) outputEl.textContent = 'Iniciando apuração...';

    const startedAt = Date.now();
    timerId = setInterval(() => {
      const secs = Math.floor((Date.now() - startedAt) / 1000);
      setStatus(`Processando dados... ${secs}s`);
    }, 1000);

    const r = await fetch('/apuracao/calcularGilRat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token() },
      body: JSON.stringify(body)
    });
    const j = await r.json();
    ultimaApuracao = j.resultado || j;
    if (outputEl) outputEl.textContent = JSON.stringify(j, null, 2);
    if (j.apuracoes) buildCharts(j.apuracoes);
    setStatus('Apuração concluída com sucesso.');
  } catch (err) {
    console.error('Erro ao gerar apuração:', err);
    setStatus('Falha ao processar a apuração.');
    alert('Erro de rede/servidor ao gerar a apuração. Verifique o console para detalhes.');
  } finally {
    if (timerId) clearInterval(timerId);
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Gerar Apuração';
    }
  }
}

async function gerarPDFApuracao() {
  if (!ultimaApuracao) {
    alert('Gere a apuração antes de gerar o relatório PDF.');
    return;
  }

  const cnpj = document.getElementById('municipio_cnpj')?.value || '';
  const municipio = document.getElementById('municipio_nome')?.value.trim() || '';
  if (!municipio) {
    alert('Selecione um município antes de gerar o relatório PDF.');
    return;
  }
  const response = await fetch('/reports/apuracao/pdf', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token()
    },
    body: JSON.stringify({
      resultado: ultimaApuracao,
      cnpj: cnpj,
      municipio: municipio,
      comp_ini: document.getElementById('comp_ini')?.value.trim() || '',
      comp_fim: document.getElementById('comp_fim')?.value.trim() || ''
    })
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Falha ao gerar o relatório PDF');
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'relatorio_apuracao_sat_gilrat.pdf';
  link.click();
  URL.revokeObjectURL(url);
}