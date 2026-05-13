from flask import jsonify

def json_response(data):
    if isinstance(data, list):
        return jsonify([
            item.to_dict() if hasattr(item, 'to_dict') else item
            for item in data
        ])

    if hasattr(data, 'to_dict'):
        return jsonify(data.to_dict())

    return jsonify(data)