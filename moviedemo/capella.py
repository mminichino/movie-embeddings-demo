##
##

from cbcmgr.cb_capella import Capella
from cbcmgr.cb_bucket import Bucket


def create_bucket(profile: str, project: str, database: str, name: str, quota: int, replicas: int = 1):
    project_config = Capella(profile=profile).get_project(project)
    project_id = project_config.get('id')

    bucket = Bucket.from_dict(dict(
        name=name,
        ram_quota_mb=quota,
        num_replicas=replicas,
        max_ttl=0
    ))

    cluster = Capella(project_id=project_id, profile=profile).get_cluster(database)
    cluster_id = cluster.get('id')
    Capella(project_id=project_id, profile=profile).add_bucket(cluster_id, bucket)
