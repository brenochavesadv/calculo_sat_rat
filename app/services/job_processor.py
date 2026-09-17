import re

from run import db

def process_jobfile_bytes(data: bytes, filename: str = None, jf=None, municipio_cnpj: str = None):
    """Process uploaded file bytes in-memory.

    If a JobFile instance `jf` is provided it will be updated (status/error/processed_at)
    and committed to the database. Otherwise the function returns the importer result
    dictionary (same shape as the existing importers).

    This mirrors `process_jobfile` but does not read/remove any disk file.
    """
    res = None
    try:
        # import here to avoid heavy imports at module import time
        from app.imports.import_s1005_evtTabEstab import import_s1005_evtTabEstab
        from app.imports.import_s1010_evtTabRubrica import import_s1010_evtTabRubrica
        from app.imports.import_s1200_evtRemun import import_s1200_evtRemun
        from app.imports.import_s1202_evtRmnRPPS import import_s1202_evtRmnRPPS
        from app.imports.import_s1210_evtPgtos import import_s1210_evtPgtos
        from app.imports.import_s1298_evtReabreEvPer import import_s1298_evtReabreEvPer
        from app.imports.import_s1299_evtFechaEvPer import import_s1299_evtFechaEvPer
        from app.imports.import_s5001_evtBasesTrab import import_s5001_evtBasesTrab
        from app.imports.import_s5002_evtIrrfBenef import import_s5002_evtIrrfBenef
        from app.imports.import_s5011_evtCs import import_s5011_evtCs

        name = (filename or '').lower()
        print(f"ℹ️ Processing file: {filename}, inferred name: {name}")

        event_match = re.search(r'\.s-(\d{4})\.xml$', name)
        event_code = event_match.group(1) if event_match else None

        # map the explicit eSocial event code when available; fall back to legacy substring checks only if needed
        if event_code == '1005':
            res = import_s1005_evtTabEstab(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1010':
            res = import_s1010_evtTabRubrica(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1200':
            res = import_s1200_evtRemun(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1202':
            res = import_s1202_evtRmnRPPS(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1210':
            res = import_s1210_evtPgtos(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1298':
            res = import_s1298_evtReabreEvPer(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '1299':
            res = import_s1299_evtFechaEvPer(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '5001':
            res = import_s5001_evtBasesTrab(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '5002':
            res = import_s5002_evtIrrfBenef(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        elif event_code == '5011':
            res = import_s5011_evtCs(data, source_file=filename, municipio_cnpj=municipio_cnpj)
        #elif 'ir' in name:
            #res = import_   (data, source_file=filename, municipio_cnpj=municipio_cnpj)
        else:
            res = {'sucess': False, 'error': 'unknown_file_type'}

        # normalize importer result keys (some importers return 'sucess' spelled incorrectly)
        if isinstance(res, dict):
            # determine boolean success from common keys
            success_flag = bool(res.get('sucess') or res.get('success') or (res.get('inserted') and int(res.get('inserted')) > 0))
            # ensure the canonical key `sucess` exists for downstream code
            res['sucess'] = success_flag
            # interpret result and update jf if provided
            if res.get('error'):
                if jf:
                    jf.status = 'error'
                    jf.error = str(res.get('error'))
            else:
                if jf:
                    jf.status = 'success'
                    jf.error = None

        try:
            from flask import current_app
            current_app.logger.info('process_jobfile_bytes result for %s: %s', filename, str(res))
        except Exception:
            pass
    except Exception as e:
        if jf:
            jf.status = 'error'
            jf.error = str(e)
        else:
            res = {'success': False, 'error': str(e)}
    finally:
        if jf:
            from datetime import datetime, timezone
            jf.processed_at = datetime.now(timezone.utc)
            db.session.add(jf)
            db.session.commit()
            # extra debug: log the persisted jobfile id/status/error to help trace UI discrepancies
            try:
                from flask import current_app
                current_app.logger.info('JobFile persisted id=%s status=%s error=%s', jf.id, jf.status, jf.error)
            except Exception:
                pass
    return res


def process_jobfile(jf):
    """Process a JobFile saved on disk. Reads the file bytes and delegates
    to `process_jobfile_bytes` so both folder and single-file flows behave
    identically and update the same `JobFile` row.
    """
    # mark as processing early so UI polling shows progress
    try:
        jf.status = 'processing'
        db.session.add(jf)
        db.session.commit()
    except Exception:
        db.session.rollback()
    try:
        data = b''
        if jf.filepath:
            with open(jf.filepath, 'rb') as fh:
                data = fh.read()
        res = process_jobfile_bytes(data, filename=jf.filename, jf=jf)
        return res
    except Exception as e:
        # ensure jf is marked as error
        try:
            jf.status = 'error'
            jf.error = str(e)
            from datetime import datetime, timezone
            jf.processed_at = datetime.now(timezone.utc)
            db.session.add(jf)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return {'sucess': False, 'error': str(e)}
