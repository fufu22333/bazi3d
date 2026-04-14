from flask import Blueprint, Response, jsonify, request
import requests


proxy_bp = Blueprint("proxy", __name__, url_prefix="/api/proxy")


@proxy_bp.get("/glb")
def proxy_glb():
    source_url = request.args.get("url", type=str)
    if not source_url:
        return jsonify({"error": "url is required"}), 400

    try:
        upstream = requests.get(source_url, timeout=30)
        upstream.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"error": f"failed to fetch glb: {exc}"}), 502

    response = Response(upstream.content, content_type="model/gltf-binary")
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
