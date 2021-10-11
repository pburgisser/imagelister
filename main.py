from flask import Flask,render_template,Response
from kubernetes import client, config
from prometheus_client import Gauge,generate_latest
from configparser import ConfigParser
import yaml

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

with open("config.yaml","r") as ymlfile:
  cfg = yaml.load(ymlfile)

ALLOWED_REGISTRIES = cfg["allowed_registries"]


app = Flask(__name__)
c = Gauge('image_allowed', 'Description of counter', ['namespace','image','pod','parent'])
def is_allowed(image):
  for registry in ALLOWED_REGISTRIES:
    is_allowed = 0
    if image.startswith(registry):
      is_allowed = 1
  return is_allowed

def list_images():
  config.load_kube_config()

  v1 = client.CoreV1Api()
  api_instance = client.AppsV1Api()
  images_table = []
  ret = v1.list_pod_for_all_namespaces()
  
  for i in ret.items:
    
    containers = i.spec.containers
    init_containers = i.spec.init_containers if i.spec.init_containers is not None else []
    for container in containers:
      images_table.append({"name": i.metadata.name,"namespace": i.metadata.namespace,"image":container.image,"parent": "pod","is_allowed":is_allowed(container.image)})
    for container in init_containers:
      images_table.append({"name": i.metadata.name,"namespace": i.metadata.namespace,"image":container.image,"parent": "init","is_allowed":is_allowed(container.image)})

  return images_table

@app.route("/")
def listimages():
  return render_template('imageslist.html', images=list_images())

@app.route("/metrics")
def metrics():
  for image in list_images():
    c.labels(namespace=image['namespace'],image=image['image'],pod=image['name'],parent=image['parent']).set(image['is_allowed'])
  return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)