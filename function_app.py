import json
import logging

import azure.functions as func
import requests
from azure.core.exceptions import ClientAuthenticationError

from upload_sample_indicators import upload_sample_indicators


app = func.FunctionApp()
UPLOAD_EXCEPTIONS = (
    ClientAuthenticationError,
    KeyError,
    requests.RequestException,
    RuntimeError,
    ValueError,
)


@app.function_name(name="UploadSampleIndicatorsHttp")
@app.route(
    route="upload-sample-indicators",
    methods=["POST"],
    auth_level=func.AuthLevel.FUNCTION,
)
def upload_sample_indicators_http(req: func.HttpRequest) -> func.HttpResponse:
    del req
    try:
        result = upload_sample_indicators()
    except UPLOAD_EXCEPTIONS:
        logging.exception("The HTTP-triggered indicator upload failed.")
        return func.HttpResponse(
            body=json.dumps({"error": "The indicator upload failed."}),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        body=json.dumps(result),
        status_code=200,
        mimetype="application/json",
    )


@app.function_name(name="UploadSampleIndicatorsTimer")
@app.timer_trigger(
    schedule="%UPLOAD_SCHEDULE%",
    arg_name="timer",
    run_on_startup=False,
    use_monitor=True,
)
def upload_sample_indicators_timer(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.warning("The indicator upload timer is running later than scheduled.")

    try:
        result = upload_sample_indicators()
    except UPLOAD_EXCEPTIONS:
        logging.exception("The timer-triggered indicator upload failed.")
        raise

    logging.info("The timer-triggered indicator upload completed: %s", result)
