import logging
import os
import subprocess

from flask import Flask, json, jsonify, request, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.before_request
def log_request_info():
    logger.info("=== REQUEST START ===")
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.method in ["POST", "PUT"] and request.content_length:
        logger.info(f"Content Length: {request.content_length}")


@app.after_request
def log_response_info(response):
    logger.info(f"Response Status: {response.status_code}")
    logger.info("=== REQUEST END ===")
    return response


def stream_process(command, cwd=None, shell=True):
    if cwd is None:
        cwd = os.getcwd()

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        shell=shell,
    )

    for line in iter(process.stdout.readline, ""):
        yield line

    for line in iter(process.stderr.readline, ""):
        yield line


def write_file(file_name, content):
    path = os.path.join("data", file_name)
    logger.info(f"Writing file: {file_name} to path: {path}")
    logger.info(f"Content length: {len(content)} characters")

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    try:
        with open(path, "w+") as f:
            f.write(content)
        logger.info(f"Successfully wrote file: {file_name}")
    except Exception as e:
        logger.error(f"Error writing file {file_name}: {str(e)}")
        raise


@app.route("/terravision/graph", methods=["GET"])
def terravision_graph():
    logger.info("=== TERRAVISION GRAPH ENDPOINT ===")

    try:
        # Full workflow: init, validate, generate graph, transform, create image
        command = """
mkdir -p ./output && \
echo "Initializing Terraform..." && \
terraform init && \
echo "Validating configuration..." && \
terraform validate && \
echo "Generating graph..." && \
terraform graph | sed s/"RL"/"TB"/g | node ../index.js | tee /dev/stderr | dot -Tpng > ./output/diagram.dot.png && \
echo "Diagram generated successfully!"
"""
        logger.info("Starting Terraform graph generation workflow")
        logger.info("Working directory: ./data")

        return app.response_class(
            stream_process(command, cwd="./data"), mimetype="text/plain",
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Graph generation failed: {str(e)}")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f'Command output: {e.output if hasattr(e, "output") else "N/A"}')
        return jsonify(error=str(e)), 500
    except Exception as e:
        logger.error(f"Unexpected error in terravision_graph: {str(e)}")
        return jsonify(error=f"Unexpected error: {str(e)}"), 500


@app.route("/terravision/write", methods=["POST"])
def terravision_write():
    logger.info("=== TERRAVISION WRITE ENDPOINT ===")

    try:
        # Log raw request data
        raw_data = request.data
        logger.info(f"Raw request data length: {len(raw_data)} bytes")

        data = json.loads(raw_data)
        logger.info(f"Parsed JSON data keys: {list(data.keys())}")

        expected_files = ["main.tf", "variables.tf", "terraform.tfvars"]
        logger.info(f"Expected files: {expected_files}")

        for file_name in expected_files:
            if file_name in data:
                content = data[file_name]["value"]
                logger.info(
                    f"Processing file: {file_name}, content preview: {content[:100]}..."
                )
                write_file(file_name, content)
            else:
                logger.warning(f"Missing expected file: {file_name}")

        logger.info("All files processed successfully")
        return jsonify(success=True)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return jsonify(error="Invalid JSON data"), 400
    except KeyError as e:
        logger.error(f"Missing key in data: {str(e)}")
        return jsonify(error=f"Missing required key: {str(e)}"), 400
    except Exception as e:
        logger.error(f"Unexpected error in terravision_write: {str(e)}")
        return jsonify(error=str(e)), 500


@app.route("/terravision/validate", methods=["GET"])
def terravision_validate():
    logger.info("=== TERRAVISION VALIDATE ENDPOINT ===")

    try:
        command = """
echo "Initializing Terraform..." && \
terraform init && \
echo "Validating configuration..." && \
terraform validate && \
echo "Validation completed successfully!"
"""
        logger.info("Starting Terraform validation workflow")
        logger.info(f"Working directory: ./data")

        return app.response_class(
            stream_process(command, cwd="./data"),
            mimetype="text/plain",
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Validation failed: {str(e)}")
        logger.error(f"Return code: {e.returncode}")
        return jsonify(error=str(e)), 500
    except Exception as e:
        logger.error(f"Unexpected error in terravision_validate: {str(e)}")
        return jsonify(error=f"Unexpected error: {str(e)}"), 500


@app.route("/terravision/output")
def terravision_output():
    return send_from_directory("./data/output", "diagram.dot.png")


@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint for Docker health checks"""
    logger.info("Health check requested")
    from datetime import datetime

    return (
        jsonify(
            {
                "status": "healthy",
                "service": "terravision-api",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
            },
        ),
        200,
    )


if __name__ == "__main__":
    logger.info("=== TERRAVISION FLASK APP STARTING ===")
    logger.info("Host: 0.0.0.0, Port: 8001")
    logger.info("CORS enabled for all routes")
    app.run(host="0.0.0.0", port=8001)
