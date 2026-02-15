import pytest

from indieshout.models.content import Content, ContentType
from indieshout.publishers.base import BasePublisher
from indieshout.blog.base import BaseBlogPublisher


class ConcretePublisher(BasePublisher):
    def authenticate(self) -> bool:
        return True

    def validate(self, content: Content) -> bool:
        return bool(content.text)

    def format_content(self, content: Content) -> dict:
        return {"text": content.text}

    def publish(self, content: Content) -> dict:
        return {"status": "ok", "id": "123"}


class TestBasePublisher:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BasePublisher(config={})

    def test_concrete_publisher(self):
        pub = ConcretePublisher(config={"key": "value"})
        assert pub.config == {"key": "value"}
        assert pub.authenticate() is True

        content = Content(content_type=ContentType.SNS, text="test")
        assert pub.validate(content) is True
        assert pub.format_content(content) == {"text": "test"}
        assert pub.publish(content)["status"] == "ok"


class TestBaseBlogPublisher:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseBlogPublisher(config={})
