"""블로그 + SNS 통합 게시 워크플로우."""

from pathlib import Path

from indieshout.blog.content_loader import ContentLoader
from indieshout.blog.hugo_publisher import HugoPublisher
from indieshout.models.content import Content, ContentType
from indieshout.publishers.threads import ThreadsPublisher
from indieshout.publishers.twitter import TwitterPublisher


class PublishWorkflow:
    """블로그 + SNS 통합 게시 워크플로우."""

    def __init__(self, config: dict):
        """PublishWorkflow 초기화.

        Args:
            config: 설정 dict
        """
        self.config = config
        self.content_loader = ContentLoader()
        self.hugo_publisher = HugoPublisher(config)

        # SNS 퍼블리셔 초기화
        self.publishers = {}
        if config.get("twitter"):
            self.publishers["x"] = TwitterPublisher(config)
        if config.get("threads"):
            self.publishers["threads"] = ThreadsPublisher(config)

    def publish_from_folder(
        self,
        folder_name: str,
        dry_run: bool = False,
        skip_blog: bool = False,
        skip_sns: bool = False,
    ) -> dict:
        """폴더에서 블로그 + SNS 통합 게시.

        Args:
            folder_name: blog-content 하위 폴더 이름
            dry_run: True면 실제 게시 안 함
            skip_blog: True면 블로그 게시 건너뛰기
            skip_sns: True면 SNS 게시 건너뛰기

        Returns:
            게시 결과 dict
        """
        # 1. 폴더에서 콘텐츠 로드
        print(f"📂 폴더 로드: {folder_name}")
        data = self.content_loader.load_from_folder(folder_name)

        blog_content = data["blog_content"]
        sns_text = data["sns_text"]
        platforms = data["platforms"]

        print(f"✅ 로드 완료:")
        print(f"  - 제목: {blog_content.title}")
        print(f"  - 이미지: {len(blog_content.image_paths or [])}장")
        print(f"  - SNS 플랫폼: {', '.join(platforms)}")

        result = {"blog": None, "sns": {}}

        # 2. 블로그 게시
        blog_url = None
        if not skip_blog:
            print(f"\n📝 블로그 게시 중...")
            if dry_run:
                print("  [DRY RUN] 블로그 게시 생략")
                blog_url = f"https://example.com/posts/{blog_content.slug or 'test'}/"
                result["blog"] = {"url": blog_url, "status": "dry_run"}
            else:
                try:
                    self.hugo_publisher.authenticate()
                    self.hugo_publisher.validate(blog_content)
                    blog_result = self.hugo_publisher.publish(blog_content)
                    blog_url = blog_result["url"]
                    result["blog"] = blog_result

                    print(f"✅ 블로그 게시 완료: {blog_url}")
                    if blog_result.get("images"):
                        print(f"  - S3 이미지: {len(blog_result['images'])}장 업로드")

                except Exception as e:
                    print(f"❌ 블로그 게시 실패: {e}")
                    return result

        # 3. SNS 게시 (블로그 URL 포함)
        if not skip_sns and sns_text:
            print(f"\n📱 SNS 게시 중...")

            # SNS 텍스트에 블로그 URL 추가
            full_sns_text = sns_text
            if blog_url:
                full_sns_text = f"{sns_text}\n\n🔗 {blog_url}"

            # Content 객체 생성 (SNS용)
            sns_content = Content(
                content_type=ContentType.SNS,
                text=full_sns_text,
                platforms=platforms,
            )

            # 각 플랫폼에 게시
            for platform in platforms:
                if platform not in self.publishers:
                    print(f"  ⚠️ {platform}: 설정되지 않음 (건너뛰기)")
                    continue

                publisher = self.publishers[platform]

                if dry_run:
                    print(f"  [DRY RUN] {platform}: 게시 생략")
                    result["sns"][platform] = {"status": "dry_run"}
                else:
                    try:
                        publisher.authenticate()
                        publisher.validate(sns_content)
                        sns_result = publisher.publish(sns_content)
                        result["sns"][platform] = sns_result

                        print(f"  ✅ {platform}: 게시 완료")

                    except Exception as e:
                        print(f"  ❌ {platform}: 게시 실패 - {e}")
                        result["sns"][platform] = {"error": str(e)}

        # 4. 최종 요약
        print(f"\n{'='*50}")
        print("📊 게시 결과 요약")
        print(f"{'='*50}")

        if result["blog"]:
            print(f"✅ 블로그: {result['blog']['url']}")
        elif skip_blog:
            print(f"⏭️ 블로그: 건너뛰기")
        else:
            print(f"❌ 블로그: 실패")

        if result["sns"]:
            print(f"\nSNS 게시:")
            for platform, sns_result in result["sns"].items():
                if "error" in sns_result:
                    print(f"  ❌ {platform}: {sns_result['error']}")
                else:
                    print(f"  ✅ {platform}: 성공")
        elif skip_sns:
            print(f"⏭️ SNS: 건너뛰기")

        return result
