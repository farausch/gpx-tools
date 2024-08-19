import logging
import uuid
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from gpx_overlay import find_gas_stations_sampled, parse_gpx, plot_route_and_gas_stations_gm

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

html_contents = {}

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

def process_gpx_file(id, file_content, sampling_rate, search_radius):
    logger.info('Processing GPX file with sampling rate {} and search radius {}...'.format(sampling_rate, search_radius))
    route = parse_gpx(file_content)
    gas_stations = find_gas_stations_sampled(route, sampling_rate, search_radius)
    global html_contents
    html_contents[id] = plot_route_and_gas_stations_gm(route, gas_stations)._repr_html_()
    logger.info('Stored map for GPX file with id {}'.format(id))

@app.post("/gpx")
async def upload_gpx_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    random_id = str(uuid.uuid4())
    sampling_rate = 500
    search_radius = 10000
    logger.info('Received GPX file {} with sampling rate {} and search radius {}'.format(file.filename, sampling_rate, search_radius))
    file_content = await file.read()
    background_tasks.add_task(process_gpx_file, random_id, file_content, sampling_rate, search_radius)
    return {"id": random_id}

@app.get("/map/{id}")
def get_map(id):
    logger.info('Getting map with id {}...'.format(id))
    if id not in html_contents:
        raise HTTPException(status_code=404, detail="Map id not found")
    html_map = html_contents.get(id)
    html_contents.pop(id)
    return html_map
