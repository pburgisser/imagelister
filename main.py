from __future__ import print_function
from kubernetes import client, config
from terminaltables import AsciiTable
from pprint import pprint
import sys
import csv



def main():
  config.load_kube_config()

  v1 = client.CoreV1Api()
  api_instance = client.AppsV1Api()

  images_dict = []
  images_table = [['namespace','image']]
  ret = v1.list_pod_for_all_namespaces()
  
  for i in ret.items:
    image_value = {"namespace": i.metadata.namespace, "image": i.status.container_statuses[0].image}
    images_dict.append(image_value)
    images_table.append([i.metadata.namespace,i.status.container_statuses[0].image])
  table = AsciiTable(images_table)
  print(table.table)
  with open('images.csv', 'w', newline='') as f:
      fieldnames = ['namespace', 'image']
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(images_dict)

if __name__ == "__main__":
  sys.exit(main())