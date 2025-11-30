import click
from duo.crawler import DuoCrawler

@click.group()
def cli():
    """duo-crawler CLI"""


@cli.command('hello', help='say hello')
def hello():
    click.echo("Hello, I'm DuoCrawler!")


@cli.command("sessions", help="download sessions from Duolingo")
def download_course():
    crawler = DuoCrawler()
    crawler.download_sessions()


@cli.command("base-info", help="download base info from Duolingo")
def download_base_info():
    crawler = DuoCrawler()
    crawler.download_base_info()


if __name__ == "__main__":
    cli()