import click

from indieshout.formatter.content_formatter import ContentFormatter
from indieshout.models.content import Content, ContentType
from indieshout.publishers.threads import ThreadsPublisher
from indieshout.publishers.twitter import TwitterPublisher
from indieshout.utils.config import load_config
from indieshout.utils.logger import setup_logger
from indieshout.workflows.publish_workflow import PublishWorkflow

PLATFORM_PUBLISHERS = {
    "x": TwitterPublisher,
    "threads": ThreadsPublisher,
}


@click.group()
@click.option("--config", "config_path", default=None, help="설정 파일 경로 (기본: config/config.yaml)")
@click.option("--verbose", is_flag=True, default=False, help="상세 로그 출력")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None, verbose: bool) -> None:
    """IndieShout — 1인 개발자 마케팅 멀티 퍼블리셔"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    ctx.obj["logger"] = setup_logger(verbose)
    ctx.obj["verbose"] = verbose


@cli.group()
@click.pass_context
def blog(ctx: click.Context) -> None:
    """블로그 게시 명령"""
    pass


@blog.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--platforms", default=None, help="게시 대상 플랫폼 (쉼표 구분, 예: x,threads)")
@click.pass_context
def publish(ctx: click.Context, file: str, platforms: str | None) -> None:
    """마크다운 파일을 블로그에 게시하고 SNS에 링크를 공유합니다."""
    logger = ctx.obj["logger"]

    platform_list = [p.strip() for p in platforms.split(",")] if platforms else []

    with open(file) as f:
        text = f.read()

    content = Content(
        content_type=ContentType.BLOG,
        text=text,
        platforms=platform_list,
    )

    formatter = ContentFormatter()
    formatted = formatter.format_for_platform(content, "default")

    logger.info("블로그 게시 (dry-run)")
    logger.info(f"파일: {file}")
    logger.info(f"플랫폼: {platform_list or '(전체)'}")

    click.echo("--- dry-run 결과 ---")
    click.echo(f"타입: {content.content_type.value}")
    click.echo(f"파일: {file}")
    click.echo(f"플랫폼: {platform_list or '(전체)'}")
    click.echo(f"본문 길이: {len(text)}자")
    click.echo(f"포맷된 텍스트:\n{formatted[:200]}{'...' if len(formatted) > 200 else ''}")


@blog.command("publish-folder")
@click.argument("folder_name")
@click.option("--dry-run/--no-dry-run", default=False, help="Dry-run 모드 (기본: 비활성)")
@click.option("--skip-blog", is_flag=True, help="블로그 게시 건너뛰기")
@click.option("--skip-sns", is_flag=True, help="SNS 게시 건너뛰기")
@click.pass_context
def publish_folder(
    ctx: click.Context,
    folder_name: str,
    dry_run: bool,
    skip_blog: bool,
    skip_sns: bool,
) -> None:
    """blog-content 폴더에서 블로그 + SNS 통합 게시.

    폴더 구조:
        blog-content/{folder_name}/
            content.md    # 블로그 본문
            meta.md       # SNS 텍스트 + 메타데이터
            assets/       # 이미지들 (1.jpg, 2.png, ...)

    예시:
        indieshout blog publish-folder my-first-post
        indieshout blog publish-folder my-first-post --dry-run
        indieshout blog publish-folder my-first-post --skip-sns
    """
    config = ctx.obj["config"]

    try:
        workflow = PublishWorkflow(config)
        result = workflow.publish_from_folder(
            folder_name,
            dry_run=dry_run,
            skip_blog=skip_blog,
            skip_sns=skip_sns,
        )

        # 성공 여부 확인
        if result.get("blog") or skip_blog:
            click.echo("\n✅ 작업 완료!")
        else:
            click.echo("\n❌ 작업 실패")
            exit(1)

    except FileNotFoundError as e:
        click.echo(f"❌ 오류: {e}")
        click.echo("\n💡 팁: blog-content 폴더 구조를 확인하세요:")
        click.echo("  blog-content/")
        click.echo("    {folder_name}/")
        click.echo("      content.md")
        click.echo("      meta.md")
        click.echo("      assets/")
        exit(1)
    except Exception as e:
        click.echo(f"❌ 예상치 못한 오류: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


@cli.group()
@click.pass_context
def sns(ctx: click.Context) -> None:
    """SNS 게시 명령"""
    pass


@sns.command()
@click.argument("text")
@click.option("--image", default=None, type=click.Path(exists=True), help="첨부 이미지 경로")
@click.option("--platforms", default=None, help="게시 대상 플랫폼 (쉼표 구분, 예: x,threads)")
@click.option("--dry-run/--no-dry-run", default=True, help="Dry-run 모드 (기본: 활성)")
@click.pass_context
def post(ctx: click.Context, text: str, image: str | None, platforms: str | None, dry_run: bool) -> None:
    """텍스트를 SNS에 게시합니다."""
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    platform_list = [p.strip() for p in platforms.split(",")] if platforms else []
    image_paths = [image] if image else None

    content = Content(
        content_type=ContentType.SNS,
        text=text,
        platforms=platform_list,
        image_paths=image_paths,
    )

    if dry_run:
        formatter = ContentFormatter()
        formatted = formatter.format_for_platform(content, "default")

        logger.info("SNS 게시 (dry-run)")
        logger.info(f"플랫폼: {platform_list or '(전체)'}")

        click.echo("--- dry-run 결과 ---")
        click.echo(f"타입: {content.content_type.value}")
        click.echo(f"플랫폼: {platform_list or '(전체)'}")
        click.echo(f"이미지: {image or '없음'}")
        click.echo(f"포맷된 텍스트:\n{formatted}")
        return

    # 실제 게시 모드
    targets = platform_list or list(PLATFORM_PUBLISHERS.keys())
    results: list[dict] = []

    for platform in targets:
        publisher_cls = PLATFORM_PUBLISHERS.get(platform)
        if publisher_cls is None:
            click.echo(f"[{platform}] skipped — 미구현 플랫폼")
            results.append({"platform": platform, "status": "skipped"})
            continue

        try:
            publisher = publisher_cls(config)
            publisher.authenticate()
            publisher.validate(content)
            result = publisher.publish(content)
            click.echo(f"[{platform}] 게시 완료: {result}")
            results.append({"platform": platform, "status": "success", **result})
        except Exception as e:
            click.echo(f"[{platform}] 게시 실패: {e}")
            results.append({"platform": platform, "status": "error", "error": str(e)})

    # 결과 요약
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    click.echo(f"\n--- 결과: 성공 {success}, 실패 {failed}, 건너뜀 {skipped} ---")
