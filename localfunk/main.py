import argparse
import os
import subprocess

from pyngrok import ngrok

from localfunk import sam, server


def main():
    parser = parse()
    args = parser.parse_args()
    run(args)


def parse():
    parser = argparse.ArgumentParser(description="Proxy Lambdas to local code")
    parser.add_argument(
        "--template", type=str, default="template.yaml", help="path to template",
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="port to run local server on",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="url to proxy to, will skip starting ngrok",
    )
    parser.add_argument(
        "--guided",
        action="store_true",
        help="use guided in sam deploy, will use this by default if no samconfig.toml found",
    )
    parser.add_argument(
        "--server", action="store_true", help="only run local server",
    )
    return parser


def run(args):
    temp_template = "./locafunk_template.yaml"

    if args.server:
        server.start(args.port, args.template)
    else:
        # ngrok
        if args.url:
            public_url = args.url
        else:
            public_url = ngrok.connect(args.port).public_url

        # build
        sam.build(public_url.split("//")[-1], args.template, temp_template)

        # deploy
        deploy_command = ["sam", "deploy", f"-t{temp_template}"]
        if args.guided or not os.path.exists("samconfig.toml"):
            deploy_command.append("--guided")
        subprocess.run(deploy_command, check=True)

        sam.cleanup(temp_template)

        # local server
        server.start(args.port, args.template)
