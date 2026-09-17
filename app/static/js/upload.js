/*
  Improved uploader:
  - only accepts .xml files
  - uploads in configurable batches to avoid huge single requests (important for thousands of files)
  - shows a counter (processed / total) and a progress bar that reflects total progress
  - uses XHR per-batch to get upload progress events
*/

// Note: this uploader expects an input with id="municipio_cnpj" containing the municipality CNPJ.
// The server `POST /upload/file` uses municipio_cnpj to look up the Municipio.

document.getElementById('uploadForm').addEventListener('submit', async e => {
  e.preventDefault();
  const input = document.getElementById('lotes');
  const submitBtn = document.querySelector('#uploadForm button[type=submit]');
  const municipio_cnpj = (document.getElementById('municipio_cnpj') ? document.getElementById('municipio_cnpj').value : '').trim();
  if (!municipio_cnpj) return alert('Informe o CNPJ do município (municipio_cnpj)');

  // collect XML files only
  const filesAll = Array.from(input.files || []);
  const xmlFiles = filesAll.filter(f => f && /\.xml$/i.test(f.name));
  if (!xmlFiles.length) return alert('Selecione um ou mais arquivos XML');

  // UI elements: counters and output
  const output = document.getElementById('uploadOutput');
  const uploadedCounterEl = document.getElementById('uploadUploadedCounter');
  const processedCounterEl = document.getElementById('uploadProcessedCounter');
  const totalCountEls = document.querySelectorAll('#uploadTotalCount, #uploadTotalCount2');
  if (totalCountEls) totalCountEls.forEach(el => el.textContent = String(xmlFiles.length));
  if (uploadedCounterEl) uploadedCounterEl.textContent = '0';
  if (processedCounterEl) processedCounterEl.textContent = '0';
  if (output) output.textContent = 'Iniciando upload sequencial...';

  // disable submit while uploading/processing
  if (submitBtn) submitBtn.disabled = true;

  let uploaded = 0;
  let processed = 0;
  let failed = 0;
  const uploadedFileIds = [];
  const errorLogs = [];

  // upload files sequentially (no progress bar)
  for (let i = 0; i < xmlFiles.length; i++) {
    const f = xmlFiles[i];
    output.textContent = `Enviando arquivo ${i+1}/${xmlFiles.length}: ${f.name}`;

    const fd = new FormData();
    fd.append('municipio_cnpj', municipio_cnpj);
    fd.append('file', f);

    try {
  const res = await fetch('/upload/file', { method: 'POST', body: fd, credentials: 'include', headers: { 'Authorization': 'Bearer ' + token() } });
      if (!res.ok) {
        failed += 1;
        const txt = await res.text();
        const msg = `Erro: ${f.name}: ${txt}`;
        output.textContent = msg;
        errorLogs.push(msg);
        continue;
      }
      const j = await res.json();
      const file_id = j.file_id || j.fileId || j.id;
      if (!file_id) {
        failed += 1;
        const msg = `Resposta inválida: ${f.name}`;
        output.textContent = msg;
        errorLogs.push(msg);
        continue;
      }
      // If the server already processed the file synchronously it may return processing_result
      const procRes = j.processing_result || null;
      if (procRes && (procRes.status === 'success' || procRes.status === 'error' || procRes.ok || procRes.inserted !== undefined)) {
        // server already processed this file
        uploaded += 1;
        if (uploadedCounterEl) uploadedCounterEl.textContent = `${uploaded}`;
        if (procRes.status === 'success' || procRes.ok || (procRes.inserted && procRes.inserted > 0)) {
          processed += 1;
          if (processedCounterEl) processedCounterEl.textContent = `${processed}`;
          output.textContent = `Arquivo enviado e processado: ${f.name} (id=${file_id}) — ${processed}/${xmlFiles.length}`;
        } else {
          failed += 1;
          const msg = `Falha: ${f.name} — ${JSON.stringify(procRes)}`;
          output.textContent = msg;
          errorLogs.push(msg);
        }
      } else {
        // not yet processed on server side; queue for polling
        uploadedFileIds.push(file_id);
        uploaded += 1;
        if (uploadedCounterEl) uploadedCounterEl.textContent = `${uploaded}`;
        output.textContent = `Arquivo enviado: ${f.name} (id=${file_id}) — ${uploaded}/${xmlFiles.length}`;
      }
      // small polite delay
      await new Promise(r => setTimeout(r, 120));
    } catch (err) {
      console.error('Erro no upload', err);
      failed += 1;
      const msg = `Erro: ${f.name} - ${err.message}`;
      output.textContent = msg;
      errorLogs.push(msg);
    }
  }

  // After all uploads finished, start processing phase by polling statuses
  output.textContent = `Upload concluído: ${uploaded} enviados, iniciando processamento...`;

  // Create a persistent error log UI now so we can append errors as they occur
  let logContainer = document.getElementById('uploadLogsContainer');
  const existingBtn = document.getElementById('showUploadLogsBtn');
  if (existingBtn) existingBtn.remove();
  if (!logContainer) {
    logContainer = document.createElement('div');
    logContainer.id = 'uploadLogsContainer';
    logContainer.style.display = 'none';
    logContainer.style.whiteSpace = 'pre-wrap';
    logContainer.style.background = '#f8f8f8';
    logContainer.style.border = '1px solid #ddd';
    logContainer.style.padding = '8px';
    logContainer.style.marginTop = '8px';
    logContainer.style.maxHeight = '300px';
    logContainer.style.overflow = 'auto';
  }

  const logBtn = document.createElement('button');
  logBtn.id = 'showUploadLogsBtn';
  logBtn.type = 'button';
  logBtn.textContent = errorLogs.length ? `Mostrar erros (${errorLogs.length})` : 'Mostrar erros (0)';
  logBtn.style.marginLeft = '8px';

  function renderLogs() {
    if (!errorLogs.length) {
      logContainer.textContent = 'Nenhum erro registrado.';
      logBtn.textContent = 'Mostrar erros (0)';
      return;
    }
    logContainer.innerHTML = '';
    const ul = document.createElement('ul');
    ul.style.paddingLeft = '18px';
    errorLogs.forEach(msg => {
      const li = document.createElement('li');
      li.textContent = msg;
      ul.appendChild(li);
    });
    logContainer.appendChild(ul);
    logBtn.textContent = `Mostrar erros (${errorLogs.length})`;
  }

  logBtn.addEventListener('click', () => {
    if (logContainer.style.display === 'none') {
      logContainer.style.display = 'block';
      logBtn.textContent = `Ocultar erros (${errorLogs.length})`;
    } else {
      logContainer.style.display = 'none';
      logBtn.textContent = `Mostrar erros (${errorLogs.length})`;
    }
  });

  // insert the controls near the output area
  if (output && output.parentNode) {
    output.parentNode.insertBefore(logBtn, output.nextSibling);
    output.parentNode.insertBefore(logContainer, logBtn.nextSibling);
  } else if (output) {
    output.appendChild(logBtn);
    output.appendChild(logContainer);
  } else {
    document.body.appendChild(logBtn);
    document.body.appendChild(logContainer);
  }
  renderLogs();

  // Poll each uploaded file until it reaches success or error
  async function waitForFileFinal(file_id, interval = 1500) {
    while (true) {
    try {
      const r = await fetch(`/upload/file_status?file_id=${encodeURIComponent(file_id)}`, { credentials: 'include', headers: { 'Authorization': 'Bearer ' + token() } });
        if (!r.ok) return { status: 'error', error: await r.text() };
        const j = await r.json();
        if (j.status === 'success' || j.status === 'error') return j;
      } catch (e) {
        // ignore transient errors
      }
      await new Promise(r => setTimeout(r, interval));
    }
  }

  for (let idx = 0; idx < uploadedFileIds.length; idx++) {
    const fid = uploadedFileIds[idx];
    const fileName = xmlFiles[idx].name;
    output.textContent = `Aguardando processamento do arquivo ${idx+1}/${uploadedFileIds.length} (id=${fid})...`;
    const result = await waitForFileFinal(fid, 1500);
    if (result && result.status === 'success') {
      processed += 1;
      output.textContent = `Processado ${processed} / ${uploadedFileIds.length} — id=${fid}`;
    } else {
      failed += 1;
      const msg = `Falha: ${fileName} - ${result && result.error ? JSON.stringify(result.error) : 'unknown'}`;
      // push the error and update UI immediately so user sees it as it happens
      errorLogs.push(msg);
      renderLogs();
      // ensure the log panel is visible when an error occurs
      logContainer.style.display = 'block';
      output.textContent = msg;
    }
    if (processedCounterEl) processedCounterEl.textContent = `${processed}`;
    // small delay between polls
    await new Promise(r => setTimeout(r, 120));
  }

  // re-enable submit
  if (submitBtn) submitBtn.disabled = false;

  if (failed) {
    output.textContent = `Concluído com ${failed} falhas. Processados com sucesso: ${processed}`;
  } else {
    output.textContent = `Processamento concluído. Processados: ${processed}`;
  }

  // (log UI was created earlier so errors are visible as they occur)
});