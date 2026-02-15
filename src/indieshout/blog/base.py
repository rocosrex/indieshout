from abc import abstractmethod
from pathlib import Path

from indieshout.models.content import Content
from indieshout.publishers.base import BasePublisher


class BaseBlogPublisher(BasePublisher):
    @abstractmethod
    def read_post(self, file_path: Path) -> Content:
        """마크다운 파일을 읽어 Content 객체로 변환."""
        ...

    @abstractmethod
    def deploy(self, content: Content) -> bool:
        """블로그 배포 (git push 등)."""
        ...

    @abstractmethod
    def get_post_url(self, content: Content) -> str:
        """게시된 포스트의 URL 반환."""
        ...
