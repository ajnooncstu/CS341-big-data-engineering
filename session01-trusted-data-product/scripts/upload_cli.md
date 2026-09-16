# Upload Raw Traffic Data Using AWS CLI

This guide assumes you are using:

- Windows
- Command Prompt (`cmd`)
- AWS Academy / Learner Lab
- AWS CLI

The goal is to upload the prepared traffic dataset from your computer to Amazon S3.

---

## 1. Start the AWS Learner Lab

Before using the AWS CLI:

1. Open the Learner Lab.
2. Click **Start Lab**.
3. Wait until the lab is ready.
4. Open the section that shows your temporary AWS CLI credentials.

You will need:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

Learner Lab credentials are temporary, so you may need to repeat this setup when you start a new lab session.

---

## 2. Open Command Prompt

Open Windows Command Prompt.

You can search for:

```text
cmd
```

Then open **Command Prompt**.

---

## 3. Set the AWS credentials in cmd

Replace the placeholders with the values from your Learner Lab.

```cmd
set AWS_ACCESS_KEY_ID=<your access key>
set AWS_SECRET_ACCESS_KEY=<your secret key>
set AWS_SESSION_TOKEN=<your session token>
```

Example:

```cmd
set AWS_ACCESS_KEY_ID=ASIAxxxxxxxxxxxx
set AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
set AWS_SESSION_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
```

Do not include angle brackets (`< >`) in the real command.

---

## 4. Verify your AWS identity

Run:

```cmd
aws sts get-caller-identity
```

If the credentials are working, you should see output containing information such as:

```text
Account
Arn
UserId
```

If the command fails:

1. Make sure the Learner Lab is still running.
2. Copy the latest temporary credentials again.
3. Run the three `set` commands again.
4. Retry:

```cmd
aws sts get-caller-identity
```

---

## 5. Move to the folder that contains the dataset

Use `cd` to move to the folder where you extracted the Session 1 dataset.

Example:

```cmd
cd C:\Users\Student\Downloads\CS341\Session01
```

Check that you can see the `raw` folder:

```cmd
dir
```

Expected structure:

```text
raw
└── traffic
    ├── year=2025
    └── year=2026
```

You can inspect the traffic folder with:

```cmd
dir raw\traffic
```

---

## 6. Check your S3 bucket

Replace `<YOUR_BUCKET>` with your actual bucket name.

```cmd
aws s3 ls s3://<YOUR_BUCKET>/
```

Example:

```cmd
aws s3 ls s3://cs341-yourstudentid/
```

If the bucket exists and your credentials are valid, the command should return the bucket contents.

---

## 7. Upload the raw traffic files

Run:

```cmd
aws s3 cp raw\traffic\ s3://<YOUR_BUCKET>/raw/traffic/ --recursive
```

Example:

```cmd
aws s3 cp raw\traffic\ s3://cs341-yourstudentid/raw/traffic/ --recursive
```

This copies all files and subfolders under:

```text
raw\traffic\
```

to:

```text
s3://<YOUR_BUCKET>/raw/traffic/
```

---

## 8. Verify the upload

Run:

```cmd
aws s3 ls s3://<YOUR_BUCKET>/raw/traffic/ --recursive
```

Check that:

- the monthly CSV files are present;
- both `year=2025` and `year=2026` appear;
- the folder structure is correct;
- no expected month is missing.

The uploaded structure should look conceptually like:

```text
raw/traffic/year=2025/month=06/traffic_2025_06.csv
raw/traffic/year=2025/month=07/traffic_2025_07.csv
...
raw/traffic/year=2026/month=05/traffic_2026_05.csv
```

---

## 9. Checkpoint

Before continuing to Glue, confirm:

- [ ] `aws sts get-caller-identity` works
- [ ] the bucket is accessible
- [ ] all expected files are in S3
- [ ] the S3 folder structure is correct

Think about:

> Which step was ingestion?

> Which AWS service is storing the data?

At this point, the files are stored in S3, but they are not yet a queryable table.

Next:

> Create a Glue Data Catalog table for the files in `s3://<YOUR_BUCKET>/raw/traffic/`.
