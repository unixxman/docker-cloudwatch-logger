import subprocess
import logging

import click
import boto3
import watchtower

logging.basicConfig(level=logging.INFO)


class Container:
    def __init__(self, docker_image: str, bash_command: str, cw_group: str, cw_stream: str,
               aws_key: str, aws_secret: str, aws_region: str):
        self.logger = self.get_logger(
            cw_group, cw_stream,
            aws_key, aws_secret, aws_region)
        self.docker_image = docker_image
        self.bash_command = bash_command
        self.proc = None

    def run(self) -> None:
        # note - if you want to use a python script as the bash_command,
        # you must disable output buffering to be able to capture logs.
        # Use the -u command line switch (python -u ...)
        # or set the PYTHONUNBUFFERED env var in the docker container.
        run_command = f'docker run --name {self.docker_image}-container {self.docker_image} {self.bash_command}'
        self.proc = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE)
        for line in iter(self.proc.stdout.readline, b''):
            self.logger.info(line.decode('utf-8'))

    def stop(self):
        if self.proc:
            subprocess.run(['docker', 'rm', f'{self.docker_image}-container'])
            print('containder is deleted')
        

    @staticmethod
    def get_logger(cw_group: str, cw_stream: str,
                aws_key: str, aws_secret: str, aws_region: str) -> logging.Logger:
        logger = logging.getLogger(__name__)
        client = boto3.client(
            'logs',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region
        )
        logger.addHandler(
            watchtower.CloudWatchLogHandler(
                log_group_name=cw_group, 
                log_stream_name=cw_stream, boto3_client=client
            )
        )
        return logger


@click.command()
@click.option('--docker-image', required=True,  help='Name of a Docker image')
@click.option('--bash-command', required=True, help='Bash command to run inside the Docker image')
@click.option('--aws-cloudwatch-group', required=True, help='AWS CloudWatch group to publish logs')
@click.option('--aws-cloudwatch-stream', required=True, help='AWS CloudWatch stream to publish logs')
@click.option('--aws-access-key-id', required=True)
@click.option('--aws-secret-access-key', required=True)
@click.option('--aws-region', default='us-east-1')
def main(docker_image, bash_command, aws_cloudwatch_group, aws_cloudwatch_stream,
         aws_access_key_id, aws_secret_access_key, aws_region):
    container = Container(docker_image, bash_command, aws_cloudwatch_group, aws_cloudwatch_stream,
                          aws_access_key_id, aws_secret_access_key, aws_region)
    try:
        container.run()
    finally:
        container.stop()


if __name__ == '__main__':
    main()
