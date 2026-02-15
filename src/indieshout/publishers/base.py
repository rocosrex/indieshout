from abc import ABC, abstractmethod

from indieshout.models.content import Content


class BasePublisher(ABC):
    def __init__(self, config: dict) -> None:
        self.config = config

    @abstractmethod
    def authenticate(self) -> bool:
        """인증 수행 및 토큰 검증."""
        ...

    @abstractmethod
    def validate(self, content: Content) -> bool:
        """게시 전 유효성 검사."""
        ...

    @abstractmethod
    def format_content(self, content: Content) -> dict:
        """플랫폼에 맞게 콘텐츠 변환."""
        ...

    @abstractmethod
    def publish(self, content: Content) -> dict:
        """게시 실행 후 결과 반환."""
        ...
