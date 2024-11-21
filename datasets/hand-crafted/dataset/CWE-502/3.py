import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/parse_xml", methods=["POST"])
def parse_xml():
    xml_data = request.data
    try:

        root = ET.fromstring(xml_data)
        return jsonify({"message": "XML parsed successfully", "data": root.tag})
    except ET.ParseError as e:
        return jsonify({"error": str(e)}), 400
