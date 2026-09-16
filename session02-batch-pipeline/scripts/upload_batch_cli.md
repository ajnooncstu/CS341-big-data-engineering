# Upload a Monthly Batch

Valid batch:

```cmd
aws s3 cp data\valid\traffic_2026_06.csv s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06/
```

Invalid batch:

```cmd
aws s3 cp data\invalid\traffic_2026_06_bad.csv s3://<YOUR_BUCKET>/incoming/traffic/batch_id=2026-06-bad/
```

Verify:

```cmd
aws s3 ls s3://<YOUR_BUCKET>/incoming/traffic/ --recursive
```
