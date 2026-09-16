# AWS Step Functions Orchestration

Suggested teaching flow:

```text
Start
  |
CheckBatch
  |
AlreadyProcessed?
   /          \
 YES          NO
  |            |
 Stop       Validate
               |
             Valid?
             /    \
           YES     NO
            |       |
       Transform  Quarantine
            |
          Verify
            |
          Success
```

`state-machine.json` is a scaffold. Replace placeholder Lambda ARNs with actual resources if you execute it in AWS.
