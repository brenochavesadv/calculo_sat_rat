from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint("selic", __name__)

@bp.post("/")
@jwt_required()
def get_selic(tipo_evento):
    # Implement the logic to retrieve the SELIC data
    return jsonify({"message": "SELIC data retrieved successfully"}), 200