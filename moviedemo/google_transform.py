##
##

from typing import Optional, Tuple, List
from cbcmgr.cb_transform import Transform
from moviedemo.restmgr import RESTManager
import socket
import googleapiclient.discovery
import google.auth
import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel
)


class GoogleEmbedding(Transform):

    def __init__(self, *args, region: str = 'us-central1', **kwargs):
        super().__init__(*args, **kwargs)
        self.gcp_account = None
        self.gcp_project = None
        self.gcp_region = region
        self.gcp_account_file = None
        self.gcp_account_email = None
        self.gcp_zone_list = []
        self.gcp_zone = None

        socket.setdefaulttimeout(120)

        self.credentials, self.gcp_project, self.gcp_account_email = self.default_auth()

        self.gcp_client = googleapiclient.discovery.build('compute', 'v1', credentials=self.credentials)
        vertexai.init(project=self.gcp_project, location=self.gcp_region, credentials=self.credentials)

    @staticmethod
    def default_auth():
        try:
            credentials, project_id = google.auth.default()
            if hasattr(credentials, "service_account_email"):
                account_email = credentials.service_account_email
            else:
                account_email = credentials.signer_email
            return credentials, project_id, account_email
        except Exception as err:
            raise RuntimeError(f"error connecting to GCP: {err}")

    @staticmethod
    def get_text_embeddings(contextual_text: str, dimension: int = 1408) -> List[float]:

        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

        embeddings = model.get_embeddings(
            image=None,
            contextual_text=contextual_text,
            dimension=dimension,
        )

        return embeddings.text_embedding

    @staticmethod
    def get_image_embeddings(image_bytes: bytes, contextual_text: Optional[str] = None, dimension: int = 1408) -> Tuple[Optional[List[float]], Optional[List[float]]]:
        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
        image = Image(image_bytes=image_bytes)

        embeddings = model.get_embeddings(
            image=image,
            contextual_text=contextual_text,
            dimension=dimension,
        )

        return embeddings.image_embedding, embeddings.text_embedding

    def transform(self, source: dict) -> Tuple[str, dict]:
        poster_url = source['poster_path']
        movie_overview = source['overview']
        record_id = str(source['id'])
        image_bytes = RESTManager().get_url_content(poster_url)

        image_embedding, text_embedding = self.get_image_embeddings(image_bytes, movie_overview)

        embedding_model = "multimodalembedding"

        document = dict(
            title=source.get('title'),
            release_date=source.get('release_date'),
            popularity=source.get('popularity'),
            imdb_id=source.get('imdb_id'),
            overview=source.get('overview'),
            poster_path=source.get('poster_path'),
            backdrop_path=source.get('backdrop_path'),
            embedding_model=embedding_model,
            image_embedding=image_embedding,
            text_embedding=text_embedding
        )

        return record_id, document
