##
##

from typing import Optional, Tuple, List
import socket
import googleapiclient.discovery
import google.auth
import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel
)


class GoogleEmbedding:

    def __init__(self, region: str = 'us-central1'):
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
    def get_image_embeddings(
        image_bytes: bytes,
        contextual_text: Optional[str] = None,
        dimension: int = 1408,
    ) -> Tuple[Optional[List[float]], Optional[List[float]]]:

        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
        image = Image(image_bytes=image_bytes)

        embeddings = model.get_embeddings(
            image=image,
            contextual_text=contextual_text,
            dimension=dimension,
        )

        return embeddings.image_embedding, embeddings.text_embedding

    @staticmethod
    def get_text_embeddings(contextual_text: str, dimension: int = 1408) -> List[float]:

        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")

        embeddings = model.get_embeddings(
            image=None,
            contextual_text=contextual_text,
            dimension=dimension,
        )

        return embeddings.text_embedding
