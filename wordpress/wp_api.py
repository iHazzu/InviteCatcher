import requests
from typing import Optional


class WpApi:
    def __init__(self, domain: str, user: str, password: str):
        self.domain = domain
        self.user = user
        self.password = password
        self.api_url = domain + "wp-json/wp/v2/"
        self.jwt_token = self.generate_jwt_token()

    def generate_jwt_token(self) -> str:
        params = {
            'username': self.user,
            'password': self.password
        }
        url = self.domain + "wp-json/jwt-auth/v1/token"
        req = requests.post(url=url, params=params)
        return req.json()['token']

    def authenticate(self, headers: dict) -> dict:
        if not headers:
            auth = {'Authorization': f"Bearer {self.jwt_token}"}
        else:
            auth = headers.copy()
            auth['Authorization'] = f"Bearer {self.jwt_token}"
        return auth

    def api_req(self, method: str, endpoint: str, params: dict = None, data=None, headers: dict = None):
        resp = requests.request(
            method=method,
            url=self.api_url + endpoint,
            params=params,
            data=data,
            headers=self.authenticate(headers)
        )
        if resp.status_code == 403:  # jwt token expired
            self.jwt_token = self.generate_jwt_token()
            resp = requests.request(
                method=method,
                url=self.api_url + endpoint,
                params=params,
                data=data,
                headers=self.authenticate(headers)
            )
        return resp.json()

    def get_post(self, post_type: str, search: str) -> Optional[dict]:
        payload = {
            'post_type': post_type,
            'search': search
        }
        posts = self.api_req(method="GET", endpoint=post_type, params=payload)
        if posts:
            return posts[0]
        else:
            return None

    def upload_image(self, filename: str, image: bytes) -> dict:
        ext = filename.split(".")[-1]
        headers = {
            'Content-Type': f'image/{ext}',
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return self.api_req(method="POST", endpoint="media", data=image, headers=headers)

    def create_post(self, post_type: str, title: str, desc: str, media_id: int):
        payload = {
            'title': title,
            'content': desc,
            'status': 'publish',
            'featured_media': media_id
        }
        self.api_req(method="POST", endpoint=post_type, data=payload)

    def edit_post(self, post_type, post_id: int, desc: str):
        payload = {
            'id': post_id,
            'content': desc
        }
        self.api_req(method="POST", endpoint=f"{post_type}/{post_id}", data=payload)