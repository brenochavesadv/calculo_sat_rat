from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.xml_parser import parse_xml_bytes, text
from app import db
import os
import uuid
from werkzeug.utils import secure_filename

# import tables for migrations
from app.models.esocial_s1005_evtTabEstab import ESocialS1005EvtTabEstab
from app.models.esocial_s1010_evtTabRubrica import ESocialS1010EvtTabRubrica
from app.models.esocial_s1200_evtRemun import ESocialS1200EvtRemun
from app.models.esocial_s1202_evtRmnRPPS import ESocialS1202EvtRmnRPPS
from app.models.esocial_s1210_evtPgtos import ESocialS1210EvtPgtos
from app.models.esocial_s5001_evtBasesTrab import ESocialS5001EvtBasesTrab
from app.models.esocial_s5002_evtIrrfBenef import ESocialS5002EvtIrrfBenef
from app.models.esocial_s5011_evtCs import ESocialS5011EvtCs
from app.models.import_skip import ImportSkip
from app.models.municipio import Municipio
from app.models.job import Job, JobFile

bp = Blueprint("upload", __name__)

@bp.post('/folder')
@jwt_required()
def upload_folder():
    """Receive multiple XML files uploaded from a selected folder and process each file.
    Expects form fields: municipio_nome, uf, codigo_ibge and files[] (XML files).
    """
    municipio_cnpj = request.form.get('municipio_cnpj')
    if not municipio_cnpj:
        return jsonify({'error':'Município não informado'}), 400
    # validate municipio exists in DB
    municipio = Municipio.query.filter_by(cnpj=(municipio_cnpj or '').strip()).first()
    if not municipio:
        return jsonify({'error':'Município não encontrado na base (cnpj inválido)'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error':'Nenhum arquivo enviado'}), 400

    # create staging directory for this upload
    staging_root = os.path.join(current_app.config.get('UPLOAD_FOLDER', '.'), 'staging')
    os.makedirs(staging_root, exist_ok=True)
    upload_id = uuid.uuid4().hex
    staging_dir = os.path.join(staging_root, upload_id)
    os.makedirs(staging_dir, exist_ok=True)

    # create a Job record
    job = Job(upload_id=upload_id, status='queued')
    db.session.add(job)
    db.session.flush()  # get job.id

    file_ids = []
    for f in files:
        filename = (f.filename or '')
        if not filename.lower().endswith('.xml'):
            continue
        safe_name = secure_filename(filename)
        save_path = os.path.join(staging_dir, safe_name)
        try:
            f.save(save_path)
            # validate that the municipio_cnpj first 8 digits match nrInsc in the XML
            try:
                with open(save_path, 'rb') as fh:
                    data = fh.read()
                root = parse_xml_bytes(data)
                nrInsc_xml = text(root, './/nrInsc', '')
                # normalize digits only
                import re
                muni_digits = re.sub(r'\D', '', (municipio_cnpj or ''))
                if muni_digits:
                    muni_prefix = muni_digits[:8]
                else:
                    muni_prefix = ''
                if muni_prefix and nrInsc_xml and muni_prefix != nrInsc_xml[:8]:
                    # mismatch: record as queued file but mark as error so caller can see
                    jf = JobFile(job_id=job.id, filename=filename, filepath=save_path, status='error', error=f'municipio_cnpj prefix {muni_prefix} does not match nrInsc {nrInsc_xml}')
                    db.session.add(jf)
                    db.session.flush()
                    file_ids.append(jf.id)
                    continue
            except Exception:
                # if parsing fails, continue and let importer validate later
                pass
            jf = JobFile(job_id=job.id, filename=filename, filepath=save_path, status='queued')
            db.session.add(jf)
            db.session.flush()
            file_ids.append(jf.id)
        except Exception as ex:
            #print('Erro salvando jobfile', filename, ex)
            continue

    # process files sequentially in this request (remove the need for a separate worker)
    processing_results = []
    try:
        from app.services.job_processor import process_jobfile
        # load freshly created job files and process one-by-one
        for fid in file_ids:
            jf = JobFile.query.get(fid)
            if jf:
                res = process_jobfile(jf)
                processing_results.append({'file_id': jf.id, 'result': res})
    except Exception as ex:
        print('Erro durante o processamento síncrono dos arquivos:', ex)

    db.session.commit()
    return jsonify({'ok': True, 'upload_id': upload_id, 'file_ids': file_ids, 'queued': len(file_ids), 'processing_results': processing_results})



@bp.get('/status')
@jwt_required()
def upload_status():
    """Return aggregated job status by job_id.
    Query param: job_id
    Returns counts per state and an optional list of file statuses (first 200 files).
    """
    job_id = request.args.get('job_id')
    if not job_id:
        return jsonify({'error':'job_id query parameter required'}), 400
    job = Job.query.filter_by(upload_id=job_id).first()
    if not job:
        return jsonify({'error':'job not found'}), 404
    total = job.files.count()
    queued = job.files.filter_by(status='queued').count()
    processing = job.files.filter_by(status='processing').count()
    success = job.files.filter_by(status='success').count()
    error = job.files.filter_by(status='error').count()
    # include sample file statuses (limit)
    files = []
    for jf in job.files.order_by(JobFile.id).limit(200):
        files.append({'id': jf.id, 'filename': jf.filename, 'status': jf.status, 'error': jf.error})
    return jsonify({'job_id': job.upload_id, 'total': total, 'queued': queued, 'processing': processing, 'success': success, 'error': error, 'files': files})


@bp.post('/file')
@jwt_required()
def upload_file():
    """Receive a single XML file, save to staging, and enqueue a Celery task for it.
    Expects form field: municipio_cnpj and file 'file'. Returns task_id.
    """
    municipio_cnpj = request.form.get('municipio_cnpj')
    if not municipio_cnpj:
        return jsonify({'error': 'Município não informado (municipio_cnpj)'}), 400

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'Nenhum arquivo enviado (campo file)'}), 400

    filename = (f.filename or '')
    if not filename.lower().endswith('.xml'):
        return jsonify({'error': 'Apenas arquivos XML são aceitos'}), 400

    # process file in-memory (do not save to disk)
    try:
        data = f.read()
        # enforce a safe in-memory size (configurable)
        max_in_memory = current_app.config.get('MAX_IN_MEMORY_UPLOAD_BYTES', 50 * 1024 * 1024)
        if len(data) > max_in_memory:
            return jsonify({'error': f'File too large for in-memory processing (limit {max_in_memory} bytes)'}), 413

        # quick validation: municipio_cnpj prefix vs nrInsc inside XML
        try:
            root = parse_xml_bytes(data)
            nrInsc_xml = text(root, './/nrInsc', '')
            import re
            muni_digits = re.sub(r'\D', '', (municipio_cnpj or ''))
            muni_prefix = muni_digits[:8] if muni_digits else ''
            if nrInsc_xml and muni_prefix and muni_prefix != nrInsc_xml[:8]:
                return jsonify({'error': f'municipio_cnpj prefix {muni_prefix} does not match nrInsc {nrInsc_xml}'}), 400
        except Exception:
            # parsing issue -> let importer handle it
            pass

        # create Job and JobFile records for audit (no filepath)
        upload_id = uuid.uuid4().hex
        job = Job(upload_id=upload_id, status='queued')
        db.session.add(job)
        db.session.flush()
        jf = JobFile(job_id=job.id, filename=filename, filepath='', status='queued')
        db.session.add(jf)
        db.session.flush()

        # process synchronously in-memory
        from app.services.job_processor import process_jobfile_bytes
        res = process_jobfile_bytes(data, filename=filename, jf=jf, municipio_cnpj=municipio_cnpj)

        db.session.commit()
        return jsonify({'ok': True, 'file_id': jf.id, 'job_id': job.upload_id, 'processing_result': res})
    except Exception as ex:
        db.session.rollback()
        return jsonify({'error': str(ex)}), 500



@bp.get('/file_status')
@jwt_required()
def file_status():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error':'file_id query parameter required'}), 400
    # use Session.get to avoid SQLAlchemy legacy Query.get warning
    jf = db.session.get(JobFile, file_id)
    if not jf:
        return jsonify({'error':'file not found'}), 404
    return jsonify({'id': jf.id, 'filename': jf.filename, 'status': jf.status, 'error': jf.error})
