import click

from indieshout.formatter.content_formatter import ContentFormatter
from indieshout.models.content import Content, ContentType
from indieshout.publishers.threads import ThreadsPublisher
from indieshout.publishers.twitter import TwitterPublisher
from indieshout.utils.config import load_config
from indieshout.utils.logger import setup_logger

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
