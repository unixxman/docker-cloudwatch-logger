# docker-cloudwatch-logger

## Install dependencies
```pip install -r requirements.txt```

## Example usage
```python logger.py --docker-image python --bash-command $'pip install pip -U && pip install tqdm && python -u -c \"import time\ncounter = 0\nwhile True:\n\tprint(counter)\n\tcounter = counter + 1\n\ttime.sleep(0.1)\"' --aws-cloudwatch-group test --aws-cloudwatch-stream test --aws-access-key-id $AWS_SECRET --aws-secret-access-key $AWS_KEY --aws-region $AWS_REGION```